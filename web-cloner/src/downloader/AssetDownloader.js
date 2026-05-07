import fs from 'fs/promises';
import path from 'path';
import axios from 'axios';
import { URL } from 'url';
import { beautify } from 'js-beautify';

export class AssetDownloader {
  constructor(config, outputDir) {
    this.config = config;
    this.outputDir = outputDir;
    this.downloadedAssets = new Map();
    this.failedDownloads = [];
    this.totalSize = 0;
  }

  async initialize() {
    // Create output directories
    const dirs = [
      'assets/images',
      'assets/css',
      'assets/js',
      'assets/fonts',
      'assets/videos',
      'assets/documents',
      'pages'
    ];

    for (const dir of dirs) {
      await fs.mkdir(path.join(this.outputDir, dir), { recursive: true });
    }

    return this;
  }

  async downloadAsset(assetUrl, baseUrl, type = 'unknown') {
    try {
      const parsedUrl = new URL(assetUrl, baseUrl);
      const fileName = this.generateFileName(parsedUrl.pathname, type);
      const outputPath = this.getOutputPath(type, fileName);

      // Check if already downloaded
      if (this.downloadedAssets.has(outputPath)) {
        return this.downloadedAssets.get(outputPath);
      }

      // Check size limits
      const headResponse = await axios.head(parsedUrl.href, { timeout: 5000 });
      const contentLength = parseInt(headResponse.headers['content-length'] || '0');

      if (contentLength > (this.config.limits?.maxDownloadSize || 104857600)) {
        throw new Error(`Asset too large: ${contentLength} bytes`);
      }

      if (this.totalSize + contentLength > (this.config.limits?.maxTotalSize || 1073741824)) {
        throw new Error('Total size limit exceeded');
      }

      // Download asset
      const response = await axios.get(parsedUrl.href, {
        responseType: 'arraybuffer',
        timeout: 30000,
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
      });

      // Save asset
      await fs.writeFile(outputPath, Buffer.from(response.data));
      
      this.downloadedAssets.set(outputPath, {
        originalUrl: assetUrl,
        localPath: outputPath,
        fileName,
        type,
        size: contentLength
      });

      this.totalSize += contentLength;

      return {
        originalUrl: assetUrl,
        localPath: outputPath,
        fileName,
        type,
        size: contentLength
      };

    } catch (error) {
      this.failedDownloads.push({ url: assetUrl, error: error.message, type });
      throw error;
    }
  }

  async downloadImages(images, baseUrl) {
    const results = [];
    
    for (const image of images) {
      if (!this.config.assets?.downloadImages) continue;

      try {
        // Handle srcset
        if (image.srcset) {
          const srcsetUrls = image.srcset.split(',').map(s => s.trim().split(' ')[0]);
          for (const srcUrl of srcsetUrls) {
            const result = await this.downloadAsset(srcUrl, baseUrl, 'image');
            results.push(result);
          }
        }

        // Handle regular src
        if (image.src && !image.src.startsWith('data:')) {
          const result = await this.downloadAsset(image.src, baseUrl, 'image');
          results.push(result);
        }
      } catch (error) {
        // Continue with next image
      }
    }

    return results;
  }

  async downloadStylesheets(stylesheets, baseUrl) {
    const results = [];

    for (const stylesheet of stylesheets) {
      try {
        const result = await this.downloadAsset(stylesheet, baseUrl, 'css');
        
        // Beautify CSS if enabled
        if (this.config.assets?.beautifyCode) {
          const content = await fs.readFile(result.localPath, 'utf-8');
          const beautified = beautify.css(content, { indent_size: 2 });
          await fs.writeFile(result.localPath, beautified);
        }

        results.push(result);
      } catch (error) {
        // Continue with next stylesheet
      }
    }

    return results;
  }

  async downloadScripts(scripts, baseUrl) {
    const results = [];

    for (const script of scripts) {
      try {
        const result = await this.downloadAsset(script, baseUrl, 'js');
        
        // Beautify JS if enabled
        if (this.config.assets?.beautifyCode) {
          const content = await fs.readFile(result.localPath, 'utf-8');
          const beautified = beautify.js(content, { indent_size: 2 });
          await fs.writeFile(result.localPath, beautified);
        }

        results.push(result);
      } catch (error) {
        // Continue with next script
      }
    }

    return results;
  }

  async downloadVideos(videos, baseUrl) {
    const results = [];

    for (const video of videos) {
      if (!this.config.assets?.downloadVideos) continue;

      try {
        const result = await this.downloadAsset(video, baseUrl, 'video');
        results.push(result);
      } catch (error) {
        // Try yt-dlp for YouTube/Vimeo
        if (this.config.assets?.ytDlpEnabled) {
          try {
            await this.downloadWithYtDlp(video);
          } catch (e) {
            // Failed to download
          }
        }
      }
    }

    return results;
  }

