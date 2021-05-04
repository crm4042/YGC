import Utilities
import random

K = 100


"""
Author: Chris Murphy (crm4042@g.rit.edu)
"""

class Wire:

    """
    Represents a single wire on the circuit.
    """

    def __init__(self):

        """
        Initializes a wire with k and p values
        """

        self.k = [bin(random.getrandbits(K))[2:], bin(random.getrandbits(K))[2:]]
        for b in range(2):
            self.k[b] = ("0"*(K-len(self.k[b])))+self.k[b]
        self.p = [random.randint(0, 1)]
        self.p.append(1-self.p[0])


def main():
    w = Wire()
    print(w.k)
    print(w.p)


if __name__ == '__main__':
    main()
