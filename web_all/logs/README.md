# Web-All Error Logging System Documentation

## Overview

This production-ready error logging system provides comprehensive error tracking, monitoring, and debugging capabilities for the web-all application. It includes:

1. **Centralized Logger** (`utils/logger.py`) - Captures all errors, warnings, and operational logs
2. **Web Dashboard** (`gui/error_logs.html`) - Real-time error monitoring interface for web-all repo
3. **Domain Cloning Errors** (`gui/domain_cloning_errors.html`) - Specialized dashboard for domain cloning failures
4. **REST API Endpoints** - Programmatic access to logs and error data

## Features

### ✅ Production-Ready Features

- **Automatic Log Rotation**: Logs rotate at 10MB with configurable backup count
- **Structured Logging**: JSON-formatted error context for easy parsing
- **Multi-Level Logging**: DEBUG, INFO, WARNING, ERROR levels
- **Thread-Safe**: Singleton pattern with thread locking
- **Error History Tracking**: In-memory error history (up to 1000 entries)
- **Export Functionality**: Export errors to JSON for external analysis
- **Separate Log Files**: Dedicated files for different components:
  - `web_all.log` - Main application log
  - `errors.log` - Error-specific log
  - `cloner.log` - Website cloner operations
  - `api.log` - API server operations

### 🎨 Dashboard Features

#### General Error Logs Dashboard (`/gui/error_logs.html`)
- Real-time error statistics
- Filterable error and warning lists
- Search functionality
- Auto-refresh every 30 seconds
- Export to JSON capability
- System health status indicator

#### Domain Cloning Errors Dashboard (`/gui/domain_cloning_errors.html`)
- Domain-specific error filtering
- Error type categorization (Timeout, Network, Parse, DNS, SSL)
- Severity indicators (Critical, High, Medium, Low)
- Activity timeline visualization
- Success rate tracking
- Common errors analysis

## Installation & Setup

### 1. Import the Logger

```python
from web_all.utils.logger import log_capture, get_logger, log_error, log_warning, log_info

# Option 1: Use the global instance
log_capture.log_error("Something went wrong", exception=e, context={"url": "https://example.com"})

# Option 2: Get a named logger
logger = get_logger("cloner")
logger.info("Cloning started")

# Option 3: Use convenience functions
log_error("Connection failed", exception=e)
log_warning("Rate limit approaching")
log_info("Operation completed")
```

### 2. Access the Dashboards

Start the API server:

```bash
cd /workspace
python -m web_all.api.server
```

Then access the dashboards in your browser:
- **General Error Logs**: `http://localhost:8000/gui/error_logs.html`
- **Domain Cloning Errors**: `http://localhost:8000/gui/domain_cloning_errors.html`

### 3. API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/logs/summary` | GET | Get comprehensive logs summary |
| `/api/v1/logs/errors` | GET | Get paginated error logs |
| `/api/v1/logs/errors/export` | GET | Export all errors to JSON |
| `/api/v1/logs/cloning/summary` | GET | Get cloning-specific error summary |
| `/api/v1/logs/clear` | POST | Clear all logs (admin only) |
| `/api/v1/logs/files` | GET | Get log file information |

## Usage Examples

### Basic Logging

```python
from web_all.utils.logger import log_capture

# Log an info message
log_capture.log_info("User logged in", {"user_id": 123})

# Log a warning
log_capture.log_warning("High memory usage", {"memory_percent": 85})

# Log an error with exception
try:
    result = risky_operation()
except Exception as e:
    log_capture.log_error(
        "Operation failed",
        exception=e,
        context={"operation": "risky_operation", "retry_count": 3}
    )
```

### Using Named Loggers

```python
from web_all.utils.logger import get_logger

# Get component-specific logger
cloner_logger = get_logger("cloner")
api_logger = get_logger("api")

cloner_logger.info("Starting clone operation")
api_logger.debug("Request received")
```

### Exporting Errors

```python
from web_all.utils.logger import log_capture

# Export errors to default location
output_path = log_capture.export_errors_to_json()
print(f"Errors exported to: {output_path}")

# Export to custom location
custom_path = log_capture.export_errors_to_json("/path/to/custom/export.json")
```

