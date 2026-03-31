import { resolveBrowserRuntime, buildLaunchOptions } from './playwright_runtime.mjs';
import {
  docspaceBase,
  workspaceBase,
  docspaceEnabled,
  workspaceEnabled,
  docspaceTargetUrl,
  workspaceTargetUrl,
  officeAdminEmail,
  officeAdminPassword,
} from './runtime_config.mjs';

const runtime = resolveBrowserRuntime(process.env.PLAYWRIGHT_BROWSER || 'chromium');
if (!runtime.available) {
  console.log(JSON.stringify({ status: 'skipped', reason: 'browser_unavailable', runtime }, null, 2));
  process.exit(0);
}

const browser = await runtime.browserType.launch(buildLaunchOptions(runtime));
const context = await browser.newContext({ ignoreHTTPSErrors: true });

async function bootstrapWorkspace(page) {
  await page.goto(`${workspaceBase}/Wizard.aspx`, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(1500);

  if (!(await page.locator('#newEmailAddress').count())) {
    return { bootstrapped: false, wizardDetected: false, url: page.url() };
  }

  await page.locator('#newEmailAddress').fill(officeAdminEmail);
  await page.locator('#newPwd').fill(officeAdminPassword);
  await page.locator('#confPwd').fill(officeAdminPassword);
  if (await page.locator('#policyAcceptedOpenSource').count()) {
    await page.locator('#policyAcceptedOpenSource').check();
  }
  await page.locator('#saveSettingsBtn').click();
  await page.waitForTimeout(5000);

  return {
    bootstrapped: true,
    wizardDetected: true,
    url: page.url(),
  };
}

async function checkWorkspace() {
  const page = await context.newPage();
  const bootstrap = await bootstrapWorkspace(page);

  await page.goto(`${workspaceBase}/Auth.aspx?refererurl=%2fDefault.aspx`, { waitUntil: 'domcontentloaded' });
  await page.fill('#login', officeAdminEmail);
  await page.fill('#pwd', officeAdminPassword);
  await page.click('#loginButton');
  await page.waitForTimeout(5000);

  const url = page.url();
  const body = ((await page.textContent('body')) || '').slice(0, 1000);
  const success =
    url.includes('/workspace/Default.aspx') ||
    /My documents|Calendar|Portal Settings|Documents/i.test(body);

  await page.close();
  return {
    name: 'workspace_auth',
    enabled: workspaceEnabled && Boolean(workspaceTargetUrl),
    ok: success,
    url,
    bootstrap,
    body,
  };
}

async function checkDocspace() {
  const page = await context.newPage();
  const seen = [];

  page.on('response', async (resp) => {
    const req = resp.request();
    const url = resp.url();
    if (req.method() === 'POST' && /\/api\/2\.0\/authentication$/.test(url)) {
      let text = '';
      try {
        text = (await resp.text()).slice(0, 800);
      } catch {}
      seen.push({ url, status: resp.status(), text });
    }
  });

  await page.goto(`${docspaceBase}/login`, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(1500);
  const email = page.locator('#login_username, input[type="email"], input[name="email"], #login');
  const password = page.locator('#login_password, input[type="password"]');
  if (await email.count()) {
    await email.first().fill(officeAdminEmail);
  }
  if (await password.count()) {
    await password.first().fill(officeAdminPassword);
  }
  const button = page.locator('#login_submit, button:has-text("Sign in"), button:has-text("Sign In"), input[type="submit"]');
  if (await button.count()) {
    await button.first().click();
  }
  await page.waitForTimeout(5000);

  const authResponse = seen.find(item => item.url.includes('/api/2.0/authentication'));
  const url = page.url();
  const body = ((await page.textContent('body')) || '').slice(0, 1000);
  await page.close();

  return {
    name: 'docspace_auth',
    enabled: docspaceEnabled && Boolean(docspaceTargetUrl),
    ok: Boolean(authResponse && authResponse.status === 200),
    url,
    authResponse,
    body,
  };
}

const checks = [];
if (docspaceEnabled && docspaceTargetUrl) {
  checks.push(await checkDocspace());
}
if (workspaceEnabled && workspaceTargetUrl) {
  checks.push(await checkWorkspace());
}

await browser.close();

const failures = checks.filter(check => check.enabled && !check.ok);
const payload = {
  status: failures.length ? 'failed' : 'ok',
  checks,
  failures: failures.map(check => `${check.name} failed`),
};

console.log(JSON.stringify(payload, null, 2));
if (failures.length) {
  process.exit(1);
}
