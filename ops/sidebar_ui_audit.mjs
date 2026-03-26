import playwright from '/home/lebedeffson/Code/Документооборот/.tmp_e2e/node_modules/playwright/index.js';

const { chromium } = playwright;
const base = 'https://localhost:18443';

const browser = await chromium.launch({
  headless: true,
  args: ['--ignore-certificate-errors'],
});

const context = await browser.newContext({
  ignoreHTTPSErrors: true,
  viewport: { width: 1440, height: 1200 },
});

const page = await context.newPage();
const issues = [];
let currentUrl = '';

page.on('framenavigated', frame => {
  if (frame === page.mainFrame()) currentUrl = frame.url();
});

page.on('pageerror', err => {
  issues.push({
    type: 'pageerror',
    url: currentUrl,
    message: err.message,
  });
});

page.on('console', msg => {
  if (msg.type() === 'error') {
    issues.push({
      type: 'console',
      url: currentUrl,
      message: msg.text(),
    });
  }
});

try {
  await page.goto(`${base}/index.php?module=users/login`, { waitUntil: 'networkidle' });
  await page.locator('input[name="username"]').fill('admin');
  await page.locator('input[name="password"]').fill('admin123');
  await Promise.all([
    page.waitForNavigation({ waitUntil: 'networkidle' }),
    page.locator('button[type="submit"], input[type="submit"]').first().click(),
  ]);

  const links = await page.$$eval('ul.page-sidebar-menu a[href]', nodes =>
    nodes
      .map(node => ({
        text: node.innerText.replace(/\s+/g, ' ').trim(),
        href: node.href,
      }))
      .filter(item => item.text)
  );

  const uniqueLinks = [];
  const seen = new Set();

  for (const link of links) {
    const key = `${link.text}|${link.href}`;
    if (!seen.has(key)) {
      seen.add(key);
      uniqueLinks.push(link);
    }
  }

  const visited = [];

  for (const link of uniqueLinks) {
    if (!link.href.startsWith(base)) continue;
    if (link.href.includes('logout')) continue;

    try {
      await page.goto(link.href, { waitUntil: 'networkidle', timeout: 25000 });
      const title = await page.locator('h1,.page-title,.caption').first().innerText().catch(() => '');
      visited.push({
        text: link.text,
        href: link.href,
        ok: true,
        title,
      });
    } catch (error) {
      visited.push({
        text: link.text,
        href: link.href,
        ok: false,
        error: error.message,
      });
      issues.push({
        type: 'nav-fail',
        url: link.href,
        message: error.message,
      });
    }
  }

  const result = {
    status: issues.length ? 'failed' : 'ok',
    checked: visited.length,
    issues,
    visited,
  };

  console.log(JSON.stringify(result, null, 2));

  if (issues.length) {
    process.exitCode = 1;
  }
} finally {
  await context.close();
  await browser.close();
}
