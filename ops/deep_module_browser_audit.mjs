import { mkdirSync } from 'node:fs';
import { resolveBrowserRuntime, buildLaunchOptions } from './playwright_runtime.mjs';
import {
  publicBase,
  docsBase,
  bridgeBase,
  naudocUsername,
  naudocPassword,
  adminUsername,
  adminPassword,
  employeeUsername,
  nurseUsername,
  roleDefaultPassword,
} from './runtime_config.mjs';

const base = publicBase;
const runtime = resolveBrowserRuntime(process.env.PLAYWRIGHT_BROWSER || 'chromium');

if (!runtime.available) {
  console.log(JSON.stringify({
    status: 'skipped',
    browser: runtime.browserName,
    reason: `Browser executable for ${runtime.browserName} not found`,
    checked: 0,
    issues: [],
    visited: [],
  }, null, 2));
  process.exit(0);
}

const outDir = '/home/lebedeffson/Code/Документооборот/.tmp_e2e/deep-module-audit';
mkdirSync(outDir, { recursive: true });

const browser = await runtime.browserType.launch(buildLaunchOptions(runtime.browserName, runtime.executablePath));

const textErrorPatterns = [
  /warning:/i,
  /deprecated:/i,
  /fatal error/i,
  /parse error/i,
  /traceback/i,
  /nameerror/i,
  /unauthorized/i,
  /not found/i,
  /не авторизованы/i,
  /доступ запрещен/i,
  /неправильн.*парол/i,
  /внутренняя ошибка сервера/i,
  /при выполнении вашей операции произошла внутренняя ошибка сервера/i,
  /загрузка не удалась/i,
  /document loading failed/i,
  /download failed/i,
];

const overlapSelectors = [
  '.platform-switcher a',
  '.platform-entry-grid .platform-card',
  '.platform-module-grid .platform-card',
  '.platform-status-grid .platform-card',
];

function attachPageWatchers(page, issues, contextLabel) {
  page.on('pageerror', err => {
    issues.push({
      type: 'pageerror',
      context: contextLabel,
      url: page.url(),
      message: err.message,
    });
  });

  page.on('console', msg => {
    if (msg.type() === 'error') {
      issues.push({
        type: 'console',
        context: contextLabel,
        url: page.url(),
        message: msg.text(),
      });
    }
  });
}

async function loginRukovoditel(username, password, roleLabel, issues) {
  const context = await browser.newContext({
    ignoreHTTPSErrors: true,
    viewport: { width: 1440, height: 1200 },
  });
  const page = await context.newPage();
  attachPageWatchers(page, issues, `${roleLabel}:login`);

  await page.goto(`${base}/index.php?module=users/login`, { waitUntil: 'domcontentloaded' });
  await page.locator('input[name="username"]').fill(username);
  await page.locator('input[name="password"]').fill(password);
  await Promise.all([
    page.waitForNavigation({ waitUntil: 'domcontentloaded' }),
    page.locator('button[type="submit"], input[type="submit"]').first().click(),
  ]);

  return { context, page };
}

async function checkVisibleOverlaps(page, url) {
  return await page.evaluate((selectors) => {
    const overlaps = [];

    for (const selector of selectors) {
      const elements = Array.from(document.querySelectorAll(selector)).filter((node) => {
        const rect = node.getBoundingClientRect();
        return rect.width > 0 && rect.height > 0;
      });

      for (let i = 0; i < elements.length; i += 1) {
        const a = elements[i].getBoundingClientRect();

        for (let j = i + 1; j < elements.length; j += 1) {
          const b = elements[j].getBoundingClientRect();
          const intersects = !(a.right <= b.left || b.right <= a.left || a.bottom <= b.top || b.bottom <= a.top);

          if (intersects) {
            overlaps.push({
              selector,
              first: elements[i].textContent.trim().slice(0, 80),
              second: elements[j].textContent.trim().slice(0, 80),
              url,
            });
          }
        }
      }
    }

    return overlaps;
  }, overlapSelectors);
}

