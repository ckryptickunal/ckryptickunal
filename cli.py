import argparse
import os
from usage_monitor.monitor import run_monitor
from usage_monitor.heatmap import generate_heatmap


def main() -> None:
    parser = argparse.ArgumentParser(description="App usage monitor and heatmap generator")
    subparsers = parser.add_subparsers(dest="command", required=True)

    monitor_parser = subparsers.add_parser("monitor", help="Start monitoring active app usage")
    monitor_parser.add_argument("--db", default=os.path.join(os.getcwd(), "usage.db"), help="Path to SQLite database (default: ./usage.db)")
    monitor_parser.add_argument("--poll", type=float, default=1.0, help="Polling interval in seconds (default: 1.0)")

    heatmap_parser = subparsers.add_parser("heatmap", help="Generate a usage heatmap image from the database")
    heatmap_parser.add_argument("--db", default=os.path.join(os.getcwd(), "usage.db"), help="Path to SQLite database (default: ./usage.db)")
    heatmap_parser.add_argument("--out", default=os.path.join(os.getcwd(), "heatmap.png"), help="Path to output heatmap image (default: ./heatmap.png)")
    heatmap_parser.add_argument("--since", default=None, help="Optional start date (YYYY-MM-DD) or relative (e.g., 7d)")
    heatmap_parser.add_argument("--until", default=None, help="Optional end date (YYYY-MM-DD). Defaults to today")

    args = parser.parse_args()

    if args.command == "monitor":
        run_monitor(db_path=args.db, poll_interval=args.poll)
    elif args.command == "heatmap":
        generate_heatmap(db_path=args.db, output_path=args.out, since=args.since, until=args.until)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()