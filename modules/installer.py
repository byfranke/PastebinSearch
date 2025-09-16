"""
Installer and Uninstaller for PastebinSearch Tool
Handles installation, dependency management, and system setup
"""

import os
import sys
import subprocess
import shutil
import json
import platform
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import tempfile
import urllib.request

class ToolInstaller:
    """Handles installation and uninstallation of PastebinSearch"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.tool_name = "PastebinSearch"
        self.version = "3.1.0"
        self.python_min_version = (3, 8)
        
        # Installation paths
        if self.system == "windows":
            self.install_base = Path.home() / "AppData" / "Local" / self.tool_name
            self.bin_path = self.install_base / "bin"
            self.scripts_path = Path.home() / "AppData" / "Local" / "Microsoft" / "WindowsApps"
        else:
            self.install_base = Path.home() / ".local" / "share" / self.tool_name.lower()
            self.bin_path = Path.home() / ".local" / "bin"
            self.scripts_path = self.bin_path
        
        # Configuration
        self.config_path = Path.home() / f".{self.tool_name.lower()}"
        
        # Requirements
        self.core_requirements = [
            "rich>=13.7.0",
            "aiohttp>=3.9.0",
            "beautifulsoup4>=4.12.0",
            "requests>=2.31.0",
            "python-dotenv>=1.0.0",
            "asyncio-throttle>=1.0.2",
            "loguru>=0.7.2",
            "pydantic>=2.4.0",
            "colorama>=0.4.6"
        ]
        
        self.optional_requirements = [
            ("playwright>=1.35.0", "Browser automation with Playwright"),
            ("selenium>=4.10.0", "Browser automation with Selenium"),
            ("pandas>=1.5.0", "Advanced data export features"),
            ("cryptography>=3.4.0", "Enhanced security features")
        ]
    
    async def install(self):
        """Install the tool"""
        print(f"🚀 Installing {self.tool_name} v{self.version}...")
        
        try:
            # Check system requirements
            if not self.check_system_requirements():
                return False
            
            # Create directories
            self.create_directories()
            
            # Install Python dependencies
            if not await self.install_dependencies():
                return False
            
            # Copy tool files
            if not self.copy_tool_files():
                return False
            
            # Create scripts and shortcuts
            if not self.create_scripts():
                return False
            
            # Setup configuration
            self.setup_configuration()
            
            # Install optional components
            await self.install_optional_components()
            
            # Final setup
            self.finalize_installation()
            
            self.show_installation_success()
            return True
            
        except Exception as e:
            print(f"❌ Installation failed: {e}")
            # Show diagnostic information
            await self.show_diagnostic_info()
            return False
    
    def check_system_requirements(self) -> bool:
        """Check if system meets requirements"""
        print("🔍 Checking system requirements...")
        
        # Check Python version
        current_version = sys.version_info[:2]
        if current_version < self.python_min_version:
            print(f"❌ Python {self.python_min_version[0]}.{self.python_min_version[1]}+ required. Current: {current_version[0]}.{current_version[1]}")
            return False
        
        print(f"✅ Python {current_version[0]}.{current_version[1]} - OK")
        
        # Check pip
        try:
            subprocess.run([sys.executable, "-m", "pip", "--version"], 
                         check=True, capture_output=True)
            print("✅ pip - OK")
        except subprocess.CalledProcessError:
            print("❌ pip not found or not working")
            return False
        
        # Check internet connection for package installation
        try:
            urllib.request.urlopen('https://pypi.org', timeout=5)
            print("✅ Internet connection - OK")
        except:
            print("⚠️  Limited internet connection - some features may not work")
        
        # Check available disk space (estimate 100MB needed)
        free_space = shutil.disk_usage(Path.home()).free
        required_space = 100 * 1024 * 1024  # 100MB
        
        if free_space < required_space:
            print(f"❌ Insufficient disk space. Required: 100MB, Available: {free_space // (1024*1024)}MB")
            return False
        
        print("✅ Disk space - OK")
        return True
    
    def create_directories(self):
        """Create necessary directories"""
        print("📁 Creating directories...")
        
        directories = [
            self.install_base,
            self.bin_path,
            self.config_path,
            self.install_base / "modules",
            self.install_base / "config",
            self.install_base / "logs",
            self.install_base / "templates",
            self.install_base / "assets"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"  ✅ {directory}")
    
    async def install_dependencies(self) -> bool:
        """Install Python dependencies"""
        print("📦 Installing Python dependencies...")
        
        try:
            # Create temporary requirements file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                for req in self.core_requirements:
                    f.write(f"{req}\n")
                temp_req_file = f.name
            
            # Try different installation methods based on system
            install_commands = [
                # Method 1: User installation (recommended)
                [sys.executable, "-m", "pip", "install", "-r", temp_req_file, "--user"],
                # Method 2: Virtual environment friendly
                [sys.executable, "-m", "pip", "install", "-r", temp_req_file, "--user", "--break-system-packages"],
                # Method 3: System package manager hint
                ["pip3", "install", "-r", temp_req_file, "--user"]
            ]
            
            success = False
            last_error = None
            
            for i, cmd in enumerate(install_commands, 1):
                try:
                    print(f"  📦 Trying installation method {i}...")
                    
                    process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        universal_newlines=True,
                        bufsize=1
                    )
                    
                    # Show installation progress
                    while True:
                        output = process.stdout.readline()
                        if output == '' and process.poll() is not None:
                            break
                        if output and ("Collecting" in output or "Installing" in output):
                            print(f"    📦 {output.strip()}")
                    
                    if process.returncode == 0:
                        success = True
                        print(f"  ✅ Dependencies installed successfully using method {i}")
                        break
                    else:
                        last_error = f"Method {i} failed with return code {process.returncode}"
                        
                except FileNotFoundError:
                    last_error = f"Method {i}: Command not found"
                    continue
                except Exception as e:
                    last_error = f"Method {i}: {str(e)}"
                    continue
            
            # Clean up
            os.unlink(temp_req_file)
            
            if not success:
                print("❌ All installation methods failed!")
                print("\n🔧 Alternative installation methods:")
                print("  1. Create virtual environment:")
                print("     python3 -m venv pastebinsearch_env")
                print("     source pastebinsearch_env/bin/activate")
                print("     pip install -r requirements.txt")
                print("")
                print("  2. Use system package manager:")
                print("     sudo apt install python3-rich python3-aiohttp python3-bs4")
                print("     sudo apt install python3-requests python3-pydantic")
                print("")
                print("  3. Use pipx (if available):")
                print("     pipx install --spec . pastebinsearch")
                print("")
                print(f"  Last error: {last_error}")
                
                return False
            
            return True
                
        except Exception as e:
            print(f"❌ Dependency installation error: {e}")
            return False
    
    def copy_tool_files(self) -> bool:
        """Copy tool files to installation directory"""
        print("📋 Copying tool files...")
        
        try:
            # Get current directory (where the tool is being run from)
            source_dir = Path(__file__).parent.parent
            
            # Files to copy
            files_to_copy = [
                ("pastebinsearch.py", self.install_base),
                ("requirements.txt", self.install_base),
                ("README.md", self.install_base),
                ("modules/", self.install_base),
                ("config/", self.install_base),
                ("templates/", self.install_base),
                ("assets/", self.install_base)
            ]
            
            for src_path, dest_dir in files_to_copy:
                src = source_dir / src_path
                dest = dest_dir / src_path
                
                if src.is_file():
                    shutil.copy2(src, dest)
                    print(f"  ✅ Copied {src.name}")
                elif src.is_dir():
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(src, dest)
                    print(f"  ✅ Copied directory {src.name}/")
                else:
                    print(f"  ⚠️  Skipped missing {src_path}")
            
            return True
            
        except Exception as e:
            print(f"❌ File copy error: {e}")
            return False
    
    def create_scripts(self) -> bool:
        """Create executable scripts and shortcuts"""
        print("🔗 Creating scripts and shortcuts...")
        
        try:
            if self.system == "windows":
                return self.create_windows_scripts()
            else:
                return self.create_unix_scripts()
        except Exception as e:
            print(f"❌ Script creation error: {e}")
            return False
    
    def create_windows_scripts(self) -> bool:
        """Create Windows batch scripts"""
        try:
            # Create batch script
            batch_content = f"""@echo off
