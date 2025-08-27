# Security Scripts

This directory contains utility scripts for managing and monitoring security in the B2B Marketplace application.

## Available Scripts

### 1. Generate Secret Key (`generate_secret.py`)

Generates a cryptographically secure secret key for use in the application.

```bash
python generate_secret.py
```

### 2. Setup Security Configuration (`setup_security.py`)

Helps set up secure configuration by creating a `.env` file with proper security settings.

```bash
python setup_security.py
```

### 3. Analyze Security Logs (`analyze_security_logs.py`)

Analyzes application logs for security patterns, suspicious activities, and potential threats.

```bash
python analyze_security_logs.py
```

Features:
- IP activity analysis
- Detection of suspicious patterns
- Request pattern analysis
- Time-based analysis
- Security recommendations

### 4. Security Check (`security_check.py`)

Performs a comprehensive security check of the application configuration and dependencies.

```bash
python security_check.py
```

Checks:
- Environment configuration
- Dependency vulnerabilities
- Security headers
- Rate limiting implementation
- Logging setup

## Best Practices

1. **Secret Management**
   - Never commit secrets or sensitive configuration to version control
   - Use different secrets for development and production
   - Regularly rotate secrets

2. **Configuration**
   - Keep `.env` file secure and never commit it
   - Ensure proper file permissions
   - Back up configurations securely

3. **Monitoring**
   - Regularly analyze security logs
   - Monitor for suspicious activities
   - Keep dependencies updated

4. **Security Headers**
   - Implement all recommended security headers
   - Configure Content Security Policy
   - Enable HTTPS-only features

## Prerequisites

- Python 3.8 or higher
- Required packages:
  ```bash
  pip install python-dotenv cryptography safety
  ```

## Contributing

When contributing to security features:
1. Follow secure coding practices
2. Add appropriate logging
3. Include security tests
4. Document security considerations

## Security Reporting

If you discover any security issues, please report them immediately to the security team and do not disclose them publicly.