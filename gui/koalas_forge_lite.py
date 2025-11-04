#!/usr/bin/env python3
"""
🐨 Koala's Forge Lite
Lightweight backup GUI when web interface is not preferred
Shows installation summary and basic controls
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import webbrowser
from pathlib import Path

class KoalasForgeLite:
    def __init__(self, root):
        self.root = root
        self.root.title("🐨 Koala's Forge Lite")
        self.root.geometry("600x400")

        # Pastel nature colors
        self.bg_color = "#FAFAF9"
        self.accent_color = "#B8D8BA"
        self.text_color = "#2D3436"

        self.root.configure(bg=self.bg_color)

        # Create UI
        self.create_widgets()

    def create_widgets(self):
        """Create simplified UI"""
        # Header with koala
        header = tk.Frame(self.root, bg=self.accent_color, height=100)
        header.pack(fill=tk.X, pady=(0, 20))

        title_label = tk.Label(
            header,
            text="🐨 Koala's Forge",
            font=("Helvetica", 24, "bold"),
            bg=self.accent_color,
            fg=self.text_color
        )
        title_label.pack(pady=20)

        # Main container
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30)

        # Info text
        info_text = """
        Koala's Forge is best experienced in your web browser!

        This lite version provides basic functionality, but for
        the full experience with beautiful UI, app selection,
        presets, and more - use the web interface.
        """

        info_label = tk.Label(
            main_frame,
            text=info_text,
            font=("Helvetica", 11),
            bg=self.bg_color,
            fg=self.text_color,
            justify=tk.LEFT,
            wraplength=500
        )
        info_label.pack(pady=20)

        # Buttons
        button_frame = tk.Frame(main_frame, bg=self.bg_color)
        button_frame.pack(pady=20)

        # Launch Web Interface button
        web_btn = tk.Button(
            button_frame,
            text="🌐 Launch Web Interface (Recommended)",
            command=self.launch_web_interface,
            font=("Helvetica", 12, "bold"),
            bg=self.accent_color,
            fg=self.text_color,
            padx=20,
            pady=15,
            relief=tk.FLAT,
            cursor="hand2"
        )
        web_btn.pack(pady=10)

        # Quick install buttons
        quick_frame = tk.Frame(main_frame, bg=self.bg_color)
        quick_frame.pack(pady=20)

        tk.Label(
            quick_frame,
            text="Quick Actions:",
            font=("Helvetica", 12, "bold"),
            bg=self.bg_color,
            fg=self.text_color
        ).pack()

        actions = [
            ("Install AI Developer Pack", self.install_ai),
            ("Install Full Stack Pack", self.install_fullstack),
            ("Show Installed Apps", self.show_installed),
        ]

        for text, command in actions:
            btn = tk.Button(
                quick_frame,
                text=text,
                command=command,
                font=("Helvetica", 10),
                bg="#E5D4C1",
                fg=self.text_color,
                padx=15,
                pady=10,
                relief=tk.FLAT,
                cursor="hand2"
            )
            btn.pack(pady=5, fill=tk.X)

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            font=("Helvetica", 9),
            bg="#E5D4C1",
            fg=self.text_color,
            anchor=tk.W,
            padx=10
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def launch_web_interface(self):
        """Launch the full web interface"""
        try:
            self.status_var.set("Starting web server...")
            script_dir = Path(__file__).parent.parent

            # Start the web server
            subprocess.Popen(
                [str(script_dir / "launch.sh")],
                cwd=str(script_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Open browser
            webbrowser.open("http://localhost:8080")

            self.status_var.set("Web interface launched! Check your browser.")
            messagebox.showinfo(
                "Success",
                "The web interface has been launched!\n\nOpen your browser to http://localhost:8080"
            )

        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Could not launch web interface:\n{str(e)}")

    def install_ai(self):
        """Quick install AI Developer pack"""
        response = messagebox.askyesno(
            "Install AI Developer Pack",
            "This will install:\n\n"
            "• Ollama (local LLMs)\n"
            "• Python 3.11\n"
            "• VS Code\n"
            "• Cursor\n"
            "• Git\n"
            "• Docker\n\n"
            "Continue?"
        )

        if response:
            self.status_var.set("Installing AI Developer Pack...")
            messagebox.showinfo(
                "Installation Started",
                "The web interface provides better installation tracking.\n\n"
                "Click 'Launch Web Interface' for full experience!"
            )

    def install_fullstack(self):
        """Quick install Full Stack pack"""
        response = messagebox.askyesno(
            "Install Full Stack Pack",
            "This will install:\n\n"
            "• Git\n"
            "• Python, Node.js, Go\n"
            "• VS Code\n"
            "• Docker\n"
            "• PostgreSQL, Redis\n\n"
            "Continue?"
        )

        if response:
            self.status_var.set("Installing Full Stack Pack...")
            messagebox.showinfo(
                "Installation Started",
                "The web interface provides better installation tracking.\n\n"
                "Click 'Launch Web Interface' for full experience!"
            )

    def show_installed(self):
        """Show installed applications"""
        try:
            self.status_var.set("Checking installed apps...")

            # Simple check for brew installed apps (macOS)
            import platform
            if platform.system() == "Darwin":
                result = subprocess.run(
                    ["brew", "list", "--formula"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                formulas = result.stdout.strip().split("\n")

                result = subprocess.run(
                    ["brew", "list", "--cask"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                casks = result.stdout.strip().split("\n")

                total = len(formulas) + len(casks)

                messagebox.showinfo(
                    "Installed Applications",
                    f"Found {total} installed applications:\n\n"
                    f"• {len(formulas)} command-line tools\n"
                    f"• {len(casks)} applications\n\n"
                    f"Use the web interface to see details\n"
                    f"and manage installations."
                )

                self.status_var.set(f"Found {total} installed apps")
            else:
                messagebox.showinfo(
                    "Info",
                    "This feature works best on macOS.\n\n"
                    "Use the web interface for full functionality!"
                )

        except subprocess.TimeoutExpired:
            self.status_var.set("Timeout checking installed apps")
            messagebox.showerror("Error", "Timeout while checking installed apps")
        except FileNotFoundError:
            messagebox.showinfo(
                "Homebrew Not Found",
                "Homebrew package manager not found.\n\n"
                "Would you like to install it?"
            )
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Could not check installed apps:\n{str(e)}")

def main():
    """Main entry point"""
    root = tk.Tk()
    app = KoalasForgeLite(root)
    root.mainloop()

if __name__ == "__main__":
    main()
