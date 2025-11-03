#!/usr/bin/env python3
"""
GUI Server for Speedy App Installer
Provides web interface and WebSocket backend for installation control
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Try to import required packages
try:
    import websockets
    from aiohttp import web
except ImportError:
    print("Required packages not installed. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "aiohttp", "websockets"])
    import websockets
    from aiohttp import web

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class InstallerServer:
    def __init__(self, host='localhost', port=8080, ws_port=8765):
        self.host = host
        self.port = port
        self.ws_port = ws_port
        self.app = web.Application()
        self.websocket_clients = set()
        self.installation_process = None
        self.install_stats = {
            'installed': 0,
            'failed': 0,
            'diskUsed': 0,
            'startTime': None
        }

        # Get project root (must be before setup_routes)
        self.project_root = Path(__file__).parent.parent

        # Ensure logs directory exists
        logs_dir = self.project_root / 'logs'
        logs_dir.mkdir(exist_ok=True)

        # Setup routes
        self.setup_routes()

    def setup_routes(self):
        """Setup HTTP routes"""
        self.app.router.add_get('/', self.index)
        self.app.router.add_static('/logs',
                                  str(self.project_root / 'logs'),
                                  name='logs')
        self.app.router.add_get('/api/status', self.get_status)
        self.app.router.add_get('/api/packages', self.get_packages)
        self.app.router.add_post('/api/install', self.start_install)
        self.app.router.add_post('/api/stop', self.stop_install)
        self.app.router.add_get('/api/hardware', self.detect_hardware)
        self.app.router.add_get('/api/terminal-progress', self.get_terminal_progress)
        self.app.router.add_post('/api/terminal-update', self.terminal_update)

    async def index(self, request):
        """Serve the main HTML interface"""
        html_path = self.project_root / 'gui' / 'web_interface.html'
        if html_path.exists():
            with open(html_path, 'r') as f:
                content = f.read()
            return web.Response(text=content, content_type='text/html')
        else:
            return web.Response(text="GUI file not found", status=404)

    async def get_status(self, request):
        """Get current installation status"""
        status = {
            'running': self.installation_process is not None,
            'stats': self.install_stats,
            'system': await self.get_system_info()
        }
        return web.json_response(status)

    async def get_packages(self, request):
        """Get available packages from config"""
        try:
            import yaml
            config_path = self.project_root / 'apps.yaml'
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            return web.json_response(config)
        except Exception as e:
            logger.error(f"Error loading packages: {e}")
            return web.json_response({'error': str(e)}, status=500)

    async def start_install(self, request):
        """Start installation process"""
        try:
            data = await request.json()
            mode = data.get('mode', 'full')
            packages = data.get('packages', [])

            if self.installation_process:
                return web.json_response(
                    {'error': 'Installation already in progress'},
                    status=400
                )

            # Reset stats
            self.install_stats = {
                'installed': 0,
                'failed': 0,
                'diskUsed': 0,
                'startTime': datetime.now().isoformat()
            }

            # Start installation in background
            asyncio.create_task(self.run_installation(mode, packages))

            return web.json_response({'status': 'started', 'mode': mode})

        except Exception as e:
            logger.error(f"Error starting installation: {e}")
            return web.json_response({'error': str(e)}, status=500)

    async def stop_install(self, request):
        """Stop installation process"""
        if self.installation_process:
            try:
                self.installation_process.terminate()
                await asyncio.sleep(0.5)
                if self.installation_process.poll() is None:
                    self.installation_process.kill()
                self.installation_process = None

                await self.broadcast({
                    'type': 'status',
                    'message': 'Installation stopped',
                    'level': 'warning'
                })

                return web.json_response({'status': 'stopped'})
            except Exception as e:
                logger.error(f"Error stopping installation: {e}")
                return web.json_response({'error': str(e)}, status=500)
        else:
            return web.json_response(
                {'error': 'No installation in progress'},
                status=400
            )

    async def get_terminal_progress(self, request):
        """Get progress from terminal installation"""
        try:
            progress_file = Path('/tmp/app_installer_progress.json')
            if progress_file.exists():
                with open(progress_file, 'r') as f:
                    data = json.load(f)
                return web.json_response(data)
            else:
                return web.json_response({'status': 'idle', 'progress': 0})
        except Exception as e:
            logger.error(f"Error reading terminal progress: {e}")
            return web.json_response({'error': str(e)}, status=500)

    async def terminal_update(self, request):
        """Receive updates from terminal installation"""
        try:
            data = await request.json()

            # Broadcast to all WebSocket clients
            await self.broadcast(data)

            return web.json_response({'status': 'received'})
        except Exception as e:
            logger.error(f"Error processing terminal update: {e}")
            return web.json_response({'error': str(e)}, status=500)

    async def detect_hardware(self, request):
        """Detect system hardware"""
        try:
            hardware_script = self.project_root / 'scripts' / 'detect_hardware.sh'
            result = subprocess.run(
                [str(hardware_script)],
                capture_output=True,
                text=True,
                timeout=10
            )

            # Parse hardware info
            info = await self.get_system_info()

            return web.json_response(info)
        except Exception as e:
            logger.error(f"Error detecting hardware: {e}")
            return web.json_response({'error': str(e)}, status=500)

    async def get_system_info(self) -> Dict[str, str]:
        """Get system information"""
        info = {}

        try:
            # OS Info
            if sys.platform == 'darwin':
                os_version = subprocess.run(
                    ['sw_vers', '-productVersion'],
                    capture_output=True,
                    text=True
                ).stdout.strip()
                info['os'] = f"macOS {os_version}"

                # CPU Info
                cpu = subprocess.run(
                    ['sysctl', '-n', 'machdep.cpu.brand_string'],
                    capture_output=True,
                    text=True
                ).stdout.strip()
                info['cpu'] = cpu

                # RAM Info
                mem = subprocess.run(
                    ['sysctl', '-n', 'hw.memsize'],
                    capture_output=True,
                    text=True
                ).stdout.strip()
                if mem:
                    mem_gb = int(mem) / (1024**3)
                    info['ram'] = f"{mem_gb:.1f}GB"

            elif sys.platform.startswith('linux'):
                # Linux system info
                info['os'] = subprocess.run(
                    ['lsb_release', '-d'],
                    capture_output=True,
                    text=True
                ).stdout.strip().replace('Description:', '').strip()

                # CPU info from /proc/cpuinfo
                with open('/proc/cpuinfo', 'r') as f:
                    for line in f:
                        if 'model name' in line:
                            info['cpu'] = line.split(':')[1].strip()
                            break

                # Memory info
                with open('/proc/meminfo', 'r') as f:
                    for line in f:
                        if 'MemTotal' in line:
                            mem_kb = int(line.split()[1])
                            info['ram'] = f"{mem_kb / (1024**2):.1f}GB"
                            break

            # Disk space
            df = subprocess.run(
                ['df', '-h', '/'],
                capture_output=True,
                text=True
            ).stdout.split('\n')[1].split()
            if len(df) >= 4:
                info['storage'] = f"{df[3]} free of {df[1]}"

        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            info['error'] = str(e)

        return info

    async def run_installation(self, mode: str, packages: list):
        """Run the installation process"""
        try:
            install_script = self.project_root / 'install.sh'

            # Build command
            cmd = [str(install_script)]
            if mode != 'custom':
                cmd.append(f'--{mode}')
            else:
                # TODO: Implement custom package selection
                pass

            # Start installation process
            self.installation_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            # Read output line by line
            while True:
                if self.installation_process is None:
                    break

                line = self.installation_process.stdout.readline()
                if not line:
                    break

                # Parse output and send to clients
                await self.process_output_line(line)

            # Wait for process to complete
            if self.installation_process:
                return_code = self.installation_process.wait()

                if return_code == 0:
                    await self.broadcast({
                        'type': 'status',
                        'message': 'Installation completed successfully!',
                        'level': 'success'
                    })
                else:
                    await self.broadcast({
                        'type': 'status',
                        'message': f'Installation failed with code {return_code}',
                        'level': 'error'
                    })

                self.installation_process = None

        except Exception as e:
            logger.error(f"Installation error: {e}")
            await self.broadcast({
                'type': 'status',
                'message': f'Installation error: {str(e)}',
                'level': 'error'
            })
            self.installation_process = None

    async def process_output_line(self, line: str):
        """Process installation output line"""
        line = line.strip()
        if not line:
            return

        # Determine output level
        level = 'info'
        if '✅' in line or 'success' in line.lower():
            level = 'success'
            self.install_stats['installed'] += 1
        elif '❌' in line or 'error' in line.lower() or 'failed' in line.lower():
            level = 'error'
            self.install_stats['failed'] += 1
        elif '⚠️' in line or 'warning' in line.lower():
            level = 'warning'

        # Send to all WebSocket clients
        await self.broadcast({
            'type': 'output',
            'content': line,
            'level': level
        })

        # Update stats periodically
        await self.broadcast({
            'type': 'stats',
            'installed': self.install_stats['installed'],
            'failed': self.install_stats['failed'],
            'diskUsed': self.install_stats['diskUsed']
        })

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all WebSocket clients"""
        if self.websocket_clients:
            message_str = json.dumps(message)
            # Send to all connected clients
            disconnected_clients = set()
            for client in self.websocket_clients:
                try:
                    await client.send(message_str)
                except websockets.exceptions.ConnectionClosed:
                    disconnected_clients.add(client)

            # Remove disconnected clients
            self.websocket_clients -= disconnected_clients

    async def handle_websocket(self, websocket):
        """Handle WebSocket connections"""
        # Add client to set
        self.websocket_clients.add(websocket)
        logger.info(f"WebSocket client connected. Total clients: {len(self.websocket_clients)}")

        try:
            # Send initial system info
            system_info = await self.get_system_info()
            await websocket.send(json.dumps({
                'type': 'system_info',
                **system_info
            }))

            # Handle messages from client
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.handle_websocket_message(websocket, data)
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON received: {message}")
                except Exception as e:
                    logger.error(f"Error handling WebSocket message: {e}")

        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            # Remove client from set
            self.websocket_clients.discard(websocket)
            logger.info(f"WebSocket client disconnected. Total clients: {len(self.websocket_clients)}")

    async def handle_websocket_message(self, websocket, data: Dict[str, Any]):
        """Handle incoming WebSocket messages"""
        action = data.get('action')

        if action == 'install':
            mode = data.get('mode', 'full')
            packages = data.get('packages', [])

            if not self.installation_process:
                asyncio.create_task(self.run_installation(mode, packages))
                await websocket.send(json.dumps({
                    'type': 'status',
                    'message': f'Starting {mode} installation...',
                    'level': 'info'
                }))
            else:
                await websocket.send(json.dumps({
                    'type': 'status',
                    'message': 'Installation already in progress',
                    'level': 'warning'
                }))

        elif action == 'stop':
            if self.installation_process:
                self.installation_process.terminate()
                self.installation_process = None
                await websocket.send(json.dumps({
                    'type': 'status',
                    'message': 'Installation stopped',
                    'level': 'warning'
                }))

        elif action == 'detect_hardware':
            info = await self.get_system_info()
            await websocket.send(json.dumps({
                'type': 'system_info',
                **info
            }))

        elif action == 'test':
            # Run tests
            test_script = self.project_root / 'test_install.sh'
            if test_script.exists():
                process = subprocess.Popen(
                    [str(test_script)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )

                for line in iter(process.stdout.readline, ''):
                    if line:
                        await websocket.send(json.dumps({
                            'type': 'output',
                            'content': line.strip(),
                            'level': 'info'
                        }))

                process.wait()

    async def run_http_server(self):
        """Run the HTTP server"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        logger.info(f"HTTP server started at http://{self.host}:{self.port}")

    async def run_websocket_server(self):
        """Run the WebSocket server"""
        server = await websockets.serve(
            self.handle_websocket,
            self.host,
            self.ws_port
        )
        logger.info(f"WebSocket server started at ws://{self.host}:{self.ws_port}")
        await asyncio.Future()  # Run forever

    async def run(self):
        """Run both servers"""
        await asyncio.gather(
            self.run_http_server(),
            self.run_websocket_server()
        )

def main():
    """Main entry point"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║           🚀 SPEEDY APP INSTALLER - GUI SERVER 🚀            ║
╚═══════════════════════════════════════════════════════════════╝
    """)

    server = InstallerServer()

    print(f"Starting servers...")
    print(f"  Web Interface: http://localhost:8080")
    print(f"  WebSocket API: ws://localhost:8765")
    print(f"\nPress Ctrl+C to stop the server\n")

    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()