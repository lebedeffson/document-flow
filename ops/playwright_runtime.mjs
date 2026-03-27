import playwright from 'playwright';

export function resolveBrowserRuntime(requestedBrowser = process.env.PLAYWRIGHT_BROWSER || 'firefox') {
  const browserType = playwright[requestedBrowser];
  if (!browserType) {
    throw new Error(`Unsupported PLAYWRIGHT_BROWSER: ${requestedBrowser}`);
  }

  const executablePath =
    (requestedBrowser === 'firefox' && (process.env.PLAYWRIGHT_FIREFOX_PATH || process.env.FIREFOX_PATH)) ||
    (requestedBrowser === 'chromium' && (process.env.PLAYWRIGHT_CHROMIUM_PATH || process.env.CHROMIUM_PATH)) ||
    null;

  return {
    playwright,
    browserName: requestedBrowser,
    browserType,
    executablePath,
    available: true,
  };
}

export function buildLaunchOptions(browserName, executablePath) {
  const options = {
    headless: true,
  };

  if (executablePath) {
    options.executablePath = executablePath;
  }

  if (browserName === 'chromium') {
    options.args = ['--ignore-certificate-errors'];
  }

  return options;
}
