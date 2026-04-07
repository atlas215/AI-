"""
Module: HAND_CONTROL
Purpose: Physical Hardware Interaction and Execution for ATLAS System
Owner: SIR BOSS
Libraries: PyAutoGUI, Time
"""

import pyautogui
import time
import sys
from datetime import datetime

# Safety Feature: Move mouse to any corner of the screen to abort Atlas
pyautogui.FAILSAFE = True

class AtlasHandControl:
    def __init__(self):
        """Initializes Hardware Controllers and Action Speed."""
        self.version = "ATLAS-HC-V1.0"
        # Standard delay between actions (0.5 seconds for stability)
        pyautogui.PAUSE = 0.5
        print(f"[{datetime.now()}] INFO: {self.version} Executive Limbs Online.")

    def move_to_and_click(self, x, y, clicks=1, button='left'):
        """
        Moves the cursor to coordinates and performs a click.
        :param x, y: Screen coordinates from VISION_SYSTEM
        """
        try:
            # Human-like movement duration (0.2s)
            pyautogui.moveTo(x, y, duration=0.2, tween=pyautogui.easeInOutQuad)
            pyautogui.click(clicks=clicks, button=button)
            return True
        except Exception as e:
            print(f"ERROR: Hand Execution Failed at {x},{y} - {e}")
            return False

    def type_string(self, text, interval=0.05):
        """
        Types text as if a human were typing.
        :param text: String to type (e.g., C code or WhatsApp message)
        :param interval: Delay between each character
        """
        pyautogui.write(text, interval=interval)

    def press_hotkey(self, *args):
        """
        Executes keyboard combinations (e.g., 'ctrl', 's').
        """
        pyautogui.hotkey(*args)

    def scroll_desktop(self, amount):
        """Scrolls up (positive) or down (negative)."""
        pyautogui.scroll(amount)

    def emergency_stop(self):
        """Immediate system exit logic."""
        print("CRITICAL: EMERGENCY STOP TRIGGERED BY SIR BOSS.")
        sys.exit()

# Unit Test for Sir Boss
if __name__ == "__main__":
    hands = AtlasHandControl()
    
    print("Testing Hand Precision...")
    
    # 1. Test Mouse Movement
    # Moves mouse to the center of a standard 1920x1080 screen
    hands.move_to_and_click(960, 540, clicks=0) 
    
    # 2. Test Typing Simulation
    # WARNING: This will type wherever your cursor is active
    print("Typing Readiness Message in 2 seconds...")
    time.sleep(2)
    hands.type_string("// ATLAS SYSTEM: READY FOR C-CONSTRUCTION, SIR.", interval=0.02)
    
    print("\n[SUCCESS]: Hardware Interface Verified.")