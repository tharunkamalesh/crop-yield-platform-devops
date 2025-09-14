#!/usr/bin/env python3
"""
AI Crop Yield Prediction & Advisory Platform - Startup Script
Launches both backend and frontend services
"""

import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path

class AppLauncher:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.running = True
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\n🛑 Shutting down services...")
        self.running = False
        self.stop_services()
        sys.exit(0)
    
    def check_dependencies(self):
        """Check if required dependencies are installed"""
        print("🔍 Checking dependencies...")
        
        # Check Python dependencies
        try:
            import flask
            import pandas
            import numpy
            import sklearn
            print("✅ Python dependencies: OK")
        except ImportError as e:
            print(f"❌ Python dependency missing: {e}")
            print("💡 Run: pip install -r backend/requirements.txt")
            return False
        
        # Check Node.js
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Node.js: {result.stdout.strip()}")
            else:
                print("❌ Node.js not found")
                return False
        except FileNotFoundError:
            print("❌ Node.js not found")
            return False
        
        # Check npm
        try:
            result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ npm: {result.stdout.strip()}")
            else:
                print("❌ npm not found")
                return False
        except FileNotFoundError:
            print("❌ npm not found")
            return False
        
        return True
    
    def install_frontend_dependencies(self):
        """Install frontend dependencies if needed"""
        frontend_dir = Path("frontend")
        node_modules = frontend_dir / "node_modules"
        
        if not node_modules.exists():
            print("📦 Installing frontend dependencies...")
            try:
                subprocess.run(['npm', 'install'], cwd=frontend_dir, check=True)
                print("✅ Frontend dependencies installed")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install frontend dependencies: {e}")
                return False
        else:
            print("✅ Frontend dependencies: OK")
        
        return True
    
    def start_backend(self):
        """Start the Flask backend server"""
        print("🚀 Starting backend server...")
        
        backend_dir = Path("backend")
        if not backend_dir.exists():
            print("❌ Backend directory not found")
            return False
        
        try:
            # Set environment variables
            env = os.environ.copy()
            env['FLASK_ENV'] = 'development'
            env['FLASK_DEBUG'] = '1'
            
            # Start backend
            self.backend_process = subprocess.Popen(
                [sys.executable, 'app.py'],
                cwd=backend_dir,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait a bit for backend to start
            time.sleep(3)
            
            if self.backend_process.poll() is None:
                print("✅ Backend server started on http://localhost:5000")
                return True
            else:
                stdout, stderr = self.backend_process.communicate()
                print(f"❌ Backend failed to start: {stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to start backend: {e}")
            return False
    
    def start_frontend(self):
        """Start the React frontend development server"""
        print("🚀 Starting frontend server...")
        
        frontend_dir = Path("frontend")
        if not frontend_dir.exists():
            print("❌ Frontend directory not found")
            return False
        
        try:
            # Start frontend
            self.frontend_process = subprocess.Popen(
                ['npm', 'start'],
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait a bit for frontend to start
            time.sleep(5)
            
            if self.frontend_process.poll() is None:
                print("✅ Frontend server started on http://localhost:3000")
                return True
            else:
                stdout, stderr = self.frontend_process.communicate()
                print(f"❌ Frontend failed to start: {stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to start frontend: {e}")
            return False
    
    def monitor_services(self):
        """Monitor running services"""
        print("\n📊 Monitoring services...")
        print("Press Ctrl+C to stop all services")
        
        while self.running:
            # Check backend
            if self.backend_process and self.backend_process.poll() is not None:
                print("⚠️  Backend service stopped unexpectedly")
                self.running = False
                break
            
            # Check frontend
            if self.frontend_process and self.frontend_process.poll() is not None:
                print("⚠️  Frontend service stopped unexpectedly")
                self.running = False
                break
            
            time.sleep(5)
    
    def stop_services(self):
        """Stop all running services"""
        if self.backend_process:
            print("🛑 Stopping backend...")
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
        
        if self.frontend_process:
            print("🛑 Stopping frontend...")
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
    
    def run(self):
        """Main launcher function"""
        print("🌾 AI Crop Yield Prediction & Advisory Platform")
        print("=" * 60)
        
        # Check dependencies
        if not self.check_dependencies():
            print("\n❌ Dependency check failed. Please install missing dependencies.")
            return False
        
        # Install frontend dependencies
        if not self.install_frontend_dependencies():
            print("\n❌ Failed to install frontend dependencies.")
            return False
        
        print("\n🚀 Starting services...")
        
        # Start backend
        if not self.start_backend():
            print("\n❌ Failed to start backend service.")
            return False
        
        # Start frontend
        if not self.start_frontend():
            print("\n❌ Failed to start frontend service.")
            self.stop_services()
            return False
        
        print("\n🎉 All services started successfully!")
        print("\n📱 Access your application:")
        print("   🌐 Frontend: http://localhost:3000")
        print("   🔧 Backend API: http://localhost:5000")
        print("   📊 Health Check: http://localhost:5000/api/health")
        
        # Monitor services
        self.monitor_services()
        
        return True

def main():
    """Main entry point"""
    launcher = AppLauncher()
    
    try:
        success = launcher.run()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
    finally:
        launcher.stop_services()

if __name__ == "__main__":
    main()
