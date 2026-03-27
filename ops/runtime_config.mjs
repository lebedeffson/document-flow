import { readFileSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

function loadEnvDefaults() {
  const defaultEnvFile = fileURLToPath(new URL('../.env', import.meta.url));
  const envFile = process.env.DOCFLOW_ENV_FILE || defaultEnvFile;
  if (!existsSync(envFile)) {
    return;
  }

  const content = readFileSync(envFile, 'utf-8');
  for (const rawLine of content.split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line || line.startsWith('#')) {
      continue;
    }
    const separatorIndex = line.indexOf('=');
    if (separatorIndex === -1) {
      continue;
    }
    const key = line.slice(0, separatorIndex).trim();
    const value = line.slice(separatorIndex + 1).trim().replace(/^['"]|['"]$/g, '');
    if (!(key in process.env)) {
      process.env[key] = value;
    }
  }
}

loadEnvDefaults();

function stripTrailingSlash(value) {
  return value.replace(/\/+$/, '');
}

export const publicBase = stripTrailingSlash(
  process.env.DOCFLOW_PUBLIC_BASE ||
    process.env.RUKOVODITEL_PUBLIC_URL ||
    'https://localhost:18443'
);

export const docsBase = stripTrailingSlash(
  process.env.DOCFLOW_DOCS_BASE ||
    process.env.NAUDOC_PUBLIC_URL ||
    `${publicBase}/docs`
);

export const bridgeBase = stripTrailingSlash(
  process.env.DOCFLOW_BRIDGE_PUBLIC_BASE ||
    `${publicBase}/bridge`
);

export const naudocUsername = process.env.NAUDOC_USERNAME || 'admin';
export const naudocPassword = process.env.NAUDOC_PASSWORD || 'admin';

export const officeBase = stripTrailingSlash(
  process.env.DOCFLOW_OFFICE_PUBLIC_BASE ||
    `${publicBase}/office`
);

export const httpBase = stripTrailingSlash(
  process.env.DOCFLOW_HTTP_BASE ||
    'http://localhost:18090'
);
