#!/usr/bin/env python3
"""
ATLAS v2.0 System Verification Script
Checks all dependencies, configurations, and system readiness
"""

import sys
import os
from pathlib import Path
import json

class AtlasVerifier:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.success = []
        self.project_root = Path(__file__).parent
        
    def verify_python_version(self):
        """Check Python version is 3.12+"""
        version = sys.version_info
        if version.major >= 3 and version.minor >= 12:
            self.success.append(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        else:
            self.errors.append(f"❌ Python 3.12+ required, got {version.major}.{version.minor}")
    
    def verify_files(self):
        """Check required files exist"""
        required_files = [
            "BRAIN_ENGINE.PY",
            "COMM_LINK.PY", 
            "HAND_CONTROL.PY",
            "CONSTRUCTOR.py",
            "VISION_SYSTEM.PY",
            "config.py",
            "requirements.txt",
            "README.md",
        ]
        
        for f in required_files:
            path = self.project_root / f
            if path.exists():
                size = path.stat().st_size
                self.success.append(f"✅ {f} ({size} bytes)")
            else:
                self.errors.append(f"❌ Missing file: {f}")
    
    def verify_dependencies(self):
        """Check required packages are installed"""
        required = [
            "fastapi",
            "uvicorn",
            "aiohttp",
            "pydantic",
            "dotenv",
            "groq",
            "huggingface_hub",
            "git",
            "github",
        ]
        
        for pkg in required:
            try:
                __import__(pkg)
                self.success.append(f"✅ {pkg} installed")
            except ImportError:
                self.errors.append(f"❌ {pkg} not installed. Run: pip install -r requirements.txt")
    
    def verify_env_file(self):
        """Check .env file setup"""
        env_path = self.project_root / ".env"
        if env_path.exists():
            # Read and check for required keys
            env_vars = {}
            try:
                with open(env_path) as f:
                    for line in f:
                        if '=' in line and not line.startswith('#'):
                            key, _ = line.split('=', 1)
                            env_vars[key.strip()] = True
            except Exception as e:
                self.errors.append(f"❌ Error reading .env: {e}")
                return
            
            required_keys = [
                "GROQ_API_KEY",
                "HUGGINGFACE_API_KEY",
                "GITHUB_API_KEY",
                "JUDGE0_API_KEY",
            ]
            
            for key in required_keys:
                if key in env_vars:
                    self.success.append(f"✅ {key} configured")
                else:
                    self.warnings.append(f"⚠️  {key} not in .env (optional but recommended)")
        else:
            self.warnings.append("⚠️  .env file not found. Copy env.example to .env")
    
    def verify_config_file(self):
        """Check config.py is valid Python"""
        try:
            spec = __import__('importlib.util').util.spec_from_file_location(
                "config", 
                self.project_root / "config.py"
            )
            if spec and spec.loader:
                self.success.append("✅ config.py is valid Python")
            else:
                self.errors.append("❌ config.py cannot be imported")
        except Exception as e:
            self.errors.append(f"❌ config.py error: {e}")
    
    def verify_git_repo(self):
        """Check git repository is initialized"""
        git_dir = self.project_root / ".git"
        if git_dir.exists():
            self.success.append("✅ Git repository initialized")
        else:
            self.warnings.append("⚠️  Git repository not initialized. Run: git init")
    
    def verify_memory_files(self):
        """Check memory files can be created"""
        memory_files = ["memory.json", "brain_decisions.json"]
        for f in memory_files:
            path = self.project_root / f
            try:
                if not path.exists():
                    # Try to create and delete
                    path.write_text('{"test": true}')
                    path.unlink()
                self.success.append(f"✅ {f} writable")
            except Exception as e:
                self.errors.append(f"❌ Cannot write {f}: {e}")
    
    def verify_logs_dir(self):
        """Check logs directory can be created"""
        logs_dir = self.project_root / "logs"
        try:
            logs_dir.mkdir(exist_ok=True)
            (logs_dir / "vision").mkdir(exist_ok=True)
            self.success.append("✅ logs/ directory writable")
        except Exception as e:
            self.errors.append(f"❌ Cannot create logs directory: {e}")
    
    def verify_asyncio_support(self):
        """Check asyncio and async/await support"""
        try:
            import asyncio
            import aiohttp
            self.success.append("✅ asyncio and aiohttp available")
        except ImportError as e:
            self.errors.append(f"❌ Missing async support: {e}")
    
    def verify_api_libs(self):
        """Check API client libraries"""
        libs = {
            "groq": "Groq API client",
            "requests": "HTTP client",
            "git": "Git library",
            "github": "GitHub API client",
        }
        
        for lib, description in libs.items():
            try:
                __import__(lib)
                self.success.append(f"✅ {description} available")
            except ImportError:
                self.warnings.append(f"⚠️  {lib} ({description}) not installed")
    
    def print_report(self):
        """Print verification report"""
        print("\n" + "="*60)
        print("ATLAS v2.0 System Verification Report")
        print("="*60)
        
        if self.success:
            print("\n✅ SUCCESSES:")
            for msg in self.success:
                print(f"   {msg}")
        
        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for msg in self.warnings:
                print(f"   {msg}")
        
        if self.errors:
            print("\n❌ ERRORS:")
            for msg in self.errors:
                print(f"   {msg}")
        
        print("\n" + "="*60)
        
        # Overall status
        if not self.errors:
            print("✅ VERIFICATION PASSED - System is ready!")
            if self.warnings:
                print("   (Warnings can be addressed before production)")
            return 0
        else:
            print(f"❌ VERIFICATION FAILED - {len(self.errors)} critical issues")
            print("\nQuick fixes:")
            print("   1. pip install -r requirements.txt")
            print("   2. cp env.example .env && nano .env")
            print("   3. git config user.email 'atlas@example.com'")
            print("   4. Run this script again")
            return 1
    
    def run_all_checks(self):
        """Run all verification checks"""
        print("\nRunning ATLAS v2.0 System Verification...")
        print("-" * 60)
        
        self.verify_python_version()
        self.verify_files()
        self.verify_dependencies()
        self.verify_env_file()
        self.verify_config_file()
        self.verify_git_repo()
        self.verify_memory_files()
        self.verify_logs_dir()
        self.verify_asyncio_support()
        self.verify_api_libs()
        
        return self.print_report()

def main():
    verifier = AtlasVerifier()
    exit_code = verifier.run_all_checks()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
