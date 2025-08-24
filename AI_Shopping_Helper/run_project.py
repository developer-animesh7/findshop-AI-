#!/usr/bin/env python3
"""
AI Shopping Helper - One-Click Project Launcher
================================================

This script provides a comprehensive solution to run the entire AI Shopping Helper project
with just one command. It handles:

- Virtual environment setup and activation
- Dependency installation and updates
- Database initialization
- FastAPI backend server startup
- Next.js frontend development server startup
- Browser launch with the application
- Graceful shutdown and cleanup

Usage:
    python run_project.py [--no-browser] [--dev]

Options:
    --no-browser: Skip automatic browser launch
    --dev: Run in development mode with hot reload
"""

import subprocess
import sys
import os
import time
import webbrowser
import signal
import threading
import platform
from pathlib import Path
import argparse
import json

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class AIShoppingHelperLauncher:
    def __init__(self, no_browser=False, dev_mode=False):
        self.project_root = Path(__file__).parent.absolute()
        self.venv_path = self.project_root / "venv"
        self.no_browser = no_browser
        self.dev_mode = dev_mode
        self.backend_process = None
        self.frontend_process = None
        self.server_process = None
        self.backend_port = 8000
        self.frontend_port = 3000
        
        # Set up executables
        if platform.system() == "Windows":
            self.python_exec = self.venv_path / "Scripts" / "python.exe"
            self.pip_exec = self.venv_path / "Scripts" / "pip.exe"
        else:
            self.python_exec = self.venv_path / "bin" / "python"
            self.pip_exec = self.venv_path / "bin" / "pip"
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.handle_interrupt)
        signal.signal(signal.SIGTERM, self.handle_interrupt)
        
    def _get_python_executable(self):
        """Get the correct Python executable path for the virtual environment"""
        if platform.system() == "Windows":
            return self.venv_path / "Scripts" / "python.exe"
        else:
            return self.venv_path / "bin" / "python"
    
    def _get_pip_executable(self):
        """Get the correct pip executable path for the virtual environment"""
        if platform.system() == "Windows":
            return self.venv_path / "Scripts" / "pip.exe"
        else:
            return self.venv_path / "bin" / "pip"
    
    def print_banner(self):
        """Print the project banner"""
        banner = f"""
{Colors.HEADER}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════╗
║                    AI Shopping Helper                        ║
║              Smart Product Comparison for India              ║
║                                                              ║
║  🛒 Find better deals and save money with AI-powered        ║
║     product comparison and quality scoring                   ║
╚══════════════════════════════════════════════════════════════╝
{Colors.ENDC}
"""
        print(banner)
    
    def log_step(self, step, message):
        """Log a step with formatting"""
        print(f"{Colors.OKBLUE}[{step}]{Colors.ENDC} {message}")
    
    def log_success(self, message):
        """Log success message"""
        print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")
    
    def log_warning(self, message):
        """Log warning message"""
        print(f"{Colors.WARNING}⚠️  {message}{Colors.ENDC}")
    
    def log_error(self, message):
        """Log error message"""
        print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")
    
    def check_python_version(self):
        """Check if Python version is compatible"""
        self.log_step("STEP 1", "Checking Python version...")
        
        if sys.version_info < (3, 8):
            self.log_error(f"Python 3.8+ is required. Current version: {sys.version}")
            return False
        
        self.log_success(f"Python {sys.version.split()[0]} is compatible")
        return True
    
    def create_virtual_environment(self):
        """Create virtual environment if it doesn't exist"""
        self.log_step("STEP 2", "Setting up virtual environment...")
        
        if self.venv_path.exists():
            self.log_success("Virtual environment already exists")
            return True
        
        try:
            subprocess.run([sys.executable, "-m", "venv", str(self.venv_path)], 
                         check=True, capture_output=True)
            self.log_success("Virtual environment created successfully")
            return True
        except subprocess.CalledProcessError as e:
            self.log_error(f"Failed to create virtual environment: {e}")
            return False
    
    def install_dependencies(self):
        """Install project dependencies"""
        self.log_step("STEP 3", "Installing dependencies...")
        
        requirements_file = self.project_root / "requirements.txt"
        if not requirements_file.exists():
            self.log_error("requirements.txt not found")
            return False
        
        try:
            # Upgrade pip first
            subprocess.run([str(self.pip_exec), "install", "--upgrade", "pip"], 
                         check=True, capture_output=True)
            
            # Install requirements
            subprocess.run([str(self.pip_exec), "install", "-r", str(requirements_file)], 
                         check=True, capture_output=True)
            
            self.log_success("Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            self.log_error(f"Failed to install dependencies: {e}")
            return False
    
    def initialize_database(self):
        """Initialize the SQLite database"""
        self.log_step("STEP 4", "Initializing database...")
        
        try:
            # Change to project directory and run database initialization
            env = os.environ.copy()
            env['PYTHONPATH'] = str(self.project_root)
            
            subprocess.run([
                str(self.python_exec), "-c", 
                "from backend.database.db_connection import init_db; init_db()"
            ], cwd=str(self.project_root), check=True, capture_output=True, env=env)
            
            self.log_success("Database initialized with default categories")
            return True
        except subprocess.CalledProcessError as e:
            self.log_error(f"Failed to initialize database: {e}")
            return False
    
    def setup_nextjs_frontend(self):
        """Setup Next.js frontend dependencies"""
        frontend_dir = self.project_root / "frontend-nextjs"
        
        if not frontend_dir.exists():
            self.log_error("Next.js frontend directory not found!")
            return False
            
        self.log_step("STEP 5", "Setting up Next.js frontend...")
        
        try:
            # Check if Node.js is installed
            result = subprocess.run(["node", "--version"], 
                                  capture_output=True, text=True, cwd=frontend_dir)
            if result.returncode != 0:
                self.log_error("Node.js is not installed! Please install Node.js first.")
                return False
                
            node_version = result.stdout.strip()
            self.log_success(f"Found Node.js: {node_version}")
            
            # Install npm dependencies
            self.log_success("Installing npm dependencies...")
            result = subprocess.run(["npm", "install"], 
                                  cwd=frontend_dir, check=True, capture_output=True)
            
            self.log_success("Next.js frontend setup completed!")
            return True
            
        except subprocess.CalledProcessError as e:
            self.log_error(f"Failed to setup Next.js frontend: {e}")
            return False
        except FileNotFoundError:
            self.log_error("npm not found! Please install Node.js and npm first.")
            return False

    def start_nextjs_frontend(self):
        """Start Next.js development server"""
        frontend_dir = self.project_root / "frontend-nextjs"
        
        try:
            self.log_step("STEP 6", f"Starting Next.js development server on port {self.frontend_port}...")
            
            # Start Next.js dev server
            cmd = ["npm", "run", "dev", "--", "--port", str(self.frontend_port)]
            self.frontend_process = subprocess.Popen(
                cmd,
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Wait for frontend to start
            time.sleep(5)
            
            if self.frontend_process.poll() is None:
                self.log_success(f"Next.js frontend started successfully on http://localhost:{self.frontend_port}")
                return True
            else:
                self.log_error("Failed to start Next.js frontend")
                return False
                
        except Exception as e:
            self.log_error(f"Error starting Next.js frontend: {e}")
            return False

    def start_server(self):
        """Start the FastAPI server"""
        self.log_step("STEP 7", "Starting FastAPI server...")
        
        try:
            # Start uvicorn server
            cmd = [
                str(self.python_exec), "-m", "uvicorn", 
                "app:app", 
                "--host", "0.0.0.0", 
                "--port", "8000", 
                "--reload"
            ]
            
            self.server_process = subprocess.Popen(
                cmd, 
                cwd=str(self.project_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Wait for server to start
            self.log_success("Server starting...")
            time.sleep(3)
            
            # Check if server is running
            if self.server_process.poll() is None:
                self.log_success("FastAPI server started successfully on http://localhost:8000")
                return True
            else:
                self.log_error("Server failed to start")
                return False
                
        except Exception as e:
            self.log_error(f"Failed to start server: {e}")
            return False
    
    def open_browser(self):
        """Open the application in the default browser"""
        self.log_step("STEP 8", "Opening application in browser...")
        
        try:
            time.sleep(2)  # Give server time to fully start
            url = f"http://localhost:{self.frontend_port}"
            webbrowser.open(url)
            self.log_success(f"Application opened in browser: {url}")
            return True
        except Exception as e:
            self.log_warning(f"Could not open browser automatically: {e}")
            self.log_warning(f"Please manually open http://localhost:{self.frontend_port} in your browser")
            return True
    
    def display_info(self):
        """Display application information"""
        info = f"""
{Colors.OKCYAN}{Colors.BOLD}🚀 AI Shopping Helper is now running!{Colors.ENDC}

{Colors.BOLD}Backend URLs:{Colors.ENDC}
  🌐 FastAPI Server:       http://localhost:{self.backend_port}
  📚 API Documentation:    http://localhost:{self.backend_port}/docs
  🔧 Health Check:         http://localhost:{self.backend_port}/health

{Colors.BOLD}Frontend URLs:{Colors.ENDC}
  ⚛️  Next.js App:         http://localhost:{self.frontend_port}
  🔄 Hot Reload:          Enabled

{Colors.BOLD}Available API Endpoints:{Colors.ENDC}
  📋 GET  /api/categories  - List all product categories
  🔍 POST /api/analyze     - Analyze product quality and find alternatives
  💬 POST /api/feedback    - Submit user feedback

{Colors.BOLD}Features:{Colors.ENDC}
  ✨ AI-powered product quality scoring
  🔍 Multi-platform price comparison (Amazon, Flipkart, Myntra)
  📊 Category-specific analysis scorecards
  💰 Smart alternative recommendations
  🖼️  Image and URL-based product analysis
  ⚛️  Modern React + TypeScript frontend (Next.js)

{Colors.WARNING}Press Ctrl+C to stop the servers{Colors.ENDC}
"""
        print(info)
    
    def cleanup(self):
        """Clean up resources"""
        if self.frontend_process:
            self.log_step("CLEANUP", "Stopping Next.js frontend...")
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
            self.log_success("Frontend server stopped")
            
        if self.server_process:
            self.log_step("CLEANUP", "Stopping FastAPI backend...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
            self.log_success("Backend server stopped")
    
    def handle_interrupt(self, signum, frame):
        """Handle Ctrl+C interrupt"""
        print(f"\n{Colors.WARNING}Received interrupt signal...{Colors.ENDC}")
        self.cleanup()
        print(f"{Colors.OKGREEN}Thank you for using AI Shopping Helper! 👋{Colors.ENDC}")
        sys.exit(0)
    
    def run(self):
        """Main execution method"""
        # Set up signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self.handle_interrupt)
        
        try:
            self.print_banner()
            
            # Execute all setup steps
            if not self.check_python_version():
                return False
            
            if not self.create_virtual_environment():
                return False
            
            if not self.install_dependencies():
                return False
            
            if not self.initialize_database():
                return False
            
            # Setup and start Next.js frontend
            if not self.setup_nextjs_frontend():
                return False
            if not self.start_nextjs_frontend():
                return False
            
            if not self.start_server():
                return False
            
            if not self.no_browser:
                if not self.open_browser():
                    return False
            
            self.display_info()
            
            # Keep the script running and monitor servers
            try:
                while True:
                    if self.server_process and self.server_process.poll() is not None:
                        self.log_error("Backend server process ended unexpectedly")
                        break
                    if self.frontend_process and self.frontend_process.poll() is not None:
                        self.log_error("Frontend server process ended unexpectedly")
                        break
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
            
        except Exception as e:
            self.log_error(f"Unexpected error: {e}")
            return False
        finally:
            self.cleanup()
        
        return True

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="AI Shopping Helper - One-Click Project Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run_project.py                      # Run with Next.js frontend
    python run_project.py --no-browser         # Don't open browser
    python run_project.py --dev                # Development mode
        """
    )
    
    parser.add_argument(
        '--no-browser', 
        action='store_true',
        help='Skip automatic browser launch'
    )
    parser.add_argument(
        '--dev', 
        action='store_true',
        help='Run in development mode with hot reload'
    )
    
    args = parser.parse_args()
    
    try:
        launcher = AIShoppingHelperLauncher(
            no_browser=args.no_browser,
            dev_mode=args.dev
        )
        success = launcher.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Operation cancelled by user{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"{Colors.FAIL}Unexpected error: {e}{Colors.ENDC}")
        sys.exit(1)

if __name__ == "__main__":
    main()
