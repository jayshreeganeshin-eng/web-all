import { ConfigLoader, Logger } from './utils/ConfigLoader.js';
import { CloneManager } from './CloneManager.js';
import { WebServer } from './api/WebServer.js';

class WebClonerApp {
  constructor() {
    this.config = null;
    this.logger = null;
    this.cloneManager = null;
    this.webServer = null;
  }

  async initialize(configPath = null) {
    console.log('🚀 Initializing Web Cloner Pro...');
    
    // Load configuration
    this.config = await ConfigLoader.load(configPath);
    
    // Setup logger
    this.logger = Logger.create(this.config);
    this.logger.info('Configuration loaded');

    // Initialize clone manager
    this.cloneManager = new CloneManager(this.config);
    this.logger.info('Clone manager initialized');

    return this;
  }

  async start() {
    // Start web server with API
    this.webServer = new WebServer(this.config, this.cloneManager);
    await this.webServer.start();

    // Start cleanup routine
    this.startCleanupRoutine();

    this.logger.info('Web Cloner Pro started successfully');
    
    return this;
  }

  async stop() {
    console.log('\n👋 Shutting down Web Cloner Pro...');
    
    if (this.webServer) {
      await this.webServer.stop();
    }

    this.logger.info('Web Cloner Pro stopped');
  }

  startCleanupRoutine() {
    // Cleanup old jobs every hour
    setInterval(async () => {
      try {
        await this.cloneManager.cleanupOldJobs(24);
      } catch (e) {
        this.logger.error('Cleanup failed:', e.message);
      }
    }, 60 * 60 * 1000);
  }

  // CLI command to start a clone job
  async clone(url, options = {}) {
    const jobId = `cli-${Date.now()}`;
    const config = { ...this.config, ...options };
    
    console.log(`🕷️  Starting clone of: ${url}`);
    console.log(`📁 Output: ${config.output?.directory || './output'}`);
    
    const job = await this.cloneManager.startJob(jobId, url, config);
    
    // Wait for completion
    return new Promise((resolve, reject) => {
      const checkStatus = async () => {
        const currentJob = await this.cloneManager.getJobStatus(jobId);
        
        if (currentJob.status === 'completed') {
          console.log(`✅ Clone completed!`);
          console.log(`📊 Pages: ${currentJob.result.pagesCount}`);
          console.log(`🖼️  Screenshots: ${currentJob.result.screenshotsCount}`);
          console.log(`📦 Assets: ${currentJob.result.assetsCount}`);
          resolve(currentJob);
        } else if (currentJob.status === 'failed') {
          console.error(`❌ Clone failed: ${currentJob.error}`);
          reject(new Error(currentJob.error));
        } else {
          setTimeout(checkStatus, 2000);
        }
      };
      
      checkStatus();
    });
  }
}

// Main entry point
async function main() {
  const app = new WebClonerApp();
  
  // Handle graceful shutdown
  process.on('SIGINT', async () => {
    await app.stop();
    process.exit(0);
  });

  process.on('SIGTERM', async () => {
    await app.stop();
    process.exit(0);
  });

  try {
    // Check for CLI arguments
    const args = process.argv.slice(2);
    const configPath = args.find(arg => arg.startsWith('--config='))?.split('=')[1];
    const targetUrl = args.find(arg => !arg.startsWith('--'));

    await app.initialize(configPath);

    if (targetUrl) {
      // CLI mode - clone immediately
      const options = {};
      
      if (args.includes('--stealth')) options.stealth = { enabled: true };
      if (args.includes('--ai-fix')) options.aiAutofix = { enabled: true };
      if (args.includes('--no-validate')) options.testing = { runValidation: false };
      
      await app.clone(targetUrl, options);
      await app.stop();
    } else {
      // Server mode - start API
      await app.start();
    }
  } catch (error) {
    console.error('Fatal error:', error);
    process.exit(1);
  }
}

// Export for programmatic use
export { WebClonerApp };

// Run if executed directly
if (process.argv[1]?.endsWith('index.js')) {
  main();
}

export default WebClonerApp;
