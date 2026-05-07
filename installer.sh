#!/bin/bash

# ArchiverPro One-Command Installer
# This script sets up the environment, installs dependencies, and initializes the project.

set -e

echo "🚀 Starting ArchiverPro Installation..."

# 1. Check for Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js v18+ first."
    exit 1
fi

echo "✅ Node.js found: $(node -v)"

# 2. Create Project Structure
PROJECT_DIR="archiver-pro"
if [ -d "$PROJECT_DIR" ]; then
    echo "⚠️  Directory $PROJECT_DIR already exists. Cleaning up..."
    rm -rf "$PROJECT_DIR"
fi

mkdir -p "$PROJECT_DIR"/{src/{api,jobs,workers,utils},public,logs,data}
cd "$PROJECT_DIR"

echo "📂 Project structure created."

# 3. Initialize NPM and Install Dependencies
echo "📦 Installing dependencies..."
npm init -y

npm install express cors helmet morgan uuid bull ioredis sqlite3 sequelize
npm install puppeteer cheerio axios node-fetch
npm install winston chalk commander inquirer
npm install --save-dev nodemon jest eslint

# 4. Create Basic Boilerplate Files
echo "📝 Generating boilerplate code..."

# .env file
cat > .env <<EOF
PORT=3000
NODE_ENV=development
DB_PATH=./data/archiver.db
REDIS_URL=redis://localhost:6379
ALLOWED_DOMAINS=example.com,myownsite.org
LOG_LEVEL=info
EOF

# Main Server Entry Point
cat > src/api/server.js <<EOF
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const { initJobRoutes } = require('./routes');
const logger = require('../utils/logger');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(helmet());
app.use(cors());
app.use(morgan('combined'));
app.use(express.json());

// Routes
initJobRoutes(app);

// Health Check
app.get('/health', (req, res) => {
    res.status(200).json({ status: 'ok', timestamp: new Date().toISOString() });
});

app.listen(PORT, () => {
    logger.info(\`ArchiverPro API listening on port \${PORT}\`);
});
EOF

mkdir -p src/api/routes
cat > src/api/routes/index.js <<EOF
const jobRoutes = require('./jobs');

module.exports.initJobRoutes = (app) => {
    app.use('/api/jobs', jobRoutes);
};
EOF

cat > src/api/routes/jobs.js <<EOF
const express = require('express');
const router = express.Router();
const { createJob, getJobStatus } = require('../../jobs/manager');
const { validateDomain } = require('../../utils/compliance');

// POST /api/jobs - Create a new archive job
router.post('/', async (req, res) => {
    const { url, options } = req.body;

    // Compliance Check
    if (!validateDomain(url)) {
        return res.status(403).json({ error: 'Domain not in allow-list or failed permission check.' });
    }

    try {
        const job = await createJob(url, options);
        res.status(201).json({ message: 'Job created', jobId: job.id });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// GET /api/jobs/:id - Get job status
router.get('/:id', async (req, res) => {
    try {
        const status = await getJobStatus(req.params.id);
        res.json(status);
    } catch (err) {
        res.status(404).json({ error: 'Job not found' });
    }
});

module.exports = router;
EOF

# Job Manager
mkdir -p src/jobs
cat > src/jobs/manager.js <<EOF
const { v4: uuidv4 } = require('uuid');
const logger = require('../utils/logger');
// In a real app, this would interact with a DB and Queue

const activeJobs = new Map();

module.exports.createJob = async (url, options) => {
    const jobId = uuidv4();
    const job = {
        id: jobId,
        url,
        options,
        status: 'pending',
        createdAt: new Date(),
        progress: 0
    };
    
    activeJobs.set(jobId, job);
    logger.info(\`Job \${jobId} created for \${url}\`);
    
    // Here we would dispatch to a worker queue
    // dispatchToWorker(job);
    
    return job;
};

module.exports.getJobStatus = async (jobId) => {
    const job = activeJobs.get(jobId);
    if (!job) throw new Error('Job not found');
    return job;
};
EOF

# Compliance Utility
mkdir -p src/utils
cat > src/utils/compliance.js <<EOF
const allowedDomains = (process.env.ALLOWED_DOMAINS || '').split(',');

module.exports.validateDomain = (url) => {
    try {
        const parsed = new URL(url);
        const domain = parsed.hostname.replace('www.', '');
        
        // Check against allow-list
        const isAllowed = allowedDomains.some(allowed => 
            domain === allowed || domain.endsWith('.' + allowed)
        );

        if (!isAllowed) {
            console.warn(\`Blocked attempt to crawl unauthorized domain: \${domain}\`);
            return false;
        }

        // Additional permission checklist logic could go here
        // e.g., checking robots.txt, requiring user confirmation flags
        
        return true;
    } catch (e) {
        return false;
    }
};
EOF

# Logger Utility
cat > src/utils/logger.js <<EOF
const winston = require('winston');

const logger = winston.createLogger({
    level: process.env.LOG_LEVEL || 'info',
    format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.json()
    ),
    transports: [
        new winston.transports.File({ filename: './logs/error.log', level: 'error' }),
        new winston.transports.File({ filename: './logs/combined.log' }),
        new winston.transports.Console({
            format: winston.format.simple()
        })
    ]
});

module.exports = logger;
EOF

# 5. Final Instructions
echo ""
echo "✅ Installation Complete!"
echo ""
echo "📁 Project directory: $PROJECT_DIR"
echo ""
echo "Next steps:"
echo "1. cd $PROJECT_DIR"
echo "2. Update .env with your allowed domains."
echo "3. (Optional) Start Redis if using advanced queuing: docker run -d -p 6379:6379 redis"
echo "4. Run the server: npm start"
echo ""
echo "⚠️  REMINDER: Always ensure you have explicit permission to archive target websites."
