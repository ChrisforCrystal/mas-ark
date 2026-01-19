import chalk from 'chalk';
import inquirer from 'inquirer';
import path from 'path';
import fs from 'fs';
import {Generator, GeneratorOptions} from '../index.js';
import {TemplateDiscovery} from '../templateDiscovery.js';
import {TemplateEngine} from '../templateEngine.js';
import {ArkError, ErrorCode} from '../../../lib/errors.js';

interface MarketplaceConfig {
  name: string;
  destination: string;
  description: string;
  initGit: boolean;
  gitUserName?: string;
  gitUserEmail?: string;
}

export function createMarketplaceGenerator(): Generator {
  const generator = new MarketplaceGenerator();
  return {
    name: 'marketplace',
    description: 'Central repository for sharing reusable ARK components',
    templatePath: 'marketplace',
    generate: async (
      name: string,
      destination: string,
      options: GeneratorOptions
    ) => {
      await generator.generate(name, destination, options);
    },
  };
}

class MarketplaceGenerator {
  private readonly templateDiscovery: TemplateDiscovery;
  private readonly templateEngine: TemplateEngine;

  constructor() {
    this.templateDiscovery = new TemplateDiscovery();
    this.templateEngine = new TemplateEngine();
  }

  /**
   * Get marketplace configuration from user input and validation
   */
  private async getMarketplaceConfig(
    destination: string,
    options: GeneratorOptions
  ): Promise<MarketplaceConfig> {
    // Always use "ark-marketplace" as the name
    const normalizedName = 'ark-marketplace';
    const targetDir = path.resolve(destination, normalizedName);

    // Check if directory already exists
    if (fs.existsSync(targetDir)) {
      throw new ArkError(
        `Directory ${targetDir} already exists. Please choose a different name or location.`,
        ErrorCode.VALIDATION_ERROR
      );
    }

    const config: MarketplaceConfig = {
      name: normalizedName,
      destination: targetDir,
      description: 'Ark marketplace for sharing ARK components',
      initGit: true,
    };

    // Get current git configuration
    const gitConfig = await this.getGitUserConfig();

    // Use command line options if provided, otherwise use current git config, fallback to defaults
    config.initGit = !options.skipGit;
    config.gitUserName =
      options.gitUserName || gitConfig.name || 'Marketplace Team';
    config.gitUserEmail =
      options.gitUserEmail || gitConfig.email || 'marketplace@example.com';

    return config;
  }

  /**
   * Get current git user configuration (secure implementation)
   */
  private async getGitUserConfig(): Promise<{name?: string; email?: string}> {
    try {
      const {execa} = await import('execa');

      // Use secure PATH and argument arrays to prevent injection
      const gitPath = process.env.GIT_PATH || '/usr/bin/git';
      const secureEnv = {
        PATH: '/usr/local/bin:/usr/bin:/bin',
        ...process.env,
      };

      const nameResult = await execa(gitPath, ['config', 'user.name'], {
        env: secureEnv,
        stdio: 'pipe',
        timeout: 5000, // 5 second timeout
      });

      const emailResult = await execa(gitPath, ['config', 'user.email'], {
        env: secureEnv,
        stdio: 'pipe',
        timeout: 5000,
      });

      return {
        name: nameResult.stdout.trim(),
        email: emailResult.stdout.trim(),
      };
    } catch {
      return {};
    }
  }

  /**
   * Get marketplace configuration with interactive prompts
   */
  private async getInteractiveConfig(
    config: MarketplaceConfig
  ): Promise<MarketplaceConfig> {
    console.log(chalk.cyan('\n🏪 Marketplace Configuration\n'));

    const answers = await inquirer.prompt([
      {
        type: 'input',
        name: 'destination',
        message: 'Where would you like to create the marketplace?',
        default: path.dirname(config.destination),
        validate: (input: string) => {
          if (!input.trim()) {
            return 'Destination path is required';
          }
          return true;
        },
      },
      {
        type: 'confirm',
        name: 'initGit',
        message: `Initialize Git repository with ${config.gitUserName} <${config.gitUserEmail}>?`,
        default: config.initGit,
      },
    ]);

    // Update config with answers
    const updatedConfig = {
      ...config,
      destination: path.resolve(answers.destination, config.name),
      initGit: answers.initGit,
    };

    // Check if the updated destination already exists
    if (fs.existsSync(updatedConfig.destination)) {
      throw new ArkError(
        `Directory ${updatedConfig.destination} already exists. Please choose a different location.`,
        ErrorCode.VALIDATION_ERROR
      );
    }

    return updatedConfig;
  }

