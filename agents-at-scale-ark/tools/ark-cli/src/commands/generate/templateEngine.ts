import fs from 'fs';
import path from 'path';
import chalk from 'chalk';
import {SecurityUtils} from '../../lib/security.js';
import {TemplateError} from '../../lib/errors.js';

export interface TemplateVariables {
  [key: string]: string | number | boolean;
}

export interface TemplateOptions {
  skipIfExists?: boolean;
  createDirectories?: boolean;
  exclude?: string[];
  include?: string[];
}

export class TemplateEngine {
  private variables: TemplateVariables = {};

  /**
   * Set template variables for substitution
   */
  setVariables(variables: TemplateVariables): void {
    this.variables = {...this.variables, ...variables};
  }

  /**
   * Get current template variables
   */
  getVariables(): TemplateVariables {
    return {...this.variables};
  }

  /**
   * Process a template directory and copy it to destination
   */
  async processTemplate(
    templatePath: string,
    destinationPath: string,
    options: TemplateOptions = {}
  ): Promise<void> {
    const {
      skipIfExists = false,
      createDirectories = true,
      exclude = ['.git', 'node_modules', '.DS_Store'],
      include = [],
    } = options;

    // Validate paths for security
    SecurityUtils.validatePath(templatePath, 'template path');
    SecurityUtils.validatePath(destinationPath, 'destination path');

    if (!fs.existsSync(templatePath)) {
      throw new TemplateError(
        `Template path does not exist: ${templatePath}`,
        templatePath,
        [
          'Check that the template directory exists',
          'Verify the template path is correct',
          'Ensure templates are properly installed',
        ]
      );
    }

    if (createDirectories) {
      await this.ensureDirectorySafe(destinationPath, destinationPath);
    }

    await this.copyDirectory(templatePath, destinationPath, {
      skipIfExists,
      exclude,
      include,
      baseDir: destinationPath,
    });
  }

  /**
   * Process a single template file
   */
  async processFile(
    templateFilePath: string,
    destinationFilePath: string,
    options: {skipIfExists?: boolean; baseDir?: string} = {}
  ): Promise<void> {
    const {skipIfExists = false, baseDir = process.cwd()} = options;

    // Validate paths for security
    SecurityUtils.validatePath(templateFilePath, 'template file path');
    SecurityUtils.validatePath(destinationFilePath, 'destination file path');
    SecurityUtils.validateOutputPath(destinationFilePath, baseDir);

    if (skipIfExists && fs.existsSync(destinationFilePath)) {
      console.log(
        chalk.yellow(`⏭️  Skipping existing file: ${destinationFilePath}`)
      );
      return;
    }

    let templateContent: string;
    try {
      templateContent = fs.readFileSync(templateFilePath, 'utf-8');
    } catch (error) {
      throw new TemplateError(
        `Failed to read template file: ${templateFilePath}. ${error instanceof Error ? error.message : String(error)}`,
        templateFilePath,
        [
          'Check that the template file exists',
          'Verify file permissions',
          'Ensure the template path is correct',
        ]
      );
    }

    // Validate template content for security
    SecurityUtils.validateTemplateContent(templateContent, templateFilePath);

    const processedContent = this.substituteVariables(templateContent);

    // Ensure destination directory exists
    const destinationDir = path.dirname(destinationFilePath);
    await this.ensureDirectorySafe(destinationDir, baseDir);

    // Write file securely
    await SecurityUtils.writeFileSafe(
      destinationFilePath,
      processedContent,
      baseDir
    );
    // Show important generated content with relative paths
    if (this.isImportantContent(destinationFilePath)) {
      const relativePath = this.getRelativePath(destinationFilePath);
      console.log(chalk.green(`📝 ${relativePath}`));
    }
  }

  /**
   * Substitute template variables in content
   */
  private substituteVariables(content: string): string {
    let result = content;

    // Replace template variables in Golang template format {{ .Values.variableName }}
    for (const [key, value] of Object.entries(this.variables)) {
      // Escape regex metacharacters in key to prevent ReDoS attacks
      const escapedKey = key.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const regex = new RegExp(`{{\\s*\\.Values\\.${escapedKey}\\s*}}`, 'g');
      result = result.replace(regex, String(value));
    }

    return result;
  }

