import Node
import Utilities

import math
import multiprocessing
import nacl.encoding
import nacl.secret
import nacl.utils
import random


HOST = "0.0.0.0"
PORT = 10124


ENCODER = nacl.encoding.RawEncoder()


class OT_Sender:

    """
    Oblivious Transfer sender's (Alice) protocol.
    This corresponds to Parakh's protocol defined in:
    https://arxiv.org/pdf/0909.2852.pdf
    """

    def __init__(self, host, port, partner_host, partner_port, prime, generator, uniform1, uniform2, secret1, secret2):
        self.node = Node.Node(host, port)
        self.node.connect([(partner_host, partner_port)])
        self.addr = (host, port)
        self.partner_addr = (partner_host, partner_port)
        self.prime = prime
        self.generator = generator
        self.uniform1 = uniform1
        self.uniform2 = uniform2
        self.secret1 = secret1
        self.secret2 = secret2

    def protocol(self):

        try:
            # print("x1: " + str(self.uniform1))
            # print("x2: " + str(self.uniform2))

            # 1) Generates the nonce N_A_1 and sends g^{x_1+N_A_1} mod p
            N_A_1 = random.randint(1, self.prime-1)
            message_1 = Utilities.square_multiply(self.generator, self.uniform1+N_A_1, self.prime)
            self.node.send_messages({self.partner_addr: message_1})
            # print("NA1: "+str(N_A_1))
            # print("Message 1: "+str(message_1))

            # 3) Receives (g^{x_1+N_A_1}/g^{x_B})^{N_B*N_B_1} mod p and g^{N_B} mod p
            message_2 = self.node.get_message_at(0)
            # print("Message 2: "+str(message_2))

            # 4) Generates the nonce N_A_2 and sends ((g^{x_1+N_A_1}/g^{x_B})^{N_B*N_B_1})^{N_A_2} mod p
            N_A_2 = random.randint(1, self.prime-1)
            message_3 = Utilities.square_multiply(message_2[0], N_A_2, self.prime)
            # print("N_A_2: "+str(N_A_2))
            # print("Message 3: "+str(message_3))

            # 6) Generates (g^{N_B})^*N_A_1*N_A_2} mod p and ((g^{N_B})^{x_1-x_2+N_A_1})^{N_A_2} mod p
            K_1 = Utilities.square_multiply(message_2[1], N_A_1*N_A_2, self.prime)
            K_2 = Utilities.square_multiply(Utilities.square_multiply(message_2[1], self.uniform1-self.uniform2+N_A_1, self.prime), N_A_2, self.prime)
            # print("K_1: "+str(K_1))
            # print("K_2: "+str(K_2))

            nonce = 0
            box1 = nacl.secret.SecretBox(K_1.to_bytes(32, byteorder="little", signed=False))
            c1 = box1.encrypt(self.secret1.to_bytes(int(math.ceil(len(bin(self.secret1)[2:])/8)), byteorder="little",
                                                    signed=False), nonce=nonce.to_bytes(24, byteorder="little",
                                                                                        signed=False),
                              encoder=ENCODER)
            box2 = nacl.secret.SecretBox(K_2.to_bytes(32, byteorder="little", signed=False))
            c2 = box2.encrypt(self.secret2.to_bytes(int(math.ceil(len(bin(self.secret2)[2:]) / 8)), byteorder="little",
                                                    signed=False), nonce=nonce.to_bytes(24, byteorder="little",
                                                                                        signed=False),
                              encoder=ENCODER)

            self.node.send_messages({self.partner_addr: (message_3,
                                                         int.from_bytes(c1.ciphertext, byteorder="little", signed=False),
                                                         0, int.from_bytes(c2.ciphertext, byteorder="little", signed=False),
                                                         0)})

            return

        finally:
            self.node.close()

