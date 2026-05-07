# ArchiverPro Architecture Diagram

## System Overview

```mermaid
graph TD
    User[User / Admin] --> WebUI[React Web UI]
    User --> CLI[Command Line Interface]
    User --> API[REST API Client]

    WebUI --> API_Gateway[Express.js API Gateway]
    CLI --> API_Gateway
    API --> API_Gateway

    subgraph "Backend Core"
        API_Gateway --> JobManager[Job Manager]
        JobManager --> Queue[Task Queue (Bull/Redis)]
        
        Queue --> CrawlerWorker[Crawler Worker]
        Queue --> RendererWorker[Headless Renderer Worker]
        Queue --> ExtractorWorker[Data Extractor Worker]
        
        CrawlerWorker --> Downloader[Asset Downloader]
        RendererWorker --> Puppeteer[Puppeteer Instance]
        ExtractorWorker --> Parser[HTML/JSON Parser]
        
        JobManager --> DB[(SQLite/PostgreSQL)]
        JobManager --> Logger[Audit Logger]
    end

    subgraph "Storage Layer"
        Downloader --> FileSystem[Local File System]
        Downloader --> S3[Optional S3 Bucket]
        DB --> MetaDB[Metadata & Job Status]
        Logger --> LogFiles[Audit Logs]
    end

    subgraph "External Targets"
        CrawlerWorker --> TargetSite[Target Website]
        Puppeteer --> TargetSite
        Downloader --> TargetSite
    end

    style User fill:#f9f,stroke:#333
    style WebUI fill:#bbf,stroke:#333
    style API_Gateway fill:#bfb,stroke:#333
    style JobManager fill:#fbf,stroke:#333
    style DB fill:#fbb,stroke:#333
```

## Component Descriptions

### 1. Frontend Layer
- **React Web UI**: Dashboard for job creation, monitoring, and log viewing.
- **CLI**: Direct command-line access for scripting and automation.
- **REST API Clients**: External integrations.

### 2. API Gateway (Express.js)
- Handles authentication (JWT).
- Validates domain allow-lists.
- Enforces permission checklists before job submission.
- Routes requests to the Job Manager.

### 3. Job Manager
- Core orchestration logic.
- Manages job states (Pending, Running, Paused, Completed, Failed).
- Interacts with the database for persistence.
- Dispatches tasks to the appropriate worker queues.

### 4. Worker Pool
- **Crawler Worker**: Traverses links, parses sitemaps, respects `robots.txt`.
- **Renderer Worker**: Spins up headless browsers (Puppeteer) for JS-heavy sites.
- **Extractor Worker**: Parses structured data (JSON-LD, RSS, OpenGraph).
- **Downloader**: Fetches binary assets (images, videos, fonts).

### 5. Storage & Compliance
- **Database**: Stores job metadata, URL trees, and audit trails.
- **File System**: Stores mirrored content with rewritten links.
- **Audit Logger**: Immutable logs of every action for compliance review.

## Data Flow
1. User submits a job via UI/CLI with a target URL.
2. API Gateway checks the **Domain Allow-list** and **Permission Checklist**.
3. If approved, Job Manager creates a record in the DB and pushes to the Queue.
4. Workers pick up tasks, fetch content, and save to disk/DB.
5. Progress is updated in real-time via WebSockets to the UI.
6. Upon completion, a summary report is generated in the Audit Log.
