import random
import requests
import socket
from threading import Thread

from p2pnetwork.node import Node
from p2pnetwork.nodeconnection import NodeConnection
import message_class


class TrafficAccidentSharingNode(Node):
    def __init__(self, host=""):

        port = self.find_available_port()
        super().__init__(host=host, port=port)

        self.message = None
        self.message_trigger = False
        self.roles = [0, 0, 0] # IoT, ML, AR
        self.role_list = {"I": [], "M": [], "A": []}
        self.nodes_map = {}

        master = self.ask_master(avail_port=port)
        if master[0]:
            print("You are not the master. Connecting to the master node...")
        else:
            print("You are the master. Waiting for connections from peers...")
            self.roles = [1, 1, 1]
        self.my_start(master=master)


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


    def ask_master(self, avail_port: int, hostname: str="127.0.0.1", port: int=8421) -> tuple | None:
        """
        Asks the access server to check who is the master.
        Returns a tuple. If the asker is the master, the tuple is (None, None), otherwise ({master_host}, {master_port}).
        """
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


    def connect_with_node(self, host, port, reconnect=False) -> None | NodeConnection:
        """
        Override the original method. Now the method returns the ndoe that we just connect to or None if the connection attempt fails.
        """
        if host == self.host and port == self.port:
            print("connect_with_node: Cannot connect with yourself!!")
            return None

        # Check if node is already connected with this node!
        for node in self.nodes_outbound:
            if node.host == host and node.port == port:
                print("connect_with_node: Already connected with this node (" + node.id + ").")
                return None

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.debug_print("connecting to %s port %s" % (host, port))
            sock.connect((host, port))

            # Basic information exchange (not secure) of the id's of the nodes!
            sock.send((self.id + ":" + str(self.port)).encode('utf-8')) # Send my id and port to the connected node!
            connected_node_id = sock.recv(4096).decode('utf-8') # When a node is connected, it sends its id!

            # Cannot connect with yourself
            if self.id == connected_node_id:
                print("connect_with_node: You cannot connect with yourself?!")
                sock.send("CLOSING: Already having a connection together".encode('utf-8'))
                sock.close()
                return None

            # Fix bug: Cannot connect with nodes that are already connected with us!
            #          Send message and close the socket.
            for node in self.nodes_inbound:
                if node.host == host and node.id == connected_node_id:
                    print("connect_with_node: This node (" + node.id + ") is already connected with us.")
                    sock.send("CLOSING: Already having a connection together".encode('utf-8'))
                    sock.close()
                    return None

            thread_client = self.create_new_connection(sock, connected_node_id, host, port)
            thread_client.start()

            self.nodes_outbound.add(thread_client)
            self.outbound_node_connected(thread_client)

            # If reconnection to this host is required, it will be added to the list!
            if reconnect:
                self.debug_print("connect_with_node: Reconnection check is enabled on node " + host + ":" + str(port))
                self.reconnect_to_nodes.append({
                    "host": host, "port": port, "tries": 0
                })

            print(f"Now connected with {host}:{port}.")
            return thread_client

        except Exception as e:
            self.debug_print("TcpServer.connect_with_node: Could not connect with node. (" + str(e) + ")")
            return None


    def inbound_node_connected(self, node):
        """
        When receiving a connection, makes the connection accessable thru host+port
        """
        self.nodes_map[f"{node.host}:{node.port}"] = node
        return super().inbound_node_connected(node)


    def outbound_node_connected(self, node):
        """
        When establishing a connection, makes the connection accessable thru host+port
        """
        self.nodes_map[f"{node.host}:{node.port}"] = node
        return super().outbound_node_connected(node)


    def node_message(self, node, data):
        """
        Override to trigger the main loop functions
        """
        self.message = (node, data)
        self.message_trigger = True


    def my_start(self, master: tuple):

        def receiver():
            while True:
                if self.message_trigger:
                    print(f"{self.message[0].host}:{self.message[0].port}>> {self.message[1]}.")

                    # As the master, receiving node's request for a role
                    if message_class.ask_role in self.message[1] and not master[0]:
                        node_specifier = f"{self.message[0].host}:{self.message[0].port}"
                        chosen_role = random.choice(["I", "A", "M"])
                        self.role_list[chosen_role].append(node_specifier)
                        self.send_to_node(n=self.nodes_map[node_specifier], data=message_class.set_role+chosen_role)
                        # print(f"Giving {node_specifier} the role of {chosen_role}.", self.role_list)

                    # As a non-master, receiving a role from the master
                    if message_class.set_role in self.message[1] and master[0]:
                        role = self.message[1][-1]
                        if role == "I":
                            self.roles[0] = 1
                        elif role == "M":
                            self.roles[1] = 1
                        elif role == "A":
                            self.roles[2] = 1
                        # print(f"Your role is {role}.", self.roles)


                    # reset the message and message_trigger
                    self.message = None
                    self.message_trigger = False

        self.start()
        if master[0]:
            master_node = self.connect_with_node(master[0], int(master[1]))
            self.send_to_node(master_node, message_class.ask_role)
        else:
            pass
            # TODO
                # IoT nodes calls the IoT services, and sends request to ML peers
                # ML nodes calls the ML services
                # whenever a node wants traffic info, it calls the XR nodes
                # XR nodes calls the XR services and sends the image to the requester
                # the Master node by default takes all responsibilities to avoid cases where not enough nodes are present

        t_receive = Thread(target=receiver)
        t_receive.start()

        while True:
            input_command = input(
"""
Please input the command:\n
\t [Q]uit the network\n
\t [R]equest accident info\n
>>\t
"""
            )
            if input_command == "Q":
                if master[0]:
                    self.send_to_node(master_node, message_class.leave + str(self.roles))
                    self.node_request_to_stop()
                else:
                    # TODO From all inbound nodes randomly select one to be the new master
                        # Inform everyone that the master should change
                    self.node_request_to_stop()


if __name__ == "__main__":
    myNode = TrafficAccidentSharingNode()

