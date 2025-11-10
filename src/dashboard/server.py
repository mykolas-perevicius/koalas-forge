#!/usr/bin/env python3
"""
Dashboard Server for Koala's Forge
Serves web interface and API endpoints
"""

import asyncio
import json
import os
import subprocess
import webbrowser
from pathlib import Path
from typing import Dict, List, Any
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socketserver
import threading
from datetime import datetime


class DashboardHandler(SimpleHTTPRequestHandler):
    """Custom HTTP handler for dashboard"""

    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/api/status':
            self.send_json_response(self.get_system_status())
        elif self.path == '/api/packages':
            self.send_json_response(self.get_packages())
        elif self.path == '/api/installed':
            self.send_json_response(self.get_installed_packages())
        elif self.path == '/api/history':
            self.send_json_response(self.get_install_history())
        elif self.path == '/api/stats':
            self.send_json_response(self.get_stats())
        elif self.path == '/' or self.path == '/index.html':
            self.serve_dashboard()
        else:
            super().do_GET()

    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/api/install':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            result = self.install_package(data.get('package'))
            self.send_json_response(result)
        elif self.path == '/api/uninstall':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            result = self.uninstall_package(data.get('package'))
            self.send_json_response(result)

    def send_json_response(self, data: Dict):
        """Send JSON response"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def serve_dashboard(self):
        """Serve the dashboard HTML"""
        dashboard_path = Path(__file__).parent / 'index.html'
        if dashboard_path.exists():
            with open(dashboard_path, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_error(404, "Dashboard not found")

    def get_system_status(self) -> Dict:
        """Get system status"""
        try:
            result = subprocess.run(
                ['./koala', 'status'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return {
                'status': 'online',
                'version': '1.9.0',
                'output': result.stdout
            }
        except:
            return {'status': 'error', 'version': '1.9.0'}

    def get_packages(self) -> Dict:
        """Get all available packages"""
        try:
            result = subprocess.run(
                ['./koala', 'list'],
                capture_output=True,
                text=True,
                timeout=10
            )
            # Parse output to extract packages
            lines = result.stdout.split('\n')
            packages = []
            current_category = None

            for line in lines:
                if line and not line.startswith(' '):
                    # Category line
                    if '(' in line:
                        current_category = line.split('(')[0].strip()
                elif line.strip().startswith('•') or line.strip().startswith('-'):
                    # Package line
                    pkg_name = line.strip().lstrip('•-').strip()
                    if pkg_name and current_category:
                        packages.append({
                            'name': pkg_name.split()[0],
                            'category': current_category,
                            'installed': False
                        })

            return {'packages': packages, 'total': len(packages)}
        except Exception as e:
            return {'error': str(e), 'packages': []}

    def get_installed_packages(self) -> Dict:
        """Get installed packages"""
        try:
            result = subprocess.run(
                ['./koala', 'list', '--installed'],
                capture_output=True,
                text=True,
                timeout=30
            )
            # Parse the output
            lines = result.stdout.split('\n')
            installed = []

            for line in lines:
                if '✅' in line:
                    # Extract package name
                    parts = line.split('✅')[-1].strip().split()
                    if parts:
                        installed.append(parts[0])

            return {'installed': installed, 'count': len(installed)}
        except Exception as e:
            return {'error': str(e), 'installed': []}

    def get_install_history(self) -> Dict:
        """Get installation history"""
        try:
            result = subprocess.run(
                ['./koala', 'history', '--limit', '20'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return {'history': result.stdout}
        except Exception as e:
            return {'error': str(e), 'history': ''}

    def get_stats(self) -> Dict:
        """Get system statistics"""
        installed = self.get_installed_packages()
        packages = self.get_packages()

        return {
            'total_packages': packages.get('total', 0),
            'installed_count': installed.get('count', 0),
            'categories': 14,
            'commands': 32,
            'version': '1.9.0'
        }

    def install_package(self, package: str) -> Dict:
        """Install a package"""
        try:
            result = subprocess.run(
                ['./koala', 'install', package, '-y'],
                capture_output=True,
                text=True,
                timeout=60
            )
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def uninstall_package(self, package: str) -> Dict:
        """Uninstall a package"""
        try:
            result = subprocess.run(
                ['./koala', 'uninstall', package, '-y'],
                capture_output=True,
                text=True,
                timeout=60
            )
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}


class DashboardServer:
    """Dashboard server manager"""

    def __init__(self, port: int = 8080):
        self.port = port
        self.server = None
        self.thread = None

    def start(self):
        """Start the dashboard server"""
        os.chdir(Path(__file__).parent.parent.parent)  # Change to project root

        Handler = DashboardHandler
        self.server = socketserver.TCPServer(("", self.port), Handler)

        # Start server in a thread
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.daemon = True
        self.thread.start()

        print(f"🌐 Dashboard server running at http://localhost:{self.port}")

        # Open in browser
        webbrowser.open(f'http://localhost:{self.port}')

        return self.server

    def stop(self):
        """Stop the dashboard server"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()

    async def launch_electron(self):
        """Launch Electron app"""
        electron_path = Path(__file__).parent / 'electron'

        if not electron_path.exists():
            print("⚠️  Electron app not found. Install with: npm install electron")
            return

        try:
            # Check if electron is installed
            result = subprocess.run(
                ['npm', 'list', 'electron'],
                capture_output=True,
                cwd=electron_path
            )

            if result.returncode != 0:
                print("📦 Installing Electron...")
                subprocess.run(['npm', 'install'], cwd=electron_path)

            # Launch Electron
            print("🖥️  Launching Electron GUI...")
            subprocess.Popen(
                ['npm', 'start'],
                cwd=electron_path,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except FileNotFoundError:
            print("⚠️  npm not found. Please install Node.js first.")
        except Exception as e:
            print(f"⚠️  Could not launch Electron: {e}")


async def launch_dashboard(open_browser: bool = True, open_electron: bool = True):
    """Launch dashboard in browser and Electron"""
    server = DashboardServer(port=8080)

    # Start web server
    server.start()

    # Launch Electron if requested
    if open_electron:
        await server.launch_electron()

    print("\n✨ Dashboard is running!")
    print("   Browser: http://localhost:8080")
    print("   Press Ctrl+C to stop\n")

    try:
        # Keep running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Stopping dashboard...")
        server.stop()


if __name__ == "__main__":
    asyncio.run(launch_dashboard())