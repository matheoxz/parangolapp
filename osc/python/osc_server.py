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
        try:
            local_ip = socket.gethostbyname(socket.gethostname())
        except Exception:
            local_ip = "127.0.0.1"
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
