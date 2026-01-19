/**
 * Utilities for name validation and normalization
 */

import {ValidationError} from '../../../lib/errors.js';

/**
 * Convert a string to lowercase kebab-case
 * Examples:
 * - "My Project" -> "my-project"
 * - "MyProject" -> "my-project"
 * - "my_project" -> "my-project"
 * - "myProject123" -> "my-project123"
 */
export function toKebabCase(str: string): string {
  if (str.length > 1000) {
    throw new Error('Input string too long for processing');
  }

  let result = str
    .trim()
    // Replace spaces and underscores with hyphens
    .replace(/[\s_]+/g, '-')
    // Insert hyphens before uppercase letters (camelCase -> kebab-case)
    .replace(/([a-z])([A-Z])/g, '$1-$2')
    // Convert to lowercase
    .toLowerCase()
    // Remove any double hyphens
    .replace(/-+/g, '-');

  // Remove leading/trailing hyphens using string methods to avoid regex backtracking
  while (result.startsWith('-')) {
    result = result.slice(1);
  }
  while (result.endsWith('-')) {
    result = result.slice(0, -1);
  }

  return result;
}

/**
 * Validate that a name follows kebab-case format
 */
export function isValidKebabCase(str: string): boolean {
  // Must be lowercase, can contain letters, numbers, and hyphens
  // Cannot start or end with hyphen, cannot have consecutive hyphens
  const kebabRegex = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
  return kebabRegex.test(str);
}

/**
 * Validate that a name is suitable for Kubernetes resources
 */
export function isValidKubernetesName(str: string): boolean {
  // Kubernetes names must be lowercase alphanumeric or '-'
  // Must start and end with alphanumeric character
  // Max length 63 characters
  return (
    isValidKebabCase(str) &&
    str.length <= 63 &&
    str.length >= 1 &&
    /^[a-z0-9]/.test(str) &&
    /[a-z0-9]$/.test(str)
  );
}

/**
 * Get validation error message for invalid names
 */
export function getNameValidationError(name: string): string | null {
  try {
    validateNameStrict(name);
    return null;
  } catch (error) {
    if (error instanceof ValidationError) {
      return error.message;
    }
    return error instanceof Error ? error.message : String(error);
  }
}

/**
 * Strict name validation that throws ValidationError with suggestions
 */
export function validateNameStrict(name: string, type: string = 'name'): void {
  if (!name || name.trim().length === 0) {
    throw new ValidationError(`${type} cannot be empty`, 'name', [
      `Provide a valid ${type}`,
    ]);
  }

  const trimmed = name.trim();

  if (trimmed.length > 63) {
    throw new ValidationError(
      `${type} must be 63 characters or less (got ${trimmed.length})`,
      'name',
      [`Shorten the ${type} to 63 characters or less`]
    );
  }

  if (!isValidKubernetesName(trimmed)) {
    const suggested = toKebabCase(trimmed);
    const suggestions = [];

    if (suggested !== trimmed && isValidKubernetesName(suggested)) {
      suggestions.push(`Try: "${suggested}"`);
    }
    suggestions.push(
      `${type} must be lowercase letters, numbers, and hyphens only`
    );
    suggestions.push(`${type} cannot start or end with a hyphen`);
    suggestions.push(`${type} cannot contain consecutive hyphens`);

    throw new ValidationError(
      `Invalid ${type}: "${trimmed}"`,
      'name',
      suggestions
    );
  }
}

/**
 * Normalize and validate a name for use in generators
 */
export function normalizeAndValidateName(
  input: string,
  type: string = 'name'
): {
  name: string;
  wasTransformed: boolean;
} {
  const original = input.trim();
  const normalized = toKebabCase(original);

  // Validate the normalized name
  validateNameStrict(normalized, type);

  return {
    name: normalized,
    wasTransformed: normalized !== original,
  };
}
