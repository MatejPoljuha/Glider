import json
import socket
import random
import queue
from time import sleep


def receive_server(receiving_port: int, comm_queue: queue.Queue = None, host_ip='127.0.0.1'):
    """
    Sets up a socket that listens for incoming connections and receives data.
    :param receiving_port: port on which the socket listens on
    :param comm_queue: queue in which the received data is pushed
    :param host_ip: localhost
    :return:
    """
    # creates socket object and allows it to be reused if program is relaunched (needed for Linux/Mac)
    with socket.socket() as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # binds the socket to localhost and desired port
        sock.bind((host_ip, receiving_port))

        # socket starts listening for connections, can ignore 5 unaccepted connections before refusing further ones
        sock.listen(5)
        print('Socket is listening on port: ', receiving_port)

        while True:
            # creates a new temporary socket to receive data on
            temp_socket, address = sock.accept()

            with temp_socket:
                print('Accepted connection from: ', address)
                # receives the data and converts it into dictionary
                json_received = json.loads(temp_socket.recv(1024))
                print("Json received -->", json_received)

                # puts received data in a queue
                if comm_queue is not None:
                    comm_queue.put(json_received)


def send_client(destination_port: int, input_dict: dict, host_ip='127.0.0.1'):
    # converts input dictionary into json
    json_to_send = json.dumps(input_dict)

    # creates socket object and allows it to be reused if program is relaunched (needed for Linux/Mac)
    with socket.socket() as sock:
        # try to connect to the server socket and send the dictionary(json) to it
        try:
            sock.connect((host_ip, destination_port))
            sock.send(json_to_send.encode('utf-8'))
        except ConnectionRefusedError:
            print('Connection refused on port: ', destination_port)

        print(json_to_send, 'was sent to server on port: ', destination_port)

        # close socket after sending the data
        sock.close()


def simulate_dps_messages():
    while True:
        temp_dict = {'aircraft_position': [random.randint(0, 400), random.randint(0, 400)]}
        send_client(destination_port=1501, input_dict=temp_dict)
        sleep(3.0)