REM PastebinSearch v3.0 Windows Launcher
REM Created by installer

set PYTHONPATH={self.install_base};%PYTHONPATH%
cd /d "{self.install_base}"
"{sys.executable}" pastebinsearch.py %*
"""
            
            batch_file = self.bin_path / "pastebinsearch.bat"
            with open(batch_file, 'w') as f:
                f.write(batch_content)
            
            print(f"  ✅ Created {batch_file}")
            
            # Create PowerShell script
            ps_content = f"""#!/usr/bin/env pwsh
# PastebinSearch v3.0 PowerShell Launcher
# Created by installer

$env:PYTHONPATH = "{self.install_base};$env:PYTHONPATH"
Set-Location "{self.install_base}"
& "{sys.executable}" pastebinsearch.py @args
"""
            
            ps_file = self.bin_path / "pastebinsearch.ps1"
            with open(ps_file, 'w') as f:
                f.write(ps_content)
            
            print(f"  ✅ Created {ps_file}")
            
            # Create simple executable wrapper
            exe_content = f"""@echo off
REM PastebinSearch Launcher
"{sys.executable}" "{self.install_base}\\pastebinsearch.py" %*
"""
            
            exe_file = self.bin_path / "pastebinsearch.cmd"
            with open(exe_file, 'w') as f:
                f.write(exe_content)
            
            print(f"  ✅ Created {exe_file}")
            
            # Try to add to PATH
            if self.add_to_windows_path():
                print("  🎯 You can now use 'pastebinsearch' from anywhere!")
            
            return True
            
        except Exception as e:
            print(f"❌ Windows script creation failed: {e}")
            return False
    
    def create_unix_scripts(self) -> bool:
        """Create Unix shell scripts"""
        try:
            # Create main shell script
            script_content = f"""#!/bin/bash
