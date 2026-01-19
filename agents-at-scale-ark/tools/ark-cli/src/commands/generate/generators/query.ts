import chalk from 'chalk';
import inquirer from 'inquirer';
import path from 'path';
import fs from 'fs';
import {Generator, GeneratorOptions} from '../index.js';
import {TemplateEngine, TemplateVariables} from '../templateEngine.js';
import {TemplateDiscovery} from '../templateDiscovery.js';
import {toKebabCase, validateNameStrict} from '../utils/nameUtils.js';
import {getCurrentProjectInfo} from '../utils/projectUtils.js';
import {
  ErrorHandler,
  TemplateError,
  ValidationError,
} from '../../../lib/errors.js';

interface QueryConfig {
  name: string;
  queryName: string;
  projectName: string;
  projectDirectory: string;
  targetType: 'agent' | 'team';
  targetName: string;
  inputMessage: string;
}

export function createQueryGenerator(): Generator {
  return {
    name: 'query',
    description: 'Generate a new query to test agents or teams',
    templatePath: 'templates/query',
    generate: async (
      name: string,
      destination: string,
      options: GeneratorOptions
    ) => {
      const generator = new QueryGenerator();
      await generator.generate(name, destination, options);
    },
  };
}

class QueryGenerator {
  private readonly templateDiscovery: TemplateDiscovery;
  private readonly templateEngine: TemplateEngine;

  constructor() {
    this.templateDiscovery = new TemplateDiscovery();
    this.templateEngine = new TemplateEngine();
  }

  /**
   * Get query configuration from user input and validation
   */
  private async getQueryConfig(
    name: string,
    _destination: string,
    _options: GeneratorOptions
  ): Promise<QueryConfig> {
    // Validate that we're in a project directory and get project info
    const {projectName, projectDir} = getCurrentProjectInfo();

    // Validate and normalize query name
    const queryName = toKebabCase(name);
    validateNameStrict(queryName, 'query name');

    // Check if query already exists
    const queriesDir = path.join(projectDir, 'queries');
    const queryFilePath = path.join(queriesDir, `${queryName}-query.yaml`);

    if (fs.existsSync(queryFilePath)) {
      console.log(
        chalk.yellow(`⚠️  Query file already exists: ${queryFilePath}`)
      );

      const {overwrite} = await inquirer.prompt([
        {
          type: 'confirm',
          name: 'overwrite',
          message: 'Do you want to overwrite the existing query?',
          default: false,
        },
      ]);

      if (!overwrite) {
        throw new ValidationError(
          'Query generation cancelled by user',
          'overwrite',
          [
            `Use a different query name`,
            `Use --force flag to overwrite without prompting`,
          ]
        );
      }
    }

    // Ask user what type of target they want
    const {targetType} = await inquirer.prompt([
      {
        type: 'list',
        name: 'targetType',
        message: 'What should this query target?',
        choices: [
          {name: 'Agent - Target a single AI agent', value: 'agent'},
          {name: 'Team - Target a team of agents', value: 'team'},
        ],
        default: 'agent',
      },
    ]);

    // Get available targets based on type
    const targetDir = path.join(
      projectDir,
      targetType === 'agent' ? 'agents' : 'teams'
    );
    const filePattern = targetType === 'agent' ? '-agent.yaml' : '-team.yaml';
    let availableTargets: string[] = [];

    if (fs.existsSync(targetDir)) {
      const targetFiles = fs
        .readdirSync(targetDir)
        .filter((file) => file.endsWith(filePattern))
        .map((file) => file.replace(filePattern, ''));
      availableTargets = targetFiles;
    }

    let targetName: string;

    if (availableTargets.length > 0) {
      // Ask user to select a target or provide a custom one
      const choices = [
        ...availableTargets.map((target) => ({name: target, value: target})),
        {name: 'Other (specify manually)', value: 'custom'},
      ];

      const {selectedTarget} = await inquirer.prompt([
        {
          type: 'list',
          name: 'selectedTarget',
          message: `Which ${targetType} should this query target?`,
          choices,
          default: availableTargets[0],
        },
      ]);

      if (selectedTarget === 'custom') {
        const {customTarget} = await inquirer.prompt([
          {
            type: 'input',
            name: 'customTarget',
            message: `Enter the ${targetType} name:`,
            validate: (input) => {
              if (!input.trim()) {
                return `${targetType} name cannot be empty`;
              }
              return true;
            },
          },
        ]);
        targetName = toKebabCase(customTarget);
      } else {
        targetName = selectedTarget;
      }
    } else {
      // No targets found, ask for manual input
      console.log(chalk.yellow(`⚠️  No ${targetType}s found in the project.`));
      const {customTarget} = await inquirer.prompt([
        {
          type: 'input',
          name: 'customTarget',
          message: `Enter the ${targetType} name this query should target:`,
          validate: (input) => {
            if (!input.trim()) {
              return `${targetType} name cannot be empty`;
            }
            return true;
          },
        },
      ]);
      targetName = toKebabCase(customTarget);
    }

    // Ask for the input message
    const {inputMessage} = await inquirer.prompt([
      {
        type: 'input',
        name: 'inputMessage',
        message: 'What message should the query send to the agent?',
        default: `Hello! Can you help me understand what you can do for the ${projectName} project?`,
        validate: (input) => {
          if (!input.trim()) {
            return 'Input message cannot be empty';
          }
          return true;
        },
      },
    ]);

    return {
      name,
      queryName,
      projectName,
      projectDirectory: projectDir,
      targetType,
      targetName,
      inputMessage,
    };
  }

