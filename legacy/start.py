#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import time
import requests
import sys

def check_chrome_installation():
    """Check if Chrome/Chromium is installed"""
    browsers = ['chromium-browser', 'chromium', 'google-chrome']
    for browser in browsers:
        try:
            result = subprocess.run(['which', browser], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"Found browser: {browser}")
                return browser
        except:
            pass
    return None

def wait_for_backend(port=5000, timeout=30):
    """Wait for backend server to start"""
    print(f"Waiting for backend server on port {port}...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f'http://localhost:{port}/health', timeout=2)
            if response.status_code == 200:
                data = response.json()
                print(f"Backend server is ready! User: {data.get('user', 'unknown')}, Root: {data.get('is_root', False)}")
                return True
        except requests.exceptions.RequestException:
            pass
        
        # Show progress
        elapsed = int(time.time() - start_time)
        print(f"Waiting... {elapsed}s/{timeout}s", end='\r')
        time.sleep(1)
    
    print(f"\nBackend server timeout after {timeout} seconds")
    return False

def start_chrome_kiosk(port=5000):
    """Start Chrome in kiosk mode"""
    browser = check_chrome_installation()
    if not browser:
        print("Error: No Chrome/Chromium browser found!")
        print("Please install: sudo apt install chromium-browser")
        return False
    
    # Close existing Chrome processes
    print("Closing existing browser processes...")
    subprocess.run(['pkill', 'chromium-browser'], capture_output=True)
    subprocess.run(['pkill', 'chrome'], capture_output=True)
    subprocess.run(['pkill', 'chromium'], capture_output=True)
    time.sleep(2)
    
    # Check if running as root
    is_root = os.geteuid() == 0
    
    # Build Chrome command
    chrome_command = [
        browser,
        '--kiosk',
        '--noerrdialogs',
        '--disable-session-crashed-bubble',
        '--disable-infobars',
        '--disable-features=TranslateUI',
        '--disable-component-update',
        '--autoplay-policy=no-user-gesture-required',
        '--check-for-update-interval=31536000',
        '--disable-dev-shm-usage',
        '--no-first-run',
        '--disable-background-timer-throttling',
        '--disable-renderer-backgrounding',
        '--disable-backgrounding-occluded-windows',
        '--disable-pinch',  # Disable pinch-to-zoom
        '--overscroll-history-navigation=0',  # Disable swipe navigation
    ]
    
    # Add sandbox parameters if running as root
    if is_root:
        chrome_command.extend([
            '--no-sandbox',
            '--disable-setuid-sandbox',
        ])
        print("Running with root permissions, adding sandbox disable parameters")
    
    # Add URL
    url = f'http://localhost:{port}'
    chrome_command.append(url)
    
    print(f"Starting {browser} in kiosk mode...")
    print(f"URL: {url}")
    
    try:
        # Set environment variables
        env = os.environ.copy()
        if is_root:
            env['QTWEBENGINE_DISABLE_SANDBOX'] = '1'
        
        # Start Chrome
        process = subprocess.Popen(
            chrome_command,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # Check if process started successfully
        time.sleep(3)
        if process.poll() is not None:
            print("Browser failed to start")
            return False
        else:
            print("Browser started successfully in kiosk mode")
            return True
            
    except Exception as e:
        print(f"Failed to start browser: {e}")
        return False

def main():
    print("=" * 50)
    print("Smart Park Frontend Launcher")
    print("=" * 50)
    
    # Display current user info
    current_user = os.getenv('USER', 'unknown')
    is_root = os.geteuid() == 0
    print(f"Frontend running as: {current_user} (root: {is_root})")
    
    # Wait for backend server
    if not wait_for_backend():
        print("Please make sure backend service is running:")
        print("sudo python app.py")
        sys.exit(1)
    
    # Start Chrome
    if not start_chrome_kiosk():
        print("Failed to start browser frontend")
        sys.exit(1)
    
    print("Frontend is running. Press Ctrl+C to stop.")
    
    # Keep the script running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping frontend...")
        # Clean up browser processes
        subprocess.run(['pkill', 'chromium-browser'], capture_output=True)
        subprocess.run(['pkill', 'chrome'], capture_output=True)

if __name__ == '__main__':
    main()
