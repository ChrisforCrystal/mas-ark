import fs from 'fs';
import path from 'path';
import {ProjectStructureError} from '../../../lib/errors.js';

export interface ProjectValidationResult {
  isValid: boolean;
  projectName?: string;
  error?: string;
}

/**
 * Validate if the given directory is a valid ARK project
 */
export function validateProjectStructure(
  projectDir: string
): ProjectValidationResult {
  // Check for required project files
  const chartYamlPath = path.join(projectDir, 'Chart.yaml');
  const agentsDir = path.join(projectDir, 'agents');

  if (!fs.existsSync(chartYamlPath)) {
    return {
      isValid: false,
      error:
        'Chart.yaml not found. This does not appear to be a valid ARK project directory.',
    };
  }

  if (!fs.existsSync(agentsDir)) {
    return {
      isValid: false,
      error:
        'agents/ directory not found. This does not appear to be a valid ARK project directory.',
    };
  }

  // Try to extract project name from Chart.yaml
  try {
    const chartContent = fs.readFileSync(chartYamlPath, 'utf-8');
    const nameMatch = /^name:\s*([a-zA-Z0-9\s._-]{1,200}?)$/m.exec(
      chartContent
    );
    if (nameMatch) {
      return {
        isValid: true,
        projectName: nameMatch[1].trim(),
      };
    }
  } catch (error) {
    return {
      isValid: false,
      error: `Failed to read Chart.yaml: ${error}`,
    };
  }

  return {
    isValid: true,
  };
}

/**
 * Check file/directory validation
 */
function validateRequiredPath(
  projectDir: string,
  required: {path: string; type: 'file' | 'directory'},
  missing: string[],
  wrongType: string[]
): void {
  const fullPath = path.join(projectDir, required.path);

  if (!fs.existsSync(fullPath)) {
    missing.push(required.path);
    return;
  }

  const stat = fs.statSync(fullPath);
  if (required.type === 'file' && !stat.isFile()) {
    wrongType.push(`${required.path} (expected file, found directory)`);
  } else if (required.type === 'directory' && !stat.isDirectory()) {
    wrongType.push(`${required.path} (expected directory, found file)`);
  }
}

/**
 * Extract project name from Chart.yaml
 */
function extractProjectName(projectDir: string): string {
  const chartYamlPath = path.join(projectDir, 'Chart.yaml');
  const chartContent = fs.readFileSync(chartYamlPath, 'utf-8');
  const nameMatch = /^name:\s*([a-zA-Z0-9\s._-]{1,200}?)$/m.exec(chartContent);
  if (nameMatch) {
    return nameMatch[1].trim();
  }
  throw new Error('No name field found in Chart.yaml');
}

/**
 * Validate project structure and throw detailed error if invalid
 */
export function validateProjectStructureStrict(projectDir: string): string {
  const requiredFiles = [
    {path: 'Chart.yaml', type: 'file' as const},
    {path: 'agents', type: 'directory' as const},
    {path: 'teams', type: 'directory' as const},
    {path: 'queries', type: 'directory' as const},
    {path: 'models', type: 'directory' as const},
  ];

  const missing: string[] = [];
  const wrongType: string[] = [];

  for (const required of requiredFiles) {
    validateRequiredPath(projectDir, required, missing, wrongType);
  }

  if (missing.length > 0 || wrongType.length > 0) {
    const issues = [];
    if (missing.length > 0) {
      issues.push(`Missing: ${missing.join(', ')}`);
    }
    if (wrongType.length > 0) {
      issues.push(`Wrong type: ${wrongType.join(', ')}`);
    }

    throw new ProjectStructureError(
      `Invalid ARK project structure: ${issues.join('; ')}`,
      projectDir,
      [
        'Ensure you are in a valid ARK project directory',
        'Run "ark generate project" to create a new project',
        'Check that all required files and directories exist',
      ]
    );
  }

  try {
    return extractProjectName(projectDir);
  } catch (error) {
    throw new ProjectStructureError(
      `Failed to read project name from Chart.yaml: ${error instanceof Error ? error.message : String(error)}`,
      projectDir,
      [
        'Ensure Chart.yaml exists and is readable',
        'Check that Chart.yaml contains a valid name field',
        'Verify file permissions',
      ]
    );
  }
}

/**
 * Get the current project directory (current working directory)
 */
export function getCurrentProjectDirectory(): string {
  return process.cwd();
}

/**
 * Check if the current directory is a valid ARK project
 */
export function validateCurrentProject(): ProjectValidationResult {
  return validateProjectStructure(getCurrentProjectDirectory());
}

/**
 * Get current project info with strict validation
 */
export function getCurrentProjectInfo(): {
  projectName: string;
  projectDir: string;
} {
  const projectDir = getCurrentProjectDirectory();
  const projectName = validateProjectStructureStrict(projectDir);
  return {projectName, projectDir};
}
