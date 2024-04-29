import requests
import socket

from python_p2p.node import Node


class TrafficAccidentSharingNode(Node):
    def __init__(self, host=""):
        port = self.find_available_port()
        file_port = self.find_available_port()
        super().__init__(host, port, file_port)
        master = self.ask_master(avail_port=port)
        if master[0]:
            self.master = False
            self.master_host = master[0]
            self.master_port = master[1]
            print("You are not the master. Connecting to the master node...")
        else:
            self.master = True
            print("You are the master. Waiting for connections from peers...")


    def find_available_port(self) -> int:
        # Create a socket object
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            # Bind the socket to an available port
            s.bind(('localhost', 0))
            # Get the port number assigned by the OS
            port = s.getsockname()[1]
            return port
        except socket.error as e:
            print(f"Failed to find an available port: {e}")
        finally:
            # Close the socket
            s.close()


    def ask_master(self, avail_port: int, hostname: str="127.0.0.1", port: int=8421) -> tuple:
        url = f"http://{hostname}:{port}/"    # Construct the URL using the provided hostname and port
        headers = {"port": str(avail_port)}    # The port to receive connection from peers.
        try:
            response = requests.get(url, headers=headers)  # Send the GET request
            if response.status_code == 200:
                if response.headers["Master"] == "True":
                    return (None, None)
                elif response.headers["Master"] == "False":
                    master_host = response.headers["Master_host"]
                    master_port = response.headers["Master_port"]
                    return (master_host, master_port)
            else:
                print(f"GET request failed with status code {response.status_code}.")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    myNode = TrafficAccidentSharingNode()

