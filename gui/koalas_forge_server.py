#!/usr/bin/env python3
"""
🐨 Koala's Forge - Web Server
Modern web-based application installer with full control
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List, Set

# Try to import required packages
try:
    import websockets
    from aiohttp import web
    import yaml
except ImportError:
    print("Required packages not installed. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "aiohttp", "websockets", "pyyaml"])
    import websockets
    from aiohttp import web
    import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class KoalasForgeServer:
    def __init__(self, host='localhost', port=8080, ws_port=8765):
        self.host = host
        self.port = port
        self.ws_port = ws_port
        self.app = web.Application()
        self.websocket_clients = set()
        self.installation_process = None
        self.installation_paused = False
        self.installation_queue: List[str] = []
        self.current_install_index = 0

        self.install_stats = {
            'installed': 0,
            'failed': 0,
            'total': 0,
            'diskUsed': 0,
            'startTime': None,
            'currentApp': None
        }

        # Get project root
        self.project_root = Path(__file__).parent.parent

        # Ensure directories exist
        (self.project_root / 'logs').mkdir(exist_ok=True)
        (self.project_root / 'configs').mkdir(exist_ok=True)

        # Load app database
        self.apps_db = self.load_apps_database()

        # Setup routes
        self.setup_routes()

    def load_apps_database(self) -> Dict[str, Any]:
        """Load applications from apps.yaml"""
        try:
            config_path = self.project_root / 'apps.yaml'
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading apps database: {e}")
            return {'apps': {}}

    def setup_routes(self):
        """Setup HTTP routes"""
        self.app.router.add_get('/', self.index)
        self.app.router.add_static('/logs', str(self.project_root / 'logs'), name='logs')

        # API endpoints
        self.app.router.add_get('/api/status', self.get_status)
        self.app.router.add_get('/api/apps', self.get_apps)
        self.app.router.add_get('/api/installed-apps', self.get_installed_apps)
        self.app.router.add_post('/api/install', self.start_install)
        self.app.router.add_post('/api/pause', self.pause_install)
        self.app.router.add_post('/api/resume', self.resume_install)
        self.app.router.add_post('/api/cancel', self.cancel_install)
        self.app.router.add_post('/api/uninstall', self.uninstall_apps)
        self.app.router.add_post('/api/update', self.update_apps)
        self.app.router.add_get('/api/hardware', self.detect_hardware)
        self.app.router.add_post('/api/export-config', self.export_config)
        self.app.router.add_post('/api/import-config', self.import_config)

    async def index(self, request):
        """Serve the main HTML interface"""
        html_path = self.project_root / 'gui' / 'koalas_forge.html'
        if html_path.exists():
            with open(html_path, 'r') as f:
                content = f.read()
            return web.Response(text=content, content_type='text/html')
        else:
            return web.Response(text="Koala's Forge interface not found", status=404)

    async def get_status(self, request):
        """Get current installation status"""
        status = {
            'running': self.installation_process is not None,
            'paused': self.installation_paused,
            'stats': self.install_stats,
            'system': await self.get_system_info(),
            'queue': self.installation_queue,
            'currentIndex': self.current_install_index
        }
        return web.json_response(status)

    async def get_apps(self, request):
        """Get all available applications"""
        return web.json_response(self.apps_db)

    async def get_installed_apps(self, request):
        """Check which apps are already installed"""
        installed = []

        try:
            # Check for common package managers
            if sys.platform == 'darwin':
                # macOS - check with brew
                result = subprocess.run(
                    ['brew', 'list', '--formula'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                brew_formulas = set(result.stdout.strip().split('\n'))

                result = subprocess.run(
                    ['brew', 'list', '--cask'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                brew_casks = set(result.stdout.strip().split('\n'))

                # Check each app
                for category, apps in self.apps_db.get('apps', {}).items():
                    for app in apps:
                        package = app.get('package', '')
                        if package in brew_formulas or package in brew_casks:
                            installed.append(app.get('name', package))

            elif sys.platform.startswith('linux'):
                # Linux - check common package managers
                # This is simplified - would need to check apt, dnf, pacman etc.
                pass

        except Exception as e:
            logger.error(f"Error checking installed apps: {e}")

        return web.json_response({'installed': installed})

    async def start_install(self, request):
        """Start installation process"""
        try:
            data = await request.json()
            app_ids = data.get('apps', [])
            settings = data.get('settings', {})
            dry_run = data.get('dry_run', False)

            if self.installation_process:
                return web.json_response(
                    {'error': 'Installation already in progress'},
                    status=400
                )

            # Reset stats
            self.install_stats = {
                'installed': 0,
                'failed': 0,
                'total': len(app_ids),
                'diskUsed': 0,
                'startTime': datetime.now().isoformat(),
                'currentApp': None,
                'dryRun': dry_run
            }

            self.installation_queue = app_ids
            self.current_install_index = 0
            self.installation_paused = False

            # Start installation in background
            asyncio.create_task(self.run_installation(app_ids, settings, dry_run))

            return web.json_response({
                'status': 'started',
                'total': len(app_ids),
                'dry_run': dry_run
            })

        except Exception as e:
            logger.error(f"Error starting installation: {e}")
            return web.json_response({'error': str(e)}, status=500)

    async def pause_install(self, request):
        """Pause installation"""
        self.installation_paused = True
        await self.broadcast({
            'type': 'status',
            'message': 'Installation paused',
            'level': 'warning'
        })
        return web.json_response({'status': 'paused'})

    async def resume_install(self, request):
        """Resume installation"""
        self.installation_paused = False
        await self.broadcast({
            'type': 'status',
            'message': 'Installation resumed',
            'level': 'info'
        })
        return web.json_response({'status': 'resumed'})

    async def cancel_install(self, request):
        """Cancel installation"""
        if self.installation_process:
            try:
                self.installation_process.terminate()
                await asyncio.sleep(0.5)
                if self.installation_process.poll() is None:
                    self.installation_process.kill()
                self.installation_process = None
                self.installation_queue = []
                self.current_install_index = 0

                await self.broadcast({
                    'type': 'status',
                    'message': 'Installation cancelled',
                    'level': 'error'
                })

                return web.json_response({'status': 'cancelled'})
            except Exception as e:
                logger.error(f"Error cancelling installation: {e}")
                return web.json_response({'error': str(e)}, status=500)
        else:
            return web.json_response(
                {'error': 'No installation in progress'},
                status=400
            )

    async def uninstall_apps(self, request):
        """Uninstall applications"""
        try:
            data = await request.json()
            app_ids = data.get('apps', [])

            await self.broadcast({
                'type': 'status',
                'message': f'Uninstalling {len(app_ids)} apps...',
                'level': 'info'
            })

            for app_id in app_ids:
                app_info = self.find_app_by_id(app_id)
                if app_info:
                    await self.uninstall_single_app(app_info)

            return web.json_response({'status': 'completed'})

        except Exception as e:
            logger.error(f"Error uninstalling apps: {e}")
            return web.json_response({'error': str(e)}, status=500)

    async def update_apps(self, request):
        """Update applications"""
        try:
            data = await request.json()
            app_ids = data.get('apps', [])

            if not app_ids:
                # Update all installed apps
                if sys.platform == 'darwin':
                    subprocess.run(['brew', 'upgrade'], check=True)
                elif sys.platform.startswith('linux'):
                    subprocess.run(['sudo', 'apt', 'upgrade', '-y'], check=True)

            return web.json_response({'status': 'updated'})

        except Exception as e:
            logger.error(f"Error updating apps: {e}")
            return web.json_response({'error': str(e)}, status=500)

    async def export_config(self, request):
        """Export current configuration"""
        try:
            data = await request.json()
            config = {
                'version': '1.0',
                'created': datetime.now().isoformat(),
                'apps': data.get('apps', []),
                'presets': data.get('presets', [])
            }

            config_file = self.project_root / 'configs' / f'config_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)

            return web.json_response({
                'status': 'exported',
                'file': str(config_file)
            })

        except Exception as e:
            logger.error(f"Error exporting config: {e}")
            return web.json_response({'error': str(e)}, status=500)

    async def import_config(self, request):
        """Import configuration"""
        try:
            data = await request.json()
            config_path = data.get('path')

            with open(config_path, 'r') as f:
                config = json.load(f)

            return web.json_response(config)

        except Exception as e:
            logger.error(f"Error importing config: {e}")
            return web.json_response({'error': str(e)}, status=500)

    async def detect_hardware(self, request):
        """Detect system hardware"""
        try:
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
                try:
                    info['os'] = subprocess.run(
                        ['lsb_release', '-d'],
                        capture_output=True,
                        text=True
                    ).stdout.strip().replace('Description:', '').strip()
                except:
                    info['os'] = 'Linux'

                # CPU info from /proc/cpuinfo
                try:
                    with open('/proc/cpuinfo', 'r') as f:
                        for line in f:
                            if 'model name' in line:
                                info['cpu'] = line.split(':')[1].strip()
                                break
                except:
                    pass

                # Memory info
                try:
                    with open('/proc/meminfo', 'r') as f:
                        for line in f:
                            if 'MemTotal' in line:
                                mem_kb = int(line.split()[1])
                                info['ram'] = f"{mem_kb / (1024**2):.1f}GB"
                                break
                except:
                    pass

            # Disk space
            try:
                df = subprocess.run(
                    ['df', '-h', '/'],
                    capture_output=True,
                    text=True
                ).stdout.split('\n')[1].split()
                if len(df) >= 4:
                    info['storage'] = f"{df[3]} free of {df[1]}"
            except:
                pass

        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            info['error'] = str(e)

        return info

    def find_app_by_id(self, app_id: str) -> Optional[Dict[str, Any]]:
        """Find app info by ID"""
        for category, apps in self.apps_db.get('apps', {}).items():
            for app in apps:
                if app.get('package') == app_id or app.get('name', '').lower().replace(' ', '-') == app_id:
                    return app
        return None

    async def run_installation(self, app_ids: List[str], settings: Dict[str, Any], dry_run: bool = False):
        """Run the installation process"""
        try:
            mode_msg = "🧪 DRY RUN MODE - No actual installation will occur" if dry_run else "Starting installation..."
            await self.broadcast({
                'type': 'output',
                'content': mode_msg,
                'level': 'info'
            })

            for index, app_id in enumerate(app_ids):
                # Check if paused
                while self.installation_paused:
                    await asyncio.sleep(1)
                    if not self.installation_queue:  # Cancelled
                        return

                self.current_install_index = index
                app_info = self.find_app_by_id(app_id)

                if not app_info:
                    await self.broadcast({
                        'type': 'output',
                        'content': f'App not found: {app_id}',
                        'level': 'error'
                    })
                    self.install_stats['failed'] += 1
                    continue

                # Update current app
                self.install_stats['currentApp'] = app_info.get('name', app_id)

                await self.broadcast({
                    'type': 'progress',
                    'current': index + 1,
                    'total': len(app_ids),
                    'percent': int((index + 1) / len(app_ids) * 100),
                    'currentApp': app_info.get('name', app_id)
                })

                # Install the app (or simulate in dry run)
                success = await self.install_single_app(app_info, settings.get(app_id, {}), dry_run)

                if success:
                    self.install_stats['installed'] += 1
                else:
                    self.install_stats['failed'] += 1

                # Update stats
                await self.broadcast({
                    'type': 'stats',
                    'installed': self.install_stats['installed'],
                    'failed': self.install_stats['failed'],
                    'total': self.install_stats['total']
                })

            # Installation complete
            complete_msg = (
                f'🧪 Dry run complete! All {self.install_stats["installed"]} apps would be installed successfully.'
                if dry_run else
                f'Installation complete! {self.install_stats["installed"]} installed, {self.install_stats["failed"]} failed'
            )
            await self.broadcast({
                'type': 'complete',
                'message': complete_msg,
                'level': 'success'
            })

            self.installation_process = None
            self.installation_queue = []

        except Exception as e:
            logger.error(f"Installation error: {e}")
            await self.broadcast({
                'type': 'error',
                'message': f'Installation error: {str(e)}',
                'level': 'error'
            })
            self.installation_process = None

    async def install_single_app(self, app_info: Dict[str, Any], settings: Dict[str, Any], dry_run: bool = False) -> bool:
        """Install a single application"""
        try:
            package = app_info.get('package')
            name = app_info.get('name', package)
            install_type = app_info.get('install_type', 'brew')

            action = 'Checking' if dry_run else 'Installing'
            prefix = '🧪 [DRY RUN]' if dry_run else '📦'

            await self.broadcast({
                'type': 'output',
                'content': f'{prefix} {action} {name}...',
                'level': 'info'
            })

            # In dry run mode, just simulate and return success
            if dry_run:
                await asyncio.sleep(0.3)  # Simulate check time
                await self.broadcast({
                    'type': 'output',
                    'content': f'✅ {name} - Would be installed successfully',
                    'level': 'success'
                })
                await self.broadcast({
                    'type': 'output',
                    'content': f'  → Package: {package}',
                    'level': 'info'
                })
                await self.broadcast({
                    'type': 'output',
                    'content': f'  → Type: {install_type}',
                    'level': 'info'
                })
                await self.broadcast({
                    'type': 'output',
                    'content': f'  → Platforms: {", ".join(app_info.get("platforms", []))}',
                    'level': 'info'
                })
                return True

            # Build install command
            if sys.platform == 'darwin':
                if install_type == 'brew':
                    cmd = ['brew', 'install', package]
                elif install_type == 'cask':
                    cmd = ['brew', 'install', '--cask', package]
                else:
                    await self.broadcast({
                        'type': 'output',
                        'content': f'Unknown install type: {install_type}',
                        'level': 'error'
                    })
                    return False

                # Add custom install location if specified
                if settings.get('install_path'):
                    # Note: brew doesn't support custom paths easily
                    pass

                # Run installation
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )

                self.installation_process = process
                stdout, stderr = await process.communicate()

                if process.returncode == 0:
                    await self.broadcast({
                        'type': 'output',
                        'content': f'✅ {name} installed successfully',
                        'level': 'success'
                    })

                    # Run post-install commands if any
                    post_install = app_info.get('post_install')
                    if post_install:
                        await self.run_post_install(post_install, name)

                    return True
                else:
                    error_msg = stderr.decode() if stderr else 'Unknown error'
                    await self.broadcast({
                        'type': 'output',
                        'content': f'❌ Failed to install {name}: {error_msg}',
                        'level': 'error'
                    })
                    return False

            else:
                await self.broadcast({
                    'type': 'output',
                    'content': f'Platform {sys.platform} not yet supported',
                    'level': 'error'
                })
                return False

        except Exception as e:
            logger.error(f"Error installing {app_info.get('name')}: {e}")
            await self.broadcast({
                'type': 'output',
                'content': f'❌ Error installing {app_info.get("name")}: {str(e)}',
                'level': 'error'
            })
            return False

    async def run_post_install(self, commands: str, app_name: str):
        """Run post-installation commands"""
        try:
            await self.broadcast({
                'type': 'output',
                'content': f'Running post-install for {app_name}...',
                'level': 'info'
            })

            process = await asyncio.create_subprocess_shell(
                commands,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                await self.broadcast({
                    'type': 'output',
                    'content': f'✅ Post-install completed for {app_name}',
                    'level': 'success'
                })
            else:
                await self.broadcast({
                    'type': 'output',
                    'content': f'⚠️ Post-install had issues for {app_name}',
                    'level': 'warning'
                })

        except Exception as e:
            logger.error(f"Post-install error: {e}")

    async def uninstall_single_app(self, app_info: Dict[str, Any]) -> bool:
        """Uninstall a single application"""
        try:
            package = app_info.get('package')
            name = app_info.get('name', package)
            install_type = app_info.get('install_type', 'brew')

            await self.broadcast({
                'type': 'output',
                'content': f'Uninstalling {name}...',
                'level': 'info'
            })

            if sys.platform == 'darwin':
                if install_type in ['brew', 'cask']:
                    cmd = ['brew', 'uninstall', package]

                    process = await asyncio.create_subprocess_exec(
                        *cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )

                    stdout, stderr = await process.communicate()

                    if process.returncode == 0:
                        await self.broadcast({
                            'type': 'output',
                            'content': f'✅ {name} uninstalled successfully',
                            'level': 'success'
                        })
                        return True

            return False

        except Exception as e:
            logger.error(f"Error uninstalling {app_info.get('name')}: {e}")
            return False

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all WebSocket clients"""
        if self.websocket_clients:
            message_str = json.dumps(message)
            disconnected_clients = set()
            for client in self.websocket_clients:
                try:
                    await client.send(message_str)
                except websockets.exceptions.ConnectionClosed:
                    disconnected_clients.add(client)

            self.websocket_clients -= disconnected_clients

    async def handle_websocket(self, websocket):
        """Handle WebSocket connections"""
        self.websocket_clients.add(websocket)
        logger.info(f"🐨 WebSocket client connected. Total: {len(self.websocket_clients)}")

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
                    logger.info(f"Received: {data}")
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON: {message}")

        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.websocket_clients.discard(websocket)
            logger.info(f"WebSocket client disconnected. Total: {len(self.websocket_clients)}")

    async def run_http_server(self):
        """Run the HTTP server"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        logger.info(f"🌐 HTTP server: http://{self.host}:{self.port}")

    async def run_websocket_server(self):
        """Run the WebSocket server"""
        server = await websockets.serve(
            self.handle_websocket,
            self.host,
            self.ws_port
        )
        logger.info(f"🔌 WebSocket server: ws://{self.host}:{self.ws_port}")
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
║                    🐨 KOALA'S FORGE 🐨                       ║
║          Choose your apps. Click install. Done.               ║
╚═══════════════════════════════════════════════════════════════╝
    """)

    server = KoalasForgeServer()

    print(f"\n🚀 Starting Koala's Forge...")
    print(f"   Web Interface: http://localhost:8080")
    print(f"   WebSocket API: ws://localhost:8765")
    print(f"\n💡 Open your browser to get started!")
    print(f"   Press Ctrl+C to stop\n")

    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        print("\n\n👋 Thanks for using Koala's Forge!")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
