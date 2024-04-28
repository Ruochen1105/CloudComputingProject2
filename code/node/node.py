import requests
import socket

def find_available_port() -> int:
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

def send_get_request(hostname: str, port: int, avail_port: int) -> None:
    url = f"http://{hostname}:{port}/"    # Construct the URL using the provided hostname and port
    headers = {"port": avail_port}    # The port to receive connection from peers.
    try:
        response = requests.get(url, headers=headers)  # Send the GET request
        if response.status_code == 200:
            print("GET request successful!")
            print("Response headers:")
            for key, value in response.headers.items():
                print(f"{key}: {value}")  # Print the response headers
            print("\nResponse body:")
            print(response.text)  # Print the response content
        else:
            print(f"GET request failed with status code {response.status_code}.")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    print(find_available_port())