  async downloadFonts(fonts, baseUrl) {
    const results = [];

    if (!this.config.assets?.downloadFonts) return results;

    for (const font of fonts) {
      try {
        const result = await this.downloadAsset(font, baseUrl, 'font');
        results.push(result);
      } catch (error) {
        // Continue with next font
      }
    }

    return results;
  }

  async downloadWithYtDlp(videoUrl) {
    // Placeholder for yt-dlp integration
    // In production, use yt-dlp-wrap package
    console.log(`Would download video with yt-dlp: ${videoUrl}`);
  }

  async downloadAll(pageData, baseUrl) {
    await this.initialize();

    const results = {
      images: [],
      stylesheets: [],
      scripts: [],
      videos: [],
      fonts: []
    };

    // Download all asset types concurrently
    if (this.config.assets?.downloadImages) {
      results.images = await this.downloadImages(pageData.images || [], baseUrl);
    }

    if (pageData.stylesheets?.length > 0) {
      results.stylesheets = await this.downloadStylesheets(pageData.stylesheets, baseUrl);
    }

    if (pageData.scripts?.length > 0) {
      results.scripts = await this.downloadScripts(pageData.scripts, baseUrl);
    }

    if (this.config.assets?.downloadVideos) {
      results.videos = await this.downloadVideos(pageData.videos || [], baseUrl);
    }

    if (this.config.assets?.downloadFonts) {
      results.fonts = await this.downloadFonts(pageData.fonts || [], baseUrl);
    }

    return results;
  }

  async savePage(pageData, baseUrl) {
    const urlObj = new URL(pageData.url);
    let filePath;

    // Generate file path based on URL
    if (urlObj.pathname === '/') {
      filePath = path.join(this.outputDir, 'pages', 'index.html');
    } else {
      const cleanPath = urlObj.pathname.replace(/\/$/, '');
      const dirPath = path.join(this.outputDir, 'pages', cleanPath);
      await fs.mkdir(dirPath, { recursive: true });
      filePath = path.join(dirPath, 'index.html');
    }

    // Process HTML - rewrite asset URLs
    let html = pageData.html;
    html = this.rewriteAssetUrls(html, baseUrl);

    // Add base tag if enabled
    if (this.config.output?.addBaseTag) {
      html = html.replace('<head>', '<head>\n<base href="/">');
    }

    await fs.writeFile(filePath, html, 'utf-8');

    return { path: filePath, url: pageData.url };
  }

  rewriteAssetUrls(html, baseUrl) {
    let processedHtml = html;

    // Rewrite image URLs
    this.downloadedAssets.forEach((asset, localPath) => {
      if (asset.type === 'image') {
        const relativePath = path.relative(path.dirname(this.outputDir), localPath);
        processedHtml = processedHtml.replace(
          new RegExp(asset.originalUrl.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g'),
          `/${relativePath}`
        );
      }
    });

    // Rewrite CSS URLs
    this.downloadedAssets.forEach((asset, localPath) => {
      if (asset.type === 'css') {
        const relativePath = path.relative(path.dirname(this.outputDir), localPath);
        processedHtml = processedHtml.replace(
          new RegExp(asset.originalUrl.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g'),
          `/${relativePath}`
        );
      }
    });

    // Rewrite JS URLs
    this.downloadedAssets.forEach((asset, localPath) => {
      if (asset.type === 'js') {
        const relativePath = path.relative(path.dirname(this.outputDir), localPath);
        processedHtml = processedHtml.replace(
          new RegExp(asset.originalUrl.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g'),
          `/${relativePath}`
        );
      }
    });

    return processedHtml;
  }

  getOutputPath(type, fileName) {
    const typeMap = {
      'image': 'assets/images',
      'css': 'assets/css',
      'js': 'assets/js',
      'font': 'assets/fonts',
      'video': 'assets/videos',
      'document': 'assets/documents'
    };

    const dir = typeMap[type] || 'assets/other';
    return path.join(this.outputDir, dir, fileName);
  }

  generateFileName(urlPath, type) {
    const ext = path.extname(urlPath) || this.getDefaultExtension(type);
    const baseName = path.basename(urlPath, ext) || `asset_${Date.now()}`;
    return `${baseName}${ext}`;
  }

  getDefaultExtension(type) {
    const extensions = {
      'image': '.jpg',
      'css': '.css',
      'js': '.js',
      'font': '.woff2',
      'video': '.mp4',
      'document': '.pdf'
    };
    return extensions[type] || '.bin';
  }

  getStats() {
    return {
      totalAssets: this.downloadedAssets.size,
      totalSize: this.totalSize,
      failedDownloads: this.failedDownloads.length,
      byType: Array.from(this.downloadedAssets.values()).reduce((acc, asset) => {
        acc[asset.type] = (acc[asset.type] || 0) + 1;
        return acc;
      }, {})
    };
  }
}

export default AssetDownloader;