async function auditPage(page, route, role, issues, visited) {
  console.error(`[deep-audit] ${role} -> ${route.label}`);
  await page.goto(route.url, { waitUntil: route.waitUntil || 'domcontentloaded', timeout: 35000 });
  await page.waitForTimeout(400);

  const bodyText = await page.locator('body').innerText().catch(() => '');
  const matchedPattern = textErrorPatterns.find((pattern) => pattern.test(bodyText));
  const title = await page.locator('h1,.page-title,.caption,.page-header h1').first().innerText().catch(() => '');
  const overlaps = await checkVisibleOverlaps(page, route.url).catch(() => []);

  if (matchedPattern) {
    issues.push({
      type: 'body-text-error',
      role,
      url: route.url,
      label: route.label,
      message: matchedPattern.toString(),
    });
  }

  if (overlaps.length) {
    issues.push({
      type: 'layout-overlap',
      role,
      url: route.url,
      label: route.label,
      message: JSON.stringify(overlaps.slice(0, 5)),
    });
  }

  if (route.expectText) {
    const matched = bodyText.includes(route.expectText);
    if (!matched) {
      issues.push({
        type: 'missing-text',
        role,
        url: route.url,
        label: route.label,
        message: `Expected text not found: ${route.expectText}`,
      });
    }
  }

  visited.push({
    role,
    label: route.label,
    url: route.url,
    ok: !matchedPattern && !overlaps.length,
    title,
  });

  if (matchedPattern || overlaps.length) {
    const safeLabel = `${role}-${route.label}`.toLowerCase().replace(/[^a-z0-9а-яё_-]+/gi, '-');
    await page.screenshot({
      path: `${outDir}/${safeLabel}-${runtime.browserName}.png`,
      fullPage: true,
    }).catch(() => {});
  }
}

async function auditOnlyoffice(role, issues, visited) {
  console.error(`[deep-audit] ${role.label} -> onlyoffice-editor`);
  const { context, page } = await loginRukovoditel(role.username, role.password, `${role.label}:onlyoffice`, issues);

  try {
    await page.goto(`${base}/index.php?module=items/info&path=25-1`, { waitUntil: 'domcontentloaded' });
    const editorLink = page.locator('a:has-text("Открыть документ в редакторе")').first();
    await editorLink.waitFor({ state: 'visible', timeout: 15000 });

    const [popup] = await Promise.all([
      page.waitForEvent('popup'),
      editorLink.click(),
    ]);

    attachPageWatchers(popup, issues, `${role.label}:onlyoffice-popup`);
    await popup.waitForLoadState('domcontentloaded');
    await popup.waitForTimeout(7000);

    const bodyText = await popup.locator('body').innerText().catch(() => '');
    const frameUrls = popup.frames().map((frame) => frame.url());
    const editorFrameLoaded = frameUrls.some((url) => url.includes('/office/') && url.includes('/documenteditor/'));
    const hasFailureText = textErrorPatterns.some((pattern) => pattern.test(bodyText));

    if (!editorFrameLoaded || hasFailureText) {
      issues.push({
        type: 'onlyoffice-failed',
        role: role.label,
        url: popup.url(),
        label: 'onlyoffice-editor',
        message: `editorFrameLoaded=${editorFrameLoaded}; hasFailureText=${hasFailureText}`,
      });

      await popup.screenshot({
        path: `${outDir}/${role.label.toLowerCase()}-onlyoffice-${runtime.browserName}.png`,
        fullPage: true,
      }).catch(() => {});
    }

    visited.push({
      role: role.label,
      label: 'onlyoffice-editor',
      url: popup.url(),
      ok: editorFrameLoaded && !hasFailureText,
      title: 'ONLYOFFICE Docs',
    });

    await popup.close();
  } finally {
    await context.close();
  }
}

async function auditRukovoditelRole(role, routes, issues, visited) {
  const { context, page } = await loginRukovoditel(role.username, role.password, role.label, issues);

  try {
    for (const route of routes) {
      await auditPage(page, route, role.label, issues, visited);
    }
  } finally {
    await context.close();
  }
}

async function auditNauDoc(issues, visited) {
  console.error('[deep-audit] naudoc -> login');
  const context = await browser.newContext({
    ignoreHTTPSErrors: true,
    viewport: { width: 1440, height: 1200 },
    httpCredentials: {
      username: naudocUsername,
      password: naudocPassword,
    },
  });
  const page = await context.newPage();
  attachPageWatchers(page, issues, 'naudoc');

  const routes = [
    { label: 'naudoc-home', url: `${docsBase}/home`, waitUntil: 'domcontentloaded' },
    { label: 'naudoc-storage', url: `${docsBase}/storage/view`, waitUntil: 'domcontentloaded' },
    { label: 'naudoc-staff-directory', url: `${docsBase}/storage/system/directories/staff_list_directory/view`, waitUntil: 'domcontentloaded' },
    { label: 'naudoc-department-directory', url: `${docsBase}/storage/system/directories/department_list_directory/view`, waitUntil: 'domcontentloaded' },
  ];

  try {
    for (const route of routes) {
      await auditPage(page, route, 'naudoc', issues, visited);
    }
  } finally {
    await context.close();
  }
}

async function auditBridge(issues, visited) {
  console.error('[deep-audit] bridge -> overview');
  const context = await browser.newContext({
    ignoreHTTPSErrors: true,
    viewport: { width: 1440, height: 1200 },
  });
  const page = await context.newPage();
  attachPageWatchers(page, issues, 'bridge');

  try {
    await auditPage(page, {
      label: 'bridge-overview',
      url: `${bridgeBase}/`,
      waitUntil: 'domcontentloaded',
      expectText: 'NauDoc Bridge',
    }, 'bridge', issues, visited);
  } finally {
    await context.close();
  }
}

