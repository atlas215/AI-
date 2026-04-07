"""
Project: ATLAS SYSTEM v1.0
Role: Supreme Commander (The General)
Owner: SIR BOSS
Environment: Python 3.12.8 | Mbeya, Tanzania
"""

import time
import sys
from datetime import datetime

# Importing the Atlas Specialized Modules
from BRAIN_ENGINE import AtlasBrainEngine
from VISION_SYSTEM import AtlasVisionSystem
from HAND_CONTROL import AtlasHandControl
from COMM_LINK import AtlasCommLink

class AtlasGeneral:
    def __init__(self):
        print(f"\n{'='*40}")
        print(f"SYSTEM BOOT: {datetime.now()}")
        print(f"{'='*40}")
        
        # Initialize all specialized limbs
        try:
            self.brain = AtlasBrainEngine()
            self.vision = AtlasVisionSystem()
            self.hands = AtlasHandControl()
            self.comm = AtlasCommLink(target_phone="+255XXXXXXXXX") # YOUR NUMBER HERE
            
            self.is_active = True
            print("\n[SUCCESS]: ALL SYSTEMS ONLINE. ATLAS IS READY, SIR.")
        except Exception as e:
            print(f"\n[CRITICAL]: BOOT FAILURE - {e}")
            sys.exit()

    def run_cycle(self):
        """The core operational loop of the Atlas Engine."""
        print(f"\n--- CYCLE START: {datetime.now().strftime('%H:%M:%S')} ---")
        
        # 1. VISUAL RECONNAISSANCE
        # Capture screen and save evidence
        self.vision.save_visual_evidence("AUTO_SCAN")
        
        # 2. NEURAL ANALYSIS
        # Mock features: Atlas analyzes the screen for 'Productivity Patterns'
        # In a real scenario, this data comes from VISION_SYSTEM
        environmental_data = [0.5] * 10 
        confidence = self.brain.process_input(environmental_data)
        
        # 3. DECISION MAKING
        if confidence > 0.7:
            report = "High confidence detected. Executing High-Value Task."
            # Command Hands to perform a task (e.g., Opening MSYS2)
            self.hands.press_hotkey('win', 'r')
            time.sleep(1)
            self.hands.type_string("msys2", interval=0.1)
            self.hands.press_hotkey('enter')
        else:
            report = "Environment stable. Monitoring systems..."

        # 4. REMOTE UPLINK
        # Send update to Sir Boss every cycle
        self.comm.send_whatsapp_report(f"Status: {report} | Confidence: {confidence:.2f}")

    def start_mission(self, duration_hours=1):
        """Runs the General in a loop for a specified duration."""
        end_time = time.time() + (duration_hours * 3600)
        
        try:
            while time.time() < end_time:
                self.run_cycle()
                print("Waiting 60 seconds for next cycle...")
                time.sleep(60) # Prevents bando drainage
        except KeyboardInterrupt:
            self.shutdown()

    def shutdown(self):
        """Graceful termination of the Atlas Entity."""
        print(f"\n{'='*40}")
        print("SHUTDOWN SEQUENCE INITIATED...")
        self.brain.shutdown_sequence()
        self.comm.send_whatsapp_report("SYSTEM OFFLINE. Sir, I am resting now.")
        print("ATLAS IS OFFLINE. STANDBY FOR SIR BOSS.")
        print(f"{'='*40}")

# START THE ENGINE
if __name__ == "__main__":
    # Create the General
    general = AtlasGeneral()
    
    # Run the mission for 1 hour (or as needed)
    # Ensure WhatsApp Web is OPEN and FOCUSSED for the first run test!
    general.start_mission(duration_hours=1)