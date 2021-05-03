import Gate
import Wire
import random


class Circuit:
    def __init__(self, inputs: dict, gates: list, wires: list):
        self.inputs = inputs
        self.gates = gates
        self.wires = wires

    def get_wire_corresponding_to(self, num, activation):
        return self.wires[num].k[activation], self.wires[num].p[activation]


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

