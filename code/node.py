"""
Ruochen Miao rm5327 and Chengying Wang cw4450
"""
import random
import socket
from threading import Thread
import requests


from p2pnetwork.node import Node
from p2pnetwork.nodeconnection import NodeConnection


class TrafficAccidentSharingNode(Node):
    """
    Node of the proejct
    """
    def __init__(self, host="", hostname: str="127.0.0.1", hostport: int=8421):

        port = self.find_available_port()
        super().__init__(host=host, port=port, max_connections=999)

        self.hostname = hostname
        self.hostport = hostport
        self.message = None
        self.message_trigger = False
        self.role = None # [I]oT, [M]L, [A]R
        self.role_list = {"I": [], "M": [], "A": []}
        self.nodes_map = {}

        self.master = self.ask_master(avail_port=port)
        if not self.is_master:
            print("You are not the master. Connecting to the master node...")
        else:
            print("You are the master. Waiting for connections from peers...")
        self.my_start()


    @property
    def is_master(self):
        """
        If the node is the master node
        """
        return not self.master[0]


    def find_available_port(self) -> int:
        """
        Finds an available port for the node to use.
        """
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


    def ask_master(self, avail_port: int) -> tuple | None:
        """
        Asks the access server to check who is the master.
        Returns a tuple. If the asker is the master, the tuple is (None, None), otherwise ({master_host}, {master_port}).
        """
        url = f"http://{self.hostname}:{self.hostport}/"
        headers = {"port": str(avail_port)}
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                if response.headers["Master"] == "True":
                    return (None, None)
                if response.headers["Master"] == "False":
                    master_host = response.headers["Master_host"]
                    master_port = response.headers["Master_port"]
                    return (master_host, master_port)
            else:
                print(f"GET request failed with status code {response.status_code}.")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")


    def inbound_node_connected(self, node):
        """
        When receiving a connection, makes the connection accessable thru host+port
        """
        self.nodes_map[f"{node.host}:{node.port}"] = node


    def outbound_node_connected(self, node):
        """
        When establishing a connection, makes the connection accessable thru host+port
        """
        self.nodes_map[f"{node.host}:{node.port}"] = node


    def node_message(self, node, data):
        """
        Override to handle income messages
        """
        print(f"[Testing msg] {node.host}:{node.port}>> {data}.") # Debugging purpose

        # As the master, receiving node's request for a role
        if data["type"] == "ASKROLE" and self.is_master:
            # The node that requests a role
            node_specifier = f"{node.host}:{node.port}"
            # Choose the role
            if not self.role_list["A"]: # Prioritize AR service
                chosen_role = "A"
            elif not self.role_list["M"]:
                chosen_role = "M"
            elif not self.role_list["I"]:
                chosen_role = "I"
            else:
                chosen_role = random.choice(["I", "A", "M"])
            # Record the role and send the role to the requester
            self.role_list[chosen_role].append(node_specifier)
            self.send_to_node(n=self.nodes_map[node_specifier], data={"type": "SETROLE", "ROLE": chosen_role})
            # Also send the existing peers to the requester
            peers = list(self.nodes_map.keys())
            peers.remove(node_specifier)
            self.send_to_node(n=self.nodes_map[node_specifier], data={"type": "NEWPEER", "PEER": peers})
            # print(f"Giving {node_specifier} the role of {chosen_role}.", self.role_list)


        # As a non-master, receiving new peers
        elif data["type"] == "NEWPEER" and not self.is_master:
            for peer in data["PEER"]:
                new_host, new_port = peer.split(":")
                self.connect_with_node(host=new_host, port=int(new_port))


        # As a non-master, receiving a role from the master
        elif data["type"] == "SETROLE" and not self.is_master:
            self.role = data["ROLE"]
            print(f"Your role is {self.role}.")


        # As the master, receiving node's request to leave
        elif data["type"] == "LEAVE" and self.is_master:
            self.role_list[data["ROLE"]].remove(f"{node.host}:{node.port}")


        # As a non-master, receiving master's info of the new master
        elif data["type"] == "NEWMASTER":
            self.master = [data["host"], data["port"]]


        # As a non-master, receiving master's request to be the new master
        elif data["type"] == "INHERIT":
            self.master = [None, None]
            self.role_list = data["roles"]


        elif data["type"] == "DISCONNECT":
            del self.nodes_map[f"{node.host}:{node.port}"]


        # As the master, receiving node's request for a service
        # TODO


    def IoT_service(self):
        """
        For the node to access the IoT service on the cloud.
        """
        print("IoT to be implemented")


    def ML_service(self):
        """
        For the node to access the ML service on the cloud.
        """
        print("ML to be implemented.")



    def AR_service(self):
        """
        For the node to access the AR service on the cloud.
        """
        print("AR to be implemented.")


    def my_start(self):
        """
        Main loop of the node
        """
        self.start()

        if not self.is_master:
            self.connect_with_node(self.master[0], int(self.master[1]))
            self.send_to_node(n=self.nodes_map[f"{self.master[0]}:{self.master[1]}"], data={"type": "ASKROLE"})

        # TODO
            # IoT nodes calls the IoT services, and sends request to ML peers
            # ML nodes calls the ML services
            # whenever a node wants traffic info, it calls the XR nodes
            # XR nodes calls the XR services and sends the image to the requester

        while not self.terminate_flag.is_set():

            input_command = input("-"*50 + "\n" + "Please input the command:\n\t [Q]uit the network\n\t [R]equest accident info\n>>\n" + "-"*50 + "\n")

            if input_command == "Q": # Quitting
                self.send_to_nodes(data={"type": "DISCONNECT"})
                if not self.is_master: # not the master
                    self.send_to_node(n=self.nodes_map[f"{self.master[0]}:{self.master[1]}"], data={"type": "LEAVE", "ROLE": self.role})
                    self.stop()
                else: # being the master
                    if len(self.nodes_map) == 0: # No one else in the network
                        url = f"http://{self.hostname}:{self.hostport}/leave"
                        try:
                            response = requests.get(url)
                            if response.status_code == 200:
                                self.stop()
                        except requests.exceptions.RequestException as e:
                            print(f"An error occurred: {e}")
                    else: # someone else in the network
                        new_master = random.sample(population=list(self.nodes_map.keys()), k=1)[0] # randomly select the new master
                        new_host, new_port = new_master.split(":")

                        for role, lissy in self.role_list.items():
                            if new_master in lissy:
                                self.role_list[role].remove(new_master)
                        self.send_to_nodes(data={"type": "NEWMASTER", "host": new_host, "port": new_port}, exclude=[self.nodes_map[new_master]])
                        self.send_to_node(n=self.nodes_map[new_master], data={"type": "INHERIT", "roles": self.role_list})

                        # update the master record on the access server
                        url = f"http://{self.hostname}:{self.hostport}/new"
                        headers = {"host": new_host, "port": new_port}
                        try:
                            response = requests.get(url, headers=headers)
                            if response.status_code == 200:
                                self.stop()
                            else:
                                print(f"GET request failed with status code {response.status_code}.")
                        except requests.exceptions.RequestException as e:
                            print(f"An error occurred: {e}")

            elif input_command == "R":
                pass

            elif input_command == "_L": # For debugging purpose, print local attributes
                print("Debugging:")
                print(self.nodes_map)
                print(self.role_list)
                print(self.master)


if __name__ == "__main__":
    myNode = TrafficAccidentSharingNode()
