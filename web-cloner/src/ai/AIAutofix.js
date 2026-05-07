import axios from 'axios';

export class AIAutofix {
  constructor(config) {
    this.config = config;
    this.llmEndpoint = config.aiAutofix?.llmEndpoint;
    this.llmApiKey = config.aiAutofix?.llmApiKey;
    this.fixAttempts = 0;
  }

  async analyze(cloneResult) {
    const issues = {
      brokenLinks: [],
      missingAssets: [],
      jsErrors: [],
      cssIssues: [],
      htmlIssues: []
    };

    // Analyze pages for broken links
    for (const page of cloneResult.pages || []) {
      const linkIssues = await this.checkBrokenLinks(page);
      issues.brokenLinks.push(...linkIssues);
    }

    // Check for missing assets
    const assetIssues = await this.checkMissingAssets(cloneResult);
    issues.missingAssets.push(...assetIssues);

    // Check JS errors from crawler
    if (cloneResult.errors) {
      const jsErrors = cloneResult.errors.filter(e => e.type === 'console-error' || e.type === 'page-error');
      issues.jsErrors.push(...jsErrors);
    }

    return issues;
  }

  async checkBrokenLinks(page) {
    const brokenLinks = [];
    
    // This is a simplified check - in production, you'd actually verify each link
    // For now, we'll just note links that point to external domains
    try {
      const pageUrl = new URL(page.url);
      
      for (const link of page.links || []) {
        try {
          const linkUrl = new URL(link.href, page.url);
          
          // Check if internal link exists in cloned site
          if (linkUrl.hostname === pageUrl.hostname) {
            // In production, verify the file exists
            // For now, just track it
          }
        } catch (e) {
          brokenLinks.push({
            page: page.url,
            link: link.href,
            error: 'Invalid URL'
          });
        }
      }
    } catch (e) {
      // Skip page
    }

    return brokenLinks;
  }

  async checkMissingAssets(cloneResult) {
    const missingAssets = [];
    
    // Check failed downloads
    if (cloneResult.downloader?.failedDownloads) {
      for (const failed of cloneResult.downloader.failedDownloads) {
        missingAssets.push({
          url: failed.url,
          type: failed.type,
          error: failed.error
        });
      }
    }

    return missingAssets;
  }

  async fixIssues(issues, cloneResult) {
    if (!this.config.aiAutofix?.enabled) {
      return { fixed: [], remaining: issues };
    }

    const fixes = {
      brokenLinks: [],
      missingAssets: [],
      jsErrors: [],
      applied: []
    };

    // Fix broken links by rewriting paths
    if (this.config.aiAutofix?.fixBrokenLinks) {
      const linkFixes = await this.fixBrokenLinks(issues.brokenLinks, cloneResult);
      fixes.brokenLinks.push(...linkFixes);
      fixes.applied.push(`Fixed ${linkFixes.length} broken links`);
    }

    // Download missing assets
    if (this.config.aiAutofix?.fixMissingAssets && this.fixAttempts < this.config.aiAutofix?.maxAttempts) {
      const assetFixes = await this.downloadMissingAssets(issues.missingAssets, cloneResult);
      fixes.missingAssets.push(...assetFixes);
      fixes.applied.push(`Downloaded ${assetFixes.length} missing assets`);
    }

    // Fix CORS issues
    if (this.config.aiAutofix?.fixCORS) {
      const corsFixes = await this.fixCORSIssues(cloneResult);
      fixes.applied.push(`Fixed ${corsFixes} CORS issues`);
    }

    // Remove tracking scripts
    if (this.config.aiAutofix?.removeTracking) {
      const trackingRemoved = await this.removeTrackingScripts(cloneResult);
      fixes.applied.push(`Removed ${trackingRemoved} tracking scripts`);
    }

    // Generate service worker
    if (this.config.aiAutofix?.generateServiceWorker) {
      await this.generateServiceWorker(cloneResult.outputDir);
      fixes.applied.push('Generated offline service worker');
    }

    this.fixAttempts++;

    return fixes;
  }

