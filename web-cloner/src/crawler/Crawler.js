import puppeteer from 'puppeteer-extra';
import stealthPlugin from 'puppeteer-extra-plugin-stealth';
import { EventEmitter } from 'events';
import { URL } from 'url';
import fs from 'fs/promises';
import path from 'path';
import axios from 'axios';
import cheerio from 'cheerio';

export class Crawler extends EventEmitter {
  constructor(config) {
    super();
    this.config = config;
    this.browser = null;
    this.page = null;
    this.visitedUrls = new Set();
    this.queue = [];
    this.pages = [];
    this.assets = new Map();
    this.screenshots = [];
    this.errors = [];
  }

  async initialize() {
    // Enable stealth mode if configured
    if (this.config.stealth?.enabled) {
      puppeteer.use(stealthPlugin());
    }

    const launchOptions = {
      headless: 'new',
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-accelerated-2d-canvas',
        '--disable-gpu',
        '--window-size=1920,1080'
      ]
    };

    if (this.config.stealth?.enabled) {
      launchOptions.args.push('--disable-blink-features=AutomationControlled');
    }

    this.browser = await puppeteer.launch(launchOptions);
    this.page = await this.browser.newPage();

    // Set viewport
    await this.page.setViewport({ width: 1920, height: 1080 });

    // Configure request interception for asset tracking
    await this.setupRequestInterception();

    // Setup authentication if provided
    if (this.config.auth?.credentials?.username) {
      await this.authenticate(this.config.auth.credentials);
    }

    // Setup cookies if provided
    if (this.config.auth?.cookies?.length > 0) {
      await this.page.setCookie(...this.config.auth.cookies);
    }

