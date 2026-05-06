# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 4.0.x   | :white_check_mark: |
| 3.0.x   | :white_check_mark: |
| < 3.0   | :x:                |

## Reporting a Vulnerability

We take the security of web-all seriously. If you believe you've found a security vulnerability, please follow these steps:

### How to Report

1. **DO NOT** create a public GitHub issue
2. Email us at: security@web-all.dev
3. Include the following information:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)
   - Your contact information

### What to Expect

- We will acknowledge your report within 48 hours
- We aim to resolve critical issues within 7 days
- You will receive updates on our progress
- We will credit you in our security advisory (unless you prefer to remain anonymous)

## Security Best Practices for Users

### When Using web-all

1. **Respect robots.txt**: Enable `--respect-robots` flag
2. **Rate Limiting**: Use appropriate delays between requests
3. **Legal Compliance**: Only clone sites you have permission to
4. **Credential Safety**: Never commit API keys or credentials
5. **Tor Usage**: Use Tor responsibly and legally

### Configuration Security

- Store API keys in environment variables, not in code
- Use `.env` files and add them to `.gitignore`
- Rotate credentials regularly
- Use separate credentials for development and production

### Network Security

- Run behind a firewall in production
- Use HTTPS for API endpoints
- Implement authentication for sensitive operations
- Monitor logs for suspicious activity

## Known Limitations

- web-all is a scraping tool and inherits risks from target websites
- JavaScript execution in headless browsers has inherent risks
- Always validate and sanitize scraped content before use

## Security Updates

Security patches are released as soon as possible. Update regularly:

```bash
pip install --upgrade web-all
```

## Bug Bounty Program

Currently, we do not have a formal bug bounty program. However, we recognize and appreciate responsible disclosure.

## Contact

For security-related questions: security@web-all.dev
