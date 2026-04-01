import { resolveBrowserRuntime, buildLaunchOptions } from './playwright_runtime.mjs';
import {
  workspaceBase,
  workspaceEnabled,
  workspaceTargetUrl,
  officeAdminEmail,
  officeAdminPassword,
} from './runtime_config.mjs';

const runtime = resolveBrowserRuntime(process.env.PLAYWRIGHT_BROWSER || 'chromium');
if (!runtime.available) {
  console.log(JSON.stringify({ status: 'skipped', reason: 'browser_unavailable', runtime }, null, 2));
  process.exit(0);
}

if (!workspaceEnabled) {
  console.log(JSON.stringify({ status: 'skipped', reason: 'workspace_disabled' }, null, 2));
  process.exit(0);
}

const browser = await runtime.browserType.launch(buildLaunchOptions(runtime));
const context = await browser.newContext({ ignoreHTTPSErrors: true });
const page = await context.newPage();

await page.goto(
  `${workspaceBase}/Auth.aspx?refererurl=${encodeURIComponent('/addons/calendar/')}`,
  { waitUntil: 'domcontentloaded' }
);

if (await page.locator('#login').count()) {
  await page.fill('#login', officeAdminEmail);
  await page.fill('#pwd', officeAdminPassword);
  await page.click('#loginButton');
}

await page.waitForTimeout(8000);

const url = page.url();
const title = await page.title();
const body = ((await page.textContent('body')) || '').slice(0, 2000);
const ok =
  /\/workspace\/addons\/calendar\//i.test(url) &&
  (/Calendar/i.test(title) || /Calendar/i.test(body));

await browser.close();

const payload = {
  status: ok ? 'ok' : 'failed',
  check: {
    name: 'workspace_calendar_entry',
    enabled: workspaceEnabled && Boolean(workspaceTargetUrl),
    ok,
    url,
    title,
    body,
  },
  failures: ok ? [] : ['workspace_calendar_entry failed'],
};

console.log(JSON.stringify(payload, null, 2));
if (!ok) {
  process.exit(1);
}