class OT_Receiver:

    """
    Oblivious Transfer sender's (Bob) protocol.
    This corresponds to Parakh's protocol defined in:
    https://arxiv.org/pdf/0909.2852.pdf
    """

    def __init__(self, host, port, partner_host, partner_port, prime, generator, uniform1, uniform2, choice):
        self.node = Node.Node(host, port)
        self.node.connect([(partner_host, partner_port)])
        self.addr = (host, port)
        self.partner_addr = (partner_host, partner_port)
        self.prime = prime
        self.generator = generator
        self.uniform1 = uniform1
        self.uniform2 = uniform2
        self.choice = choice

    def protocol(self):
        try:
            # print("x1: "+str(self.uniform1))
            # print("x2: "+str(self.uniform2))

            # 1) Receives g^{x_1+N_A_1} mod p
            message_1 = self.node.get_message_at(0)
            # print("Message 1: "+str(message_1))

            # 2) Sets x_B=x_1 if we want to get number 1; otherwise x_B = x_2
            # Generate N_B and N_B_1
            x_B = self.uniform1 if self.choice == 1 else self.uniform2
            N_B = random.randint(1, self.prime-1)
            N_B_1 = random.randint(1, self.prime - 2)
            while Utilities.euclidean(N_B_1, self.prime-1) != 1:
                N_B_1 = random.randint(1, self.prime-2)
            # print("xB: "+str(x_B))
            # print("NB: "+str(N_B))
            # print("NB1: "+str(N_B_1))

            # 3) Sends (g^{x_1+N_A_1}/g^{x_B})^{N_B*N_B_1} mod p and g^{N_B} mod p
            message_2 = [Utilities.square_multiply(message_1*Utilities.inverse(Utilities.square_multiply(self.generator,
                                                                                                         x_B, self.prime),
                                                                               self.prime), N_B*N_B_1, self.prime),
                         Utilities.square_multiply(self.generator, N_B, self.prime)]
            self.node.send_messages({self.partner_addr: message_2})
            # print("Message 2: "+str(message_2))

            # 4) Receives ((g^{x_1+N_A_1}/g^{x_B})^{N_B*N_B_1})^{N_A_2} mod p
            received = self.node.get_message_at(1)
            message_3, c1, n1, c2, n2 = received
            # print("Message 3: "+str(message_3))

            # 5) Bob computes (((g^{x_1+N_A_1}/g^{x_B})^{N_B*N_B_1})^{N_A_2})^{1/N_B_1} mod p
            K_B = Utilities.square_multiply(message_3, Utilities.inverse(N_B_1, self.prime-1), self.prime)
            # print("K_B: "+str(K_B))

            # Gets the appropriate nonce and cipher
            nonce = n1 if self.choice == 1 else n2
            cipher = c1 if self.choice == 1 else c2

            # Converts the nonce and cipher to bytes
            nonce = nonce.to_bytes(24, byteorder="little", signed=False)
            cipher = cipher.to_bytes(int(math.ceil(len(bin(cipher)[2:])/8)), byteorder="little", signed=False)

            boxb = nacl.secret.SecretBox(K_B.to_bytes(32, byteorder="little", signed=False))
            p = boxb.decrypt(cipher, nonce=nonce, encoder=ENCODER)

            return int.from_bytes(p, byteorder="little", signed=False)

        finally:
            self.node.close()


def initialize_parties(party, prime, generator, uniform1, uniform2, secret1, secret2, choice):
    if party == 0:
        p = OT_Sender(HOST, PORT, HOST, PORT+1, prime, generator, uniform1, uniform2, secret1, secret2)
        p.protocol()
    else:
        p = OT_Receiver(HOST, PORT+1, HOST, PORT, prime, generator, uniform1, uniform2, choice)
        print("Result:"+str(p.protocol()))

def main():
    prime = 2903
    generator = 5
    uniform1 = random.randint(1, prime-1)
    uniform2 = random.randint(1, prime-1)
    if uniform1 < uniform2:
        uniform1, uniform2 = uniform2, uniform1
    secret1, secret2 = 176, 31
    choice = 2

    processes = list()
    for party in range(2):
        processes.append(multiprocessing.Process(target=initialize_parties, args=(party, prime, generator, uniform1,
                                                                                  uniform2, secret1, secret2, choice)))

    for process in processes:
        process.start()

    for process in processes:
        process.join()

    print("Finished Protocol")


if __name__ == '__main__':
    main()
