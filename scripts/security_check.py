import os
import sys
import json
import subprocess
from pathlib import Path
from typing import List, Dict

def check_env_file() -> Dict[str, bool]:
    env_checks = {
        'exists': False,
        'secret_key_set': False,
        'not_in_git': False
    }
    
    # Check .env file existence
    env_file = Path('.env')
    env_checks['exists'] = env_file.exists()
    
    if env_checks['exists']:
        # Check if SECRET_KEY is set
        with open(env_file, 'r') as f:
            content = f.read()
            env_checks['secret_key_set'] = 'SECRET_KEY=' in content and \
                                          not content.strip().endswith('SECRET_KEY=')
        
        # Check if .env is in .gitignore
        gitignore = Path('.gitignore')
        if gitignore.exists():
            with open(gitignore, 'r') as f:
                content = f.read()
                env_checks['not_in_git'] = '.env' in content
    
    return env_checks

def check_dependencies() -> Dict[str, List[str]]:
    security_issues = {
        'outdated': [],
        'vulnerabilities': []
    }
    
    try:
        # Check for outdated packages
        result = subprocess.run(['pip', 'list', '--outdated', '--format=json'],
                              capture_output=True, text=True)
        if result.returncode == 0:
            outdated = json.loads(result.stdout)
            security_issues['outdated'] = [
                f"{pkg['name']} (Current: {pkg['version']}, Latest: {pkg['latest_version']})"
                for pkg in outdated
            ]
        
        # Check for known vulnerabilities using safety
        try:
            result = subprocess.run(['safety', 'check', '--json'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                vulns = json.loads(result.stdout)
                security_issues['vulnerabilities'] = [
                    f"{vuln['package']}: {vuln['advisory']}"
                    for vuln in vulns
                ]
        except subprocess.CalledProcessError:
            security_issues['vulnerabilities'].append(
                "Install 'safety' package to check for known vulnerabilities")
    except Exception as e:
        print(f"Error checking dependencies: {e}")
    
    return security_issues

def check_security_headers() -> Dict[str, bool]:
    headers = {
        'Strict-Transport-Security': False,
        'X-Content-Type-Options': False,
        'X-Frame-Options': False,
        'X-XSS-Protection': False,
        'Content-Security-Policy': False,
        'Referrer-Policy': False
    }
    
    security_file = Path('app/core/security.py')
    if security_file.exists():
        with open(security_file, 'r') as f:
            content = f.read()
            for header in headers:
                headers[header] = header in content
    
    return headers

def check_rate_limiting() -> bool:
    rate_limit_files = [
        Path('app/core/middleware.py'),
        Path('app/main.py')
    ]
    
    for file in rate_limit_files:
        if file.exists():
            with open(file, 'r') as f:
                content = f.read()
                if 'RateLimitMiddleware' in content or 'RATE_LIMIT' in content:
                    return True
    
    return False

def check_logging_setup() -> bool:
    logging_file = Path('app/core/logging.py')
    if logging_file.exists():
        with open(logging_file, 'r') as f:
            content = f.read()
            return 'RequestLoggingMiddleware' in content
    
    return False

def main():
    print("Running Security Configuration Check...\n")
    
    # Check environment configuration
    env_checks = check_env_file()
    print("=== Environment Configuration ===")
    print(f"✓ .env file exists: {env_checks['exists']}")
    print(f"✓ SECRET_KEY is set: {env_checks['secret_key_set']}")
    print(f"✓ .env in .gitignore: {env_checks['not_in_git']}")
    
    # Check dependencies
    print("\n=== Dependencies ===")
    dep_checks = check_dependencies()
    if dep_checks['outdated']:
        print("\nOutdated packages:")
        for pkg in dep_checks['outdated']:
            print(f"  ! {pkg}")
    else:
        print("✓ All packages are up to date")
    
    if dep_checks['vulnerabilities']:
        print("\nVulnerabilities found:")
        for vuln in dep_checks['vulnerabilities']:
            print(f"  ! {vuln}")
    else:
        print("✓ No known vulnerabilities found")
    
    # Check security headers
    print("\n=== Security Headers ===")
    headers = check_security_headers()
    for header, implemented in headers.items():
        print(f"{'✓' if implemented else '✗'} {header}")
    
    # Check rate limiting
    print("\n=== Rate Limiting ===")
    rate_limit_implemented = check_rate_limiting()
    print(f"{'✓' if rate_limit_implemented else '✗'} Rate limiting implemented")
    
    # Check logging
    print("\n=== Request Logging ===")
    logging_implemented = check_logging_setup()
    print(f"{'✓' if logging_implemented else '✗'} Request logging implemented")
    
    print("\n=== Security Recommendations ===")
    if not all(env_checks.values()):
        print("! Set up proper environment configuration")
    if dep_checks['outdated'] or dep_checks['vulnerabilities']:
        print("! Update dependencies and fix vulnerabilities")
    if not all(headers.values()):
        print("! Implement missing security headers")
    if not rate_limit_implemented:
        print("! Implement rate limiting")
    if not logging_implemented:
        print("! Set up request logging")

if __name__ == '__main__':
    main()