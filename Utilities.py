import math
import nacl.encoding
import nacl.hash


ENCODING = nacl.encoding.RawEncoder()


def to_bin_of_size(x, n):
    bin_x = bin(x)[2:]
    return ("0"*(n-len(bin_x)))+bin_x

def square_multiply(b, p, n):
    """
    Does b^p (mod n) efficiently
    """

    result = 1
    p = bin(p)[2:]

    for index in range(len(p)):
        result = (result ** 2) % n
        if int(p[index]) == 1:
            result = (result * b) % n

    return result


def euclidean(x1, x2):
    if x1 > x2:
        a = x1
        b = x2
    else:
        a = x2
        b = x1

    q = a // b
    r = a - b * q

    while r != 0:
        a = b
        b = r

        q = a // b
        r = a - b * q

    return b

def extended_euclidean(x1, x2, check=False, verbose=False):
    if x1 > x2:
        a = [x1]
        b = [x2]
    else:
        a = [x2]
        b = [x1]

    q = [a[-1] // b[-1]]
    r = [a[-1] - b[-1] * q[-1]]

    if r[-1] == 0:
        return "Error: %d|%d" % (b[-1], a[-1])

    while r[-1] > 0:
        a.append(b[-1])
        b.append(r[-1])
        q.append(a[-1] // b[-1])
        r.append(a[-1] - b[-1] * q[-1])

    a.pop(len(a) - 1)
    b.pop(len(b) - 1)
    q.pop(len(q) - 1)
    r.pop(len(r) - 1)

    u = 1
    x = a[-1]
    v = -q[-1]
    y = b[-1]

    for index in range(len(a) - 2, -1, -1):
        if verbose:
            print(u, x, v, y)
        u, v = v, u + v * (-q[index])
        y = x
        x = a[index]

    if u * x + v * y == r[-1] and check:
        print("Valid")
    elif check:
        print("Not valid")

    return u, x, v, y

def inverse(x, n):
    if x == 1:
        return 1
    scale1, num_1, scale2, num_2 = extended_euclidean(x, n)
    return scale1 % n if num_1 == x else scale2 % n

def hash(message):
    if isinstance(message, str):
        return nacl.hash.sha512(bytes(message, 'utf-8'), ENCODING)
    elif isinstance(message, int):
        return nacl.hash.sha512(message.to_bytes(int(math.ceil(len(bin(message)[2:])/8)), byteorder="little", signed=False), ENCODING)