  /**
   * Substitute variables in file/directory names
   */
  private substituteVariablesInPath(pathStr: string): string {
    let result = pathStr;

    // Handle new .template.yaml naming convention
    if (pathStr.endsWith('.template.yaml')) {
      const templateName = path.basename(pathStr, '.template.yaml');
      result = this.deriveDestinationFilename(templateName);
    } else {
      // Use Golang template variable substitution for other files
      for (const [key, value] of Object.entries(this.variables)) {
        const regex = new RegExp(`{{\\s*\\.Values\\.${key}\\s*}}`, 'g');
        result = result.replace(regex, String(value));
      }
    }

    return result;
  }

  /**
   * Derive destination filename from template name
   */
  private deriveDestinationFilename(templateName: string): string {
    switch (templateName) {
      case 'agent':
        return `${this.variables.agentName || 'unnamed'}-agent.yaml`;
      case 'team':
        return `${this.variables.teamName || 'unnamed'}-team.yaml`;
      case 'query':
        return `${this.variables.queryName || 'unnamed'}-query.yaml`;
      default: {
        // For unknown template types, use the template name as-is with variables
        let result = `${templateName}.yaml`;
        for (const [key, value] of Object.entries(this.variables)) {
          const regex = new RegExp(`{{\\s*\\.Values\\.${key}\\s*}}`, 'g');
          result = result.replace(regex, String(value));
        }
        return result;
      }
    }
  }

  /**
   * Copy directory recursively with template processing
   */
  private async copyDirectory(
    sourcePath: string,
    destinationPath: string,
    options: {
      skipIfExists?: boolean;
      exclude?: string[];
      include?: string[];
      baseDir?: string;
    }
  ): Promise<void> {
    const {baseDir = destinationPath} = options;
    const entries = fs.readdirSync(sourcePath, {withFileTypes: true});

    for (const entry of entries) {
      if (!this.shouldProcessEntry(entry.name, options)) {
        continue;
      }

      const sourceEntry = path.join(sourcePath, entry.name);
      const destinationName = this.substituteVariablesInPath(entry.name);
      const destinationEntry = path.join(destinationPath, destinationName);

      if (entry.isDirectory()) {
        await this.processDirectory(
          sourceEntry,
          destinationEntry,
          options,
          baseDir
        );
      } else {
        await this.processFileEntry(
          sourceEntry,
          destinationEntry,
          destinationName,
          options,
          baseDir
        );
      }
    }
  }

  private shouldProcessEntry(
    entryName: string,
    options: {exclude?: string[]; include?: string[]}
  ): boolean {
    if (this.shouldExclude(entryName, options.exclude || [])) {
      return false;
    }

    if (
      options.include &&
      options.include.length > 0 &&
      !this.shouldInclude(entryName, options.include)
    ) {
      return false;
    }

    return true;
  }

  private async processDirectory(
    sourceEntry: string,
    destinationEntry: string,
    options: {skipIfExists?: boolean; exclude?: string[]; include?: string[]},
    baseDir: string
  ): Promise<void> {
    await this.ensureDirectorySafe(destinationEntry, baseDir);
    await this.copyDirectory(sourceEntry, destinationEntry, {
      ...options,
      baseDir,
    });
  }

  private async processFileEntry(
    sourceEntry: string,
    destinationEntry: string,
    destinationName: string,
    options: {skipIfExists?: boolean},
    baseDir: string
  ): Promise<void> {
    const sanitizedName = SecurityUtils.sanitizeFileName(destinationName);
    if (sanitizedName !== destinationName) {
      console.warn(
        chalk.yellow(
          `⚠️  File name sanitized: "${destinationName}" → "${sanitizedName}"`
        )
      );
      return;
    }

    if (this.isTextFile(sourceEntry)) {
      await this.processFile(sourceEntry, destinationEntry, {
        skipIfExists: options.skipIfExists,
        baseDir,
      });
    } else if (options.skipIfExists && fs.existsSync(destinationEntry)) {
      console.log(
        chalk.yellow(`⏭️  Skipping existing file: ${destinationEntry}`)
      );
    } else {
      SecurityUtils.validateOutputPath(destinationEntry, baseDir);
      fs.copyFileSync(sourceEntry, destinationEntry);
      if (this.isImportantContent(destinationEntry)) {
        const relativePath = this.getRelativePath(destinationEntry);
        console.log(chalk.green(`📋 ${relativePath}`));
      }
    }
  }

  /**
   * Ensure a directory exists, creating it if necessary
   */
  private async ensureDirectory(dirPath: string): Promise<void> {
    if (!fs.existsSync(dirPath)) {
      fs.mkdirSync(dirPath, {recursive: true});
    }
  }

