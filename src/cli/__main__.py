"""
CLI entry point for Vernachain
"""

import argparse
import sys
from .commands import start_bootstrap, start_node

def main():
    parser = argparse.ArgumentParser(description="Vernachain CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Bootstrap node command
    bootstrap_parser = subparsers.add_parser("start-bootstrap", help="Start a bootstrap node")
    bootstrap_parser.add_argument("--host", default="localhost", help="Host to bind to")
    bootstrap_parser.add_argument("--port", type=int, default=5000, help="Port to bind to")
    bootstrap_parser.add_argument("--log-level", default="info", help="Logging level")

    # Regular node command
    node_parser = subparsers.add_parser("start", help="Start a regular node")
    node_parser.add_argument("--host", default="localhost", help="Host to bind to")
    node_parser.add_argument("--port", type=int, default=5001, help="Port to bind to")
    node_parser.add_argument("--bootstrap-host", help="Bootstrap node host")
    node_parser.add_argument("--bootstrap-port", type=int, help="Bootstrap node port")
    node_parser.add_argument("--log-level", default="info", help="Logging level")

    args = parser.parse_args()

    if args.command == "start-bootstrap":
        start_bootstrap(
            host=args.host,
            port=args.port,
            log_level=args.log_level
        )
    elif args.command == "start":
        start_node(
            host=args.host,
            port=args.port,
            bootstrap_host=args.bootstrap_host,
            bootstrap_port=args.bootstrap_port,
            log_level=args.log_level
        )
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main() 
