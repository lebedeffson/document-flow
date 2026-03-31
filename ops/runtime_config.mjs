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

function boolFromEnv(name, fallback = false) {
  const raw = process.env[name];
  if (typeof raw !== 'string') {
    return fallback;
  }

  return ['1', 'true', 'yes', 'on'].includes(raw.trim().toLowerCase());
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

export const docspaceBase = stripTrailingSlash(
  process.env.DOCFLOW_DOCSPACE_PUBLIC_BASE ||
    process.env.DOCSPACE_PUBLIC_URL ||
    `${publicBase}/docspace`
);

export const workspaceBase = stripTrailingSlash(
  process.env.DOCFLOW_WORKSPACE_PUBLIC_BASE ||
    process.env.WORKSPACE_PUBLIC_URL ||
    `${publicBase}/workspace`
);

export const naudocUsername = process.env.NAUDOC_USERNAME || 'admin';
export const naudocPassword = process.env.NAUDOC_PASSWORD || 'admin';
export const showDemoLoginModes = boolFromEnv('DOCFLOW_SHOW_DEMO_LOGIN_MODES', false);
export const docspaceEnabled = boolFromEnv('DOCSPACE_ENABLED', true);
export const workspaceEnabled = boolFromEnv('WORKSPACE_ENABLED', true);
export const docspaceTargetUrl = stripTrailingSlash(process.env.DOCSPACE_TARGET_URL || '');
export const workspaceTargetUrl = stripTrailingSlash(process.env.WORKSPACE_TARGET_URL || '');
export const adminUsername = process.env.DOCFLOW_ADMIN_USERNAME || 'admin';
export const adminPassword = process.env.DOCFLOW_ADMIN_PASSWORD || 'admin123';
export const officeAdminEmail = process.env.DOCFLOW_OFFICE_ADMIN_EMAIL || 'admin@hospital.local';
export const officeAdminPassword = process.env.DOCFLOW_OFFICE_ADMIN_PASSWORD || 'Admin2026!';
export const roleDefaultPassword = process.env.DOCFLOW_ROLE_DEFAULT_PASSWORD || 'rolepass123';
export const managerUsername = process.env.DOCFLOW_MANAGER_USERNAME || 'department.head';
export const employeeUsername = process.env.DOCFLOW_EMPLOYEE_USERNAME || 'clinician.primary';
export const requesterUsername = process.env.DOCFLOW_REQUESTER_USERNAME || 'registry.operator';
export const officeUsername = process.env.DOCFLOW_OFFICE_USERNAME || 'records.office';
export const nurseUsername = process.env.DOCFLOW_NURSE_USERNAME || 'nurse.coordinator';

export const officeBase = stripTrailingSlash(
  process.env.DOCFLOW_OFFICE_PUBLIC_BASE ||
    `${publicBase}/office`
);

export const httpBase = stripTrailingSlash(
  process.env.DOCFLOW_HTTP_BASE ||
    'http://localhost:18090'
);