    return this;
  }

  async setupRequestInterception() {
    const assets = [];
    
    await this.page.setRequestInterception(true);
    
    this.page.on('request', request => {
      const resourceType = request.resourceType();
      
      // Track all requests
      if (['image', 'stylesheet', 'script', 'font', 'media', 'document'].includes(resourceType)) {
        assets.push({
          url: request.url(),
          type: resourceType,
          headers: request.headers()
        });
      }
      
      request.continue();
    });

    this.page.on('response', async response => {
      const url = response.url();
      const status = response.status();
      
      if (status >= 200 && status < 300) {
        this.emit('asset-discovered', { url, type: response.request().resourceType() });
      }
    });

    this.page.on('pageerror', error => {
      this.errors.push({ type: 'page-error', message: error.message, url: this.page.url() });
      this.emit('error', { type: 'page-error', error });
    });

    this.page.on('console', msg => {
      if (msg.type() === 'error') {
        this.errors.push({ type: 'console-error', message: msg.text(), url: this.page.url() });
      }
    });
  }

  async authenticate(credentials) {
    await this.page.authenticate(credentials);
  }

  async setViewport(device) {
    const devices = {
      'desktop': { width: 1920, height: 1080, deviceScaleFactor: 1 },
      'tablet': { width: 768, height: 1024, deviceScaleFactor: 2 },
      'mobile': { width: 375, height: 667, deviceScaleFactor: 2 },
      'iPhone 13': { width: 390, height: 844, deviceScaleFactor: 3 },
      'Pixel 5': { width: 393, height: 851, deviceScaleFactor: 2.75 },
      'iPad Pro': { width: 1024, height: 1366, deviceScaleFactor: 2 }
    };

    const viewport = devices[device] || devices['desktop'];
    await this.page.setViewport(viewport);
  }

  async navigate(url) {
    const baseUrl = new URL(url);
    
    try {
      const response = await this.page.goto(url, {
        waitUntil: ['networkidle0', 'domcontentloaded'],
        timeout: this.config.target?.timeout || 30000
      });

      // Wait for dynamic content
      await this.waitForDynamicContent();

      // Auto-scroll to load lazy content
      if (this.config.crawl?.scrollPage) {
        await this.scrollPage();
      }

      // Click navigation elements
      if (this.config.crawl?.clickElements) {
        await this.clickNavigationElements();
      }

      // Auto-accept cookie consent
      if (this.config.stealth?.cookieConsentAutoAccept) {
        await this.acceptCookieConsent();
      }

      return response;
    } catch (error) {
      this.errors.push({ type: 'navigation-error', message: error.message, url });
      throw error;
    }
  }

  async waitForDynamicContent() {
    const waitTime = this.config.crawl?.waitTime || 2000;
    await this.page.waitForTimeout(waitTime);

    // Wait for XHR requests to complete
    try {
      await this.page.waitForFunction(() => {
        return window.performance.getEntriesByType('resource').filter(r => r.initiatorType === 'xmlhttprequest').length > 0;
      }, { timeout: 5000 }).catch(() => {});
    } catch (e) {
      // No XHR requests or timeout
    }
  }

  async scrollPage() {
    await this.page.evaluate(async () => {
      await new Promise((resolve) => {
        let totalHeight = 0;
        const distance = 100;
        const timer = setInterval(() => {
          window.scrollBy(0, distance);
          totalHeight += distance;
          if (window.innerHeight + window.scrollY >= document.body.offsetHeight - distance || totalHeight > 5000) {
            clearInterval(timer);
            resolve();
          }
        }, 100);
      });
    });
  }

  async clickNavigationElements() {
    const selectors = [
      'a[href]',
      'button',
      '[role="button"]',
      '.nav-link',
      '.menu-item'
    ];

    try {
      await this.page.evaluate((selectors) => {
        selectors.forEach(selector => {
          const elements = document.querySelectorAll(selector);
          elements.forEach(el => {
            if (el.offsetParent !== null) { // Visible element
              el.click?.();
            }
          });
        });
      }, selectors);
      
      await this.waitForTimeout(1000);
    } catch (e) {
      // Some elements may not be clickable
    }
  }

  async acceptCookieConsent() {
    const cookieSelectors = [
      '#cookie-accept',
      '.cookie-accept',
      '[data-cookie-accept]',
      '#accept-cookies',
      '.accept-cookies',
      '#cookie-consent-accept',
      '[aria-label*="accept"]',
      'button[contains(text(), "Accept")]'
    ];

    for (const selector of cookieSelectors) {
      try {
        const element = await this.page.$(selector);
        if (element) {
          await element.click();
          await this.waitForTimeout(500);
          break;
        }
      } catch (e) {
        continue;
      }
    }
  }

  async takeScreenshot(pageUrl, options = {}) {
    const viewports = this.config.screenshots?.viewport || ['desktop'];
    const screenshots = [];

    for (const viewport of viewports) {
      await this.setViewport(viewport);
      
      const fileName = this.generateScreenshotFileName(pageUrl, viewport);
      const filePath = path.join(this.config.output?.directory || './output', 'screenshots', fileName);

      await fs.mkdir(path.dirname(filePath), { recursive: true });

      const screenshotOptions = {
        path: filePath,
        fullPage: this.config.screenshots?.fullPage !== false,
        type: this.config.screenshots?.formats?.[0] || 'png'
      };

      await this.page.screenshot(screenshotOptions);
      
      screenshots.push({
        url: pageUrl,
        viewport,
        path: filePath,
        fileName
      });
    }

    this.screenshots.push(...screenshots);
    this.emit('screenshot-taken', screenshots);
    
    return screenshots;
  }

  async extractPageContent() {
    const html = await this.page.content();
    const $ = cheerio.load(html);
    
    const pageData = {
      url: this.page.url(),
      html,
      title: $('title').text(),
      meta: {},
      links: [],
      images: [],
      scripts: [],
      stylesheets: [],
      videos: [],
      fonts: []
    };

    // Extract meta tags
    $('meta').each((i, el) => {
      const name = $(el).attr('name') || $(el).attr('property');
      const content = $(el).attr('content');
      if (name && content) {
        pageData.meta[name] = content;
      }
    });

    // Extract links
    $('a[href]').each((i, el) => {
      const href = $(el).attr('href');
      if (href) {
        pageData.links.push({
          href,
          text: $(el).text().trim(),
          rel: $(el).attr('rel')
        });
      }
    });

    // Extract images
    $('img[src], img[srcset]').each((i, el) => {
      const src = $(el).attr('src');
      const srcset = $(el).attr('srcset');
      if (src || srcset) {
        pageData.images.push({
          src,
          srcset,
          alt: $(el).attr('alt'),
          loading: $(el).attr('loading')
        });
      }
    });

    // Extract scripts
    $('script[src]').each((i, el) => {
      const src = $(el).attr('src');
      if (src) {
        pageData.scripts.push(src);
      }
    });

    // Extract stylesheets
    $('link[rel="stylesheet"], link[href*=".css"]').each((i, el) => {
      const href = $(el).attr('href');
      if (href) {
        pageData.stylesheets.push(href);
      }
    });

    // Extract videos
    $('video source[src], video[src]').each((i, el) => {
      const src = $(el).attr('src');
      if (src) {
        pageData.videos.push(src);
      }
    });

    // Extract fonts from CSS
    const fontUrls = await this.extractFontUrls($);
    pageData.fonts = fontUrls;

    return pageData;
  }

  async extractFontUrls($) {
    const fonts = [];
    const styleTags = $('style');
    const linkTags = $('link[rel="stylesheet"]');

    // This is simplified - in production, you'd fetch and parse CSS files
    styleTags.each((i, el) => {
      const css = $(el).html();
      const fontMatches = css.match(/url\(['"]?(.*?\.(woff2?|ttf|otf|eot))['"]?\)/gi);
      if (fontMatches) {
        fonts.push(...fontMatches.map(m => m.replace(/url\(['"]?|['"]?\)/gi, '')));
      }
    });

    return [...new Set(fonts)];
  }

  async discoverSitemapUrls(baseUrl) {
    const urls = new Set();
    const sitemapUrls = [
      '/sitemap.xml',
      '/sitemap_index.xml',
      '/sitemap-index.xml',
      '/atom.xml',
      '/rss.xml',
      '/feed.xml'
    ];

    for (const sitemapPath of sitemapUrls) {
      try {
        const sitemapUrl = new URL(sitemapPath, baseUrl).href;
        const response = await axios.get(sitemapUrl, { timeout: 5000 });
        
        if (response.status === 200) {
          const $ = cheerio.load(response.data, { xmlMode: true });
          
          // Parse sitemap.xml
          $('url loc').each((i, el) => {
            urls.add($(el).text());
          });

          // Parse sitemap index
          $('sitemap loc').each((i, el) => {
            const nestedSitemapUrl = $(el).text();
            // Recursively fetch nested sitemaps
            this.discoverSitemapUrls(nestedSitemapUrl).then(nestedUrls => {
              nestedUrls.forEach(url => urls.add(url));
            });
          });

          // Parse RSS/Atom
          $('entry link[href], item link').each((i, el) => {
            const link = $(el).attr('href') || $(el).text();
            if (link) urls.add(link);
          });

          this.emit('sitemap-discovered', { sitemap: sitemapUrl, count: urls.size });
        }
      } catch (e) {
        // Sitemap not found, continue
      }
    }

    return Array.from(urls);
  }

  async bruteForcePaths(baseUrl, paths = []) {
    const commonPaths = [
      '/admin', '/login', '/wp-admin', '/wp-login.php',
      '/dashboard', '/profile', '/settings', '/account',
      '/api', '/graphql', '/rest', '/v1', '/v2',
      '/checkout', '/cart', '/payment', '/billing',
      '/search', '/contact', '/about', '/faq', '/help'
    ];

    const pathsToTry = paths.length > 0 ? paths : commonPaths;
    const foundUrls = [];

    for (const path of pathsToTry) {
      try {
        const url = new URL(path, baseUrl).href;
        const response = await this.page.goto(url, { waitUntil: 'domcontentloaded', timeout: 5000 });
        
        if (response.status() === 200) {
          foundUrls.push(url);
          this.emit('path-discovered', { url, path });
        }
      } catch (e) {
        // Path doesn't exist
      }
    }

    return foundUrls;
  }

  async addToQueue(url, depth = 0) {
    if (this.visitedUrls.has(url) || depth > (this.config.target?.depth || 10)) {
      return;
    }

    if (this.queue.length >= (this.config.target?.maxPages || 1000)) {
      return;
    }

    this.queue.push({ url, depth });
    this.visitedUrls.add(url);
  }

  async crawl(startUrl) {
    await this.initialize();
    
    // Discover sitemap URLs first
    if (this.config.sitemap?.parseSitemapXml) {
      const sitemapUrls = await this.discoverSitemapUrls(startUrl);
      sitemapUrls.forEach(url => this.addToQueue(url, 0));
    }

    // Add start URL
    await this.addToQueue(startUrl, 0);

    // Process queue
    while (this.queue.length > 0) {
      const { url, depth } = this.queue.shift();
      
      if (this.visitedUrls.has(url)) continue;
      
      this.emit('crawling', { url, depth, remaining: this.queue.length });

      try {
        await this.navigate(url);
        
        // Extract content
        const pageData = await this.extractPageContent();
        this.pages.push(pageData);
        this.emit('page-crawled', pageData);

        // Take screenshots
        if (this.config.screenshots?.enabled) {
          await this.takeScreenshot(url);
        }

        // Extract and queue new links
        const baseUrlObj = new URL(startUrl);
        for (const link of pageData.links) {
          try {
            const absoluteUrl = new URL(link.href, url).href;
            const linkUrl = new URL(absoluteUrl);

            // Only follow same-domain links
            if (linkUrl.hostname === baseUrlObj.hostname) {
              await this.addToQueue(absoluteUrl, depth + 1);
            }
          } catch (e) {
            // Invalid URL
          }
        }

        // Brute force paths if enabled
        if (this.config.sitemap?.bruteForcePaths && depth === 0) {
          const foundPaths = await this.bruteForcePaths(startUrl, this.config.sitemap?.pathDictionary);
          foundPaths.forEach(pathUrl => this.addToQueue(pathUrl, depth + 1));
        }

      } catch (error) {
        this.errors.push({ type: 'crawl-error', message: error.message, url });
        this.emit('error', { type: 'crawl-error', url, error });
      }
    }

    await this.close();
    
    return {
      pages: this.pages,
      screenshots: this.screenshots,
      errors: this.errors,
      visitedUrls: Array.from(this.visitedUrls)
    };
  }

  async close() {
    if (this.browser) {
      await this.browser.close();
    }
  }

  generateScreenshotFileName(url, viewport) {
    const urlHash = Buffer.from(url).toString('base64').substring(0, 16);
    const timestamp = Date.now();
    return `screenshot_${viewport}_${urlHash}_${timestamp}.png`;
  }

  waitForTimeout(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

export default Crawler;
