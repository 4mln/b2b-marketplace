import json\import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

def parse_log_line(line: str) -> dict:
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        return None

def analyze_ip_activity(logs: List[dict]) -> Tuple[Counter, Dict[str, List[dict]]]:
    ip_counts = Counter()
    suspicious_ips = defaultdict(list)
    
    for log in logs:
        ip = log.get('client_ip')
        if not ip:
            continue
            
        ip_counts[ip] += 1
        
        # Check for suspicious patterns
        path = log.get('path', '')
        status_code = log.get('status_code', 0)
        
        # Detect potential security issues
        if any([
            status_code >= 400,  # Error responses
            re.search(r'[;|&]', path),  # Command injection attempts
            re.search(r'(?i)(union|select|insert|delete|update).*from', path),  # SQL injection attempts
            re.search(r'(?i)<script.*?>.*?</script>', path),  # XSS attempts
            '../' in path or '..\\' in path,  # Path traversal attempts
        ]):
            suspicious_ips[ip].append(log)
    
    return ip_counts, suspicious_ips

def analyze_request_patterns(logs: List[dict]) -> Dict[str, Counter]:
    patterns = {
        'methods': Counter(),
        'paths': Counter(),
        'status_codes': Counter(),
        'user_agents': Counter()
    }
    
    for log in logs:
        patterns['methods'][log.get('method', 'UNKNOWN')] += 1
        patterns['paths'][log.get('path', 'UNKNOWN')] += 1
        patterns['status_codes'][str(log.get('status_code', 'UNKNOWN'))] += 1
        patterns['user_agents'][log.get('user_agent', 'UNKNOWN')] += 1
    
    return patterns

def analyze_time_patterns(logs: List[dict]) -> Dict[str, int]:
    hourly_requests = defaultdict(int)
    
    for log in logs:
        timestamp = log.get('timestamp')
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                hour = dt.strftime('%Y-%m-%d %H:00')
                hourly_requests[hour] += 1
            except ValueError:
                continue
    
    return dict(hourly_requests)

def generate_security_report(log_file: Path):
    print(f"Analyzing security logs from: {log_file}\n")
    
    # Read and parse logs
    logs = []
    with open(log_file, 'r') as f:
        for line in f:
            log_entry = parse_log_line(line.strip())
            if log_entry:
                logs.append(log_entry)
    
    if not logs:
        print("No valid log entries found!")
        return
    
    # Analyze logs
    ip_counts, suspicious_ips = analyze_ip_activity(logs)
    patterns = analyze_request_patterns(logs)
    time_patterns = analyze_time_patterns(logs)
    
    # Generate report
    print("=== Security Analysis Report ===")
    print(f"\nTotal Log Entries: {len(logs)}")
    
    print("\n=== Suspicious Activity ===")
    print(f"Number of IPs with suspicious activity: {len(suspicious_ips)}")
    for ip, events in suspicious_ips.items():
        print(f"\nIP: {ip}")
        print(f"Suspicious events: {len(events)}")
        for event in events[:5]:  # Show first 5 events only
            print(f"  - {event.get('method')} {event.get('path')} (Status: {event.get('status_code')})")
    
    print("\n=== Top 10 Most Active IPs ===")
    for ip, count in ip_counts.most_common(10):
        print(f"{ip}: {count} requests")
    
    print("\n=== Request Patterns ===")
    print("\nTop HTTP Methods:")
    for method, count in patterns['methods'].most_common():
        print(f"{method}: {count}")
    
    print("\nTop Status Codes:")
    for status, count in patterns['status_codes'].most_common():
        print(f"{status}: {count}")
    
    print("\n=== Security Recommendations ===")
    print("1. Review and potentially block suspicious IPs")
    print("2. Monitor unusual request patterns")
    print("3. Investigate high-frequency error responses")
    print("4. Check for potential brute force attempts")
    print("5. Review unusual User-Agent strings")

def main():
    log_dir = Path('logs')
    if not log_dir.exists():
        print("Error: logs directory not found!")
        return
    
    # Find the most recent log file
    log_files = list(log_dir.glob('*.log'))
    if not log_files:
        print("No log files found!")
        return
    
    latest_log = max(log_files, key=lambda p: p.stat().st_mtime)
    generate_security_report(latest_log)

if __name__ == '__main__':
    main()