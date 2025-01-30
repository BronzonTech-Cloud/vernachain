#!/usr/bin/env python3

import argparse
import os
import signal
import subprocess
import sys
from typing import List, Optional
import time
import threading
import json
import shutil

class VernachainStarter:
    def __init__(self):
        self.processes: List[subprocess.Popen] = []
        self.running = True
        
        # Add the current directory to Python path
        self.env = os.environ.copy()
        self.env["PYTHONPATH"] = os.getcwd()

    def signal_handler(self, signum, frame):
        print("\nShutting down Vernachain components...")
        self.running = False
        self.cleanup()
        sys.exit(0)

    def monitor_output(self, process, name):
        while True:
            output = process.stdout.readline()
            if output:
                print(f"[{name}] {output.strip()}")
            error = process.stderr.readline()
            if error:
                print(f"[{name} ERROR] {error.strip()}", file=sys.stderr)
            if output == '' and error == '' and process.poll() is not None:
                break

    def setup_frontend_env(self, args):
        """Setup frontend environment variables and dependencies"""
        frontend_dir = os.path.join(os.getcwd(), "src", "frontend")
        env_file = os.path.join(frontend_dir, ".env")
        
        # Create or update .env file
        env_vars = {
            "VITE_API_URL": f"http://{args.api_host}:{args.api_port}",
            "VITE_EXPLORER_URL": f"http://{args.explorer_host}:{args.explorer_port}",
            "VITE_NODE_URL": f"http://{args.node_host}:{args.node_port}",
            "VITE_API_KEY": os.getenv("VERNACHAIN_API_KEY", "development_key"),
        }
        
        print("Setting up frontend environment...")
        with open(env_file, "w") as f:
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")
        
        # Check and install frontend dependencies
        if os.path.exists(os.path.join(frontend_dir, "package.json")):
            print("Checking frontend dependencies...")
            try:
                # Check if node_modules exists
                if not os.path.exists(os.path.join(frontend_dir, "node_modules")):
                    print("Installing frontend dependencies...")
                    subprocess.run(
                        ["npm", "install"],
                        cwd=frontend_dir,
                        check=True,
                        capture_output=True,
                        text=True
                    )
                return True
            except subprocess.CalledProcessError as e:
                print(f"Error installing frontend dependencies: {e.stderr}")
                return False
            except Exception as e:
                print(f"Error setting up frontend: {e}")
                return False
        return False

    def start_process(self, command: List[str], name: str, cwd: Optional[str] = None, required=True) -> Optional[subprocess.Popen]:
        try:
            print(f"Starting {name} with command: {' '.join(command)}")
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                env=self.env,
                cwd=cwd
            )
            self.processes.append(process)
            
            # Start output monitoring thread
            monitor_thread = threading.Thread(
                target=self.monitor_output,
                args=(process, name),
                daemon=True
            )
            monitor_thread.start()
            
            print(f"Started {name} (PID: {process.pid})")
            return process
        except Exception as e:
            if required:
                print(f"Failed to start {name}: {e}")
                self.cleanup()
                sys.exit(1)
            else:
                print(f"Optional component {name} not started: {e}")
            return None

    def cleanup(self):
        for process in self.processes:
            if process.poll() is None:
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    print(f"Force killing process {process.pid}")
                    process.kill()

    def start_components(self, args):
        try:
            python_exe = sys.executable
            
            # Create logs directory if it doesn't exist
            os.makedirs("logs", exist_ok=True)
            
            # Start bootstrap node if requested
            if args.bootstrap:
                bootstrap_cmd = [
                    python_exe, "cli.py", "bootstrap",
                    "--host", args.bootstrap_host,
                    "--port", str(args.bootstrap_port)
                ]
                if args.dev:
                    bootstrap_cmd.append("--debug")
                bootstrap_process = self.start_process(bootstrap_cmd, "Bootstrap Node")
                if not bootstrap_process or bootstrap_process.poll() is not None:
                    print("Bootstrap node failed to start. Check the error messages above.")
                    self.cleanup()
                    sys.exit(1)
                time.sleep(2)  # Wait for bootstrap node to initialize

            # Start regular node
            node_cmd = [
                python_exe, "cli.py", "start",
                "--host", args.node_host,
                "--port", str(args.node_port)
            ]
            if args.bootstrap:
                node_cmd.extend([
                    "--bootstrap-host", args.bootstrap_host,
                    "--bootstrap-port", str(args.bootstrap_port)
                ])
            if args.dev:
                node_cmd.append("--debug")
            node_process = self.start_process(node_cmd, "Regular Node")
            if not node_process or node_process.poll() is not None:
                print("Regular node failed to start. Check the error messages above.")
                self.cleanup()
                sys.exit(1)

            # Check if uvicorn is available
            try:
                import uvicorn
                
                # Start API Service
                api_cmd = [
                    sys.executable, "-m", "uvicorn", "src.api.service:app",
                    "--host", args.api_host,
                    "--port", str(args.api_port),
                    "--log-level", "debug" if args.dev else "info"
                ]
                if args.dev:
                    api_cmd.append("--reload")
                api_process = self.start_process(api_cmd, "API Service", required=False)
                if not api_process or api_process.poll() is not None:
                    print("API service failed to start. Check the error messages above.")
                    self.cleanup()
                    sys.exit(1)

                # Start Explorer Backend
                explorer_cmd = [
                    sys.executable, "-m", "uvicorn", "src.explorer.backend:app",
                    "--host", args.explorer_host,
                    "--port", str(args.explorer_port),
                    "--log-level", "debug" if args.dev else "info"
                ]
                if args.dev:
                    explorer_cmd.append("--reload")
                explorer_process = self.start_process(explorer_cmd, "Explorer Backend", required=False)
                if not explorer_process or explorer_process.poll() is not None:
                    print("Explorer backend failed to start. Check the error messages above.")
                    self.cleanup()
                    sys.exit(1)
            except ImportError:
                print("Warning: uvicorn not found. API and Explorer services will not be started.")
                print("To enable these services, install uvicorn: pip install uvicorn")

            if args.dev:
                # Start Frontend Development Server
                frontend_dir = os.path.join(os.getcwd(), "src", "frontend")
                if self.setup_frontend_env(args):
                    try:
                        # First build the frontend
                        subprocess.run(
                            ["npm", "run", "build"],
                            cwd=frontend_dir,
                            check=True,
                            capture_output=True,
                            text=True
                        )
                        
                        # Then start the dev server
                        frontend_cmd = ["npm", "run", "dev", "--", "--host", args.frontend_host, "--port", str(args.frontend_port)]
                        frontend_process = self.start_process(
                            frontend_cmd,
                            "Frontend Dev Server",
                            cwd=frontend_dir,
                            required=False
                        )
                        if frontend_process and frontend_process.poll() is None:
                            print(f"Frontend Dev Server started at http://{args.frontend_host}:{args.frontend_port}")
                        else:
                            print("Warning: Frontend server failed to start")
                    except Exception as e:
                        print(f"Warning: Frontend server not started: {e}")
                        print("To enable frontend, ensure Node.js and npm are installed")
                else:
                    print("Warning: Frontend setup failed")

            print("\nVernachain network is running!")
            print(f"Bootstrap Node: http://{args.bootstrap_host}:{args.bootstrap_port}")
            print(f"Regular Node: http://{args.node_host}:{args.node_port}")
            print(f"API Service: http://{args.api_host}:{args.api_port}")
            print(f"Explorer: http://{args.explorer_host}:{args.explorer_port}")
            if args.dev:
                print(f"Frontend: http://{args.frontend_host}:{args.frontend_port}")

            # Monitor processes
            while self.running:
                for process in self.processes:
                    if process.poll() is not None:
                        error_output = process.stderr.read()
                        if error_output:
                            print(f"Process error output:\n{error_output}", file=sys.stderr)
                        print(f"Process (PID: {process.pid}) exited with code {process.returncode}")
                        self.cleanup()
                        return
                time.sleep(1)

        except Exception as e:
            print(f"Error starting components: {e}")
            self.cleanup()
            sys.exit(1)

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
    parser.add_argument("--frontend-host", default="localhost", help="Frontend dev server host")
    parser.add_argument("--frontend-port", type=int, default=5173, help="Frontend dev server port")
    parser.add_argument("--dev", action="store_true", help="Start in development mode")

    args = parser.parse_args()

    starter = VernachainStarter()
    signal.signal(signal.SIGINT, starter.signal_handler)
    signal.signal(signal.SIGTERM, starter.signal_handler)

    print("Starting Vernachain components...")
    starter.start_components(args)

if __name__ == "__main__":
    main() 