# PastebinSearch v3.0 Unix Launcher
# Created by installer

export PYTHONPATH="{self.install_base}:$PYTHONPATH"
cd "{self.install_base}"
exec "{sys.executable}" pastebinsearch.py "$@"
"""
            
            script_file = self.bin_path / "pastebinsearch"
            with open(script_file, 'w') as f:
                f.write(script_content)
            
            # Make executable
            os.chmod(script_file, 0o755)
            print(f"  ✅ Created {script_file}")
            
            # Try to create system-wide link if we have permissions
            try:
                system_bin = Path("/usr/local/bin/pastebinsearch")
                if not system_bin.exists() and os.access("/usr/local/bin", os.W_OK):
                    system_bin.symlink_to(script_file)
                    print(f"  ✅ Created system link: {system_bin}")
                elif system_bin.exists():
                    print(f"  ℹ️  System link already exists: {system_bin}")
            except (PermissionError, OSError):
                print(f"  ℹ️  Could not create system link (requires sudo)")
            
            # Try to add to PATH
            self.add_to_unix_path()
            
            return True
            
        except Exception as e:
            print(f"❌ Unix script creation failed: {e}")
            return False
    
    def add_to_windows_path(self):
        """Try to add installation to Windows PATH"""
        try:
            import winreg
            
            # Try to add to user PATH (doesn't require admin)
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_ALL_ACCESS) as key:
                    current_path = winreg.QueryValueEx(key, "PATH")[0]
                    
                    if str(self.bin_path) not in current_path:
                        new_path = f"{current_path};{self.bin_path}"
                        winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
                        print(f"  ✅ Added to user PATH: {self.bin_path}")
                        print("  ℹ️  Please restart your terminal/command prompt")
                        return True
                    else:
                        print(f"  ✅ Already in PATH: {self.bin_path}")
                        return True
                        
            except FileNotFoundError:
                # PATH key doesn't exist, create it
                with winreg.CreateKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
                    winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, str(self.bin_path))
                    print(f"  ✅ Created user PATH with: {self.bin_path}")
                    print("  ℹ️  Please restart your terminal/command prompt")
                    return True
                    
        except ImportError:
            # winreg not available (non-Windows)
            pass
        except Exception as e:
            print(f"  ⚠️  Could not modify PATH automatically: {e}")
        
        # Fallback: Show manual instructions
        print(f"  ℹ️  To use 'pastebinsearch' from anywhere, add to PATH manually:")
        print(f"     1. Open System Properties > Environment Variables")
        print(f"     2. Add to user PATH: {self.bin_path}")
        print(f"     3. Restart terminal/command prompt")
        return False
    
    def add_to_unix_path(self):
        """Try to add installation to Unix PATH"""
        try:
            # Check if bin path is already in PATH
            current_path = os.environ.get('PATH', '')
            if str(self.bin_path) not in current_path:
                print(f"  ℹ️  To use 'pastebinsearch' from anywhere, add to ~/.bashrc or ~/.zshrc:")
                print(f"     export PATH=\"{self.bin_path}:$PATH\"")
        except:
            pass
    
    def setup_configuration(self):
        """Setup initial configuration"""
        print("⚙️  Setting up configuration...")
        
        try:
            # Create default config
            default_config = {
                "version": self.version,
                "installation_path": str(self.install_base),
                "installed_date": self.get_current_timestamp(),
                "python_path": sys.executable,
                "system": self.system
            }
            
            config_file = self.config_path / "install.json"
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            
            print(f"  ✅ Configuration saved to {config_file}")
            
        except Exception as e:
            print(f"⚠️  Configuration setup warning: {e}")
    
    async def install_optional_components(self):
        """Install optional components interactively"""
        print("\n🔧 Optional Components:")
        
        for requirement, description in self.optional_requirements:
            try:
                choice = input(f"Install {description}? (y/N): ").strip().lower()
                if choice in ['y', 'yes']:
                    success, message = self.install_single_package(requirement)
                    
                    if success:
                        print(f"  ✅ {requirement} installed successfully")
                        print(f"    💡 {message}")
                    else:
                        print(f"  ❌ Failed to install {requirement}")
                        print(f"    ⚠️  {message}")
                        print(f"    💡 Try manually: pip install {requirement}")
                else:
                    print(f"  ⏭️  Skipped {requirement}")
                    
            except KeyboardInterrupt:
                print("\n⏹️  Installation cancelled by user")
                break
            except Exception as e:
                print(f"  ❌ Unexpected error with {requirement}: {e}")
    
    def get_install_command(self, requirement: str) -> list:
        """Get the appropriate pip install command based on environment"""
        base_cmd = [sys.executable, "-m", "pip", "install", requirement, "--no-cache-dir"]
        
        # Check if we're in a virtual environment
        in_venv = (hasattr(sys, 'real_prefix') or 
                  (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))
        
        if in_venv:
            # In virtual environment, don't use --user
            return base_cmd
        else:
            # Not in virtual environment, use --user for safety
            return base_cmd + ["--user"]
    
    def install_single_package(self, requirement: str) -> tuple[bool, str]:
        """Install a single package with multiple fallback strategies"""
        print(f"    🔄 Installing {requirement}...")
        
        strategies = []
        
        # Strategy 1: Appropriate method based on environment
        cmd1 = self.get_install_command(requirement)
        strategies.append((cmd1, "environment-appropriate"))
        
        # Strategy 2: Force global install (fallback)
        cmd2 = [sys.executable, "-m", "pip", "install", requirement, "--no-cache-dir"]
        strategies.append((cmd2, "global"))
        
        # Strategy 3: With break-system-packages (for newer systems)
        cmd3 = [sys.executable, "-m", "pip", "install", requirement, 
               "--no-cache-dir", "--break-system-packages"]
        strategies.append((cmd3, "system-packages"))
        
        for cmd, strategy_name in strategies:
            try:
                result = subprocess.run(cmd, check=True, capture_output=True, text=True)
                return True, f"Success via {strategy_name}"
            except subprocess.CalledProcessError as e:
                error_msg = e.stderr.strip()
                print(f"    ⚠️  {strategy_name} failed: {error_msg[:100]}...")
                continue
        
        return False, "All installation strategies failed"
    
    async def show_diagnostic_info(self):
        """Show diagnostic information for troubleshooting"""
        print("\n🔍 Diagnostic Information:")
        
        # Python version
        print(f"  🐍 Python: {sys.version}")
        
        # Pip version
        try:
            result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"  📦 Pip: {result.stdout.strip()}")
            else:
                print("  ❌ Pip not available")
        except:
            print("  ❌ Cannot check pip version")
        
        # System info
        print(f"  💻 System: {platform.system()} {platform.release()}")
        print(f"  🏗️  Architecture: {platform.architecture()[0]}")
        
        # Virtual environment check
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            print("  🐍 Virtual environment: Active")
        else:
            print("  🐍 Virtual environment: Not detected")
        
        # Check internet connectivity
        try:
            import urllib.request
            urllib.request.urlopen('https://pypi.org', timeout=10)
            print("  🌐 Internet: Connected")
        except:
            print("  ❌ Internet: Connection issues detected")
        
        print("\n💡 Troubleshooting tips:")
        print("  • Ensure you're in a virtual environment")
        print("  • Try: python -m pip install --upgrade pip")
        print("  • Check internet connection")
        print("  • For Kali Linux: sudo apt update && sudo apt install python3-pip")
        print("  • Some packages may require system dependencies")
    
    async def test_optional_dependencies(self):
        """Test installation of optional dependencies"""
        print(f"🧪 Testing Optional Dependencies for {self.tool_name}")
        print("=" * 50)
        
        # Show system info first
        await self.show_diagnostic_info()
        
        print("\n🔍 Testing optional packages...")
        
        for requirement, description in self.optional_requirements:
            package_name = requirement.split(">=")[0]
            print(f"\n📦 Testing {package_name} ({description}):")
            
            # Check if already installed
            if self.check_package_availability(package_name):
                print(f"  ✅ Already installed")
                continue
            
            # Test installation
            print(f"  🔄 Attempting installation...")
            
            success = False
            methods_tried = []
            
            # Method 1: Standard user install
            try:
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", 
                    requirement, "--user", "--no-cache-dir", "--dry-run"
                ], check=True, capture_output=True, text=True)
                print(f"  ✅ Standard install: Available")
                methods_tried.append("standard")
                success = True
            except subprocess.CalledProcessError as e:
                print(f"  ❌ Standard install: {e.stderr.strip()[:100]}...")
                methods_tried.append("standard (failed)")
            
            # Method 2: System packages
            if not success:
                try:
                    result = subprocess.run([
                        sys.executable, "-m", "pip", "install", 
                        requirement, "--break-system-packages", "--dry-run"
                    ], check=True, capture_output=True, text=True)
                    print(f"  ✅ System install: Available")
                    methods_tried.append("system")
                    success = True
                except subprocess.CalledProcessError as e:
                    print(f"  ❌ System install: {e.stderr.strip()[:100]}...")
                    methods_tried.append("system (failed)")
            
            if success:
                print(f"  💡 Recommendation: Package can be installed")
            else:
                print(f"  ⚠️  Package installation may have issues")
                
                # Show specific help for common packages
                if package_name == "cryptography":
                    print(f"    💡 Try: sudo apt install build-essential libssl-dev libffi-dev python3-dev")
                elif package_name == "playwright":
                    print(f"    💡 May need: pip install playwright && playwright install")
                elif package_name == "pandas":
                    print(f"    💡 Try: sudo apt install python3-pandas")
        
        print(f"\n📊 Test Summary:")
        print(f"  • Run this test before installation to identify issues")
        print(f"  • Install system dependencies as suggested")
        print(f"  • Use virtual environment for best results")
    
    def finalize_installation(self):
        """Finalize installation"""
        print("🏁 Finalizing installation...")
        
        try:
            # Create version file
            version_info = {
                "version": self.version,
                "install_date": self.get_current_timestamp(),
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "system": platform.system(),
                "architecture": platform.architecture()[0]
            }
            
            version_file = self.install_base / "VERSION"
            with open(version_file, 'w') as f:
                json.dump(version_info, f, indent=2)
            
            print("  ✅ Version information saved")
            
            # Create uninstaller script
            self.create_uninstaller()
            
        except Exception as e:
            print(f"⚠️  Finalization warning: {e}")
    
    def create_uninstaller(self):
        """Create uninstaller script"""
        try:
            uninstaller_content = f'''#!/usr/bin/env python3
"""
Uninstaller for {self.tool_name}
"""
import shutil
from pathlib import Path

def uninstall():
    print("🗑️  Uninstalling {self.tool_name}...")
    
    # Remove installation directory
    install_path = Path("{self.install_base}")
    if install_path.exists():
        shutil.rmtree(install_path)
        print(f"✅ Removed {{install_path}}")
    
    # Remove configuration
    config_path = Path("{self.config_path}")
    if config_path.exists():
        shutil.rmtree(config_path)
        print(f"✅ Removed {{config_path}}")
    
    # Remove scripts
    scripts_to_remove = [
        Path("{self.bin_path}/pastebinsearch"),
        Path("{self.bin_path}/pastebinsearch.bat"),
        Path("{self.bin_path}/pastebinsearch.ps1")
    ]
    
    for script in scripts_to_remove:
        if script.exists():
            script.unlink()
            print(f"✅ Removed {{script}}")
    
    print("✅ {self.tool_name} uninstalled successfully!")

if __name__ == "__main__":
    uninstall()
'''
            
            uninstaller_file = self.install_base / "uninstall.py"
            with open(uninstaller_file, 'w') as f:
                f.write(uninstaller_content)
            
            if self.system != "windows":
                os.chmod(uninstaller_file, 0o755)
            
            print(f"  ✅ Uninstaller created: {uninstaller_file}")
            
        except Exception as e:
            print(f"⚠️  Uninstaller creation warning: {e}")
    
    def show_installation_success(self):
        """Show installation success message"""
        success_message = f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                           🎉 INSTALLATION COMPLETE! 🎉                        ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  {self.tool_name} v{self.version} has been successfully installed!                      ║
║                                                                               ║
║  📍 Installation Directory: {str(self.install_base):<40}║
║  ⚙️  Configuration Directory: {str(self.config_path):<38}║
║                                                                               ║
║  🚀 GETTING STARTED:                                                          ║
║                                                                               ║
║  1. Run the tool:                                                             ║
║     • From installation directory:                                            ║
║       cd "{str(self.install_base):<58}"║
║       python pastebinsearch.py                                                ║
║                                                                               ║
║  2. Or use the created scripts:                                               ║
║     • Windows: pastebinsearch.bat                                             ║
║     • Unix: pastebinsearch                                                    ║
║                                                                               ║
║  3. For help:                                                                 ║
║     python pastebinsearch.py --help                                           ║
║                                                                               ║
║  📚 DOCUMENTATION:                                                            ║
║     Check README.md in the installation directory                             ║
║                                                                               ║
║  🗑️  UNINSTALL:                                                               ║
║     python uninstall.py (in installation directory)                          ║
║                                                                               ║
║  ⚠️  IMPORTANT:                                                                ║
║     • Use this tool responsibly and ethically                                 ║
║     • Respect robots.txt and terms of service                                 ║
║     • For security research purposes only                                     ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝

🎯 Quick Start: python pastebinsearch.py --search "your search term"

Happy searching! 🔍
        """
        
        print(success_message)
    
    async def uninstall(self):
        """Uninstall the tool"""
        print(f"🗑️  Uninstalling {self.tool_name}...")
        
        try:
            # Confirm uninstallation
            confirmation = input("Are you sure you want to uninstall? (y/N): ").strip().lower()
            if confirmation not in ['y', 'yes']:
                print("⏹️  Uninstallation cancelled")
                return False
            
            # Remove installation directory
            if self.install_base.exists():
                shutil.rmtree(self.install_base)
                print(f"✅ Removed {self.install_base}")
            
            # Remove configuration
            if self.config_path.exists():
                shutil.rmtree(self.config_path)
                print(f"✅ Removed {self.config_path}")
            
            # Remove scripts
            scripts_to_remove = [
                self.bin_path / "pastebinsearch",
                self.bin_path / "pastebinsearch.bat",
                self.bin_path / "pastebinsearch.ps1"
            ]
            
            for script in scripts_to_remove:
                if script.exists():
                    script.unlink()
                    print(f"✅ Removed {script}")
            
            print(f"✅ {self.tool_name} uninstalled successfully!")
            print("Thank you for using PastebinSearch! 👋")
            
            return True
            
        except Exception as e:
            print(f"❌ Uninstallation error: {e}")
            return False
    
    def get_current_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def check_installation(self) -> Dict[str, Any]:
        """Check if tool is already installed"""
        try:
            if not self.install_base.exists():
                return {"installed": False}
            
            version_file = self.install_base / "VERSION"
            if version_file.exists():
                with open(version_file, 'r') as f:
                    version_info = json.load(f)
                
                return {
                    "installed": True,
                    "version": version_info.get("version", "unknown"),
                    "install_date": version_info.get("install_date", "unknown"),
                    "path": str(self.install_base)
                }
            
            return {"installed": True, "version": "unknown"}
            
        except Exception:
            return {"installed": False}
    
    def update_tool(self):
        """Update the tool to latest version (compatible with v2.0 users)"""
        print("🔄 PastebinSearch - Checking for updates...")
        
        try:
            import requests
            import tempfile
            import zipfile
            import shutil
            
            # GitHub API to get latest release
            api_url = "https://api.github.com/repos/byFranke/PastebinSearch/releases/latest"
            
            try:
                response = requests.get(api_url, timeout=30)
                if response.status_code == 200:
                    release_data = response.json()
                    latest_version = release_data["tag_name"].replace("v", "")
                    download_url = f"https://github.com/byFranke/PastebinSearch/archive/refs/tags/v{latest_version}.zip"
                    
                    print(f"📦 Latest version available: v{latest_version}")
                    print(f"💾 Current version: v3.1.0")
                    
                    # For now, show migration info for v2.0 users
                    if self.detect_v2_installation():
                        self.handle_v2_migration()
                    else:
                        print("ℹ️  You're running the latest Python version!")
                        print("   For manual updates, please reinstall the tool")
                        print("   This will preserve your configuration and logs")
                        
                else:
                    print("⚠️  Could not check for updates. Using fallback method.")
                    self.fallback_update_info()
                    
            except requests.RequestException:
                print("🌐 Network error. Using offline update method.")
                self.fallback_update_info()
                
        except ImportError:
            print("📋 Dependencies missing. Using basic update method.")
            self.fallback_update_info()
    
    def detect_v2_installation(self) -> bool:
        """Detect if user has v2.0 bash version installed"""
        v2_paths = [
            "/usr/bin/pastebinsearch",
            "/usr/local/bin/pastebinsearch",
            Path.home() / "bin" / "pastebinsearch"
        ]
        
        for path in v2_paths:
            if Path(path).exists():
                try:
                    with open(path, 'r') as f:
                        content = f.read()
                        if 'VERSION="2.0"' in content or "bash" in content[:50]:
                            return True
                except Exception:
                    pass
        return False
    
    def handle_v2_migration(self):
        """Handle migration from v2.0 to v3.0"""
        print("")
        print("🚀 " + "="*60)
        print("   MIGRATION FROM v2.0 TO v3.0 DETECTED")
        print("="*64)
        print("")
        print("📋 PastebinSearch has been completely rewritten in Python!")
        print("")
        print("🔄 Changes in v3.0:")
        print("   • Modern Python architecture (3.8+)")
        print("   • Rich interactive interface") 
        print("   • Advanced security pattern detection")
        print("   • Cross-platform compatibility (Linux + Windows)")
        print("   • Professional configuration system")
        print("   • Comprehensive logging")
        print("")
        print("⚠️  v2.0 bash version is no longer maintained")
        print("")
        print("🛠️  To complete the migration:")
        print("   1. Install Python 3.8+ (if not already installed)")
        print("   2. Run: python pastebinsearch.py --install")
        print("   3. Test with: python pastebinsearch.py --version")
        print("   4. Use: python pastebinsearch.py (interactive mode)")
        print("")
        print("📚 For help: python pastebinsearch.py --help")
        print("💬 Support: support@byfranke.com")
        print("")
        print("="*64)
        
        # Ask if user wants to install now
        try:
            choice = input("Install v3.0 now? (y/N): ").strip().lower()
            if choice in ['y', 'yes']:
                print("")
                print("🚀 Starting v3.0 installation...")
                self.install()
        except KeyboardInterrupt:
            print("\n⚠️  Installation cancelled. You can install later with:")
            print("   python pastebinsearch.py --install")
    
    def fallback_update_info(self):
        """Fallback update information when network/API fails"""
        print("")
        print("📋 Manual Update Instructions:")
        print("   1. Visit: https://github.com/byFranke/PastebinSearch")
        print("   2. Download the latest release")
        print("   3. Extract and run: python pastebinsearch.py --install")
        print("")
        print("🔄 Or reinstall with:")
        print("   git clone https://github.com/byFranke/PastebinSearch.git")
        print("   cd PastebinSearch && python setup.py")
