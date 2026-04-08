"""
Project: ATLAS SYSTEM v2.0 (ASYNC GENERAL)
Role: Supreme Commander (The General)
Owner: SIR BOSS
Environment: Python 3.12.8 | Asyncio-driven | Non-blocking architecture
"""

import asyncio
import sys
import logging
import json
from datetime import datetime
from typing import Optional

from BRAIN_ENGINE import AtlasBrainEngineV2
from VISION_SYSTEM import AtlasVisionSystem
from HAND_CONTROL import AtlasHandControlV2
from COMM_LINK import AtlasCommLinkV2
from config import CYCLE_INTERVAL, MAX_CONCURRENT_TASKS, ATLAS_VERSION

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ATLAS_GENERAL")

class AtlasGeneralAsync:
    """
    Asynchronous Supreme Commander for ATLAS System v2.0
    Manages non-blocking execution of all subsystems in parallel.
    """
    
    def __init__(self):
        """
        Initialize all subsystems asynchronously.
        """
        logger.info("="*60)
        logger.info(f"SYSTEM BOOT: {datetime.now()}")
        logger.info(f"VERSION: {ATLAS_VERSION}")
        logger.info("="*60)
        
        self.is_active = True
        self.cycle_count = 0
        self.tasks: set = set()
        
        try:
            logger.info("Initializing Brain Engine (LLM Router)...")
            self.brain = AtlasBrainEngineV2()
            
            logger.info("Initializing Vision System...")
            self.vision = AtlasVisionSystem()
            
            logger.info("Initializing Hand Control (Judge0)...")
            self.hands = AtlasHandControlV2()
            
            logger.info("Initializing Communication Link (FastAPI)...")
            self.comm = AtlasCommLinkV2()
            
            logger.info("\n[SUCCESS]: ALL SYSTEMS ONLINE. ATLAS IS READY, SIR.")
            
        except Exception as e:
            logger.critical(f"[CRITICAL]: BOOT FAILURE - {e}")
            sys.exit(1)
    
    async def visual_reconnaissance(self):
        """
        Async visual reconnaissance task.
        Non-blocking screen capture and analysis.
        """
        try:
            logger.info("VISUAL: Starting reconnaissance...")
            self.vision.save_visual_evidence("ASYNC_SCAN")
            logger.info("VISUAL: Reconnaissance complete")
            return {"status": "success", "subsystem": "vision"}
        except Exception as e:
            logger.error(f"VISUAL: Error - {e}")
            return {"status": "error", "subsystem": "vision", "error": str(e)}
    
    async def neural_analysis(self, environmental_data: list = None):
        """
        Async neural analysis via LLM ensemble.
        Calls 15 models in parallel without blocking.
        """
        try:
            if environmental_data is None:
                environmental_data = [0.5] * 10
            
            logger.info("NEURAL: Analyzing environment via LLM ensemble...")
            
            # Example: Request C code generation from LLM ensemble
            requirements = "Generate a safe string copy function in C"
            ensemble_result = await self.brain.get_ensemble_response(requirements)
            
            confidence = ensemble_result.get("quality_score", 0.5)
            
            logger.info(f"NEURAL: Analysis complete. Confidence: {confidence:.2f}")
            logger.info(f"NEURAL: Best provider: {ensemble_result.get('best_provider')}")
            
            return {
                "status": "success",
                "subsystem": "brain",
                "confidence": confidence,
                "selected_provider": ensemble_result.get("best_provider"),
                "code_preview": ensemble_result.get("selected_code", "")[:100]
            }
        except Exception as e:
            logger.error(f"NEURAL: Error - {e}")
            return {"status": "error", "subsystem": "brain", "error": str(e)}
    
    async def execute_hands(self, brain_result: dict):
        """
        Async hand execution with Judge0 compilation.
        Non-blocking C code compilation and execution.
        """
        try:
            if not brain_result.get("code_preview"):
                logger.warning("HANDS: No code to execute")
                return {"status": "skipped", "subsystem": "hands"}
            
            logger.info("HANDS: Starting execution workflow...")
            
            # Use the selected code from brain
            c_code = brain_result.get("code_preview", "")
            
            # Build complete workflow
            workflow = await self.hands.build_workflow(c_code)
            
            logger.info(f"HANDS: Workflow complete. Status: {workflow['final_status']}")
            
            return {
                "status": "success",
                "subsystem": "hands",
                "workflow_status": workflow['final_status'],
                "download_link": workflow.get('download_link')
            }
        except Exception as e:
            logger.error(f"HANDS: Error - {e}")
            return {"status": "error", "subsystem": "hands", "error": str(e)}
    
    async def remote_uplink(self, cycle_data: dict):
        """
        Async remote communication via FastAPI.
        Non-blocking message logging and GitHub commits.
        """
        try:
            logger.info("COMM: Sending status update...")
            
            status_msg = f"Cycle #{self.cycle_count} | Brain: {cycle_data.get('brain', {}).get('confidence', 'N/A'):.2f} | Hands: {cycle_data.get('hands', {}).get('workflow_status', 'idle')}"
            
            await self.comm.log_message("ATLAS_SYSTEM", status_msg)
            
            logger.info("COMM: Message logged and committed to GitHub")
            
            return {"status": "success", "subsystem": "comm"}
        except Exception as e:
            logger.error(f"COMM: Error - {e}")
            return {"status": "error", "subsystem": "comm", "error": str(e)}
    
    async def run_cycle(self):
        """
        Main execution cycle - all tasks run in parallel (non-blocking).
        """
        self.cycle_count += 1
        
        logger.info(f"\n--- CYCLE #{self.cycle_count} START: {datetime.now().strftime('%H:%M:%S')} ---")
        
        cycle_results = {
            "cycle": self.cycle_count,
            "timestamp": datetime.now().isoformat(),
            "vision": None,
            "brain": None,
            "hands": None,
            "comm": None
        }
        
        try:
            # CONCURRENT EXECUTION: All subsystems run in parallel
            # 1. Start all autonomous tasks
            vision_task = asyncio.create_task(self.visual_reconnaissance())
            neural_task = asyncio.create_task(self.neural_analysis())
            
            # Wait for vision and brain to complete
            vision_result = await vision_task
            neural_result = await neural_task
            
            cycle_results["vision"] = vision_result
            cycle_results["brain"] = neural_result
            
            # 2. Hand execution (depends on brain output)
            hands_result = await self.execute_hands(neural_result)
            cycle_results["hands"] = hands_result
            
            # 3. Remote communication (depends on cycle results)
            comm_result = await self.remote_uplink(cycle_results)
            cycle_results["comm"] = comm_result
            
            # Log cycle results
            logger.info(f"--- CYCLE #{self.cycle_count} COMPLETE ---")
            logger.info(f"Results: {json.dumps(cycle_results, default=str, indent=2)}")
            
        except asyncio.CancelledError:
            logger.warning(f"Cycle #{self.cycle_count} was cancelled")
            raise
        except Exception as e:
            logger.error(f"Cycle #{self.cycle_count} error: {e}", exc_info=True)
        
        return cycle_results
    
    async def start_mission(self, duration_hours: float = 1.0, max_cycles: Optional[int] = None):
        """
        Start autonomous mission with non-blocking execution.
        
        :param duration_hours: Mission duration in hours
        :param max_cycles: Maximum number of cycles (None = no limit)
        """
        end_time = asyncio.get_event_loop().time() + (duration_hours * 3600)
        
        logger.info(f"Mission start! Duration: {duration_hours} hours, Max cycles: {max_cycles}")
        
        try:
            while asyncio.get_event_loop().time() < end_time:
                if max_cycles and self.cycle_count >= max_cycles:
                    logger.info(f"Max cycles ({max_cycles}) reached. Ending mission.")
                    break
                
                # Execute cycle
                await self.run_cycle()
                
                # Sleep without blocking (async sleep)
                logger.info(f"Waiting {CYCLE_INTERVAL} seconds for next cycle...")
                await asyncio.sleep(CYCLE_INTERVAL)
        
        except KeyboardInterrupt:
            logger.info("Mission interrupted by user (Ctrl+C)")
            self.shutdown()
        except Exception as e:
            logger.error(f"Mission failed: {e}", exc_info=True)
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Graceful termination sequence."""
        logger.info("\n" + "="*60)
        logger.info("SHUTDOWN SEQUENCE INITIATED...")
        logger.info("="*60)
        
        self.brain.shutdown_sequence()
        self.comm.shutdown_sequence()
        
        logger.info("ATLAS IS OFFLINE. STANDBY FOR SIR BOSS.")
        logger.info("="*60)
        
        self.is_active = False


# ==================== MAIN ====================

async def main():
    """Main entry point for async execution."""
    # Create the General
    general = AtlasGeneralAsync()
    
    # Run the mission
    # Parameters:
    #   duration_hours: 1.0 hour mission
    #   max_cycles: Limit to 5 cycles for testing
    try:
        await general.start_mission(duration_hours=1.0, max_cycles=5)
    except KeyboardInterrupt:
        general.shutdown()

if __name__ == "__main__":
    # Run the async event loop
    asyncio.run(main())