  /**
   * Generate the query file
   */
  private async generateQueryFile(config: QueryConfig): Promise<void> {
    const templatePath = this.templateDiscovery.getTemplatePath('query');

    if (!this.templateDiscovery.templateExists('query')) {
      throw new TemplateError(
        `Query template not found at: ${templatePath}`,
        templatePath,
        [
          'Ensure the templates directory exists',
          'Check that the query template is properly installed',
          'Verify file permissions',
        ]
      );
    }

    // Set up template variables
    const variables: TemplateVariables = {
      queryName: config.queryName,
      targetType: config.targetType,
      targetName: config.targetName,
      projectName: config.projectName,
      inputMessage: config.inputMessage,
    };

    this.templateEngine.setVariables(variables);

    // Ensure queries directory exists
    const queriesDir = path.join(config.projectDirectory, 'queries');
    if (!fs.existsSync(queriesDir)) {
      fs.mkdirSync(queriesDir, {recursive: true});
      console.log(chalk.blue(`📁 Created queries directory: ${queriesDir}`));
    }

    // Process the query template file
    const templateFilePath = path.join(templatePath, 'query.template.yaml');
    const destinationFilePath = path.join(
      queriesDir,
      `${config.queryName}-query.yaml`
    );

    await this.templateEngine.processFile(
      templateFilePath,
      destinationFilePath
    );

    console.log(
      chalk.green(
        `✅ Query file created: queries/${config.queryName}-query.yaml`
      )
    );
  }

  /**
   * Main generation method
   */
  async generate(
    name: string,
    destination: string,
    options: GeneratorOptions
  ): Promise<void> {
    await ErrorHandler.catchAndHandle(async () => {
      console.log(chalk.blue('🔍 Generating query...'));

      // Get configuration
      const config = await this.getQueryConfig(name, destination, options);

      console.log(chalk.blue(`\n📝 Query details:`));
      console.log(chalk.gray(`  Name: ${config.queryName}`));
      console.log(
        chalk.gray(`  Target ${config.targetType}: ${config.targetName}`)
      );
      console.log(chalk.gray(`  Project: ${config.projectName}`));
      console.log(
        chalk.gray(
          `  Message: ${config.inputMessage.substring(0, 50)}${config.inputMessage.length > 50 ? '...' : ''}`
        )
      );

      // Generate query file
      await this.generateQueryFile(config);

      console.log(chalk.green('\n🎉 Query generation completed successfully!'));
      console.log(chalk.cyan('\n💡 Next steps:'));
      console.log(
        chalk.gray(
          `  1. Review the generated query: queries/${config.queryName}-query.yaml`
        )
      );
      console.log(
        chalk.gray(
          `  2. Test the query: kubectl apply -f queries/${config.queryName}-query.yaml`
        )
      );
      console.log(chalk.gray(`  3. Check results: kubectl get queries`));
    }, 'Generating query');
  }
}
