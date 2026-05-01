import sys
import json


def parse_summary(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    metrics = data.get('metrics', {})
    failed = metrics.get('http_req_failed', {})
    duration = metrics.get('http_req_duration', {})

    failure_rate = 0.0
    if failed:
        if 'value' in failed:
            failure_rate = float(failed.get('value', 0.0)) * 100
        else:
            failure_rate = float(failed.get('values', {}).get('rate', 0.0)) * 100

    avg_latency = None
    if duration:
        if 'avg' in duration:
            avg_latency = duration.get('avg')
        else:
            avg_latency = duration.get('values', {}).get('avg')

    return failure_rate, avg_latency


def main():
    if len(sys.argv) < 2:
        print('usage: parse_k6_summary.py <summary.json> [failure-threshold-percent]')
        sys.exit(2)

    path = sys.argv[1]
    threshold = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0

    failure_rate, avg_latency = parse_summary(path)
    print(f'failure_rate_percent={failure_rate:.3f}')
    if avg_latency is not None:
        print(f'avg_latency_ms={avg_latency:.3f}')

    if failure_rate > threshold:
        print(f'FAILURE: failure_rate {failure_rate:.3f}% > threshold {threshold}%')
        sys.exit(3)


if __name__ == '__main__':
    main()
