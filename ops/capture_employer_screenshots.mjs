import { mkdirSync } from 'node:fs';
import { resolveBrowserRuntime, buildLaunchOptions } from './playwright_runtime.mjs';
import { publicBase, docsBase, bridgeBase, naudocUsername, naudocPassword } from './runtime_config.mjs';

const runtime = resolveBrowserRuntime(process.env.PLAYWRIGHT_BROWSER || 'chromium');
const base = publicBase;
const outDir = '/home/lebedeffson/Code/Документооборот/docs/screenshots/employer';

mkdirSync(outDir, { recursive: true });

const browser = await runtime.browserType.launch(buildLaunchOptions(runtime.browserName, runtime.executablePath));

async function screenshotLogin() {
  const context = await browser.newContext({
    ignoreHTTPSErrors: true,
    viewport: { width: 1440, height: 1200 },
  });
  const page = await context.newPage();
  await page.goto(`${base}/index.php?module=users/login`, { waitUntil: 'networkidle' });
  await page.screenshot({ path: `${outDir}/01-login.png`, fullPage: true });
  await context.close();
}

async function loginRukovoditel(context, username, password) {
  const page = await context.newPage();
  await page.goto(`${base}/index.php?module=users/login`, { waitUntil: 'networkidle' });
  await page.locator('input[name="username"]').fill(username);
  await page.locator('input[name="password"]').fill(password);
  await Promise.all([
    page.waitForNavigation({ waitUntil: 'networkidle' }),
    page.locator('button[type="submit"], input[type="submit"]').first().click(),
  ]);
  return page;
}

async function screenshotAdmin() {
  const context = await browser.newContext({
    ignoreHTTPSErrors: true,
    viewport: { width: 1440, height: 1200 },
  });
  const page = await loginRukovoditel(context, 'admin', 'admin123');

  await page.goto(`${base}/index.php?module=dashboard/dashboard`, { waitUntil: 'networkidle' });
  await page.screenshot({ path: `${outDir}/02-admin-dashboard.png`, fullPage: true });

  await page.goto(`${base}/index.php?module=reports/view&reports_id=72`, { waitUntil: 'networkidle' });
  await page.screenshot({ path: `${outDir}/03-admin-tasks.png`, fullPage: true });

  await page.goto(`${base}/index.php?module=items/items&path=23`, { waitUntil: 'networkidle' });
  await page.screenshot({ path: `${outDir}/04-admin-requests.png`, fullPage: true });

  await page.goto(`${base}/index.php?module=items/items&path=21`, { waitUntil: 'networkidle' });
  await page.screenshot({ path: `${outDir}/05-admin-projects.png`, fullPage: true });

  await page.goto(`${base}/index.php?module=reports/view&reports_id=307`, { waitUntil: 'networkidle' });
  await page.screenshot({ path: `${outDir}/06-admin-discussions.png`, fullPage: true });

  await page.goto(`${base}/index.php?module=items/items&path=25`, { waitUntil: 'networkidle' });
  await page.screenshot({ path: `${outDir}/07-admin-documents.png`, fullPage: true });

  await page.goto(`${base}/index.php?module=items/items&path=26`, { waitUntil: 'networkidle' });
  await page.screenshot({ path: `${outDir}/08-admin-document-base.png`, fullPage: true });

  await page.goto(`${base}/index.php?module=items/items&path=27`, { waitUntil: 'networkidle' });
  await page.screenshot({ path: `${outDir}/09-admin-mts.png`, fullPage: true });

  await page.goto(`${base}/index.php?module=reports/view&reports_id=80`, { waitUntil: 'networkidle' });
  await page.screenshot({ path: `${outDir}/10-admin-control-report.png`, fullPage: true });

  await context.close();
}

