"""
Module: HAND_CONTROL (REFACTORED v2.0)
Purpose: Executive Execution via Subprocess + Judge0 Cloud Compilation
Owner: SIR, BURTON
Architecture: CLI execution + remote C code compilation
"""

import asyncio
import subprocess
import aiohttp
import logging
import json
import base64
from typing import Dict, Tuple, Optional
from datetime import datetime
from config import (
    JUDGE0_BASE_URL, JUDGE0_TIMEOUT, JUDGE0_API_KEY,
    JUDGE0_LANGUAGE_IDS
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HAND_CONTROL")

class Judge0Compiler:
    """
    Cloud-based C code compiler using Judge0 API.
    Handles code compilation, execution, and binary generation.
    """
    
    def __init__(self):
        """Initialize Judge0 compiler interface."""
        self.version = "ATLAS-HC-V2.0-JUDGE0"
        self.base_url = JUDGE0_BASE_URL
        self.api_key = JUDGE0_API_KEY
        self.timeout = JUDGE0_TIMEOUT
        
        logger.info(f"[{datetime.now()}] {self.version} Judge0 Compiler Online")
    
    async def _make_request(self, session: aiohttp.ClientSession, method: str, endpoint: str, 
                           data: Dict = None) -> Dict:
        """
        Make async HTTP request to Judge0 API.
        
        :param session: aiohttp ClientSession
        :param method: HTTP method (GET, POST)
        :param endpoint: API endpoint
        :param data: Request payload
        :return: Response JSON
        """
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "judge0-ce.p.rapidapi.com"
        }
        
        try:
            async with session.request(
                method, url, json=data, headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as resp:
                return await resp.json() if resp.status in [200, 201] else {}
        except Exception as e:
            logger.error(f"Judge0 API request failed: {e}")
            return {}
    
    async def compile_and_run(self, c_code: str, language: str = "c") -> Dict:
        """
        Compile and execute C code remotely via Judge0.
        
        :param c_code: C source code
        :param language: Programming language (default: c)
        :return: Compilation result with output, errors, and execution details
        """
        language_id = JUDGE0_LANGUAGE_IDS.get(language.lower(), 50)  # 50 = C
        
        logger.info(f"Submitting {language} code to Judge0 compiler...")
        
        payload = {
            "source_code": base64.b64encode(c_code.encode()).decode(),
            "language_id": language_id,
            "stdin": base64.b64encode(b"").decode(),
        }
        
        async with aiohttp.ClientSession() as session:
            # Submit code for compilation
            submission = await self._make_request(session, "POST", "/submissions/", payload)
            
            if not submission or "token" not in submission:
                return {
                    "status": "error",
                    "message": "Failed to submit code to Judge0",
                    "code": c_code[:200]
                }
            
            token = submission["token"]
            logger.info(f"Submission token: {token}")
            
            # Poll for result
            await asyncio.sleep(2)  # Wait for compilation
            result = await self._make_request(session, "GET", f"/submissions/{token}/")
            
            if result and "status" in result:
                return {
                    "status": "success",
                    "token": token,
                    "compilation_status": result.get("status", {}).get("description", "Unknown"),
                    "stdout": result.get("stdout", ""),
                    "stderr": result.get("stderr", ""),
                    "exit_code": result.get("exit_code", -1),
                    "execution_time": result.get("time", "N/A"),
                    "memory_used": result.get("memory", "N/A"),
                    "code_length": len(c_code)
                }
        
        return {"status": "error", "message": "Compilation timeout or error"}
    
    async def generate_executable(self, c_code: str, filename: str = "output") -> Tuple[bool, str]:
        """
        Compile code and generate downloadable binary/executable.
        
        :param c_code: C source code
        :param filename: Output executable name
        :return: (success, download_link_or_error)
        """
        result = await self.compile_and_run(c_code)
        
        if result["status"] != "success":
            return False, f"Compilation failed: {result.get('stderr', 'Unknown error')}"
        
        # Generate a mock download link (in production, would store on cloud)
        download_link = f"https://atlas-binaries.example.com/{filename}_{result['token']}.exe"
        
        logger.info(f"Executable available at: {download_link}")
        return True, download_link
    
    async def validate_syntax(self, c_code: str) -> bool:
        """
        Quick syntax validation without full execution.
        
        :param c_code: C source code
        :return: True if valid, False otherwise
        """
        result = await self.compile_and_run(c_code)
        return result.get("status") == "success" and "error" not in result.get("stderr", "").lower()


class AtlasHandControlV2:
    """
    Refactored Hand Control using subprocess CLI execution + Judge0 compilation.
    Replaces PyAutoGUI with direct command execution.
    """
    
    def __init__(self):
        """Initialize executive control system."""
        self.version = "ATLAS-HC-V2.0-SUBPROCESS"
        self.compiler = Judge0Compiler()
        
        logger.info(f"[{datetime.now()}] {self.version} Executive Limbs Online")
    
    async def execute_command(self, command: str, shell: bool = False) -> Dict:
        """
        Execute system command via subprocess.
        
        :param command: Command to execute (string or list)
        :param shell: Whether to execute through shell
        :return: Execution result with stdout, stderr, return code
        """
        logger.info(f"Executing command: {command}")
        
        try:
            result = subprocess.run(
                command,
                shell=shell,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "success": result.returncode == 0,
                "command": command,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "timestamp": datetime.now().isoformat()
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "command": command,
                "error": "Command execution timeout",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return {
                "success": False,
                "command": command,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def compile_c_code(self, c_code: str, language: str = "c") -> Dict:
        """
        Compile C code using Judge0.
        
        :param c_code: C source code
        :param language: Programming language
        :return: Compilation result
        """
        logger.info(f"Compiling {language} code via Judge0...")
        result = await self.compiler.compile_and_run(c_code, language)
        return result
    
    async def build_workflow(self, brain_output: str) -> Dict:
        """
        Complete workflow: Parse brain output, validate, compile, generate binary.
        
        :param brain_output: C code from brain engine
        :return: Final execution summary with binary link
        """
        logger.info("Starting Hand Control workflow...")
        
        workflow_result = {
            "step_1_syntax_validation": None,
            "step_2_compilation": None,
            "step_3_binary_generation": None,
            "final_status": "pending",
            "download_link": None,
            "timestamp": datetime.now().isoformat()
        }
        
        # Step 1: Syntax Validation
        is_valid = await self.compiler.validate_syntax(brain_output)
        workflow_result["step_1_syntax_validation"] = {
            "status": "pass" if is_valid else "fail",
            "message": "C code syntax is valid" if is_valid else "Syntax errors detected"
        }
        
        if not is_valid:
            workflow_result["final_status"] = "failed_syntax"
            return workflow_result
        
        # Step 2: Compilation
        compile_result = await self.compile_c_code(brain_output)
        workflow_result["step_2_compilation"] = compile_result
        
        if compile_result.get("status") != "success":
            workflow_result["final_status"] = "failed_compilation"
            return workflow_result
        
        # Step 3: Binary Generation
        success, binary_link = await self.compiler.generate_executable(brain_output)
        workflow_result["step_3_binary_generation"] = {
            "status": "success" if success else "failed",
            "download_link": binary_link if success else None,
            "message": binary_link if success else "Failed to generate executable"
        }
        
        workflow_result["download_link"] = binary_link if success else None
        workflow_result["final_status"] = "complete" if success else "failed_executable"
        
        return workflow_result
    
    def emergency_stop(self):
        """Emergency shutdown."""
        logger.critical("EMERGENCY STOP TRIGGERED BY SIR, BURTON")
        exit(1)

# ==================== MAIN ====================

if __name__ == "__main__":
    import asyncio
    
    async def test_hand_control():
        hands = AtlasHandControlV2()
        
        # Test 1: Execute simple command
        print("\n" + "="*60)
        print("TEST 1: Command Execution")
        print("="*60)
        result = await hands.execute_command("echo 'ATLAS Hand Control Ready'", shell=True)
        print(json.dumps(result, indent=2))
        
        # Test 2: Compile C code
        print("\n" + "="*60)
        print("TEST 2: C Code Compilation")
        print("="*60)
        c_code = """
#include <stdio.h>
int main() {
    printf("Hello from ATLAS compiled C code!\\n");
    return 0;
}
        """
        compile_result = await hands.compiler.compile_and_run(c_code)
        print(json.dumps(compile_result, indent=2))
        
        # Test 3: Full workflow
        print("\n" + "="*60)
        print("TEST 3: Build Workflow")
        print("="*60)
        workflow = await hands.build_workflow(c_code)
        print(json.dumps(workflow, indent=2))
    
    asyncio.run(test_hand_control())
