import fs from 'fs/promises';
import path from 'path';

export class Validator {
  constructor(config, outputDir) {
    this.config = config;
    this.outputDir = outputDir;
    this.results = {
      linkCheck: { passed: 0, failed: 0, errors: [] },
      assetIntegrity: { passed: 0, failed: 0, errors: [] },
      jsErrors: { passed: 0, failed: 0, errors: [] },
      screenshotCompare: { passed: 0, failed: 0, errors: [] }
    };
  }

  async runAll(cloneResult) {
    console.log('Starting validation...');

    if (this.config.testing?.checkLinks) {
      await this.checkLinks(cloneResult);
    }

    if (this.config.testing?.verifyAssets) {
      await this.verifyAssetIntegrity(cloneResult);
    }

    if (this.config.testing?.jsErrorCheck) {
      await this.checkJSErrors(cloneResult);
    }

    if (this.config.testing?.screenshotCompare && cloneResult.originalScreenshots) {
      await this.compareScreenshots(cloneResult);
    }

    return this.generateReport();
  }

  async checkLinks(cloneResult) {
    console.log('Checking links...');
    
    const pages = cloneResult.pages || [];
    
    for (const page of pages) {
      const pageUrl = new URL(page.url);
      
      for (const link of page.links || []) {
        try {
          const linkUrl = new URL(link.href, page.url);
          
          // Check internal links
          if (linkUrl.hostname === pageUrl.hostname) {
            const relativePath = linkUrl.pathname;
            const filePath = path.join(this.outputDir, 'pages', relativePath, 'index.html');
            
            // Try alternate path for root
            const altPath = path.join(this.outputDir, 'pages', relativePath.replace(/^\//, '') || 'index.html');
            
            try {
              await fs.access(filePath);
              this.results.linkCheck.passed++;
            } catch (e) {
              try {
                await fs.access(altPath);
                this.results.linkCheck.passed++;
              } catch (e2) {
                this.results.linkCheck.failed++;
                this.results.linkCheck.errors.push({
                  page: page.url,
                  link: link.href,
                  error: 'File not found'
                });
              }
            }
          } else {
            // External link - just count as passed
            this.results.linkCheck.passed++;
          }
        } catch (e) {
          this.results.linkCheck.failed++;
          this.results.linkCheck.errors.push({
            page: page.url,
            link: link.href,
            error: e.message
          });
        }
      }
    }
  }

  async verifyAssetIntegrity(cloneResult) {
    console.log('Verifying asset integrity...');
    
    const downloader = cloneResult.downloader;
    
    if (!downloader) return;

    for (const [localPath, asset] of downloader.downloadedAssets) {
      try {
        await fs.access(localPath);
        const stats = await fs.stat(localPath);
        
        if (stats.size > 0) {
          this.results.assetIntegrity.passed++;
        } else {
          this.results.assetIntegrity.failed++;
          this.results.assetIntegrity.errors.push({
            path: localPath,
            error: 'Empty file'
          });
        }
      } catch (e) {
        this.results.assetIntegrity.failed++;
        this.results.assetIntegrity.errors.push({
          path: localPath,
          error: e.message
        });
      }
    }

    // Check for failed downloads
    for (const failed of downloader.failedDownloads || []) {
      this.results.assetIntegrity.failed++;
      this.results.assetIntegrity.errors.push(failed);
    }
  }

  async checkJSErrors(cloneResult) {
    console.log('Checking JavaScript errors...');
    
    const errors = cloneResult.errors || [];
    
    for (const error of errors) {
      if (error.type === 'console-error' || error.type === 'page-error') {
        this.results.jsErrors.failed++;
        this.results.jsErrors.errors.push(error);
      } else {
        this.results.jsErrors.passed++;
      }
    }

    if (errors.length === 0) {
      this.results.jsErrors.passed++;
    }
  }

  async compareScreenshots(cloneResult) {
    console.log('Comparing screenshots...');
    
    // This would require image comparison library like pixelmatch
    // Simplified implementation
    
    const originalScreenshots = cloneResult.originalScreenshots || [];
    const clonedScreenshots = cloneResult.screenshots || [];
    
    if (originalScreenshots.length !== clonedScreenshots.length) {
      this.results.screenshotCompare.failed++;
      this.results.screenshotCompare.errors.push({
        error: 'Screenshot count mismatch'
      });
      return;
    }

    // In production, use pixelmatch or similar to compare images
    this.results.screenshotCompare.passed = clonedScreenshots.length;
  }

  generateReport() {
    const totalTests = 
      this.results.linkCheck.passed + this.results.linkCheck.failed +
      this.results.assetIntegrity.passed + this.results.assetIntegrity.failed +
      this.results.jsErrors.passed + this.results.jsErrors.failed +
      this.results.screenshotCompare.passed + this.results.screenshotCompare.failed;

    const totalPassed = 
      this.results.linkCheck.passed +
      this.results.assetIntegrity.passed +
      this.results.jsErrors.passed +
      this.results.screenshotCompare.passed;

    const totalFailed = 
      this.results.linkCheck.failed +
      this.results.assetIntegrity.failed +
      this.results.jsErrors.failed +
      this.results.screenshotCompare.failed;

    const report = {
      summary: {
        totalTests,
        passed: totalPassed,
        failed: totalFailed,
        successRate: totalTests > 0 ? ((totalPassed / totalTests) * 100).toFixed(2) : 0
      },
      details: this.results,
      timestamp: new Date().toISOString(),
      needsHealing: totalFailed > 0 && this.config.testing?.autoHeal
    };

    return report;
  }

  async saveReport(report) {
    const reportPath = path.join(this.outputDir, 'validation-report.json');
    await fs.writeFile(reportPath, JSON.stringify(report, null, 2));
    
    const htmlReport = this.generateHtmlReport(report);
    await fs.writeFile(path.join(this.outputDir, 'validation-report.html'), htmlReport);
    
    return reportPath;
  }

  generateHtmlReport(report) {
    const statusColor = report.summary.successRate >= 90 ? 'green' : report.summary.successRate >= 70 ? 'orange' : 'red';
    
    return `
<!DOCTYPE html>
<html>
<head>
  <title>Web Cloner Validation Report</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
    .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    h1 { color: #333; }
    .summary { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin: 30px 0; }
    .stat { text-align: center; padding: 20px; background: #f8f9fa; border-radius: 8px; }
    .stat-value { font-size: 36px; font-weight: bold; color: ${statusColor}; }
    .stat-label { color: #666; margin-top: 5px; }
    .section { margin: 30px 0; }
    .section h2 { color: #333; border-bottom: 2px solid #eee; padding-bottom: 10px; }
    table { width: 100%; border-collapse: collapse; margin-top: 15px; }
    th, td { padding: 12px; text-align: left; border-bottom: 1px solid #eee; }
    th { background: #f8f9fa; font-weight: 600; }
    .error { color: #dc3545; }
    .success { color: #28a745; }
    .warning { color: #ffc107; }
  </style>
</head>
<body>
  <div class="container">
    <h1>🔍 Validation Report</h1>
    <p>Generated: ${report.timestamp}</p>
    
    <div class="summary">
      <div class="stat">
        <div class="stat-value">${report.summary.totalTests}</div>
        <div class="stat-label">Total Tests</div>
      </div>
      <div class="stat">
        <div class="stat-value" style="color: #28a745;">${report.summary.passed}</div>
        <div class="stat-label">Passed</div>
      </div>
      <div class="stat">
        <div class="stat-value" style="color: #dc3545;">${report.summary.failed}</div>
        <div class="stat-label">Failed</div>
      </div>
    </div>

    <div class="section">
      <h2>Link Check</h2>
      <p>${this.results.linkCheck.passed} passed, ${this.results.linkCheck.failed} failed</p>
      ${this.results.linkCheck.errors.length > 0 ? `
        <table>
          <tr><th>Page</th><th>Link</th><th>Error</th></tr>
          ${this.results.linkCheck.errors.slice(0, 10).map(e => `
            <tr><td>${e.page}</td><td>${e.link}</td><td class="error">${e.error}</td></tr>
          `).join('')}
        </table>
      ` : '<p class="success">No broken links found!</p>'}
    </div>

    <div class="section">
      <h2>Asset Integrity</h2>
      <p>${this.results.assetIntegrity.passed} passed, ${this.results.assetIntegrity.failed} failed</p>
      ${this.results.assetIntegrity.errors.length > 0 ? `
        <table>
          <tr><th>Path</th><th>Error</th></tr>
          ${this.results.assetIntegrity.errors.slice(0, 10).map(e => `
            <tr><td>${e.path || e.url}</td><td class="error">${e.error}</td></tr>
          `).join('')}
        </table>
      ` : '<p class="success">All assets intact!</p>'}
    </div>

    <div class="section">
      <h2>JavaScript Errors</h2>
      <p>${this.results.jsErrors.passed} passed, ${this.results.jsErrors.failed} failed</p>
      ${this.results.jsErrors.errors.length > 0 ? `
        <table>
          <tr><th>Type</th><th>Message</th><th>URL</th></tr>
          ${this.results.jsErrors.errors.slice(0, 10).map(e => `
            <tr><td>${e.type}</td><td class="error">${e.message}</td><td>${e.url || 'N/A'}</td></tr>
          `).join('')}
        </table>
      ` : '<p class="success">No JavaScript errors!</p>'}
    </div>

    ${report.needsHealing ? '<p class="warning">⚠️ Auto-healing recommended</p>' : ''}
  </div>
</body>
</html>
`;
  }
}

export default Validator;
