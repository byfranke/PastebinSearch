#!/usr/bin/env python3
"""
🐧 PastebinSearch - Kali Linux / Ubuntu 23+ Installer
Specialized installer for systems with externally-managed Python environments

This installer handles:
- External package management restrictions (PEP 668)
- Virtual environment creation and activation
- Kali Linux specific configurations
- Ubuntu 23+ compatibility
- Automated dependency resolution

Usage: python obsolete/install_kali.py
"""

import sys
import os
import subprocess
import platform
import shutil
from pathlib import Path
import json

class KaliLinuxInstaller:
    def __init__(self):
        self.python_exe = sys.executable
        self.project_dir = Path(__file__).parent.parent
        self.venv_dir = self.project_dir / "venv"
        self.is_kali = self._detect_kali()
        
    def _detect_kali(self):
        """Detect if running on Kali Linux or similar systems"""
        try:
            with open('/etc/os-release', 'r') as f:
                content = f.read().lower()
                return 'kali' in content or 'parrot' in content
        except:
            return False
    
    def _print_header(self):
        """Print installation header"""
        print("\n" + "="*60)
        print("🐧 PastebinSearch - Kali Linux Installer")
        print("="*60)
        print(f"Python Version: {sys.version}")
        print(f"Platform: {platform.platform()}")
        print(f"Kali Detected: {'✅ Yes' if self.is_kali else '❌ No'}")
        print(f"Project Directory: {self.project_dir}")
        print("="*60 + "\n")
    
    def _check_externally_managed(self):
        """Check if Python environment is externally managed"""
        try:
            result = subprocess.run([
                self.python_exe, '-m', 'pip', 'install', '--dry-run', 'requests'
            ], capture_output=True, text=True)
            
            if "externally-managed-environment" in result.stderr:
                return True
        except:
            pass
        return False
    
    def _create_virtual_environment(self):
        """Create virtual environment for isolated installation"""
        print("📦 Creating virtual environment...")
        
        if self.venv_dir.exists():
            print(f"   Removing existing venv: {self.venv_dir}")
            shutil.rmtree(self.venv_dir)
        
        try:
            subprocess.run([
                self.python_exe, '-m', 'venv', str(self.venv_dir)
            ], check=True, capture_output=True)
            
            print(f"   ✅ Virtual environment created at: {self.venv_dir}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to create virtual environment: {e}")
            print("   💡 Try installing python3-venv:")
            print("      sudo apt install python3-venv")
            return False
    
    def _get_venv_python(self):
        """Get Python executable from virtual environment"""
        if os.name == 'nt':
            return self.venv_dir / "Scripts" / "python.exe"
        else:
            return self.venv_dir / "bin" / "python"
    
    def _get_venv_pip(self):
        """Get pip executable from virtual environment"""
        if os.name == 'nt':
            return self.venv_dir / "Scripts" / "pip.exe"
        else:
            return self.venv_dir / "bin" / "pip"
    
    def _install_dependencies(self):
        """Install required dependencies in virtual environment"""
        print("\n📚 Installing dependencies...")
        
        venv_pip = self._get_venv_pip()
        
        # Read requirements
        requirements_file = self.project_dir / "requirements.txt"
        if not requirements_file.exists():
            print("   ❌ requirements.txt not found!")
            return False
        
        try:
            # Upgrade pip first
            print("   Upgrading pip...")
            subprocess.run([
                str(venv_pip), 'install', '--upgrade', 'pip'
            ], check=True, capture_output=True)
            
            # Install requirements
            print("   Installing packages from requirements.txt...")
            subprocess.run([
                str(venv_pip), 'install', '-r', str(requirements_file)
            ], check=True)
            
            print("   ✅ Dependencies installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to install dependencies: {e}")
            return False
    
    def _install_system_packages(self):
        """Install system packages required for browser automation"""
        print("\n🔧 Checking system packages...")
        
        if not self.is_kali:
            print("   ⚠️  Not on Kali - skipping system package installation")
            return True
        
        packages = [
            'chromium-driver',
            'firefox-esr-driver', 
            'xvfb',  # For headless browser
            'python3-venv'
        ]
        
        try:
            print("   Installing system packages...")
            subprocess.run([
                'sudo', 'apt', 'update'
            ], check=True, capture_output=True)
            
            subprocess.run([
                'sudo', 'apt', 'install', '-y'
            ] + packages, check=True)
            
            print("   ✅ System packages installed")
            return True
            
        except subprocess.CalledProcessError:
            print("   ⚠️  Could not install system packages (sudo required)")
            print("   💡 Manual installation:")
            print(f"      sudo apt install {' '.join(packages)}")
            return True  # Don't fail installation for this
    
    def _create_launcher_script(self):
        """Create launcher script for easy execution"""
        print("\n🚀 Creating launcher script...")
        
        venv_python = self._get_venv_python()
        main_script = self.project_dir / "pastebinsearch.py"
        
        # Create shell script
        launcher_script = self.project_dir / "pastebinsearch"
        launcher_content = f"""#!/bin/bash
# PastebinSearch Launcher for Kali Linux
# Automatically activates virtual environment and runs the tool

SCRIPT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
VENV_PYTHON="{venv_python}"
MAIN_SCRIPT="{main_script}"

if [ ! -f "$VENV_PYTHON" ]; then
    echo "❌ Virtual environment not found!"
    echo "💡 Run: python obsolete/install_kali.py"
    exit 1
fi

# Run with virtual environment Python
"$VENV_PYTHON" "$MAIN_SCRIPT" "$@"
"""
        
        try:
            with open(launcher_script, 'w') as f:
                f.write(launcher_content)
            
            # Make executable
            os.chmod(launcher_script, 0o755)
            
            print(f"   ✅ Launcher created: {launcher_script}")
            return True
            
        except Exception as e:
            print(f"   ❌ Failed to create launcher: {e}")
            return False
    
    def _test_installation(self):
        """Test if installation works correctly"""
        print("\n🧪 Testing installation...")
        
        venv_python = self._get_venv_python()
        main_script = self.project_dir / "pastebinsearch.py"
        
        try:
            result = subprocess.run([
                str(venv_python), str(main_script), '--version'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("   ✅ Installation test passed!")
                print(f"   Output: {result.stdout.strip()}")
                return True
            else:
                print(f"   ❌ Installation test failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"   ❌ Installation test error: {e}")
            return False
    
    def _print_usage_instructions(self):
        """Print final usage instructions"""
        print("\n" + "="*60)
        print("🎉 Installation Complete!")
        print("="*60)
        print("\n📖 Usage Instructions:")
        print()
        print("1️⃣  Direct execution (recommended):")
        print("   ./pastebinsearch --search \"password\"")
        print()
        print("2️⃣  Manual virtual environment:")
        print("   source venv/bin/activate")
        print("   python pastebinsearch.py --search \"password\"")
        print()
        print("3️⃣  Test connectivity:")
        print("   ./pastebinsearch --diagnose")
        print()
        print("⚖️  Legal Notice:")
        print("   This tool is for authorized security research only!")
        print("   Obtain proper authorization before use.")
        print()
        print("🔗 Documentation: README.md")
        print("🌐 Website: https://byfranke.com")
        print("="*60)
    
    def install(self):
        """Main installation process"""
        self._print_header()
        
        # Check for externally managed environment
        if self._check_externally_managed():
            print("🔒 Externally-managed Python environment detected")
            print("   Creating isolated virtual environment...")
        
        # Install system packages (Kali only)
        if not self._install_system_packages():
            print("⚠️  System package installation had issues, continuing...")
        
        # Create virtual environment
        if not self._create_virtual_environment():
            print("❌ Virtual environment creation failed!")
            return False
        
        # Install Python dependencies
        if not self._install_dependencies():
            print("❌ Dependency installation failed!")
            return False
        
        # Create launcher
        if not self._create_launcher_script():
            print("⚠️  Launcher creation failed, manual execution required")
        
        # Test installation
        if not self._test_installation():
            print("⚠️  Installation test failed, but installation may still work")
        
        # Print usage instructions
        self._print_usage_instructions()
        
        return True

def main():
    """Main entry point"""
    try:
        installer = KaliLinuxInstaller()
        success = installer.install()
        
        if success:
            print("\n✅ Kali Linux installation completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Installation failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n❌ Installation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
