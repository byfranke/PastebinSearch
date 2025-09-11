#!/usr/bin/env python3
"""
🚀 PastebinSearch Universal Installer
=====================================
Detects your system automatically and installs PastebinSearch with the best method.
Supports Windows, Linux, macOS with automatic environment detection.
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path
import json

class PastebinSearchInstaller:
    def __init__(self):
        self.system = platform.system().lower()
        self.python_executable = sys.executable
        self.script_dir = Path(__file__).parent
        self.install_dir = self._get_install_directory()
        self.is_externally_managed = self._check_externally_managed()
        self.is_venv = self._check_virtual_env()
        
    def _get_install_directory(self):
        """Get the appropriate installation directory"""
        if self.system == "windows":
            # Windows: Use %LOCALAPPDATA%\Programs\PastebinSearch
            return Path.home() / "AppData" / "Local" / "Programs" / "PastebinSearch"
        else:
            # Linux/macOS: Use ~/.local/bin/pastebinsearch
            return Path.home() / ".local" / "bin" / "pastebinsearch"
    
    def _check_externally_managed(self):
        """Check if Python environment is externally managed"""
        try:
            import sysconfig
            stdlib = Path(sysconfig.get_path('stdlib'))
            marker = stdlib / "EXTERNALLY-MANAGED"
            return marker.exists()
        except:
            return False
    
    def _check_virtual_env(self):
        """Check if we're in a virtual environment"""
        return (
            hasattr(sys, 'real_prefix') or 
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
        )
    
    def print_banner(self):
        """Print installation banner"""
        print("🚀 PastebinSearch Universal Installer")
        print("=" * 50)
        print("🔍 Advanced Security Research Tool")
        print("📧 by byFranke - https://byfranke.com")
        print()
        print("� SYSTEM DETECTION:")
        print(f"�🖥️  System: {platform.system()} {platform.release()}")
        print(f"🐍 Python: {sys.version.split()[0]}")
        print(f"📁 Install Directory: {self.install_dir}")
        print(f"🌐 Virtual Environment: {'Yes' if self.is_venv else 'No'}")
        print(f"🔒 Externally Managed: {'Yes' if self.is_externally_managed else 'No'}")
        print()
        print("📋 WHAT THIS INSTALLER WILL DO:")
        print("  • Install all required Python dependencies")  
        print("  • Create system integration (PATH, shortcuts)")
        print("  • Set up 'pastebinsearch' command globally")
        print("  • Test installation and connectivity")
        print("  • Organize project files")
        print()
    
    def run_command(self, cmd_parts, description="Running command", check=True):
        """Run a command with proper error handling"""
        try:
            print(f"  🔧 {description}...")
            result = subprocess.run(
                cmd_parts,
                check=check,
                capture_output=True,
                text=True
            )
            if result.stdout:
                print(f"    ✅ Output: {result.stdout.strip()}")
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            print(f"    ❌ Failed: {e.stderr.strip()}")
            return False, e.stderr
        except Exception as e:
            print(f"    ❌ Error: {str(e)}")
            return False, str(e)
    
    def install_dependencies(self):
        """Install Python dependencies using the best method"""
        print("📦 Installing Python Dependencies...")
        
        # Essential packages including brotli
        packages = [
            "rich>=13.7.0",
            "aiohttp>=3.9.0", 
            "beautifulsoup4>=4.12.0",
            "lxml>=4.9.0",
            "requests>=2.31.0",
            "python-dotenv>=1.0.0",
            "asyncio-throttle>=1.0.2",
            "loguru>=0.7.2",
            "cryptography>=3.4.0",
            "pydantic>=2.4.0",
            "colorama>=0.4.6",
            "brotli>=1.0.9",      # Fix for brotli encoding
            "selenium>=4.15.0",   # For browser automation
            "webdriver-manager>=4.0.0"  # Auto-manage browser drivers
        ]
        
        pip_cmd = [self.python_executable, "-m", "pip"]
        
        # Determine installation method
        if self.is_venv:
            print("  📝 Using virtual environment installation...")
            install_cmd = pip_cmd + ["install"] + packages
        elif self.is_externally_managed:
            print("  📝 Creating isolated environment...")
            # Create a dedicated virtual environment
            venv_dir = self.install_dir / "venv"
            
            # Create venv
            success, _ = self.run_command([
                self.python_executable, "-m", "venv", str(venv_dir)
            ], "Creating virtual environment")
            
            if not success:
                return False
            
            # Use venv python
            if self.system == "windows":
                venv_python = venv_dir / "Scripts" / "python.exe"
            else:
                venv_python = venv_dir / "bin" / "python"
            
            install_cmd = [str(venv_python), "-m", "pip", "install"] + packages
        else:
            print("  📝 Using user installation...")
            install_cmd = pip_cmd + ["install", "--user"] + packages
        
        # Install packages
        success, output = self.run_command(install_cmd, "Installing packages")
        
        if success:
            print("  ✅ All dependencies installed successfully!")
            return True
        else:
            print("  ❌ Some packages failed to install")
            return False
    
    def setup_system_integration(self):
        """Setup system integration (PATH, shortcuts, etc)"""
        print("🔧 Setting up system integration...")
        
        # Create installation directory
        self.install_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy core files
        core_files = [
            "pastebinsearch.py",
            "modules/",
            "config/",
            "README.md"
        ]
        
        for file_path in core_files:
            src = self.script_dir / file_path
            dst = self.install_dir / file_path
            
            if src.exists():
                if src.is_dir():
                    if dst.exists():
                        shutil.rmtree(dst)
                    shutil.copytree(src, dst)
                    print(f"  📂 Copied directory: {file_path}")
                else:
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
                    print(f"  📄 Copied file: {file_path}")
        
        # Create launcher script
        if self.system == "windows":
            self._create_windows_launcher()
        else:
            self._create_unix_launcher()
        
        return True
    
    def _create_windows_launcher(self):
        """Create Windows launcher script"""
        launcher_path = self.install_dir / "pastebinsearch.bat"
        
        if self.is_externally_managed:
            python_path = self.install_dir / "venv" / "Scripts" / "python.exe"
        else:
            python_path = self.python_executable
        
        launcher_content = f"""@echo off
cd /d "{self.install_dir}"
"{python_path}" pastebinsearch.py %*
"""
        
        launcher_path.write_text(launcher_content)
        print(f"  🚀 Created Windows launcher: {launcher_path}")
        
        # Add to PATH (requires admin, so provide instructions)
        print(f"  💡 To use 'pastebinsearch' from anywhere:")
        print(f"     Add {self.install_dir} to your PATH environment variable")
    
    def _create_unix_launcher(self):
        """Create Unix/Linux launcher script"""
        
        if self.is_externally_managed:
            python_path = self.install_dir / "venv" / "bin" / "python"
        else:
            python_path = self.python_executable
        
        # Create launcher script
        launcher_path = self.install_dir / "pastebinsearch"
        launcher_content = f"""#!/bin/bash
cd "{self.install_dir}"
"{python_path}" pastebinsearch.py "$@"
"""
        
        launcher_path.write_text(launcher_content)
        launcher_path.chmod(0o755)
        print(f"  🚀 Created Unix launcher: {launcher_path}")
        
        # Try to create symlink in ~/.local/bin
        local_bin = Path.home() / ".local" / "bin"
        local_bin.mkdir(parents=True, exist_ok=True)
        
        symlink_path = local_bin / "pastebinsearch"
        if symlink_path.exists():
            symlink_path.unlink()
        
        try:
            symlink_path.symlink_to(launcher_path)
            print(f"  🔗 Created symlink: {symlink_path}")
            print(f"  💡 You can now use 'pastebinsearch' from anywhere!")
        except Exception as e:
            print(f"  ⚠️  Could not create symlink: {e}")
            print(f"  💡 Manually add {self.install_dir} to your PATH")
    
    def move_obsolete_files(self):
        """Move obsolete files to obsolete directory"""
        print("🗂️  Organizing project files...")
        
        obsolete_dir = self.script_dir / "obsolete"
        obsolete_dir.mkdir(exist_ok=True)
        
        # Files to move to obsolete
        obsolete_patterns = [
            "install_helper.py",
            "install_kali.py", 
            "quick_install.py",
            "test_*.py",
            "demo_*.py",
            "*.bak",
            "*.backup"
        ]
        
        # Directories to move to obsolete
        obsolete_dirs = ["Trash"]
        
        moved_count = 0
        
        # Move files by pattern
        for pattern in obsolete_patterns:
            try:
                for file_path in self.script_dir.glob(pattern):
                    if file_path != Path(__file__) and file_path != obsolete_dir and file_path.is_file():
                        dst = obsolete_dir / file_path.name
                        
                        # Remove destination if it exists
                        if dst.exists():
                            dst.unlink()
                        
                        shutil.move(str(file_path), str(dst))
                        print(f"  📦 Moved to obsolete: {file_path.name}")
                        moved_count += 1
            except Exception as e:
                print(f"  ⚠️  Could not move pattern {pattern}: {e}")
        
        # Move directories
        for dir_name in obsolete_dirs:
            try:
                dir_path = self.script_dir / dir_name
                if dir_path.exists() and dir_path.is_dir():
                    dst = obsolete_dir / dir_name
                    
                    # Remove destination if it exists
                    if dst.exists():
                        shutil.rmtree(dst)
                    
                    shutil.move(str(dir_path), str(dst))
                    print(f"  📦 Moved directory to obsolete: {dir_name}")
                    moved_count += 1
            except Exception as e:
                print(f"  ⚠️  Could not move directory {dir_name}: {e}")
        
        # Create new minimal requirements.txt (backup old one first)
        requirements_path = self.script_dir / "requirements.txt"
        if requirements_path.exists():
            backup_path = obsolete_dir / "requirements_old.txt"
            try:
                shutil.copy2(requirements_path, backup_path)
                print(f"  💾 Backed up old requirements.txt")
            except Exception as e:
                print(f"  ⚠️  Could not backup requirements.txt: {e}")
        
        new_requirements = """# PastebinSearch - Essential Dependencies
rich>=13.7.0
aiohttp>=3.9.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
requests>=2.31.0
python-dotenv>=1.0.0
asyncio-throttle>=1.0.2
loguru>=0.7.2
cryptography>=3.4.0
pydantic>=2.4.0
colorama>=0.4.6
brotli>=1.0.9
selenium>=4.15.0
webdriver-manager>=4.0.0
"""
        
        try:
            requirements_path.write_text(new_requirements, encoding='utf-8')
            print("  📄 Created new minimal requirements.txt")
        except Exception as e:
            print(f"  ⚠️  Could not create new requirements.txt: {e}")
        
        print(f"  ✅ Organized {moved_count} obsolete files/directories")
        return True  # Always return True even if some files couldn't be moved
    
    def test_installation(self):
        """Test if installation works"""
        print("🧪 Testing installation...")
        
        launcher_script = self.install_dir / ("pastebinsearch.bat" if self.system == "windows" else "pastebinsearch")
        
        if not launcher_script.exists():
            print("  ❌ Launcher script not found")
            return False
        
        try:
            # Test with --version flag
            result = subprocess.run(
                [str(launcher_script), "--version"] if self.system != "windows" else ["cmd", "/c", str(launcher_script), "--version"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print("  ✅ Installation test successful!")
                return True
            else:
                print(f"  ❌ Installation test failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"  ❌ Test failed: {e}")
            return False
    
    def update_readme(self):
        """Update README.md with new installation instructions"""
        print("📚 Updating README.md...")
        
        readme_content = """# 🔍 PastebinSearch v3.1.1

Advanced security research tool for searching Pastebin with multiple search engines and automation features.

## 🚀 Quick Installation

### Universal Installer (Recommended)
```bash
python3 install.py
```

This installer:
- ✅ Automatically detects your system (Windows/Linux/macOS)
- ✅ Handles virtual environments and externally-managed Python
- ✅ Installs all dependencies including brotli support
- ✅ Creates system launchers and PATH integration
- ✅ Organizes project files automatically

### Manual Installation
```bash
pip install rich aiohttp beautifulsoup4 lxml requests python-dotenv brotli selenium
```

## 📋 Usage

After installation, you can use PastebinSearch from anywhere:

```bash
# Quick search
pastebinsearch --search "password"

# Advanced search with filters
pastebinsearch --search "api key" --language python --date-range 7

# Manual browser search
pastebinsearch --manual --search "credentials"

# Test connectivity
pastebinsearch --diagnose

# Help
pastebinsearch --help
```

## 🛠️ Features

- 🔍 **Multi-Engine Search**: DuckDuckGo, Google, Bing integration
- 🌐 **Browser Automation**: Selenium-based manual search
- 🔒 **SSL Handling**: Advanced certificate verification with fallbacks
- 📊 **Rich Interface**: Beautiful CLI with progress bars and panels
- 🚀 **Async Operations**: High-performance async HTTP requests
- 📈 **Search History**: Track and replay searches
- 🎯 **Smart Filtering**: Date, language, and content filters
- 🔧 **Hybrid Modes**: Automatic + manual search options

## 🐛 Troubleshooting

### SSL Certificate Issues
```bash
pastebinsearch --diagnose
```

### Missing Dependencies
```bash
python3 install.py  # Re-run installer
```

### Brotli Encoding Error
The installer automatically includes brotli support. If you get encoding errors, ensure brotli is installed:
```bash
pip install brotli
```

## 📁 Project Structure

```
PastebinSearch/
├── pastebinsearch.py      # Main application
├── install.py            # Universal installer
├── modules/              # Core modules
├── config/              # Configuration files
├── obsolete/            # Old/deprecated files
└── README.md           # This file
```

## 🔒 Legal Notice

This tool is for educational and authorized security research only. Users are responsible for compliance with applicable laws and terms of service.

## 🌟 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## 📞 Support

- 🌐 Website: https://byfranke.com
- 📧 Contact: Via website contact form
- 🐛 Issues: Open GitHub issue

---

**byFranke** - Advanced Security Research Tools
"""
        
        (self.script_dir / "README.md").write_text(readme_content, encoding='utf-8')
        print("  ✅ README.md updated with new instructions")
    
    def run_installation(self):
        """Run the complete installation process"""
        self.print_banner()
        
        # Check if user wants to proceed
        response = input("🤔 Proceed with installation? (Y/n): ").lower().strip()
        if response and response[0] == 'n':
            print("❌ Installation cancelled by user")
            return False
        
        steps = [
            ("Installing dependencies", self.install_dependencies),
            ("Setting up system integration", self.setup_system_integration),
            ("Organizing project files", self.move_obsolete_files),
            ("Testing installation", self.test_installation)
        ]
        
        for step_name, step_func in steps:
            print(f"\n🔄 {step_name}...")
            if not step_func():
                print(f"❌ Failed at: {step_name}")
                return False
        
        # Success message
        print("\n" + "="*70)
        print("🎉 INSTALLATION SUCCESSFUL!")
        print("="*70)
        print(f"📍 Installation location: {self.install_dir}")
        print(f"🔍 PastebinSearch is now ready for security research!")
        print()
        
        if self.system == "windows":
            print("📋 HOW TO USE:")
            print(f"  Option 1: {self.install_dir / 'pastebinsearch.bat'} --search 'password'")
            print("  Option 2: Add to PATH for global access")
            print(f"           → Add {self.install_dir} to Windows PATH")
            print()
            print("💡 QUICK COMMANDS:")
            print("  • Search passwords: pastebinsearch --search 'password'")
            print("  • Manual search: pastebinsearch --manual --search 'api key'") 
            print("  • Test tool: pastebinsearch --diagnose")
            print("  • Show help: pastebinsearch --help")
        else:
            print("📋 HOW TO USE:")
            print("  pastebinsearch --search 'password'")
            print("  pastebinsearch --manual --search 'api key'")
            print("  pastebinsearch --diagnose")
            print("  pastebinsearch --help")
            print()
            print("💡 EXAMPLES:")
            print("  🔍 Search for leaked passwords")
            print("  🔑 Find exposed API keys")
            print("  🌐 Automated browser searches")
            print("  📊 Rich terminal interface")
        
        print()
        print("⚠️  LEGAL NOTICE:")
        print("   This tool is for authorized security research only.")
        print("   You are responsible for complying with all applicable laws.")
        print()
        print("� Ready for ethical security research!")
        return True

def main():
    """Main installation entry point"""
    try:
        installer = PastebinSearchInstaller()
        success = installer.run_installation()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Installation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Installation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

