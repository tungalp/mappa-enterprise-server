"""
Logging Configuration for Performance Monitoring

This module provides logging configuration specifically for performance monitoring.
It sets up separate loggers for performance metrics and provides utilities for
analyzing the performance data.

Usage:
    from service.logging_config import setup_performance_logging
    setup_performance_logging()
"""

import logging
import logging.handlers
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

def setup_performance_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    enable_console: bool = True
):
    """
    Set up performance logging configuration
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Path to log file (if None, uses default)
        max_file_size: Maximum size of log file before rotation
        backup_count: Number of backup files to keep
        enable_console: Whether to also log to console
    """
    
    # Create performance logger
    perf_logger = logging.getLogger("performance")
    perf_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear any existing handlers
    perf_logger.handlers.clear()
    
    # Set up file handler with rotation
    if log_file is None:
        log_dir = os.path.join(os.getcwd(), "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "performance.log")
    
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_file_size,
        backupCount=backup_count
    )
    
    # Create formatter for structured logging
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    perf_logger.addHandler(file_handler)
    
    # Add console handler if requested
    if enable_console:
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            '%(asctime)s - PERF - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        perf_logger.addHandler(console_handler)
    
    # Prevent propagation to root logger
    perf_logger.propagate = False
    
    return perf_logger

class PerformanceLogParser:
    """Parser for performance log files"""
    
    def __init__(self, log_file: str):
        self.log_file = log_file
    
    def parse_log_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse a single log line and extract performance data"""
        try:
            # Look for performance breakdown lines
            if "PERFORMANCE BREAKDOWN" not in line:
                return None
            
            # Extract timestamp
            timestamp_str = line.split(" - ")[0]
            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S,%f")
            
            # Extract the performance data part
            perf_part = line.split("PERFORMANCE BREAKDOWN for ")[1]
            
            # Split into request info and timing data
            parts = perf_part.split(" | ")
            request_info = parts[0]
            
            # Parse timing data
            timing_data = {}
            for part in parts[1:]:
                if ":" in part and "ms" in part:
                    if part.startswith("TOTAL:"):
                        total_str = part.replace("TOTAL:", "").strip().replace("ms", "")
                        timing_data["total_time"] = float(total_str)
                    else:
                        # Parse individual timing: "operation: 123.45ms (12.3%)"
                        key_value = part.split(":")
                        if len(key_value) == 2:
                            key = key_value[0].strip()
                            value_part = key_value[1].strip()
                            # Extract just the milliseconds value
                            ms_value = value_part.split("ms")[0].strip()
                            try:
                                timing_data[key] = float(ms_value)
                            except ValueError:
                                continue
            
            return {
                "timestamp": timestamp,
                "request_info": request_info,
                "timing_data": timing_data
            }
            
        except Exception as e:
            print(f"Error parsing log line: {e}")
            return None
    
    def parse_log_file(self, limit: Optional[int] = None) -> list:
        """Parse the entire log file and return performance data"""
        performance_data = []
        
        try:
            with open(self.log_file, 'r') as f:
                lines = f.readlines()
                
                # Process lines in reverse order to get most recent first
                for line in reversed(lines):
                    if limit and len(performance_data) >= limit:
                        break
                    
                    parsed = self.parse_log_line(line.strip())
                    if parsed:
                        performance_data.append(parsed)
                        
        except FileNotFoundError:
            print(f"Log file not found: {self.log_file}")
        except Exception as e:
            print(f"Error reading log file: {e}")
        
        return list(reversed(performance_data))  # Return in chronological order
    
    def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance summary for the last N hours"""
        data = self.parse_log_file()
        
        # Filter data by time
        cutoff_time = datetime.now().replace(hour=datetime.now().hour - hours)
        recent_data = [
            d for d in data 
            if d["timestamp"] > cutoff_time
        ]
        
        if not recent_data:
            return {"error": "No data found for the specified time period"}
        
        # Calculate statistics
        total_requests = len(recent_data)
        total_times = [d["timing_data"].get("total_time", 0) for d in recent_data]
        
        avg_total = sum(total_times) / total_requests
        max_total = max(total_times)
        min_total = min(total_times)
        
        # Find slowest endpoints
        slowest_requests = sorted(recent_data, key=lambda x: x["timing_data"].get("total_time", 0), reverse=True)[:5]
        
        return {
            "period_hours": hours,
            "total_requests": total_requests,
            "avg_response_time_ms": avg_total,
            "max_response_time_ms": max_total,
            "min_response_time_ms": min_total,
            "slowest_requests": [
                {
                    "request": req["request_info"],
                    "time_ms": req["timing_data"].get("total_time", 0),
                    "timestamp": req["timestamp"].isoformat()
                }
                for req in slowest_requests
            ]
        }

def analyze_performance_trends(log_file: str, hours: int = 24):
    """Analyze performance trends from log file"""
    parser = PerformanceLogParser(log_file)
    summary = parser.get_performance_summary(hours)
    
    print(f"\nPerformance Summary (Last {hours} hours)")
    print("=" * 50)
    
    if "error" in summary:
        print(f"Error: {summary['error']}")
        return
    
    print(f"Total Requests: {summary['total_requests']}")
    print(f"Average Response Time: {summary['avg_response_time_ms']:.2f}ms")
    print(f"Max Response Time: {summary['max_response_time_ms']:.2f}ms")
    print(f"Min Response Time: {summary['min_response_time_ms']:.2f}ms")
    
    print("\nSlowest Requests:")
    for i, req in enumerate(summary['slowest_requests'], 1):
        print(f"  {i}. {req['request']} - {req['time_ms']:.2f}ms")
    
    # Performance recommendations
    avg_time = summary['avg_response_time_ms']
    max_time = summary['max_response_time_ms']
    
    print("\nRecommendations:")
    if avg_time > 1000:
        print("  - Average response time >1s. Consider performance optimization.")
    if max_time > 5000:
        print("  - Some requests >5s. Investigate slowest endpoints.")
    if max_time / avg_time > 10:
        print("  - High variance in response times. Check for outliers.")

# Example usage
if __name__ == "__main__":
    # Set up performance logging
    logger = setup_performance_logging(
        log_level="INFO",
        enable_console=True
    )
    
    # Example of logging performance data
    logger.info(
        "PERFORMANCE BREAKDOWN for GET tenant1/api1/route1 | "
        "TOTAL: 245.67ms | "
        "tenant_lookup: 12.34ms (5.0%) | "
        "api_lookup: 23.45ms (9.5%) | "
        "handler_execution: 156.78ms (63.8%) | "
        "response_modification: 34.56ms (14.1%)"
    )
    
    print("Performance logging configured successfully!")
    print(f"Logs will be written to: logs/performance.log")
    
    # Analyze existing logs if available
    log_file = os.path.join("logs", "performance.log")
    if os.path.exists(log_file):
        analyze_performance_trends(log_file, hours=1)
