import random
import requests
import socket
from threading import Thread

from p2pnetwork.node import Node
from p2pnetwork.nodeconnection import NodeConnection


class TrafficAccidentSharingNode(Node):
    def __init__(self, host="", hostname: str="127.0.0.1", hostport: int=8421):

        port = self.find_available_port()
        super().__init__(host=host, port=port)

        self.hostname = hostname
        self.hostport = hostport
        self.message = None
        self.message_trigger = False
        self.role = None # [I]oT, [M]L, [A]R
        self.role_list = {"I": [], "M": [], "A": []}
        self.nodes_map = {}

        self.master = self.ask_master(avail_port=port)
        if self.master[0]:
            print("You are not the master. Connecting to the master node...")
        else:
            print("You are the master. Waiting for connections from peers...")
            self.roles = [1, 1, 1] # the master node can do everything
        self.my_start()


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
            print("here")
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


    def msg_receiver(self):
        while not self.terminate_flag.is_set():
            if self.message_trigger:
                print(f"[Testing msg] {self.message[0].host}:{self.message[0].port}>> {self.message[1]}.")

                # As the master, receiving node's request for a role
                if self.message[1]["type"] == "ASKROLE" and not self.master[0]:
                    # The node that requests a role
                    node_specifier = f"{self.message[0].host}:{self.message[0].port}"
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
                    # print(f"Giving {node_specifier} the role of {chosen_role}.", self.role_list)

                # As a non-master, receiving a role from the master
                if self.message[1]["type"] == "SETROLE" and self.master[0]:
                    self.role = self.message[1]["ROLE"]
                    print(f"Your role is {self.role}.")


                # As the master, receiving node's request to leave
                if self.message[1]["type"] == "LEAVE" and not self.master[0]:
                    leaving_role = self.message[1]["ROLE"]
                    node_specifier = f"{self.message[0].host}:{self.message[0].port}"
                    self.role_list[leaving_role].remove(node_specifier)
                    del self.nodes_map[node_specifier]


                # As the master, receiving node's request for a service
                # TODO


                # reset the message and message_trigger
                self.message = None
                self.message_trigger = False


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
        self.start()
        if self.master[0]: # not the master
            master_node = self.connect_with_node(self.master[0], int(self.master[1]))
            self.send_to_node(n=master_node, data={"type": "ASKROLE"})
        else: # being the master
            pass

        # TODO
            # IoT nodes calls the IoT services, and sends request to ML peers
            # ML nodes calls the ML services
            # whenever a node wants traffic info, it calls the XR nodes
            # XR nodes calls the XR services and sends the image to the requester

        t_receive = Thread(target=self.msg_receiver)
        t_receive.start()

        while not self.terminate_flag.is_set():

            input_command = input("-"*50 + "\n" + "Please input the command:\n\t [Q]uit the network\n\t [R]equest accident info\n>>\n" + "-"*50 + "\n")

            if input_command == "Q": # Quitting
                if self.master[0]: # not the master
                    self.send_to_node(n=master_node, data={"type": "LEAVE", "ROLE": self.role})
                    self.stop()
                    t_receive.join()
                    print("Receiver stopped.")
                else: # being the master
                    if len(self.nodes_map) == 0: # No one else in the network
                        url = f"http://{self.hostname}:{self.hostport}/leave"
                        try:
                            response = requests.get(url)
                            if response.status_code == 200:
                                self.stop()
                                t_receive.join()
                                print("Receiver stopped.")
                        except requests.exceptions.RequestException as e:
                            print(f"An error occurred: {e}")
                    pass
                    # TODO
                        # From all inbound nodes randomly select one to be the new master
                        # Inform everyone that the master should change
                        # Tell the access server that the master changes
                    self.stop()
                    t_receive.join()
                    print("Receiver stopped.")

            elif input_command == "R":
                pass

            elif input_command == "_L" and not self.master[0]: # For debugging purpose, list local attributes
                print("Debugging:")
                print(self.nodes_map)
                print(self.role_list)


if __name__ == "__main__":
    myNode = TrafficAccidentSharingNode()
    myNode.join()
    print("Node stopped.")