  /**
   * Safely ensure a directory exists with security validation
   */
  private async ensureDirectorySafe(
    dirPath: string,
    baseDir: string
  ): Promise<void> {
    SecurityUtils.validateOutputPath(dirPath, baseDir);

    if (!fs.existsSync(dirPath)) {
      await SecurityUtils.createDirectorySafe(dirPath, baseDir);
    }
  }

  /**
   * Check if a file should be excluded
   */
  private shouldExclude(fileName: string, excludePatterns: string[]): boolean {
    return excludePatterns.some((pattern) => {
      if (pattern.includes('*')) {
        // Safe glob pattern matching - escape regex metacharacters except *
        const escapedPattern = pattern
          .replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
          .replace(/\\\*/g, '.*');
        const regex = new RegExp(escapedPattern);
        return regex.test(fileName);
      }
      return fileName === pattern;
    });
  }

  /**
   * Check if a file should be included
   */
  private shouldInclude(fileName: string, includePatterns: string[]): boolean {
    return includePatterns.some((pattern) => {
      if (pattern.includes('*')) {
        // Safe glob pattern matching - escape regex metacharacters except *
        const escapedPattern = pattern
          .replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
          .replace(/\\\*/g, '.*');
        const regex = new RegExp(escapedPattern);
        return regex.test(fileName);
      }
      return fileName === pattern;
    });
  }

  /**
   * Check if a file is a text file that should have variable substitution
   */
  private isTextFile(filePath: string): boolean {
    const textExtensions = [
      '.txt',
      '.md',
      '.yaml',
      '.yml',
      '.json',
      '.js',
      '.ts',
      '.jsx',
      '.tsx',
      '.py',
      '.go',
      '.rs',
      '.java',
      '.cs',
      '.php',
      '.rb',
      '.sh',
      '.bash',
      '.zsh',
      '.fish',
      '.ps1',
      '.bat',
      '.cmd',
      '.dockerfile',
      '.docker',
      '.makefile',
      '.mk',
      '.toml',
      '.ini',
      '.cfg',
      '.conf',
      '.properties',
      '.xml',
      '.html',
      '.htm',
      '.css',
      '.scss',
      '.sass',
      '.less',
      '.vue',
      '.svelte',
      '.sql',
      '.r',
      '.R',
      '.swift',
      '.kt',
      '.scala',
      '.clj',
      '.hs',
      '.elm',
      '.ex',
      '.exs',
      '.erl',
      '.pl',
      '.pm',
      '.raku',
      '.lua',
    ];

    const extension = path.extname(filePath).toLowerCase();
    if (textExtensions.includes(extension)) {
      return true;
    }

    // Check for files without extensions that are commonly text
    const basename = path.basename(filePath).toLowerCase();
    const textBasenames = [
      'readme',
      'license',
      'changelog',
      'makefile',
      'dockerfile',
      'gitignore',
      'gitattributes',
      'editorconfig',
      'eslintrc',
      'prettierrc',
    ];

    return textBasenames.some((name) => basename.includes(name));
  }

  /**
   * Check if a file path represents important generated content
   */
  private isImportantContent(filePath: string): boolean {
    const normalizedPath = path.normalize(filePath);

    // Show files in important directories (agents, teams, queries, models)
    const importantDirs = ['agents', 'teams', 'queries', 'models'];
    const hasImportantDir = importantDirs.some(
      (dir) =>
        normalizedPath.includes(`${path.sep}${dir}${path.sep}`) ||
        normalizedPath.includes(`/${dir}/`)
    );

    if (hasImportantDir) {
      // Skip .keep files
      return !path.basename(filePath).includes('.keep');
    }

    return false;
  }

  /**
   * Get relative path from a full file path for display
   */
  private getRelativePath(filePath: string): string {
    const normalizedPath = path.normalize(filePath);

    // Find the project root by looking for common patterns
    const pathParts = normalizedPath.split(path.sep);

    // Look for agents, teams, queries, or models directory
    const importantDirs = ['agents', 'teams', 'queries', 'models'];
    for (let i = pathParts.length - 1; i >= 0; i--) {
      if (importantDirs.includes(pathParts[i])) {
        // Return from this directory onwards
        return pathParts.slice(i).join('/');
      }
    }

    // Fallback to just filename
    return path.basename(filePath);
  }
}
