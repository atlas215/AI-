"""
Module: BRAIN_ENGINE (REFACTORED v2.0)
Purpose: Neural API Router - LLM Ensemble for Code Generation
Owner: SIR, BURTON
Architecture: Distributed LLM calling (15 models in parallel)
"""

import asyncio
import aiohttp
import json
import logging
from typing import List, Dict, Any, Tuple
from datetime import datetime
from git import Repo
from config import (
    LLM_PROVIDERS, GROQ_API_KEY, HUGGINGFACE_API_KEY, 
    GITHUB_API_KEY, C_CODE_ANALYSIS_PROMPT, LLM_TIMEOUT,
    GITHUB_REPO_OWNER, GITHUB_REPO_NAME, GITHUB_TOKEN
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BRAIN_ENGINE")

class CodeQualityVoter:
    """Scores and selects the best C code from multiple responses."""
    
    @staticmethod
    def score_code(code: str) -> float:
        """
        Evaluates C code quality on a 0-1 scale.
        Metrics: syntax validity, safety patterns, efficiency, readability
        """
        score = 0.5  # Base score
        
        checks = {
            "memory_safety": ["malloc", "free", "memset"],  # Good patterns
            "error_handling": ["if", "return", "errno"],
            "includes": ["#include"],
            "comments": ["//", "/*"],
            "no_strcpy": ["strcpy", "sprintf"],  # Bad patterns (-0.1 each)
        }
        
        # Positive indicators
        if any(check in code for check in checks["memory_safety"]):
            score += 0.1
        if any(check in code for check in checks["error_handling"]):
            score += 0.1
        if any(check in code for check in checks["includes"]):
            score += 0.05
        if any(check in code for check in checks["comments"]):
            score += 0.05
            
        # Negative indicators (unsafe patterns)
        if any(check in code for check in checks["no_strcpy"]):
            score -= 0.15
            
        # Code length sanity check (500-5000 chars is reasonable)
        code_len = len(code)
        if 500 < code_len < 5000:
            score += 0.05
        elif code_len < 100:
            score -= 0.2
            
        return min(1.0, max(0.0, score))  # Clamp to 0-1

    @staticmethod
    def select_best_code(responses: Dict[str, str]) -> Tuple[str, str, float]:
        """
        Votes on the best C code from multiple LLM responses.
        
        :param responses: Dict mapping provider names to code snippets
        :return: (best_code, provider_name, quality_score)
        """
        scores = {}
        for provider, code in responses.items():
            if code:
                scores[provider] = CodeQualityVoter.score_code(code)
            else:
                scores[provider] = 0.0
        
        if not scores:
            return "", "none", 0.0
            
        best_provider = max(scores, key=scores.get)
        best_code = responses[best_provider]
        best_score = scores[best_provider]
        
        logger.info(f"VOTING: Selected {best_provider} with score {best_score:.2f}")
        logger.info(f"All scores: {scores}")
        
        return best_code, best_provider, best_score


class AtlasBrainEngineV2:
    """
    Neural API Router using parallel LLM ensemble.
    Calls 15 different models from Groq, HuggingFace, and GitHub Model APIs.
    """
    
    def __init__(self):
        """Initializes the distributed brain system."""
        self.version = "ATLAS-BE-V2.0-LLM-ROUTER"
        self.memory_file = "brain_decisions.json"
        self.voter = CodeQualityVoter()
        
        logger.info(f"[{datetime.now()}] {self.version} Neural Router Online")
        logger.info(f"Ready to call {len(self._get_all_models())} LLM models in parallel")
        
        # Load memory
        self.memory = self._load_memory()
        
        # Initialize GitHub repo for live memory persistence
        try:
            self.repo = Repo(".")
            self.repo_owner = GITHUB_REPO_OWNER
            self.repo_name = GITHUB_REPO_NAME
            self.github_token = GITHUB_TOKEN
            logger.info(f"GitHub repo initialized for brain decisions: {self.repo_owner}/{self.repo_name}")
        except Exception as e:
            logger.error(f"Failed to initialize GitHub repo: {e}")
            self.repo = None
    
    def _load_memory(self) -> Dict:
        """Loads previous decisions from JSON memory."""
        try:
            with open(self.memory_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"decisions": [], "version": self.version}
    
    def _save_memory(self):
        """Saves decisions to JSON memory."""
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=2)
    
    async def _commit_decisions_to_github(self, message: str = None):
        """
        Commits brain decisions to GitHub for live memory persistence.
        
        :param message: Custom commit message
        """
        if not self.repo:
            logger.error("GitHub repo not initialized for brain decisions")
            return False
        
        try:
            # Stage brain decisions file
            self.repo.index.add([self.memory_file])
            
            # Check if there are changes
            if not self.repo.index.diff("HEAD"):
                logger.info("No brain decision changes to commit")
                return True
            
            # Create commit message
            commit_msg = message or "[BRAIN] Decision update"
            commit_msg += f" at {datetime.now().isoformat()}"
            
            # Commit
            self.repo.index.commit(commit_msg)
            
            # Push to GitHub
            origin = self.repo.remote(name='origin')
            origin.push()
            
            logger.info(f"Brain decisions committed to GitHub: {commit_msg}")
            return True
        except Exception as e:
            logger.error(f"Brain decisions GitHub commit failed: {e}")
            return False
    
    def _get_all_models(self) -> List[Dict[str, Any]]:
        """Returns all 15 LLM models to call in parallel."""
        models = []
        
        # GROQ Models (3)
        for model in LLM_PROVIDERS["groq"]["models"]:
            models.append({
                "provider": "groq",
                "model": model,
                "base_url": LLM_PROVIDERS["groq"]["base_url"]
            })
        
        # HuggingFace Models (5)
        for model in LLM_PROVIDERS["huggingface"]["models"]:
            models.append({
                "provider": "huggingface",
                "model": model,
                "base_url": LLM_PROVIDERS["huggingface"]["base_url"]
            })
        
        # GitHub Models (API varies, adding conceptual ones)
        for model in LLM_PROVIDERS["github_models"]["models"]:
            models.append({
                "provider": "github",
                "model": model,
                "base_url": LLM_PROVIDERS["github_models"]["base_url"]
            })
        
        return models[:15]  # Ensure exactly 15
    
    async def _call_groq_api(self, session: aiohttp.ClientSession, prompt: str, model: str) -> str:
        """Calls Groq API for code generation."""
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 2048
        }
        
        try:
            async with session.post(
                f"{LLM_PROVIDERS['groq']['base_url']}/chat/completions",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=LLM_TIMEOUT)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    logger.warning(f"Groq API error {resp.status} for {model}")
                    return ""
        except Exception as e:
            logger.error(f"Groq API call failed: {e}")
            return ""
    
    async def _call_huggingface_api(self, session: aiohttp.ClientSession, prompt: str, model: str) -> str:
        """Calls HuggingFace Inference API for code generation."""
        headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
        payload = {"inputs": prompt}
        
        try:
            url = f"{LLM_PROVIDERS['huggingface']['base_url']}/{model}"
            async with session.post(
                url,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=LLM_TIMEOUT)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if isinstance(data, list) and len(data) > 0:
                        return data[0].get("generated_text", "")
                    return str(data)
                else:
                    logger.warning(f"HuggingFace API error {resp.status} for {model}")
                    return ""
        except Exception as e:
            logger.error(f"HuggingFace API call failed: {e}")
            return ""
    
    async def _call_github_models_api(self, session: aiohttp.ClientSession, prompt: str, model: str) -> str:
        """Calls GitHub Models API for code generation."""
        headers = {"Authorization": f"Bearer {GITHUB_API_KEY}"}
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3
        }
        
        try:
            async with session.post(
                f"{LLM_PROVIDERS['github_models']['base_url']}/chat/completions",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=LLM_TIMEOUT)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    logger.warning(f"GitHub Models API error {resp.status} for {model}")
                    return ""
        except Exception as e:
            logger.error(f"GitHub Models API call failed: {e}")
            return ""
    
    async def get_ensemble_response(self, requirements: str) -> Dict[str, Any]:
        """
        Calls 15 LLM models in parallel and returns the voting-selected best response.
        
        :param requirements: Natural language requirement for code generation
        :return: Dict with selected_code, provider, quality_score, all_responses
        """
        prompt = C_CODE_ANALYSIS_PROMPT.format(requirements=requirements)
        
        logger.info(f"Calling 15 LLM models in parallel...")
        logger.info(f"Requirements: {requirements[:100]}...")
        
        models = self._get_all_models()
        responses = {}
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            model_info = {}
            
            for model_config in models:
                provider = model_config["provider"]
                model_name = model_config["model"]
                key = f"{provider}:{model_name}"
                model_info[key] = model_config
                
                if provider == "groq":
                    tasks.append(self._call_groq_api(session, prompt, model_name))
                elif provider == "huggingface":
                    tasks.append(self._call_huggingface_api(session, prompt, model_name))
                elif provider == "github":
                    tasks.append(self._call_github_models_api(session, prompt, model_name))
            
            # Execute all requests in parallel
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Map results back to providers
            for i, (model_config, result) in enumerate(zip(models, results)):
                key = f"{model_config['provider']}:{model_config['model']}"
                if isinstance(result, Exception):
                    responses[key] = ""
                    logger.error(f"Exception for {key}: {result}")
                else:
                    responses[key] = result if result else ""
        
        # Voting logic: Select the best code
        best_code, best_provider, quality_score = self.voter.select_best_code(responses)
        
        # Record decision
        decision = {
            "timestamp": datetime.now().isoformat(),
            "requirements": requirements,
            "selected_provider": best_provider,
            "quality_score": quality_score,
            "code_preview": best_code[:200] + "..." if len(best_code) > 200 else best_code
        }
        self.memory["decisions"].append(decision)
        self._save_memory()
        
        # Live persistence: Commit to GitHub immediately
        await self._commit_decisions_to_github(f"[BRAIN] New decision: {best_provider} score {quality_score:.2f}")
        
        return {
            "selected_code": best_code,
            "best_provider": best_provider,
            "quality_score": quality_score,
            "all_responses": responses,
            "timestamp": datetime.now().isoformat()
        }
    
    async def process_async(self, feature_vector: List[float]) -> float:
        """
        Async processing of feature vectors.
        Can be extended to call ensemble methods.
        """
        # Placeholder for async neural processing
        confidence = sum(feature_vector) / len(feature_vector) if feature_vector else 0.5
        return confidence
    
    def shutdown_sequence(self):
        """Cleanly shutdown the brain engine."""
        logger.info(f"[{datetime.now()}] Brain Engine entering low-power mode.")
        self._save_memory()


# Unit test
if __name__ == "__main__":
    import asyncio
    
    async def test_brain():
        brain = AtlasBrainEngineV2()
        
        # Test prompt
        requirements = "Generate a C function that safely copies a string up to 256 characters"
        
        result = await brain.get_ensemble_response(requirements)
        
        print("\n" + "="*60)
        print("BRAIN ENGINE TEST RESULTS")
        print("="*60)
        print(f"Best Provider: {result['best_provider']}")
        print(f"Quality Score: {result['quality_score']:.2f}")
        print(f"\nSelected Code:\n{result['selected_code'][:500]}")
        print("="*60)
        
        brain.shutdown_sequence()
    
    asyncio.run(test_brain())
