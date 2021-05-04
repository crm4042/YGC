import asyncio
import json
import multiprocessing
import select
import socket
import time
import threading


"""
Author: Chris Murphy
"""


class Node:

	"""
	Represents a node of communication for point-to-point
	communication between parties
	"""

	def __init__(self, host, port):
		
		"""
		Initializes the connection for the node.

		:param self:	Node	The node object.
		:param host:	str		The hostname.
		:param port: 	int		The port number.
		"""

		self.host = host
		self.port = port
		self.stop = False

		self.message_list = list()

		# Creates the server
		self.socket_server = socket.socket(socket.AF_INET, \
			socket.SOCK_STREAM)
		# print("Bound to "+str((self.host, self.port)))
		self.socket_server.bind((self.host, self.port))
		self.socket_server.listen()

		self.server_connections = dict()

		# Creates the clients
		self.socket_clients = dict()
		self.socket_clients_lock = threading.Lock()

		# Creates a listener daemon
		self.listener = threading.Thread(name='daemon',\
			target=self.listen)
		self.listener.setDaemon(True)
	
	def connect(self, addr_list):
		
		"""
		Connects to other addresses
		:
		"""

		def connect_server():
			#print("Connecting to server")
			conn, addr = self.socket_server.accept()
			self.server_connections[addr] = conn
			#print("Finished connecting to server")

		def connect_client(addr):
			time.sleep(1)
			#print("Connecting to client at "+str(addr))
			client = socket.socket(socket.AF_INET, \
				socket.SOCK_STREAM)
			client.connect(addr)
			self.socket_clients_lock.acquire()
			self.socket_clients[addr] = client
			self.socket_clients_lock.release()
			#print("Finished connecting to client")


		threads = list()
		for addr in addr_list:
			if (self.host, self.port) == addr:
				continue

			# Creates the threads
			thread1 = threading.Thread(target=connect_server)
			thread2 = threading.Thread(target=connect_client, \
				args=[addr])

			# Starts the threads
			thread1.start()
			thread2.start()

			threads.append(thread1)
			threads.append(thread2)

		# joins the threads
		for thread in threads:
			thread.join()

		self.listener.start()

	def listen(self):
		
		"""
		Listens for incoming communications
		"""

		while not self.stop:
			receiving_connections = dict()
			for client in self.server_connections.values():
				receiving_connections[client.fileno()] = client
			read, _, _ = select.select(list(receiving_connections.keys()), [], [], .1)
			for connection in read:
				received = receiving_connections[connection].recv(16384)
				received_str = str(received, encoding='utf-8')
				if len(received_str) > 0:
					try:
						message = json.loads(received_str)
						if message is not None:
							self.message_list.append(message)
					except:
						print()

		for client in self.socket_clients.values():
			client.close()
		
		self.socket_server.close()

	def close(self):

		"""
		Closes a node's sockets
		:return: 				None
		"""

		self.stop = True
		time.sleep(3)
		while self.listener.isAlive():
			pass

	def send_messages(self, message_dict):

		"""
		Sends a set of messages

		:param message_dict: 	dict	The messages to send in the form {addr: msg}
		:return: 				None
		"""

		for addr in message_dict.keys():
			if addr == (self.host, self.port):
				if message_dict[addr] != None:
					self.message_list.append(message_dict[addr])
			else:
				self.socket_clients[addr].sendall(bytes(json.dumps(message_dict[addr]), encoding='utf-8'))

	def get_message_at(self, index):

		"""
		Gets the message at a certain index in the message list

		:param index: 			int		The index to get the message at
		:return: 						The message at the index
		"""

		while len(self.message_list) < index+1:
			pass
		return self.message_list[index]


NUM_PARTIES = 2
HOST = "127.0.0.1"
START_PORT = 9095

def init_node(party_num):

	"""
	Initializes two nodes for testing

	:param party_num: 			int		The number of the node to initialize
	:return: 					None
	"""

	addr_list = [(HOST, START_PORT + party) for party in range(NUM_PARTIES)]
	node = Node(addr_list[party_num][0], addr_list[party_num][1])
	try:
		node.connect(addr_list)
		time.sleep(3)
		messages = {addr: ("message", "Hello") for addr in addr_list}
		node.send_messages(messages)
		print("Sent messages")

	except Exception as e:
		print(e)

	finally:
		print("Closing")
		try:
			while True:
				pass
		finally:
			node.close()

def main():
	for party in range(NUM_PARTIES):
		party_process = multiprocessing.Process(target=init_node,\
			args=(party,))
		party_process.start()

	while True:
		pass

if __name__ == '__main__':
	main()
