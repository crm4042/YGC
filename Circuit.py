import Gate
import Utilities
import Wire
import random

"""
Author: Chris Murphy
"""

class Circuit:

    """
    Represents a full circuit.
    """

    def __init__(self, inputs: dict, gates: list, wires: list):

        """
        Initializes the circuit

        :param inputs:      dict        The inputs to the circuit
        :param gates:       list        An ordered list of gates
        :param wires:       list        An ordered list of wires
        """

        self.inputs = inputs
        self.gates = gates
        self.wires = wires

    def get_wire_corresponding_to(self, num, activation):

        """
        Gets the wire corresponding to a certain wire number and activation

        :param num:         int         The wire number to get
        :param activation:  int         The activation to get
        :return:            tuple       The corresponding wire
        """

        return self.wires[num].k[activation], self.wires[num].p[activation]

    def print_circuit(self):

        """
        Prints all circuit information for debugging

        :return:            None
        """

        print("INPUTS:")
        for ipt in self.inputs.keys():
            print(ipt, self.inputs[ipt])

        print("\nWIRES:")
        for index, wire in enumerate(self.wires):
            print(index, wire.k[0], wire.p[0])
            print(index, wire.k[1], wire.p[1])

        print("\nGATES")
        for index, gate in enumerate(self.gates):
            print(index, gate.primitive_garbled_gate)


def main():
    wires = [Wire.Wire() for _ in range(8)]
    inputs = {0: random.randint(0, 1), 2: random.randint(0, 1)}
    gates = [Gate.Gate("000", Gate.XOR(), [wires[0], wires[1]], wires[3]),
             Gate.Gate("001", Gate.XOR(), [wires[2], wires[3]], wires[4], True),
             Gate.Gate("010", Gate.AND(), [wires[2], wires[3]], wires[5]),
             Gate.Gate("011", Gate.AND(), [wires[0], wires[1]], wires[6]),
             Gate.Gate("100", Gate.OR(), [wires[5], wires[6]], wires[7], True)]
    circuit = Circuit(inputs, gates, wires)
    print()


if __name__ == '__main__':
    main()

