#!/usr/bin/python3
"""
    Module that defines the Onion Client, used by the user to communicate
    through the onion routing network
"""
from contextlib import contextmanager
import random
import socket
import json
import time
import packet_manager as pm
from errors import OnionSocketError, OnionNetworkError

import sender_circuit_builder as scb
import circuit_tables as ct
import RSA

BUFFER_SIZE = 1024 # Constant for now
DEFAULT_TIMEOUT = 1

class OnionClient():
    def __init__(self, number_of_nodes):
        self.initialized = False
        self.number_of_nodes = number_of_nodes

        self.circuit_table = ct.circuit_table()
        self.sender_key_table = ct.sender_key_table()
        self.network_list = {}

    def connect(self, dir_ip, dir_port):
        """
            called from exterior to tell client to prepare for transmission
            - fetch network list
            - build circuit
        """
        self._contact_dir_node(dir_ip, dir_port)
        self._build_circuit()
        self.initialized = True

    def send(self, data):
        """
            called from exterior to tell client to send message through the circuit
        """
        if not self.initialized:
            print("ERROR     Client not initialized. Call OnionClient.connect() first.\n")
            return

        print("You tried to send a message\n")


    def recv(self, buffer_size):
        """ Receives the given number of bytes from the Onion socket.
        """
        raise NotImplementedError()

    def _contact_dir_node(self, dir_ip, dir_port):
        """
            query dir node for network list, without including the client in the list of nodes
            this avoids the problem of the client using itself as a node later on

        """

        pkt = pm.new_dir_packet("dir_query", 0, 0)
        self._create(dir_ip, dir_port)
        self._send(pkt)

        # wait for a response packet; 3 tries
        tries = 3
        rec_bytes = 0
        while tries != 0:
            try:
                rec_bytes = self.client_socket.recv(BUFFER_SIZE)
            except socket.timeout:
                tries -= 1
                if tries == 0:
                    print("ERROR    Timeout while waiting for confirmation packet [3 tries]\n")
                    print("         Directory connection exiting. . .")
                    self._close()
                    return
                continue

        message = json.load(rec_bytes.decode())

        if message['type'] != "dir":
            print("ERROR    Unexpected answer from directory")
            self._close()

        self.network_list = message['table']


    def _select_random_nodes(self):
        if len(self.network_list) < self.number_of_nodes:
            print("ERROR    There are not enough nodes to build the circuit. Current: ",
                  len(self.network_list), "requested", self.number_of_nodes)
            return

        return random.sample(self.network_list['nodes in network'], self.number_of_nodes)


    def _build_circuit(self):
        nodes = self._select_random_nodes()
        builder = scb.SenderCircuitBuilder(nodes, self.circuit_table, self.sender_key_table)
        builder.start()
        builder.join()


    def _create(self, ip, port):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((ip, port))

    def _send(self, message_str):
        message_bytes = message_str.encode('utf-8')
        self.client_socket.sendall(message_bytes)

    def _close(self):
        self.client_socket.close()



