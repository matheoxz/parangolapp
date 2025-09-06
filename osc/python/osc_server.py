import threading
import socket
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
from zeroconf import Zeroconf, ServiceInfo

class GenericOSCServer:
    """
    Generic OSC UDP server with mDNS advertisement.
    """
    def __init__(self, instance_name, host, port, handlers):
        self.instance_name = instance_name
        self.host = host
        self.port = port
        self.dispatcher = Dispatcher()
        for address, callback in handlers:
            self.dispatcher.map(address, callback)
        self.server = BlockingOSCUDPServer((self.host, self.port), self.dispatcher)

    def advertise(self):
        """Advertise the OSC service via mDNS."""
        # Determine IP for mDNS advertisement; prefer explicit host if not wildcard
        if self.host and self.host != "0.0.0.0":
            local_ip = self.host
        else:
            # attempt to find outbound interface IP
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.connect(("8.8.8.8", 80))
                local_ip = sock.getsockname()[0]
            except Exception:
                local_ip = "127.0.0.1"
            finally:
                try:
                    sock.close()
                except:
                    pass
        service_type = "_osc._udp.local."
        service_name = f"{self.instance_name}.{service_type}"
        server_name = f"{self.instance_name}.local."
        info = ServiceInfo(
            service_type,
            service_name,
            addresses=[socket.inet_aton(local_ip)],
            port=self.port,
            properties={},
            server=server_name
        )
        zeroconf = Zeroconf()
        zeroconf.register_service(info)
        print(f"mDNS OSC service registered: {service_name} at {local_ip}:{self.port}")

    def start(self):
        """Start the OSC server in a background thread."""
        self.advertise()
        thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        thread.start()
        print(f"Listening for OSC on {self.host}:{self.port}")
