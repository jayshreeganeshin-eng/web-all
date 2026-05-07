import express from 'express';
import cors from 'cors';
import { v4 as uuidv4 } from 'uuid';
import fs from 'fs/promises';
import path from 'path';
import archiver from 'archiver';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export class WebServer {
  constructor(config, cloneManager) {
    this.config = config;
    this.cloneManager = cloneManager;
    this.app = express();
    this.setupMiddleware();
    this.setupRoutes();
  }

  setupMiddleware() {
    this.app.use(cors({
      origin: this.config.api?.corsOrigins || ['*']
    }));
    this.app.use(express.json());
    this.app.use(express.urlencoded({ extended: true }));
    
    // API key authentication if configured
    if (this.config.api?.authKey) {
      this.app.use((req, res, next) => {
        const apiKey = req.headers['x-api-key'];
        if (apiKey !== this.config.api.authKey) {
          return res.status(401).json({ error: 'Unauthorized' });
        }
        next();
      });
    }
  }

  setupRoutes() {
    // Health check
    this.app.get('/health', (req, res) => {
      res.json({ status: 'ok', timestamp: new Date().toISOString() });
    });

    // Start clone job
    this.app.post('/api/clone', async (req, res) => {
      try {
        const { url, options = {} } = req.body;

        if (!url) {
          return res.status(400).json({ error: 'URL is required' });
        }

        const jobId = uuidv4();
        const jobConfig = { ...this.config, ...options };
        
        await this.cloneManager.startJob(jobId, url, jobConfig);

        res.json({
          success: true,
          jobId,
          status: 'started',
          message: 'Clone job started'
        });
      } catch (error) {
        res.status(500).json({ error: error.message });
      }
    });

    // Get job status
    this.app.get('/api/status/:jobId', async (req, res) => {
      try {
        const { jobId } = req.params;
        const status = await this.cloneManager.getJobStatus(jobId);

        if (!status) {
          return res.status(404).json({ error: 'Job not found' });
        }

        res.json(status);
      } catch (error) {
        res.status(500).json({ error: error.message });
      }
    });

    // Get all jobs
    this.app.get('/api/jobs', async (req, res) => {
      try {
        const jobs = await this.cloneManager.getAllJobs();
        res.json({ jobs });
      } catch (error) {
        res.status(500).json({ error: error.message });
      }
    });

    // Download cloned site
    this.app.get('/api/download/:jobId', async (req, res) => {
      try {
        const { jobId } = req.params;
        const job = await this.cloneManager.getJobStatus(jobId);

        if (!job || job.status !== 'completed') {
          return res.status(400).json({ error: 'Job not completed' });
        }

        const zipPath = await this.cloneManager.createZip(jobId);
        
        res.download(zipPath, `clone-${jobId}.zip`);
      } catch (error) {
        res.status(500).json({ error: error.message });
      }
    });

    // Run validation
    this.app.post('/api/validate/:jobId', async (req, res) => {
      try {
        const { jobId } = req.params;
        const result = await this.cloneManager.runValidation(jobId);

        res.json(result);
      } catch (error) {
        res.status(500).json({ error: error.message });
      }
    });

    // Cancel job
    this.app.delete('/api/job/:jobId', async (req, res) => {
      try {
        const { jobId } = req.params;
        await this.cloneManager.cancelJob(jobId);

        res.json({ success: true, message: 'Job cancelled' });
      } catch (error) {
        res.status(500).json({ error: error.message });
      }
    });

    // Serve web UI
    this.app.use('/', express.static(path.join(__dirname, '../ui')));

    // Error handler
    this.app.use((err, req, res, next) => {
      console.error(err.stack);
      res.status(500).json({ error: 'Something went wrong!' });
    });
  }

  async start() {
    const port = this.config.api?.port || 3000;
    
    return new Promise((resolve) => {
      this.server = this.app.listen(port, () => {
        console.log(`🚀 Web Cloner API running on http://localhost:${port}`);
        console.log(`📊 Dashboard: http://localhost:${port}`);
        console.log(`🔌 API Endpoint: http://localhost:${port}/api/clone`);
        resolve(this.server);
      });
    });
  }

  async stop() {
    if (this.server) {
      return new Promise((resolve) => {
        this.server.close(() => {
          console.log('Server stopped');
          resolve();
        });
      });
    }
  }
}

export default WebServer;
