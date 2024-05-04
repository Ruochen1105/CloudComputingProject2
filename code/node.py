import requests
import socket

from p2pnetwork.node import Node


class TrafficAccidentSharingNode(Node):
    def __init__(self, host=""):
        port = self.find_available_port()
        file_port = self.find_available_port()
        super().__init__(host, port, file_port)
        master = self.ask_master(avail_port=port)
        if master[0]:
            self.master = False
            self.master_host, self.master_port = master
            print("You are not the master. Connecting to the master node...")
        else:
            self.master = True
            self.master_host, self.master_port = None, None
            print("You are the master. Waiting for connections from peers...")
        if self.master:
            self.start()
        else:
            self.start()
            self.connect_with_node(host=self.master_host, port=int(self.master_port))


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
        url = f"http://{hostname}:{port}/"
        headers = {"port": str(avail_port)}
        try:
            response = requests.get(url, headers=headers)
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


    def my_start(self):
        pass
        # TODO: starts the node while accepting inputs from cmd (and invoke corresponding methods)

if __name__ == "__main__":
    myNode = TrafficAccidentSharingNode()