const adminRoutes = [
  { label: 'dashboard', url: `${base}/index.php?module=dashboard/dashboard` },
  { label: 'requests-list', url: `${base}/index.php?module=items/items&path=23` },
  { label: 'requests-form', url: `${base}/index.php?module=items/form&path=23` },
  { label: 'tasks-list', url: `${base}/index.php?module=reports/view&reports_id=72` },
  { label: 'tasks-form', url: `${base}/index.php?module=items/form&path=21-1-22` },
  { label: 'projects-list', url: `${base}/index.php?module=items/items&path=21` },
  { label: 'projects-form', url: `${base}/index.php?module=items/form&path=21` },
  { label: 'discussions-list', url: `${base}/index.php?module=reports/view&reports_id=307` },
  { label: 'discussions-form', url: `${base}/index.php?module=items/form&path=21-1-24` },
  { label: 'documents-list', url: `${base}/index.php?module=items/items&path=25` },
  { label: 'documents-card', url: `${base}/index.php?module=items/info&path=25-1` },
  { label: 'documents-form', url: `${base}/index.php?module=items/form&path=25` },
  { label: 'document-base-list', url: `${base}/index.php?module=items/items&path=26` },
  { label: 'document-base-form', url: `${base}/index.php?module=items/form&path=26` },
  { label: 'mts-list', url: `${base}/index.php?module=items/items&path=27` },
  { label: 'mts-form', url: `${base}/index.php?module=items/form&path=27` },
  { label: 'control-report', url: `${base}/index.php?module=reports/view&reports_id=80` },
];

const userRoutes = [
  { label: 'dashboard', url: `${base}/index.php?module=dashboard/dashboard` },
  { label: 'requests-list', url: `${base}/index.php?module=items/items&path=23` },
  { label: 'requests-form', url: `${base}/index.php?module=items/form&path=23` },
  { label: 'tasks-report', url: `${base}/index.php?module=reports/view&reports_id=78` },
  { label: 'projects-list', url: `${base}/index.php?module=items/items&path=21` },
  { label: 'documents-list', url: `${base}/index.php?module=items/items&path=25` },
  { label: 'documents-card', url: `${base}/index.php?module=items/info&path=25-1` },
  { label: 'documents-form', url: `${base}/index.php?module=items/form&path=25` },
  { label: 'document-base-list', url: `${base}/index.php?module=items/items&path=26` },
  { label: 'mts-list', url: `${base}/index.php?module=items/items&path=27` },
  { label: 'mts-form', url: `${base}/index.php?module=items/form&path=27` },
];

const nurseRoutes = [
  { label: 'dashboard', url: `${base}/index.php?module=dashboard/dashboard` },
  { label: 'requests-list', url: `${base}/index.php?module=items/items&path=23` },
  { label: 'requests-form', url: `${base}/index.php?module=items/form&path=23` },
  { label: 'tasks-report', url: `${base}/index.php?module=reports/view&reports_id=78` },
  { label: 'projects-list', url: `${base}/index.php?module=items/items&path=21` },
  { label: 'documents-list', url: `${base}/index.php?module=items/items&path=25` },
  { label: 'documents-card', url: `${base}/index.php?module=items/info&path=25-1` },
  { label: 'documents-form', url: `${base}/index.php?module=items/form&path=25` },
  { label: 'document-base-list', url: `${base}/index.php?module=items/items&path=26` },
  { label: 'mts-list', url: `${base}/index.php?module=items/items&path=27` },
  { label: 'mts-form', url: `${base}/index.php?module=items/form&path=27` },
];

const issues = [];
const visited = [];

try {
  await auditRukovoditelRole({ label: 'admin', username: adminUsername, password: adminPassword }, adminRoutes, issues, visited);
  await auditOnlyoffice({ label: 'admin', username: adminUsername, password: adminPassword }, issues, visited);
  await auditRukovoditelRole({ label: 'employee', username: employeeUsername, password: roleDefaultPassword }, userRoutes, issues, visited);
  await auditOnlyoffice({ label: 'employee', username: employeeUsername, password: roleDefaultPassword }, issues, visited);
  await auditRukovoditelRole({ label: 'nurse', username: nurseUsername, password: roleDefaultPassword }, nurseRoutes, issues, visited);
  await auditOnlyoffice({ label: 'nurse', username: nurseUsername, password: roleDefaultPassword }, issues, visited);
  await auditNauDoc(issues, visited);
  await auditBridge(issues, visited);

  console.log(JSON.stringify({
    status: issues.length ? 'failed' : 'ok',
    browser: runtime.browserName,
    checked: visited.length,
    issues,
    visited,
  }, null, 2));

  if (issues.length) {
    process.exitCode = 1;
  }
} finally {
  await browser.close();
}
