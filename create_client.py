#!/usr/bin/python3

import argparse
import json
import os
import socket
import webbrowser

import onion_client
from onion_client import OnionClient
import node
from node import OnionNode
import get_request


def _write_to_html(filename, payload):
    # create the network file if it doesn't exist,
    try:
        f = open(filename, 'x')
    except FileExistsError:
        f = open(filename, 'w')
        f.seek(0)

    f.write(payload)
    f.close()



def main():
    """
    Use: 
        > python create_node.py -port 12346 [-dirIP '185.172.0.3' -dirPort 12345]
    """

    directory_node_ip = None
    directory_node_port = None
    try:
        with open("config.json") as config_file:
            print("Loading Directory Node Info from 'config.json' file...")
            config = json.load(config_file)
            directory_node_ip = config['DIR_NODE_IP']
            directory_node_port = config['DIR_NODE_PORT']
    except FileNotFoundError:
        raise RuntimeWarning("'config.json' file not found")

    parser = argparse.ArgumentParser(
        description='Initialize a node in the onion_routing network.'
    )
    parser.add_argument(
        '-ip',
        action='store',
        dest='ip',
        type=str,
        default=socket.gethostname(),
        help='the ip to create the node on.'
    )
    parser.add_argument(
        '-port',
        action='store',
        dest='port',
        type=str,
        help='the port to create the node on.'
    )
    parser.add_argument(
        '-dirIP',
        action='store',
        dest='dirIP',
        type=str,
        default=directory_node_ip,
        help='the IP address of the Directory Node.'
    )
    parser.add_argument(
        '-dirPort',
        action='store',
        dest='dirPort',
        type=int,
        default=directory_node_port,
        help='the Port the Directory Node is listening on.'
    )

    args = parser.parse_args()

    print("Using Directory Node IP:", args.dirIP)
    print("Using Directory Node PORT:", args.dirPort)

    if args.port is None:
        raise RuntimeError("Invalid 'port' argument")

    url = input("Please Enter a Url: ('www.perdu.com', for example)\n")

    import time
    start_time = time.time()

    client = OnionClient(args.ip, int(args.port), 3)
    client.connect(args.dirIP, int(args.dirPort))

    print("#####REQUESTING#####")
    will = client.send_through_circuit(url)
    filename = 'returned.html'
    _write_to_html(filename, will)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print("Elapsed_time: (with Onion Routing)   \t", elapsed_time, "seconds")

    webbrowser.get().open('file://' + os.path.realpath(filename), 1)
    # WITHOUT onion routing:

    start_time_2 = time.time()
    response = get_request.web_request(url).decode()
    filename_2 = 'returned2.html'
    _write_to_html(filename_2, response)
    end_time_2 = time.time()

    elapsed_time_2 = end_time_2 - start_time_2

    print("Elapsed_time: (without Onion Routing)\t", elapsed_time_2, "seconds")
    webbrowser.get().open('file://' + os.path.realpath(filename_2), 1)
    print("DONE")

if __name__ == '__main__':
    main()

