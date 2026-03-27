import { mkdirSync } from 'node:fs';
import { resolveBrowserRuntime, buildLaunchOptions } from './playwright_runtime.mjs';
import { publicBase } from './runtime_config.mjs';

const runtime = resolveBrowserRuntime(process.env.PLAYWRIGHT_BROWSER || 'firefox');
const { browserName, browserType, executablePath, available } = runtime;

if (!available) {
  console.log(JSON.stringify({
    status: 'skipped',
    browser: browserName,
    reason: `Browser executable for ${browserName} not found`,
  }, null, 2));
  process.exit(0);
}

const base = publicBase;
mkdirSync('/home/lebedeffson/Code/Документооборот/.tmp_e2e', { recursive: true });
const browser = await browserType.launch(buildLaunchOptions(browserName, executablePath));
const context = await browser.newContext({ ignoreHTTPSErrors: true });
const page = await context.newPage();
const errors = [];
page.on('console', msg => {
  if (msg.type() === 'error') errors.push(`console:${msg.text()}`);
});
page.on('pageerror', err => errors.push(`pageerror:${err.message}`));

try {
  await page.goto(`${base}/index.php?module=users/login`, { waitUntil: 'domcontentloaded' });
  await page.locator('input[name="username"]').fill('admin');
  await page.locator('input[name="password"]').fill('admin123');
  await page.locator('button[type="submit"], input[type="submit"]').first().click();
  await page.waitForURL(/module=dashboard\/?/);

  await page.goto(`${base}/index.php?module=items/info&path=25-1`, { waitUntil: 'domcontentloaded' });
  const editorLink = page.locator('a:has-text("Открыть документ в редакторе")').first();
  await editorLink.waitFor({ state: 'visible', timeout: 15000 });

  const [popup] = await Promise.all([
    page.waitForEvent('popup'),
    editorLink.click(),
  ]);

  popup.on('console', msg => {
    if (msg.type() === 'error') errors.push(`popup-console:${msg.text()}`);
  });
  popup.on('pageerror', err => errors.push(`popup-pageerror:${err.message}`));

  await popup.waitForLoadState('domcontentloaded');
  await popup.waitForTimeout(7000);

  const popupUrl = popup.url();
  const iframeEditor = await popup.locator('#iframeEditor').count();
  const iframeCount = await popup.locator('iframe').count();
  const scriptCount = await popup.locator('script[src*="/office/web-apps/apps/api/documents/api.js"]').count();
  const bodyText = await popup.locator('body').innerText().catch(() => '');
  const hasFailureText = /загрузка не удалась|loading failed|download failed|document loading failed/i.test(bodyText);
  const docEditorDefined = await popup.evaluate(() => typeof window.docEditor !== 'undefined').catch(() => false);
  const frameUrls = popup.frames().map(frame => frame.url());
  const editorFrameLoaded = frameUrls.some(url => url.includes('/office/') && url.includes('/documenteditor/'));
  const screenshotPath = `/home/lebedeffson/Code/Документооборот/.tmp_e2e/onlyoffice-browser-e2e-${browserName}.png`;
  await popup.screenshot({ path: screenshotPath, fullPage: true }).catch(() => {});

  const result = {
    status: errors.length || hasFailureText || !scriptCount || !iframeCount || !editorFrameLoaded ? 'failed' : 'ok',
    browser: browserName,
    popupUrl,
    iframeEditor,
    iframeCount,
    scriptCount,
    docEditorDefined,
    editorFrameLoaded,
    frameUrls,
    hasFailureText,
    screenshotPath,
    bodySnippet: bodyText.slice(0, 1000),
    errors,
  };

  console.log(JSON.stringify(result, null, 2));
  if (result.status !== 'ok') {
    process.exitCode = 1;
  }
  await popup.close();
} finally {
  await context.close();
  await browser.close();
}
