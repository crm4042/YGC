import math
import nacl.encoding
import nacl.hash


ENCODING = nacl.encoding.RawEncoder()

"""
Author: Chris Murphy (crm4042@g.rit.edu)
"""


def to_bin_of_size(x, n):

    """
    Converts an integer to a binary value of a certain size

    :param x:                   int     The integer value
    :param n:                   int     The size
    :return:
    """

    bin_x = bin(x)[2:]
    return ("0"*(n-len(bin_x)))+bin_x

def square_multiply(b, p, n):

    """
    Does b^p (mod n) efficiently

    :param b:                   int     The base of the exponentiation
    :param p:                   int     The power of the exponentiation
    :param n:                   int     The modulus of the exponentiation
    :return:                    int     The resulting exponentiation
    """

    result = 1
    p = bin(p)[2:]

    for index in range(len(p)):
        result = (result ** 2) % n
        if int(p[index]) == 1:
            result = (result * b) % n

    return result


def euclidean(x1, x2):

    """
    Finds the gcd between two integers.

    :param x1:                  int     The first integer to find the GCD of
    :param x2:                  int     The second integer to find the GCD of
    :return:                    int     The GCD between the two integers
    """

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

    """
    Performs the EEA to find the inverse of two integers

    :param x1:                  int     The first integer to perform the EEA with
    :param x2:                  int     The second integer to perform the EEA with
    :param check:               bool    Debugging parameter for checking the result
    :param verbose:             bool    Debugging parameter for verbose printing
    :return:                    list    A linear combination of x1 and x2 that equals 1
    """

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

    """
    Gets the inverse of a number with respect to a modulus

    :param x:                   int     The number to get the inverse of
    :param n:                   int     The number to get the modulus with respect to
    :return:                    int     The inverse of x mod n
    """

    if x == 1:
        return 1
    scale1, num_1, scale2, num_2 = extended_euclidean(x, n)
    return scale1 % n if num_1 == x else scale2 % n

def hash(message):

    """
    Hashes a single message

    :param message:             int/str The message to hash
    :return:                    bytes   The hashed message
    """

    if isinstance(message, str):
        return nacl.hash.sha512(bytes(message, 'utf-8'), ENCODING)
    elif isinstance(message, int):
        return nacl.hash.sha512(message.to_bytes(int(math.ceil(len(bin(message)[2:])/8)), byteorder="little", signed=False), ENCODING)
