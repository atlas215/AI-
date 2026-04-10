"""
Module: VISION_SYSTEM
Purpose: Visual Input and Image Processing for ATLAS System
Owner: SIR, BURTON
Libraries: OpenCV, PyAutoGUI, Pillow, NumPy
"""

import cv2
import numpy as np
import pyautogui
from PIL import Image, ImageGrab
from datetime import datetime
import os

class AtlasVisionSystem:
    def __init__(self):
        """Initializes the Optical Sensors and Workspace Directory."""
        self.version = "ATLAS-VS-V1.0"
        self.screenshot_dir = "atlas_vision_logs"
        
        # Ensure directory for visual logs exists
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)
            
        print(f"[{datetime.now()}] INFO: {self.version} Optical Sensors Online.")

    def capture_full_screen(self):
        """Captures the current desktop state and converts to OpenCV format."""
        # Grab screen using Pillow
        screenshot = ImageGrab.grab()
        # Convert to NumPy array (OpenCV uses BGR format)
        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        return frame

    def find_template_on_screen(self, template_path, threshold=0.8):
        """
        Scans the screen for a specific image pattern (e.g., WhatsApp Icon).
        :param template_path: Path to the small image to look for
        :param threshold: Matching accuracy (0.0 to 1.0)
        :return: Center coordinates (x, y) if found, else None
        """
        screen = self.capture_full_screen()
        template = cv2.imread(template_path)
        
        if template is None:
            print(f"ERROR: Template file {template_path} not found.")
            return None

        # Template Matching Logic
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val >= threshold:
            # Calculate center of the found object
            h, w = template.shape[:2]
            center_x = max_loc[0] + (w // 2)
            center_y = max_loc[1] + (h // 2)
            return (center_x, center_y)
        
        return None

    def save_visual_evidence(self, label="SCREEN_REPORT"):
        """Saves a timestamped screenshot for SIR, BURTON's review."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.screenshot_dir}/{label}_{timestamp}.png"
        
        pyautogui.screenshot(filename)
        print(f"VISUAL LOG: Screenshot saved as {filename}")
        return filename

    def analyze_pixel_color(self, x, y):
        """Checks the color at a specific coordinate (Useful for Status Lights)."""
        screen = ImageGrab.grab()
        pixel_color = screen.getpixel((x, y))
        return pixel_color # Returns (R, G, B)

# Unit Test for SIR, BURTON
if __name__ == "__main__":
    vision = AtlasVisionSystem()
    
    # 1. Test Full Screen Capture
    print("Testing Optical Capture...")
    img = vision.capture_full_screen()
    print(f"Capture successful. Resolution: {img.shape[1]}x{img.shape[0]}")
    
    # 2. Save Evidence
    log_path = vision.save_visual_evidence("BOOT_CHECK")
    
    # 3. Test Pixel Reading
    center_color = vision.analyze_pixel_color(500, 500)
    print(f"Color detected at (500,500): {center_color}")