import os
from dotenv import load_dotenv

load_dotenv()

class ProxyManager:
    def __init__(self):
        self.username = os.getenv("ROYAL_USER")
        self.password = os.getenv("ROYAL_PASS")
        self.sticky_ip = os.getenv("STICKY_IP_ENDPOINT")

    def get_proxy_config(self):
        # Returns the formatted string for tools like Proxifier or Requests
        return f"http://{self.username}:{self.password}@{self.sticky_ip}"

print("Proxy Handler Secured.")
