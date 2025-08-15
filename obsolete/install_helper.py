#!/usr/bin/env python3
"""
🛠️ PastebinSearch - Interactive Installation Helper
User-friendly installer with guided setup and troubleshooting

This helper provides:
- Interactive system detection
- Step-by-step installation guidance
- Troubleshooting for common issues
- Multiple installation methods
- Environment validation

Usage: python obsolete/install_helper.py
"""

import sys
import os
import subprocess
import platform
import shutil
from pathlib import Path
import json
import time

class InteractiveInstaller:
    def __init__(self):
        self.python_exe = sys.executable
        self.project_dir = Path(__file__).parent.parent
        self.system_info = self._gather_system_info()
        
    def _gather_system_info(self):
        """Gather comprehensive system information"""
        info = {
            'os': platform.system(),
            'platform': platform.platform(),
            'python_version': sys.version,
            'python_exe': self.python_exe,
            'architecture': platform.architecture(),
            'machine': platform.machine(),
            'has_pip': shutil.which('pip') is not None,
            'has_pip3': shutil.which('pip3') is not None,
            'has_sudo': os.name != 'nt' and shutil.which('sudo') is not None,
            'is_windows': os.name == 'nt',
            'is_linux': platform.system().lower() == 'linux',
            'is_macos': platform.system().lower() == 'darwin',
            'externally_managed': False
        }
        
        # Check for externally managed environment
        try:
            result = subprocess.run([
                self.python_exe, '-m', 'pip', 'install', '--dry-run', 'requests'
            ], capture_output=True, text=True)
            
            if "externally-managed-environment" in result.stderr:
                info['externally_managed'] = True
        except:
            pass
        
        # Detect specific distributions
        if info['is_linux']:
            info['distribution'] = self._detect_linux_distribution()
        
        return info
    
    def _detect_linux_distribution(self):
        """Detect specific Linux distribution"""
        try:
            with open('/etc/os-release', 'r') as f:
                content = f.read().lower()
                
                if 'kali' in content:
                    return 'kali'
                elif 'ubuntu' in content:
                    return 'ubuntu'
                elif 'debian' in content:
                    return 'debian'
                elif 'parrot' in content:
                    return 'parrot'
                elif 'arch' in content:
                    return 'arch'
                elif 'centos' in content or 'rhel' in content:
                    return 'rhel'
                else:
                    return 'unknown'
        except:
            return 'unknown'
    
    def _print_welcome(self):
        """Print welcome message and system information"""
        print("\n" + "="*70)
        print("🛠️  PastebinSearch - Interactive Installation Helper")
        print("="*70)
        print("Welcome! This helper will guide you through the installation process.")
        print("We'll detect your system and recommend the best installation method.")
        print("="*70)
        
        print("\n📊 System Information:")
        print(f"   Operating System: {self.system_info['os']}")
        print(f"   Platform: {self.system_info['platform']}")
        print(f"   Python Version: {sys.version.split()[0]}")
        print(f"   Python Executable: {self.system_info['python_exe']}")
        
        if self.system_info['is_linux']:
            print(f"   Linux Distribution: {self.system_info['distribution'].title()}")
        
        if self.system_info['externally_managed']:
            print("   ⚠️  Externally-managed Python environment detected")
        
        print()
    
    def _get_user_input(self, prompt, options=None, default=None):
        """Get user input with validation"""
        while True:
            if options:
                options_str = '/'.join([f"[{opt}]" if opt == default else opt for opt in options])
                full_prompt = f"{prompt} ({options_str}): "
            else:
                full_prompt = f"{prompt}: "
            
            try:
                response = input(full_prompt).strip()
                
                if not response and default:
                    return default
                
                if options and response.lower() not in [opt.lower() for opt in options]:
                    print(f"   Please choose from: {', '.join(options)}")
                    continue
                
                return response.lower() if options else response
                
            except KeyboardInterrupt:
                print("\n❌ Installation cancelled by user")
                sys.exit(1)
    
    def _recommend_installation_method(self):
        """Recommend the best installation method based on system"""
        recommendations = []
        
        # Primary recommendation
        if self.system_info['externally_managed']:
            recommendations.append({
                'method': 'kali',
                'name': 'Kali/Ubuntu Specialized Installer',
                'command': 'python obsolete/install_kali.py',
                'description': 'Handles externally-managed environments with virtual environment',
                'confidence': 'HIGH'
            })
            
            recommendations.append({
                'method': 'universal',
                'name': 'Universal Installer (fallback)',
                'command': 'python install.py',
                'description': 'May require --break-system-packages flag',
                'confidence': 'MEDIUM'
            })
        
        elif self.system_info['is_windows']:
            recommendations.append({
                'method': 'universal',
                'name': 'Universal Installer',
                'command': 'python install.py',
                'description': 'Best for Windows systems',
                'confidence': 'HIGH'
            })
        
        elif self.system_info['distribution'] in ['kali', 'ubuntu', 'debian']:
            recommendations.append({
                'method': 'kali',
                'name': 'Linux Specialized Installer',
                'command': 'python obsolete/install_kali.py',
                'description': 'Optimized for Debian-based systems',
                'confidence': 'HIGH'
            })
            
            recommendations.append({
                'method': 'universal',
                'name': 'Universal Installer',
                'command': 'python install.py',
                'description': 'General purpose installer',
                'confidence': 'MEDIUM'
            })
        
        else:
            recommendations.append({
                'method': 'universal',
                'name': 'Universal Installer',
                'command': 'python install.py',
                'description': 'Should work on most systems',
                'confidence': 'HIGH'
            })
            
            recommendations.append({
                'method': 'manual',
                'name': 'Manual Installation',
                'command': 'pip install -r requirements.txt',
                'description': 'Install dependencies manually',
                'confidence': 'MEDIUM'
            })
        
        return recommendations
    
    def _display_recommendations(self, recommendations):
        """Display installation method recommendations"""
        print("\n🎯 Recommended Installation Methods:")
        print("-" * 50)
        
        for i, rec in enumerate(recommendations, 1):
            confidence_color = "🟢" if rec['confidence'] == 'HIGH' else "🟡"
            print(f"\n{i}. {confidence_color} {rec['name']} ({rec['confidence']} confidence)")
            print(f"   Command: {rec['command']}")
            print(f"   Description: {rec['description']}")
        
        print(f"\n4. 📋 Manual Installation (if automated methods fail)")
        print(f"   Command: pip install -r requirements.txt")
        print(f"   Description: Install dependencies manually")
    
    def _run_installation_method(self, method, command):
        """Execute the chosen installation method"""
        print(f"\n🚀 Running: {command}")
        print("-" * 40)
        
        try:
            if method == 'manual':
                # Manual installation guidance
                self._manual_installation_guide()
                return True
            else:
                # Run automated installer
                result = subprocess.run(command.split(), cwd=self.project_dir)
                return result.returncode == 0
                
        except Exception as e:
            print(f"❌ Installation failed with error: {e}")
            return False
    
    def _manual_installation_guide(self):
        """Provide manual installation guidance"""
        print("\n📋 Manual Installation Guide:")
        print("="*40)
        
        steps = [
            "Install Python dependencies:",
            f"   {self.python_exe} -m pip install -r requirements.txt",
            "",
            "If you get 'externally-managed-environment' error:",
            f"   {self.python_exe} -m pip install --break-system-packages -r requirements.txt",
            "",
            "Or create a virtual environment:",
            f"   {self.python_exe} -m venv venv",
        ]
        
        if self.system_info['is_windows']:
            steps.extend([
                "   venv\\Scripts\\activate",
                f"   {self.python_exe} -m pip install -r requirements.txt"
            ])
        else:
            steps.extend([
                "   source venv/bin/activate",
                "   pip install -r requirements.txt"
            ])
        
        steps.extend([
            "",
            "Test the installation:",
            f"   {self.python_exe} pastebinsearch.py --version"
        ])
        
        for step in steps:
            print(step)
            if step.startswith("   ") and self._get_user_input(
                "Press Enter to continue (or 'skip' to skip steps)", 
                ['enter', 'skip'], 'enter'
            ) == 'skip':
                break
        
        print("\n✅ Manual installation steps provided")
    
    def _test_installation(self):
        """Test if installation was successful"""
        print("\n🧪 Testing Installation...")
        
        main_script = self.project_dir / "pastebinsearch.py"
        
        try:
            result = subprocess.run([
                self.python_exe, str(main_script), '--version'
            ], capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                print("✅ Installation test passed!")
                print(f"   Output: {result.stdout.strip()}")
                return True
            else:
                print("❌ Installation test failed")
                print(f"   Error: {result.stderr.strip()}")
                return False
                
        except subprocess.TimeoutExpired:
            print("⏱️  Installation test timed out (may still work)")
            return False
        except Exception as e:
            print(f"❌ Installation test error: {e}")
            return False
    
    def _troubleshooting_guide(self):
        """Provide troubleshooting guidance"""
        print("\n🔧 Troubleshooting Guide:")
        print("="*30)
        
        issues = [
            {
                'issue': 'ModuleNotFoundError',
                'solution': 'Try: pip install -r requirements.txt'
            },
            {
                'issue': 'externally-managed-environment',
                'solution': 'Use: python obsolete/install_kali.py'
            },
            {
                'issue': 'SSL Certificate errors',
                'solution': 'Run with: pastebinsearch.py --diagnose'
            },
            {
                'issue': 'Browser automation fails',
                'solution': 'Install: sudo apt install chromium-driver'
            },
            {
                'issue': 'Permission denied',
                'solution': 'Try: chmod +x pastebinsearch or run with python'
            }
        ]
        
        for i, item in enumerate(issues, 1):
            print(f"{i}. {item['issue']}")
            print(f"   Solution: {item['solution']}")
            print()
    
    def _final_instructions(self):
        """Display final usage instructions"""
        print("\n" + "="*60)
        print("🎉 Installation Helper Complete!")
        print("="*60)
        
        print("\n📖 Quick Start:")
        print("   python pastebinsearch.py --search \"password\"")
        print("   python pastebinsearch.py --diagnose")
        print("   python pastebinsearch.py --help")
        
        print("\n📚 Documentation:")
        print("   README.md - Complete usage guide")
        print("   Legal guidelines - For ethical usage")
        
        print("\n🔗 Support:")
        print("   Website: https://byfranke.com")
        print("   GitHub: Check issues for troubleshooting")
        
        print("\n⚖️  Legal Reminder:")
        print("   This tool is for authorized security research only!")
        print("   Always obtain proper authorization before use.")
        print("="*60)
    
    def run(self):
        """Main interactive installation process"""
        self._print_welcome()
        
        # Get recommendations
        recommendations = self._recommend_installation_method()
        self._display_recommendations(recommendations)
        
        print("\n" + "="*50)
        
        # Let user choose installation method
        choice = self._get_user_input(
            "Choose installation method", 
            ['1', '2', '3', '4'], 
            '1'
        )
        
        if choice in ['1', '2', '3']:
            method_idx = int(choice) - 1
            if method_idx < len(recommendations):
                selected = recommendations[method_idx]
                success = self._run_installation_method(selected['method'], selected['command'])
            else:
                success = False
        else:
            # Manual installation
            success = self._run_installation_method('manual', 'manual')
        
        # Test installation
        if success:
            if self._test_installation():
                print("\n✅ Installation successful!")
            else:
                print("\n⚠️  Installation completed but test failed")
                show_troubleshooting = self._get_user_input(
                    "Show troubleshooting guide?", 
                    ['y', 'n'], 
                    'y'
                )
                if show_troubleshooting == 'y':
                    self._troubleshooting_guide()
        else:
            print("\n❌ Installation failed")
            show_troubleshooting = self._get_user_input(
                "Show troubleshooting guide?", 
                ['y', 'n'], 
                'y'
            )
            if show_troubleshooting == 'y':
                self._troubleshooting_guide()
        
        # Final instructions
        self._final_instructions()

def main():
    """Main entry point"""
    try:
        installer = InteractiveInstaller()
        installer.run()
        
    except KeyboardInterrupt:
        print("\n❌ Installation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please check the logs or try manual installation")
        sys.exit(1)

if __name__ == "__main__":
    main()
