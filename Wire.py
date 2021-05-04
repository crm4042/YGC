import Utilities
import random

K = 100


class Wire:
    def __init__(self):
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
