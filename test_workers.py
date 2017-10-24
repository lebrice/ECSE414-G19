#!/usr/bin/python3

import unittest
from workers import *


class ReaderWriterTestCase(unittest.TestCase):
    def test_read_equals_sent(self):
        """
        Test that the messages read by the SocketReader correspond to those
        originally written by the SocketWriter.
        """
        message_count = 10

        # Start a reader, and let him wait for a connection.
        # Where the Reader puts incoming objects
        received_objects = ClosableQueue()
        reader = SocketReader(12345, received_objects)
        reader.start()  # Start the reader. It will wait for messages.

        # Create random messages to write to a socket
        original_messages = random_test_messages(message_count)
        # The messages to be written are held in a ClosableQueue
        messages_to_send = ClosableQueue()
        for m in original_messages:
            messages_to_send.put(m)  # Add each message to the queue.

        # Create a SocketWriter, and give him the queue of messages to send.
        writer = SocketWriter(messages_to_send, socket.gethostname(), 12345)
        writer.start()  # Start the writer

        # close the writing queue, which eventually stops the writer thread
        messages_to_send.close()
        # wait until all messages have been processed by the SocketWriter.
        writer.join()

        # If a message is done being sent by the socketWriter, than it is
        # also done being received by the socketReader, since we use TCP.

        # wait for the reader to have finished reading all messages.
        reader.join()

        messages = []
        for json_object in received_objects:
            # convert the received json to an OnionMessage instance
            message = OnionMessage.from_json(json_object)
            # print("successfully received:", message)
            messages.append(message)

        # Assert that both lists should match perfectly.
        self.assertCountEqual(messages, original_messages)


def random_test_messages(count):
    return [random_test_message(i*5) for i in range(count)]


def random_test_message(size):
    data = random_string(size)
    bob = f"""
        {{
            "header": "ONION ROUTING G12",
            "source": "127.0.0.1",
            "destination": "",
            "data": "{data}"
        }}
    """
    return OnionMessage.from_json_string(bob)


def random_string(length=1):
    import random
    import string
    letters = [random.choice(string.ascii_letters) for i in range(length)]
    return ''.join(letters)