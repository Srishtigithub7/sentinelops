from pathlib import Path
from collections import Counter
import re


# Matches our production log format:
# 2026-09-14 14:03:02 CRITICAL user-service: Database connection pool exhausted
LOG_PATTERN = re.compile(
    r"(?P<date>\S+)\s+"
    r"(?P<time>\S+)\s+"
    r"(?P<level>INFO|WARN|ERROR|CRITICAL)\s+"
    r"(?P<service>[\w-]+):\s+"
    r"(?P<message>.*)"
)


def parse_log_line(line: str) -> dict | None:
    """Convert one raw log line into structured data."""

    match = LOG_PATTERN.match(line.strip())

    if not match:
        return None

    return match.groupdict()


def load_logs(log_file: str) -> list[dict]:
    """Read the log file and parse every valid line."""

    path = Path(log_file)

    if not path.exists():
        raise FileNotFoundError(
            f"Log file not found: {path.resolve()}"
        )

    events = []

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            event = parse_log_line(line)

            if event:
                events.append(event)

    return events


def extract_pool_utilization(message: str) -> int | None:
    """Extract database connection pool utilization percentage."""

    patterns = [
        r"connection pool utilization=(\d+)%",
        r"pool utilization=(\d+)%",
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            message,
            re.IGNORECASE
        )

        if match:
            return int(match.group(1))

    return None


def extract_response_time(message: str) -> int | None:
    """Extract response_time value in milliseconds."""

    match = re.search(
        r"response_time=(\d+)ms",
        message,
        re.IGNORECASE
    )

    if match:
        return int(match.group(1))

    return None


def analyze_logs(events: list[dict]) -> dict:
    """Extract useful incident signals from parsed logs."""

    level_counts = Counter(
        event["level"]
        for event in events
    )

    service_counts = Counter(
        event["service"]
        for event in events
    )

    errors = [
        event for event in events
        if event["level"] in {"ERROR", "CRITICAL"}
    ]

    warnings = [
        event for event in events
        if event["level"] == "WARN"
    ]

    # ----------------------------------------
    # Database connection analysis
    # ----------------------------------------

    connection_timeouts = sum(
        "connection timeout" in event["message"].lower()
        for event in events
    )

    pool_exhausted_events = sum(
        "connection pool exhausted" in event["message"].lower()
        for event in events
    )

    # ----------------------------------------
    # Pool utilization analysis
    # ----------------------------------------

    pool_utilization = []

    for event in events:
        value = extract_pool_utilization(
            event["message"]
        )

        if value is not None:
            pool_utilization.append(value)

    # ----------------------------------------
    # Response time analysis
    # ----------------------------------------

    response_times = []

    for event in events:
        value = extract_response_time(
            event["message"]
        )

        if value is not None:
            response_times.append(value)

    # ----------------------------------------
    # Important events
    # ----------------------------------------

    critical_events = [
        {
            "date": event["date"],
            "time": event["time"],
            "service": event["service"],
            "message": event["message"],
        }
        for event in events
        if event["level"] == "CRITICAL"
    ]

    error_events = [
        {
            "date": event["date"],
            "time": event["time"],
            "service": event["service"],
            "message": event["message"],
        }
        for event in errors
    ]

    return {
        "total_events": len(events),

        "level_counts": dict(level_counts),

        "service_counts": dict(service_counts),

        "error_count": len(errors),

        "warning_count": len(warnings),

        "connection_timeouts": connection_timeouts,

        "pool_exhausted_events": pool_exhausted_events,

        "max_pool_utilization": (
            max(pool_utilization)
            if pool_utilization
            else None
        ),

        "max_response_time_ms": (
            max(response_times)
            if response_times
            else None
        ),

        "critical_events": critical_events,

        "error_events": error_events,
    }


def run_analysis(log_file: str) -> dict:
    """Run the complete log analysis pipeline."""

    events = load_logs(log_file)

    analysis = analyze_logs(events)

    return {
        "events": events,
        "analysis": analysis,
    }


def print_report(result: dict) -> None:
    """Display a readable incident analysis report."""

    analysis = result["analysis"]

    print()
    print("=" * 55)
    print("        SENTINELOPS LOG INTELLIGENCE REPORT")
    print("=" * 55)

    print()
    print("OVERVIEW")
    print("-" * 55)

    print(f"Total events           : {analysis['total_events']}")
    print(f"Errors                 : {analysis['error_count']}")
    print(f"Warnings               : {analysis['warning_count']}")
    print(
        f"Connection timeouts   : "
        f"{analysis['connection_timeouts']}"
    )
    print(
        f"Pool exhausted events : "
        f"{analysis['pool_exhausted_events']}"
    )

    pool = analysis["max_pool_utilization"]

    if pool is not None:
        print(
            f"Maximum pool usage    : {pool}%"
        )
    else:
        print(
            "Maximum pool usage    : Not detected"
        )

    response_time = analysis["max_response_time_ms"]

    if response_time is not None:
        print(
            f"Maximum response time : {response_time} ms"
        )
    else:
        print(
            "Maximum response time : Not detected"
        )

    print()
    print("AFFECTED SERVICES")
    print("-" * 55)

    for service, count in analysis["service_counts"].items():
        print(f"{service:<25} {count} events")

    print()
    print("CRITICAL EVENTS")
    print("-" * 55)

    for event in analysis["critical_events"]:
        print(
            f"{event['time']} | "
            f"{event['service']} | "
            f"{event['message']}"
        )

    print()
    print("ANALYSIS COMPLETE")
    print("=" * 55)
    print()


if __name__ == "__main__":

    # Project root:
    # sentinelops/
    #
    # Log file:
    # sentinelops/data/logs/production_api.log

    log_path = "data/logs/production_api.log"

    try:
        result = run_analysis(log_path)

        print_report(result)

    except FileNotFoundError as error:
        print()
        print("ERROR:", error)
        print()
        print(
            "Make sure production_api.log exists inside:"
        )
        print(
            "data/logs/"
        )