### Getting Error Summary

```python
from web_all.utils.logger import log_capture

summary = log_capture.get_error_summary()
print(f"Total errors: {summary['total_errors']}")
print(f"Total warnings: {summary['total_warnings']}")
print(f"Recent errors: {len(summary['recent_errors'])}")
```

## Log File Locations

All logs are stored in `/workspace/web_all/logs/`:

```
web_all/logs/
├── web_all.log      # Main application log (rotates at 10MB, 5 backups)
├── errors.log       # Error-only log (rotates at 10MB, 10 backups)
├── cloner.log       # Cloner-specific operations log
└── api.log          # API server operations log
```

## Error Context Structure

Each logged error includes structured context:

```json
{
  "timestamp": "2024-01-15T10:30:45.123456",
  "message": "Connection timeout",
  "level": "ERROR",
  "logger": "cloner",
  "exception_type": "TimeoutError",
  "exception_message": "Request timed out after 30s",
  "stack_trace": "Traceback (most recent call last):\n...",
  "context": {
    "url": "https://example.com/page",
    "depth": 2,
    "retry_count": 3
  }
}
```

## Best Practices

### 1. Always Include Context

```python
# ❌ Bad
log_error("Failed to connect")

# ✅ Good
log_error(
    "Failed to connect",
    exception=e,
    context={
        "url": url,
        "timeout": timeout,
        "retry_count": retry_count,
        "proxy_enabled": use_proxy
    }
)
```

### 2. Use Appropriate Log Levels

- **DEBUG**: Detailed technical information for debugging
- **INFO**: Normal operational messages
- **WARNING**: Unexpected but handled situations
- **ERROR**: Serious problems that prevent operations

### 3. Catch and Log Exceptions Properly

```python
try:
    result = perform_operation()
except SpecificException as e:
    log_warning("Expected issue occurred", context={"details": str(e)})
except Exception as e:
    log_error("Unexpected failure", exception=e, context={"operation": "perform_operation"})
    raise  # Re-raise if needed
```

### 4. Monitor Error Rates

Use the dashboard or API to monitor error rates:

```bash
# Check error summary via API
curl http://localhost:8000/api/v1/logs/summary

# Export errors for analysis
curl -o errors.json http://localhost:8000/api/v1/logs/errors/export
```

## Troubleshooting

### Issue: Logs Not Being Written

**Solution**: Ensure the logs directory exists and is writable:
```bash
mkdir -p /workspace/web_all/logs
chmod 755 /workspace/web_all/logs
```

### Issue: Too Many Errors in History

**Solution**: Clear old logs:
```python
from web_all.utils.logger import log_capture
log_capture.clear_logs()
```

Or via API:
```bash
curl -X POST http://localhost:8000/api/v1/logs/clear
```

### Issue: Performance Impact

The logging system is designed for minimal overhead:
- Uses asynchronous I/O where possible
- Log rotation prevents disk space issues
- Error history limited to 1000 entries by default

If needed, reduce the history limit:
```python
log_capture.max_error_history = 500
```

## Integration with Existing Code

The logging system integrates seamlessly with existing Python logging:

```python
import logging
from web_all.utils.logger import setup_default_logging

# Initialize default logging (already done automatically)
setup_default_logging()

# Use standard logging alongside the custom logger
logger = logging.getLogger(__name__)
logger.info("Standard log message")

# Or use the enhanced logger
from web_all.utils.logger import log_info
log_info("Enhanced log message", context={"extra": "data"})
```

## Future Enhancements

Planned improvements:
- [ ] Database storage option for long-term retention
- [ ] Real-time alerting via email/Slack
- [ ] Advanced analytics and reporting
- [ ] Log aggregation across multiple instances
- [ ] Custom log level configurations per module

## Support

For issues or questions:
1. Check the log files in `/workspace/web_all/logs/`
2. Review the error dashboards
3. Export errors using the API for detailed analysis

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Author**: Web-All Team
