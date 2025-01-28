#!/usr/bin/env python3

import argparse
import asyncio
import os
import signal
import subprocess
import sys
from typing import List, Optional
import time

class VernachainStarter:
    def __init__(self):
        self.processes: List[subprocess.Popen] = []
        self.running = True

    def signal_handler(self, signum, frame):
        print("\nShutting down Vernachain components...")
        self.running = False
        for process in self.processes:
            if process.poll() is None:  # If process is still running
                process.terminate()
        sys.exit(0)

    def start_process(self, command: List[str], name: str) -> Optional[subprocess.Popen]:
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            self.processes.append(process)
            print(f"Started {name} (PID: {process.pid})")
            return process
        except Exception as e:
            print(f"Failed to start {name}: {e}")
            return None

    def start_components(self, args):
        # Start Bootstrap Node
        if args.bootstrap:
            bootstrap_cmd = [
                sys.executable, "-m", "src.cli", "start-bootstrap",
                "--host", args.bootstrap_host,
                "--port", str(args.bootstrap_port)
            ]
            self.start_process(bootstrap_cmd, "Bootstrap Node")
            time.sleep(2)  # Wait for bootstrap node to initialize

        # Start Regular Node
        node_cmd = [
            sys.executable, "-m", "src.cli", "start",
            "--host", args.node_host,
            "--port", str(args.node_port)
        ]
        if args.bootstrap:
            node_cmd.extend([
                "--bootstrap-host", args.bootstrap_host,
                "--bootstrap-port", str(args.bootstrap_port)
            ])
        self.start_process(node_cmd, "Regular Node")

        # Start API Service
        api_cmd = [
            "uvicorn", "src.api.service:app",
            "--host", args.api_host,
            "--port", str(args.api_port),
            "--reload" if args.dev else ""
        ]
        self.start_process(api_cmd, "API Service")

        # Start Explorer Backend
        explorer_cmd = [
            "uvicorn", "src.explorer.backend:app",
            "--host", args.explorer_host,
            "--port", str(args.explorer_port),
            "--reload" if args.dev else ""
        ]
        self.start_process(explorer_cmd, "Explorer Backend")

        if args.dev:
            # Start Frontend Development Server
            frontend_cmd = ["npm", "run", "dev"]
            cwd = os.path.join(os.getcwd(), "src", "frontend")
            if os.path.exists(cwd):
                process = subprocess.Popen(
                    frontend_cmd,
                    cwd=cwd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                self.processes.append(process)
                print(f"Started Frontend Dev Server (PID: {process.pid})")

        # Monitor processes
        while self.running:
            for process in self.processes:
                if process.poll() is not None:
                    print(f"Process (PID: {process.pid}) exited with code {process.returncode}")
                    return
            time.sleep(1)

def main():
    parser = argparse.ArgumentParser(description="Start Vernachain components")
    parser.add_argument("--bootstrap", action="store_true", help="Start a bootstrap node")
    parser.add_argument("--bootstrap-host", default="localhost", help="Bootstrap node host")
    parser.add_argument("--bootstrap-port", type=int, default=5000, help="Bootstrap node port")
    parser.add_argument("--node-host", default="localhost", help="Regular node host")
    parser.add_argument("--node-port", type=int, default=5001, help="Regular node port")
    parser.add_argument("--api-host", default="localhost", help="API service host")
    parser.add_argument("--api-port", type=int, default=8000, help="API service port")
    parser.add_argument("--explorer-host", default="localhost", help="Explorer backend host")
    parser.add_argument("--explorer-port", type=int, default=8001, help="Explorer backend port")
    parser.add_argument("--dev", action="store_true", help="Start in development mode")

    args = parser.parse_args()

    starter = VernachainStarter()
    signal.signal(signal.SIGINT, starter.signal_handler)
    signal.signal(signal.SIGTERM, starter.signal_handler)

    print("Starting Vernachain components...")
    starter.start_components(args)

if __name__ == "__main__":
    main() 