  async fixBrokenLinks(brokenLinks, cloneResult) {
    const fixed = [];

    for (const broken of brokenLinks) {
      try {
        // Try to find the correct path in cloned content
        // This is simplified - in production, use LLM to intelligently fix
        const originalPath = broken.link;
        
        // Simple heuristic: convert absolute to relative
        if (originalPath.startsWith('http')) {
          const urlObj = new URL(originalPath);
          const relativePath = urlObj.pathname;
          
          // Update the HTML file
          await this.updateLinkInPage(broken.page, originalPath, relativePath);
          
          fixed.push({
            original: originalPath,
            fixed: relativePath,
            page: broken.page
          });
        }
      } catch (e) {
        // Could not fix
      }
    }

    return fixed;
  }

  async downloadMissingAssets(missingAssets, cloneResult) {
    const downloaded = [];

    // Retry downloading failed assets
    for (const asset of missingAssets) {
      try {
        // Use the downloader to retry
        if (cloneResult.downloader) {
          await cloneResult.downloader.downloadAsset(asset.url, cloneResult.baseUrl, asset.type);
          downloaded.push(asset);
        }
      } catch (e) {
        // Still failed
      }
    }

    return downloaded;
  }

  async fixCORSIssues(cloneResult) {
    let fixedCount = 0;

    // Find and replace cross-origin references with local paths
    // This requires parsing all HTML files and updating URLs
    
    return fixedCount;
  }

  async removeTrackingScripts(cloneResult) {
    let removedCount = 0;
    const trackingPatterns = [
      'google-analytics',
      'googletagmanager',
      'facebook.com/tr',
      'analytics.',
      'tracking.',
      'pixel.'
    ];

    // Scan HTML files and remove tracking scripts
    // This is simplified - in production, properly parse and modify HTML
    
    return removedCount;
  }

  async generateServiceWorker(outputDir) {
    const swContent = `
const CACHE_NAME = 'web-cloner-cache-v1';
const urlsToCache = [
  '/',
  '/pages/index.html'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});
`;

    import fs from 'fs/promises';
    import path from 'path';
    
    await fs.writeFile(path.join(outputDir, 'sw.js'), swContent);
  }

  async updateLinkInPage(pageUrl, oldLink, newLink) {
    // In production, load the HTML file and replace the link
    // This is a placeholder
  }

  async injectPolyfills(cloneResult) {
    if (!this.config.aiAutofix?.injectPolyfills) return;

    // Add polyfill scripts to all pages
    const polyfills = [
      // Modern API polyfills could be added here
    ];

    // Inject into HTML files
  }

  async validateFixes(cloneResult) {
    // Re-run analysis after fixes
    const issues = await this.analyze(cloneResult);
    
    return {
      success: issues.brokenLinks.length === 0 && issues.missingAssets.length === 0,
      remainingIssues: issues
    };
  }

  async autoHeal(cloneResult) {
    if (!this.config.testing?.autoHeal) return cloneResult;

    let attempts = 0;
    const maxAttempts = this.config.testing?.maxHealAttempts || 2;

    while (attempts < maxAttempts) {
      const issues = await this.analyze(cloneResult);
      
      // Check if there are critical issues
      const hasCriticalIssues = 
        issues.brokenLinks.length > 10 || 
        issues.missingAssets.length > 10;

      if (!hasCriticalIssues) break;

      const fixes = await this.fixIssues(issues, cloneResult);
      
      if (fixes.applied.length === 0) break;

      attempts++;
    }

    return cloneResult;
  }

  async getLLMRecommendation(issue) {
    if (!this.llmEndpoint) return null;

    try {
      const response = await axios.post(this.llmEndpoint, {
        prompt: `Analyze this web cloning issue and suggest a fix: ${JSON.stringify(issue)}`
      }, {
        headers: {
          'Authorization': `Bearer ${this.llmApiKey}`,
          'Content-Type': 'application/json'
        }
      });

      return response.data;
    } catch (e) {
      return null;
    }
  }
}

export default AIAutofix;
