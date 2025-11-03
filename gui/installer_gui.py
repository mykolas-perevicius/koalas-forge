#!/usr/bin/env python3
"""
Speedy App Installer - GUI Interface
A modern, user-friendly interface for the system setup installer
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import threading
import queue
import json
import os
import sys
from pathlib import Path
import yaml
import time
from datetime import datetime

class InstallerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 Speedy App Installer")
        self.root.geometry("1000x700")

        # Set theme colors
        self.bg_color = "#1e1e1e"
        self.fg_color = "#ffffff"
        self.accent_color = "#007ACC"
        self.success_color = "#4CAF50"
        self.error_color = "#f44336"
        self.warning_color = "#FFC107"

        self.root.configure(bg=self.bg_color)

        # Installation state
        self.installation_running = False
        self.selected_apps = {}
        self.install_process = None
        self.output_queue = queue.Queue()

        # Load configuration
        self.load_config()

        # Setup GUI
        self.setup_styles()
        self.create_widgets()
        self.detect_hardware()

        # Start output monitor
        self.monitor_output()

    def setup_styles(self):
        """Configure ttk styles for modern look"""
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Configure colors
        self.style.configure("Title.TLabel",
                           background=self.bg_color,
                           foreground=self.fg_color,
                           font=('Helvetica', 24, 'bold'))

        self.style.configure("Heading.TLabel",
                           background=self.bg_color,
                           foreground=self.fg_color,
                           font=('Helvetica', 14, 'bold'))

        self.style.configure("Custom.TButton",
                           background=self.accent_color,
                           foreground=self.fg_color,
                           font=('Helvetica', 11),
                           relief="flat")

        self.style.map("Custom.TButton",
                      background=[('active', '#005a9e')])

        self.style.configure("Success.TButton",
                           background=self.success_color)

        self.style.configure("Custom.TFrame",
                           background=self.bg_color)

        self.style.configure("Custom.TCheckbutton",
                           background=self.bg_color,
                           foreground=self.fg_color,
                           font=('Helvetica', 10))

        self.style.configure("Custom.Horizontal.TProgressbar",
                           background=self.accent_color,
                           troughcolor='#333333')

    def create_widgets(self):
        """Create all GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, style="Custom.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Title
        title_label = ttk.Label(main_frame, text="🚀 Speedy App Installer",
                               style="Title.TLabel")
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # Left panel - Installation modes
        left_panel = ttk.Frame(main_frame, style="Custom.TFrame")
        left_panel.grid(row=1, column=0, sticky="nsew", padx=(0, 10))

        modes_label = ttk.Label(left_panel, text="Installation Mode",
                               style="Heading.TLabel")
        modes_label.pack(pady=(0, 10))

        # Installation mode buttons
        self.install_mode = tk.StringVar(value="full")

        modes = [
            ("🎯 Full Installation", "full", "Complete setup with all tools"),
            ("🤖 AI/ML Tools Only", "ai", "Ollama, LLMs, and ML frameworks"),
            ("💻 Development Only", "dev", "IDEs, languages, and dev tools"),
            ("⚡ Minimal Setup", "minimal", "Essential tools only"),
            ("🎨 Custom Selection", "custom", "Choose individual packages")
        ]

        for text, value, tooltip in modes:
            rb = tk.Radiobutton(left_panel, text=text, variable=self.install_mode,
                              value=value, bg=self.bg_color, fg=self.fg_color,
                              font=('Helvetica', 11), selectcolor=self.bg_color,
                              activebackground=self.bg_color,
                              activeforeground=self.accent_color,
                              command=self.on_mode_change)
            rb.pack(anchor="w", pady=5)

            # Add tooltip
            self.create_tooltip(rb, tooltip)

        # System info panel
        info_frame = ttk.LabelFrame(left_panel, text="System Information",
                                   style="Custom.TFrame")
        info_frame.pack(fill=tk.BOTH, expand=True, pady=20)

        self.info_text = tk.Text(info_frame, height=8, width=30,
                                bg="#2b2b2b", fg=self.fg_color,
                                font=('Courier', 9))
        self.info_text.pack(padx=5, pady=5)

        # Center panel - Package selection (for custom mode)
        self.center_panel = ttk.Frame(main_frame, style="Custom.TFrame")
        self.center_panel.grid(row=1, column=1, sticky="nsew", padx=10)

        packages_label = ttk.Label(self.center_panel, text="Available Packages",
                                  style="Heading.TLabel")
        packages_label.pack(pady=(0, 10))

        # Package selection with scrollbar
        list_frame = ttk.Frame(self.center_panel)
        list_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.packages_canvas = tk.Canvas(list_frame, bg="#2b2b2b",
                                        yscrollcommand=scrollbar.set)
        self.packages_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.packages_canvas.yview)

        self.packages_frame = ttk.Frame(self.packages_canvas, style="Custom.TFrame")
        self.packages_canvas.create_window((0, 0), window=self.packages_frame,
                                          anchor="nw")

        # Initially hide custom selection
        self.center_panel.grid_remove()

        # Right panel - Output and controls
        right_panel = ttk.Frame(main_frame, style="Custom.TFrame")
        right_panel.grid(row=1, column=2, sticky="nsew")

        output_label = ttk.Label(right_panel, text="Installation Output",
                               style="Heading.TLabel")
        output_label.pack(pady=(0, 10))

        # Output text area
        self.output_text = scrolledtext.ScrolledText(right_panel, height=20,
                                                    width=50, bg="#2b2b2b",
                                                    fg=self.fg_color,
                                                    font=('Courier', 9))
        self.output_text.pack(fill=tk.BOTH, expand=True)

        # Progress bar
        self.progress = ttk.Progressbar(right_panel, mode='indeterminate',
                                       style="Custom.Horizontal.TProgressbar")
        self.progress.pack(fill=tk.X, pady=10)

        # Control buttons
        button_frame = ttk.Frame(right_panel, style="Custom.TFrame")
        button_frame.pack(fill=tk.X, pady=10)

        self.install_btn = ttk.Button(button_frame, text="🚀 Start Installation",
                                     command=self.start_installation,
                                     style="Custom.TButton")
        self.install_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(button_frame, text="⏹ Stop",
                                  command=self.stop_installation,
                                  style="Custom.TButton", state="disabled")
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        self.test_btn = ttk.Button(button_frame, text="🧪 Run Tests",
                                  command=self.run_tests,
                                  style="Custom.TButton")
        self.test_btn.pack(side=tk.LEFT, padx=5)

        # Status bar
        self.status_var = tk.StringVar(value="Ready to install")
        status_bar = ttk.Label(self.root, textvariable=self.status_var,
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Configure grid weights
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

    def load_config(self):
        """Load application configuration from YAML"""
        try:
            config_path = Path(__file__).parent.parent / "apps.yaml"
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
                self.populate_packages()
        except Exception as e:
            self.config = {"apps": {}}
            self.log_output(f"Warning: Could not load config: {e}\n", "warning")

    def populate_packages(self):
        """Populate the package selection list"""
        row = 0
        for category, apps in self.config.get("apps", {}).items():
            # Category header
            cat_label = tk.Label(self.packages_frame, text=category.replace("_", " ").title(),
                               bg=self.bg_color, fg=self.accent_color,
                               font=('Helvetica', 11, 'bold'))
            cat_label.grid(row=row, column=0, columnspan=2, sticky="w", pady=(10, 5))
            row += 1

            # Apps in category
            for app in apps:
                if isinstance(app, dict) and 'name' in app:
                    var = tk.BooleanVar(value=True)
                    cb = tk.Checkbutton(self.packages_frame, text=app['name'],
                                       variable=var, bg="#2b2b2b", fg=self.fg_color,
                                       selectcolor="#2b2b2b", font=('Helvetica', 10))
                    cb.grid(row=row, column=0, sticky="w", padx=(20, 0))

                    # Store reference
                    self.selected_apps[app['name']] = var

                    # Add description if available
                    if 'notes' in app:
                        desc = tk.Label(self.packages_frame, text=app['notes'],
                                      bg="#2b2b2b", fg="#888888",
                                      font=('Helvetica', 9))
                        desc.grid(row=row, column=1, sticky="w", padx=(10, 0))

                    row += 1

        # Update canvas scroll region
        self.packages_frame.update_idletasks()
        self.packages_canvas.configure(scrollregion=self.packages_canvas.bbox("all"))

    def on_mode_change(self):
        """Handle installation mode change"""
        if self.install_mode.get() == "custom":
            self.center_panel.grid()
        else:
            self.center_panel.grid_remove()

    def detect_hardware(self):
        """Detect and display system hardware"""
        def detect():
            try:
                script_path = Path(__file__).parent.parent / "scripts" / "detect_hardware.sh"
                result = subprocess.run([str(script_path)], capture_output=True,
                                      text=True, timeout=5)

                # Parse hardware info
                info = "System Detection:\n" + "="*25 + "\n"

                # Get system info
                if sys.platform == "darwin":
                    cpu_info = subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"],
                                            capture_output=True, text=True).stdout.strip()
                    mem_info = subprocess.run(["sysctl", "-n", "hw.memsize"],
                                            capture_output=True, text=True).stdout.strip()
                    mem_gb = int(mem_info) / (1024**3) if mem_info else 0

                    info += f"OS: macOS {subprocess.run(['sw_vers', '-productVersion'], capture_output=True, text=True).stdout.strip()}\n"
                    info += f"CPU: {cpu_info}\n"
                    info += f"RAM: {mem_gb:.1f} GB\n"
                    info += f"Arch: {subprocess.run(['uname', '-m'], capture_output=True, text=True).stdout.strip()}\n"

                self.info_text.delete(1.0, tk.END)
                self.info_text.insert(tk.END, info)

            except Exception as e:
                self.info_text.insert(tk.END, f"Detection failed: {e}\n")

        # Run in background
        thread = threading.Thread(target=detect, daemon=True)
        thread.start()

    def log_output(self, text, level="info"):
        """Add text to output with color coding"""
        self.output_text.insert(tk.END, text)

        # Color code based on level
        if level == "error":
            # Color last line red
            self.output_text.tag_add("error", "end-2c linestart", "end-1c")
            self.output_text.tag_config("error", foreground=self.error_color)
        elif level == "success":
            self.output_text.tag_add("success", "end-2c linestart", "end-1c")
            self.output_text.tag_config("success", foreground=self.success_color)
        elif level == "warning":
            self.output_text.tag_add("warning", "end-2c linestart", "end-1c")
            self.output_text.tag_config("warning", foreground=self.warning_color)

        self.output_text.see(tk.END)

    def start_installation(self):
        """Start the installation process"""
        if self.installation_running:
            messagebox.showwarning("Installation Running",
                                 "An installation is already in progress!")
            return

        # Confirm
        mode = self.install_mode.get()
        if not messagebox.askyesno("Confirm Installation",
                                  f"Start {mode} installation?\n\nThis may take 30-45 minutes."):
            return

        self.installation_running = True
        self.install_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.progress.start(10)

        # Clear output
        self.output_text.delete(1.0, tk.END)
        self.log_output("Starting installation...\n", "info")
        self.status_var.set(f"Installing in {mode} mode...")

        # Run installation in background thread
        thread = threading.Thread(target=self.run_installation, daemon=True)
        thread.start()

    def run_installation(self):
        """Execute the installation script"""
        try:
            script_path = Path(__file__).parent.parent / "install.sh"

            # Build command based on mode
            cmd = [str(script_path)]
            mode = self.install_mode.get()

            if mode != "custom":
                cmd.append(f"--{mode}")
            else:
                # For custom mode, we'd need to pass selected packages
                # This would require modifying install.sh to accept package lists
                cmd.append("--custom")
                # Add selected packages logic here

            # Run installation
            self.install_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # Read output line by line
            for line in iter(self.install_process.stdout.readline, ''):
                if not line:
                    break

                # Queue output for GUI thread
                self.output_queue.put(('output', line))

                # Check for errors or success
                if "error" in line.lower() or "failed" in line.lower():
                    self.output_queue.put(('status', 'error'))
                elif "✅" in line or "success" in line.lower():
                    self.output_queue.put(('status', 'success'))

            self.install_process.wait()

            # Installation complete
            if self.install_process.returncode == 0:
                self.output_queue.put(('complete', 'success'))
            else:
                self.output_queue.put(('complete', 'error'))

        except Exception as e:
            self.output_queue.put(('error', str(e)))
        finally:
            self.installation_running = False

    def stop_installation(self):
        """Stop the installation process"""
        if self.install_process:
            self.install_process.terminate()
            self.log_output("\nInstallation stopped by user.\n", "warning")
            self.status_var.set("Installation cancelled")
            self.installation_running = False
            self.install_btn.config(state="normal")
            self.stop_btn.config(state="disabled")
            self.progress.stop()

    def run_tests(self):
        """Run the test suite"""
        self.output_text.delete(1.0, tk.END)
        self.log_output("Running test suite...\n", "info")

        def run():
            try:
                test_path = Path(__file__).parent.parent / "test_install.sh"
                result = subprocess.run([str(test_path)], capture_output=True,
                                      text=True, timeout=30)

                self.output_queue.put(('output', result.stdout))
                if result.returncode == 0:
                    self.output_queue.put(('output', "\n✅ All tests passed!\n"))
                else:
                    self.output_queue.put(('output', f"\n❌ Tests failed with code {result.returncode}\n"))

            except Exception as e:
                self.output_queue.put(('error', f"Test error: {e}\n"))

        thread = threading.Thread(target=run, daemon=True)
        thread.start()

    def monitor_output(self):
        """Monitor output queue and update GUI"""
        try:
            while True:
                msg_type, content = self.output_queue.get_nowait()

                if msg_type == 'output':
                    self.log_output(content)
                elif msg_type == 'error':
                    self.log_output(f"❌ Error: {content}\n", "error")
                elif msg_type == 'status':
                    if content == 'error':
                        # Just change color, don't add text
                        pass
                    elif content == 'success':
                        pass
                elif msg_type == 'complete':
                    self.progress.stop()
                    self.install_btn.config(state="normal")
                    self.stop_btn.config(state="disabled")

                    if content == 'success':
                        self.log_output("\n✅ Installation completed successfully!\n", "success")
                        self.status_var.set("Installation completed successfully")
                        messagebox.showinfo("Success", "Installation completed successfully!")
                    else:
                        self.log_output("\n❌ Installation failed!\n", "error")
                        self.status_var.set("Installation failed")
                        messagebox.showerror("Error", "Installation failed. Check the output for details.")

                    self.installation_running = False

        except queue.Empty:
            pass

        # Schedule next check
        self.root.after(100, self.monitor_output)

    def create_tooltip(self, widget, text):
        """Create a tooltip for a widget"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = tk.Label(tooltip, text=text, background="#333333",
                           foreground="white", relief=tk.SOLID, borderwidth=1,
                           font=('Helvetica', 9))
            label.pack()
            widget.tooltip = tooltip

        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

def main():
    """Main entry point"""
    root = tk.Tk()
    app = InstallerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()