async function screenshotUser() {
  const context = await browser.newContext({
    ignoreHTTPSErrors: true,
    viewport: { width: 1440, height: 1200 },
  });
  const page = await loginRukovoditel(context, 'user.demo', 'rolepass123');

  await page.goto(`${base}/index.php?module=dashboard/dashboard`, { waitUntil: 'networkidle' });
  await page.screenshot({ path: `${outDir}/11-user-dashboard.png`, fullPage: true });

  await page.goto(`${base}/index.php?module=items/items&path=23`, { waitUntil: 'networkidle' });
  await page.screenshot({ path: `${outDir}/12-user-requests.png`, fullPage: true });

  await page.goto(`${base}/index.php?module=reports/view&reports_id=466`, { waitUntil: 'networkidle' });
  await page.screenshot({ path: `${outDir}/13-user-tasks.png`, fullPage: true });

  await page.goto(`${base}/index.php?module=items/items&path=21`, { waitUntil: 'networkidle' });
  await page.screenshot({ path: `${outDir}/14-user-projects.png`, fullPage: true });

  await page.goto(`${base}/index.php?module=items/items&path=25`, { waitUntil: 'networkidle' });
  await page.screenshot({ path: `${outDir}/15-user-documents.png`, fullPage: true });

  await page.goto(`${base}/index.php?module=items/info&path=25-1`, { waitUntil: 'networkidle' });
  await page.screenshot({ path: `${outDir}/16-user-document-card.png`, fullPage: true });

  const editorLink = page.locator('a:has-text("Открыть документ в редакторе")').first();
  const [popup] = await Promise.all([
    page.waitForEvent('popup'),
    editorLink.click(),
  ]);
  await popup.waitForLoadState('domcontentloaded');
  await popup.waitForTimeout(7000);
  await popup.screenshot({ path: `${outDir}/19-onlyoffice-editor.png`, fullPage: true });
  await popup.close();

  await page.goto(`${base}/index.php?module=items/items&path=26`, { waitUntil: 'networkidle' });
  await page.screenshot({ path: `${outDir}/17-user-document-base.png`, fullPage: true });

  await page.goto(`${base}/index.php?module=items/items&path=27`, { waitUntil: 'networkidle' });
  await page.screenshot({ path: `${outDir}/18-user-mts.png`, fullPage: true });

  await context.close();
}

async function screenshotNauDoc() {
  const context = await browser.newContext({
    ignoreHTTPSErrors: true,
    viewport: { width: 1440, height: 1200 },
    httpCredentials: {
      username: naudocUsername,
      password: naudocPassword,
    },
  });
  const page = await context.newPage();
  await page.goto(`${docsBase}/home`, { waitUntil: 'networkidle' });
  await page.screenshot({ path: `${outDir}/20-naudoc-home.png`, fullPage: true });
  await page.goto(`${docsBase}/storage/view`, { waitUntil: 'networkidle' });
  await page.screenshot({ path: `${outDir}/21-naudoc-storage.png`, fullPage: true });
  await page.goto(`${base}/docs/storage/system/directories/staff_list_directory/view`, { waitUntil: 'networkidle' });
  await page.screenshot({ path: `${outDir}/22-naudoc-staff-directory.png`, fullPage: true });
  await context.close();
}

async function screenshotBridge() {
  const context = await browser.newContext({
    ignoreHTTPSErrors: true,
    viewport: { width: 1440, height: 1200 },
  });
  const page = await context.newPage();
  await page.goto(`${bridgeBase}/`, { waitUntil: 'networkidle' });
  await page.screenshot({ path: `${outDir}/23-bridge-overview.png`, fullPage: true });
  await context.close();
}

try {
  await screenshotLogin();
  await screenshotAdmin();
  await screenshotUser();
  await screenshotNauDoc();
  await screenshotBridge();

  console.log(JSON.stringify({
    status: 'ok',
    browser: runtime.browserName,
    outDir,
    files: [
        '01-login.png',
        '02-admin-dashboard.png',
        '03-admin-tasks.png',
        '04-admin-requests.png',
        '05-admin-projects.png',
        '06-admin-discussions.png',
        '07-admin-documents.png',
        '08-admin-document-base.png',
        '09-admin-mts.png',
        '10-admin-control-report.png',
        '11-user-dashboard.png',
        '12-user-requests.png',
        '13-user-tasks.png',
        '14-user-projects.png',
        '15-user-documents.png',
        '16-user-document-card.png',
        '17-user-document-base.png',
        '18-user-mts.png',
        '19-onlyoffice-editor.png',
        '20-naudoc-home.png',
        '21-naudoc-storage.png',
        '22-naudoc-staff-directory.png',
        '23-bridge-overview.png',
    ],
  }, null, 2));
} finally {
  await browser.close();
}
