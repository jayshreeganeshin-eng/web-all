import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import yaml from 'yaml';
import winston from 'winston';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export class ConfigLoader {
  static async load(configPath = null) {
    const defaultConfigPath = path.join(__dirname, '../config/default.yaml');
    
    let configData = {};
    
    // Load default config
    try {
      const defaultContent = await fs.readFile(defaultConfigPath, 'utf-8');
      configData = yaml.parse(defaultContent);
    } catch (e) {
      console.warn('Could not load default config, using defaults');
    }

    // Override with custom config if provided
    if (configPath) {
      try {
        const customContent = await fs.readFile(configPath, 'utf-8');
        const customConfig = yaml.parse(customContent);
        configData = this.mergeDeep(configData, customConfig);
      } catch (e) {
        console.error('Could not load custom config:', e.message);
      }
    }

    // Override with environment variables
    configData = this.applyEnvOverrides(configData);

    return configData;
  }

  static applyEnvOverrides(config) {
    const envMap = {
      'TARGET_URL': ['target', 'url'],
      'CRAWL_DEPTH': ['target', 'depth'],
      'CRAWL_MAX_PAGES': ['target', 'maxPages'],
      'STEALTH_ENABLED': ['stealth', 'enabled'],
      'AI_AUTOFIX_ENABLED': ['aiAutofix', 'enabled'],
      'AI_LLM_ENDPOINT': ['aiAutofix', 'llmEndpoint'],
      'AI_LLM_API_KEY': ['aiAutofix', 'llmApiKey'],
      'API_PORT': ['api', 'port'],
      'API_AUTH_KEY': ['api', 'authKey'],
      'OUTPUT_DIR': ['output', 'directory'],
      'LOG_LEVEL': ['logging', 'level']
    };

    for (const [envVar, configPath] of Object.entries(envMap)) {
      const value = process.env[envVar];
      if (value !== undefined) {
        let current = config;
        for (let i = 0; i < configPath.length - 1; i++) {
          current = current[configPath[i]];
        }
        const lastKey = configPath[configPath.length - 1];
        
        // Type conversion
        if (value === 'true') current[lastKey] = true;
        else if (value === 'false') current[lastKey] = false;
        else if (!isNaN(value) && value !== '') current[lastKey] = parseInt(value);
        else current[lastKey] = value;
      }
    }

    return config;
  }

  static mergeDeep(target, source) {
    const output = Object.assign({}, target);
    
    if (this.isObject(target) && this.isObject(source)) {
      Object.keys(source).forEach(key => {
        if (this.isObject(source[key])) {
          if (!(key in target)) {
            Object.assign(output, { [key]: source[key] });
          } else {
            output[key] = this.mergeDeep(target[key], source[key]);
          }
        } else {
          Object.assign(output, { [key]: source[key] });
        }
      });
    }
    
    return output;
  }

  static isObject(item) {
    return (item && typeof item === 'object' && !Array.isArray(item));
  }
}

export class Logger {
  static create(config) {
    const logLevel = config?.logging?.level || 'info';
    const logFile = config?.logging?.file || './logs/web-cloner.log';
    const consoleLog = config?.logging?.console !== false;

    const transports = [];

    if (consoleLog) {
      transports.push(
        new winston.transports.Console({
          format: winston.format.combine(
            winston.format.colorize(),
            winston.format.simple()
          )
        })
      );
    }

    transports.push(
      new winston.transports.File({
        filename: logFile,
        format: winston.format.combine(
          winston.format.timestamp(),
          winston.format.json()
        )
      })
    );

    return winston.createLogger({
      level: logLevel,
      transports,
      defaultMeta: { service: 'web-cloner' }
    });
  }
}

export default { ConfigLoader, Logger };
