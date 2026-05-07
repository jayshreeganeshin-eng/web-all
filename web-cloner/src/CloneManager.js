import { Crawler } from './crawler/Crawler.js';
import { AssetDownloader } from './downloader/AssetDownloader.js';
import { AIAutofix } from './ai/AIAutofix.js';
import { Validator } from './utils/Validator.js';
import fs from 'fs/promises';
import path from 'path';
import archiver from 'archiver';

export class CloneManager {
  constructor(config) {
    this.config = config;
    this.jobs = new Map();
    this.outputBaseDir = config.output?.directory || './output';
  }

  async startJob(jobId, url, jobConfig) {
    const job = {
      id: jobId,
      url,
      config: jobConfig,
      status: 'running',
      progress: 0,
      startedAt: new Date().toISOString(),
      completedAt: null,
      error: null,
      result: null
    };

    this.jobs.set(jobId, job);

    // Run clone process in background
    this.runCloneProcess(job).catch(error => {
      job.status = 'failed';
      job.error = error.message;
      job.completedAt = new Date().toISOString();
    });

    return job;
  }

  async runCloneProcess(job) {
    try {
      const outputDir = path.join(this.outputBaseDir, job.id);
      await fs.mkdir(outputDir, { recursive: true });

      // Initialize crawler
      const crawler = new Crawler(job.config);
      
      crawler.on('crawling', (data) => {
        job.progress = Math.min(90, (data.depth / (job.config.target?.depth || 10)) * 100);
        job.currentUrl = data.url;
        job.pagesCrawled = this.jobs.get(job.id).pagesCrawled || 0 + 1;
      });

      crawler.on('page-crawled', (pageData) => {
        job.pagesCrawled = (job.pagesCrawled || 0) + 1;
      });

      crawler.on('screenshot-taken', (screenshots) => {
        job.screenshotsTaken = (job.screenshotsTaken || 0) + screenshots.length;
      });

      crawler.on('asset-discovered', (asset) => {
        job.assetsDiscovered = (job.assetsDiscovered || 0) + 1;
      });

      crawler.on('error', (error) => {
        job.errors = job.errors || [];
        job.errors.push(error);
      });

      // Start crawling
      console.log(`🕷️  Starting crawl: ${job.url}`);
      const crawlResult = await crawler.crawl(job.url);

      // Download assets
      console.log('⬇️  Downloading assets...');
      const downloader = new AssetDownloader(job.config, outputDir);
      await downloader.initialize();

      for (const page of crawlResult.pages) {
        await downloader.downloadAll(page, job.url);
        await downloader.savePage(page, job.url);
      }

      crawlResult.downloader = downloader;
      crawlResult.outputDir = outputDir;
      crawlResult.baseUrl = job.url;

      // AI Auto-fix if enabled
      if (job.config.aiAutofix?.enabled) {
        console.log('🤖 Running AI auto-fix...');
        const aiFixer = new AIAutofix(job.config);
        const issues = await aiFixer.analyze(crawlResult);
        const fixes = await aiFixer.fixIssues(issues, crawlResult);
        crawlResult.aiFixes = fixes;
      }

      // Validation
      if (job.config.testing?.runValidation) {
        console.log('✅ Running validation...');
        const validator = new Validator(job.config, outputDir);
        const report = await validator.runAll(crawlResult);
        await validator.saveReport(report);
        crawlResult.validationReport = report;

        // Auto-heal if needed
        if (report.needsHealing && job.config.testing?.autoHeal) {
          console.log('🔧 Auto-healing...');
          const aiFixer = new AIAutofix(job.config);
          await aiFixer.autoHeal(crawlResult);
          
          // Re-validate
          const newReport = await validator.runAll(crawlResult);
          await validator.saveReport(newReport);
          crawlResult.validationReport = newReport;
        }
      }

      // Create zip
      if (job.config.output?.createZip) {
        console.log('📦 Creating archive...');
        await this.createZip(job.id);
      }

      // Update job status
      job.status = 'completed';
      job.progress = 100;
      job.completedAt = new Date().toISOString();
      job.result = {
        pagesCount: crawlResult.pages.length,
        screenshotsCount: crawlResult.screenshots.length,
        assetsCount: downloader.getStats().totalAssets,
        errorsCount: crawlResult.errors.length,
        outputDir,
        validationReport: crawlResult.validationReport
      };

      console.log(`✅ Clone completed: ${job.result.pagesCount} pages, ${job.result.assetsCount} assets`);

    } catch (error) {
      console.error('❌ Clone failed:', error);
      throw error;
    }
  }

  async getJobStatus(jobId) {
    return this.jobs.get(jobId);
  }

  async getAllJobs() {
    return Array.from(this.jobs.values());
  }

  async cancelJob(jobId) {
    const job = this.jobs.get(jobId);
    if (job) {
      job.status = 'cancelled';
      job.completedAt = new Date().toISOString();
    }
  }

  async createZip(jobId) {
    const job = this.jobs.get(jobId);
    if (!job) throw new Error('Job not found');

    const outputDir = path.join(this.outputBaseDir, jobId);
    const zipPath = path.join(this.outputBaseDir, `clone-${jobId}.zip`);

    return new Promise((resolve, reject) => {
      const output = fs.createWriteStream(zipPath);
      const archive = archiver('zip', { zlib: { level: 9 } });

      output.on('close', () => {
        console.log(`Archive created: ${archive.pointer()} total bytes`);
        resolve(zipPath);
      });

      archive.on('error', (err) => {
        reject(err);
      });

      archive.pipe(output);
      archive.directory(outputDir, false);
      archive.finalize();
    });
  }

  async runValidation(jobId) {
    const job = this.jobs.get(jobId);
    if (!job) throw new Error('Job not found');
    if (job.status !== 'completed') throw new Error('Job not completed');

    const outputDir = path.join(this.outputBaseDir, jobId);
    const validator = new Validator(job.config, outputDir);
    
    // Load previous result if available
    const cloneResult = job.result || {};
    cloneResult.outputDir = outputDir;
    cloneResult.baseUrl = job.url;

    const report = await validator.runAll(cloneResult);
    await validator.saveReport(report);

    return report;
  }

  async cleanupOldJobs(maxAgeHours = 24) {
    const now = Date.now();
    const maxAge = maxAgeHours * 60 * 60 * 1000;

    for (const [jobId, job] of this.jobs) {
      if (job.completedAt) {
        const completedTime = new Date(job.completedAt).getTime();
        if (now - completedTime > maxAge) {
          // Delete output directory
          const outputDir = path.join(this.outputBaseDir, jobId);
          try {
            await fs.rm(outputDir, { recursive: true, force: true });
            this.jobs.delete(jobId);
            console.log(`Cleaned up old job: ${jobId}`);
          } catch (e) {
            console.error(`Failed to cleanup job ${jobId}:`, e.message);
          }
        }
      }
    }
  }
}

export default CloneManager;
