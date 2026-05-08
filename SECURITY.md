# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 3.0.x   | :white_check_mark: |
| < 3.0   | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue, please report it responsibly.

### How to Report

1. **DO NOT** create a public GitHub issue for security vulnerabilities
2. Send an email to: security@web-all.dev (or use GitHub's private vulnerability reporting feature)
3. Include as much information as possible:
   - Type of vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### What to Expect

- **Initial Response**: Within 48 hours acknowledging your report
- **Status Update**: Within 5 business days with next steps
- **Resolution**: We aim to resolve critical issues within 30 days

### Disclosure Policy

- We will notify you when the vulnerability is fixed
- We request that you keep the vulnerability confidential until we've released a patch
- We will credit you in our security advisory (unless you prefer to remain anonymous)

## Security Best Practices for Users

### When Using web-all

1. **Respect robots.txt**: Enable `--respect-robots` flag when appropriate
2. **Rate Limiting**: Use `--delay` to avoid overwhelming servers
3. **Legal Compliance**: Only clone websites you have permission to access
4. **Tor Usage**: Ensure Tor is properly configured if accessing .onion sites
5. **API Keys**: Never commit API keys to version control

### Configuration Security

- Store API keys in environment variables or `.env` files (never in code)
- Use strong SECRET_KEY in production
- Restrict ALLOWED_HOSTS in production environments
- Enable HTTPS for production deployments

## Known Limitations

- web-all is a tool that can be used for both legitimate and potentially harmful purposes
- Users are responsible for complying with website terms of service and applicable laws
- The tool does not bypass authentication or access restricted content

## Security Updates

Security updates will be released as patch versions (e.g., 3.0.1) and announced via:
- GitHub Releases
- Security Advisories on GitHub
- PyPI package updates

Stay updated by watching the repository or subscribing to security notifications.

---

**Remember**: Use web-all responsibly and ethically. Always respect website owners' rights and terms of service.