  /**
   * Show configuration summary and ask for confirmation
   */
  private async confirmGeneration(config: MarketplaceConfig): Promise<void> {
    console.log(chalk.cyan('\n📋 Marketplace Generation Summary\n'));
    console.log(`Name: ${chalk.green(config.name)}`);
    console.log(`Description: ${config.description}`);
    console.log(`Destination: ${chalk.yellow(config.destination)}`);
    console.log(
      `Git Repository: ${config.initGit ? chalk.green('Yes') : 'No'}`
    );
    if (config.initGit) {
      console.log(`Git User: ${config.gitUserName} <${config.gitUserEmail}>`);
    }

    const confirm = await inquirer.prompt([
      {
        type: 'confirm',
        name: 'proceed',
        message: 'Create marketplace with this configuration?',
        default: true,
      },
    ]);

    if (!confirm.proceed) {
      console.log(chalk.yellow('Marketplace generation cancelled.'));
      process.exit(0);
    }
  }

  /**
   * Validate git configuration values to prevent injection
   */
  private validateGitConfig(value: string, type: 'name' | 'email'): void {
    if (!value || typeof value !== 'string') {
      throw new ArkError(
        `Invalid git ${type}: must be a non-empty string`,
        ErrorCode.VALIDATION_ERROR
      );
    }

    // Prevent command injection by checking for dangerous characters
    const dangerousChars = /[\\`$;|&<>(){}[\]]/;
    if (dangerousChars.test(value)) {
      throw new ArkError(
        `Invalid git ${type}: contains dangerous characters`,
        ErrorCode.VALIDATION_ERROR,
        undefined,
        ['Remove special characters and shell metacharacters']
      );
    }

    // Additional validation for email format
    if (type === 'email') {
      const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
      if (!emailRegex.test(value)) {
        throw new ArkError(
          `Invalid git email format: ${value}`,
          ErrorCode.VALIDATION_ERROR
        );
      }
    }

    // Length validation
    if (value.length > 100) {
      throw new ArkError(
        `Git ${type} too long (max 100 characters)`,
        ErrorCode.VALIDATION_ERROR
      );
    }
  }

  /**
   * Setup git repository with initial commit (secure implementation)
   */
  private async setupGit(config: MarketplaceConfig): Promise<void> {
    try {
      const {execa} = await import('execa');

      // Use secure PATH and git path
      const gitPath = process.env.GIT_PATH || '/usr/bin/git';
      const secureEnv = {
        PATH: '/usr/local/bin:/usr/bin:/bin',
        ...process.env,
      };

      const execOptions = {
        cwd: config.destination,
        env: secureEnv,
        stdio: 'pipe' as const,
        timeout: 10000, // 10 second timeout
      };

      // Initialize git repository
      await execa(gitPath, ['init'], execOptions);

      // Configure git user if provided (with validation)
      if (config.gitUserName) {
        this.validateGitConfig(config.gitUserName, 'name');
        await execa(
          gitPath,
          ['config', 'user.name', config.gitUserName],
          execOptions
        );
      }

      if (config.gitUserEmail) {
        this.validateGitConfig(config.gitUserEmail, 'email');
        await execa(
          gitPath,
          ['config', 'user.email', config.gitUserEmail],
          execOptions
        );
      }

      // Add all files and create initial commit
      await execa(gitPath, ['add', '.'], execOptions);
      await execa(
        gitPath,
        ['commit', '-m', 'Initial marketplace structure'],
        execOptions
      );

      console.log(chalk.green('✅ Git repository initialized'));
    } catch (error) {
      console.warn(
        chalk.yellow('⚠️  Git initialization failed:'),
        error instanceof Error ? error.message : String(error)
      );
    }
  }

  /**
   * Generate marketplace structure
   */
  private async generateMarketplace(config: MarketplaceConfig): Promise<void> {
    console.log(chalk.cyan('\n🏗️  Creating marketplace structure...'));

    // Set template variables
    const variables = {
      projectName: config.name,
      description: config.description,
      PROJECT_NAME: config.name,
      authorName: config.gitUserName || 'Marketplace Team',
      authorEmail: config.gitUserEmail || 'marketplace@example.com',
    };

    this.templateEngine.setVariables(variables);

    // Get template path
    const templatePath = this.templateDiscovery.getTemplatePath('marketplace');

    // Verify template exists
    if (!this.templateDiscovery.templateExists('marketplace')) {
      throw new ArkError(
        'Marketplace template not found. Please ensure the template is available in the templates directory.',
        ErrorCode.TEMPLATE_ERROR
      );
    }

    // Configure exclude patterns
    const excludePatterns = ['.git', 'node_modules', '.DS_Store'];

    // Process template
    await this.templateEngine.processTemplate(
      templatePath,
      config.destination,
      {
        createDirectories: true,
        exclude: excludePatterns,
      }
    );

    console.log(chalk.green('✅ Marketplace structure created'));
  }

  /**
   * Show completion message with next steps
   */
  private showCompletionMessage(config: MarketplaceConfig): void {
    const relativePath = path.relative(process.cwd(), config.destination);
    const displayPath = relativePath || config.destination;

    console.log(chalk.green('\n🎉 Marketplace created successfully!'));
    console.log(chalk.cyan('\n📁 Location:'), displayPath);
    console.log(chalk.cyan('📝 Description:'), config.description);

    console.log(chalk.cyan('\n🚀 Next steps:'));
    console.log('  1. ' + chalk.yellow('cd ' + displayPath));
    console.log(
      '  2. ' + chalk.yellow('# Create remote repository on GitHub/GitLab')
    );
    console.log(
      '  3. ' + chalk.yellow('git remote add origin <YOUR_REPO_URL>')
    );
    console.log('  4. ' + chalk.yellow('git push -u origin main'));
    console.log(
      '  5. ' +
        chalk.yellow('# Add your first component to the appropriate directory')
    );
    console.log(
      '  6. ' +
        chalk.yellow(
          '# Update the README.md with marketplace-specific information'
        )
    );
    console.log(
      '  7. ' + chalk.yellow('# Set up CI/CD workflows in .github/workflows/')
    );
    console.log(
      '  8. ' +
        chalk.yellow('# Configure contribution guidelines and review process')
    );

    console.log(chalk.cyan('\n📂 Directory structure:'));
    console.log('  • agents/         - Reusable agent definitions');
    console.log('  • teams/          - Multi-agent workflow configurations');
    console.log('  • models/         - Model configurations by provider');
    console.log('  • queries/        - Query templates and patterns');
    console.log('  • tools/          - Tool definitions and implementations');
    console.log('  • mcp-servers/    - MCP server configurations');
    console.log(
      '  • projects/       - Complete Ark project templates and solutions'
    );
    console.log('  • docs/           - Documentation and guides');

    console.log(chalk.cyan('\n💡 Tips:'));
    console.log('  • Each .keep file contains guidelines for that directory');
    console.log(
      '  • Use the templates/ directory to create component templates'
    );
    console.log('  • Set up automated validation in CI/CD pipelines');
    console.log('  • Encourage comprehensive documentation for all components');

    if (config.initGit) {
      console.log(chalk.cyan('\n🔗 Git repository:'));
      console.log('  • Repository initialized with initial commit');
      console.log('  • Ready to add remote origin and push to GitHub/GitLab');
      console.log('  • Consider setting up branch protection rules');
    }
  }

  /**
   * Main generation method
   */
  async generate(
    _name: string,
    destination: string,
    options: GeneratorOptions
  ): Promise<void> {
    try {
      // Get initial configuration
      let config = await this.getMarketplaceConfig(destination, options);

      // Get interactive configuration (allows editing destination and git settings)
      config = await this.getInteractiveConfig(config);

      // Show summary and confirm
      await this.confirmGeneration(config);

      // Generate marketplace
      await this.generateMarketplace(config);

      // Setup git if requested
      if (config.initGit) {
        await this.setupGit(config);
      }

      // Show completion message
      this.showCompletionMessage(config);
    } catch (error) {
      if (error instanceof ArkError) {
        throw error;
      }
      throw new ArkError(
        `Failed to generate marketplace: ${error instanceof Error ? error.message : String(error)}`,
        ErrorCode.UNKNOWN_ERROR
      );
    }
  }
}
