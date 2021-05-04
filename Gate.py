import Utilities
import Wire


OUT = "011011110111010101110100"


class Gate:

    """
    Corresponds to a single gate in a circuit.
    """

    def __init__(self, gate_num_str: str, gate: dict, inputs: list, output: Wire.Wire,
                 generate_output_decoding_table=False):

        """
        Initializes a gate in a circuit.

        :param gate_num_str:    str     The gate number represented as a string
        :param gate:            dict    The gate information for the gate
        :param inputs:          dict    The inputs of a gate
        :param output:          dict    The outputs of a gate
        :param generate_output_decoding_table:
                                bool    Whether or not this is an output of a circuit
                                        and needs an output decoding table
        """


        self.gate = gate
        self.gate_num_str = gate_num_str
        self.inputs = inputs
        self.output = output

        # Generates a mapping of inputs to outputs
        self.primitive_garbled_gate = dict()
        for key, value in gate.items():
            key_to_wire = list()
            value_to_wire = self.output.k[value], self.output.p[value]
            for index, element in enumerate(key):
                key_to_wire.append((self.inputs[index].k[element], self.inputs[index].p[element]))
            self.primitive_garbled_gate[tuple(key_to_wire)] = value_to_wire

        # Generates the garbled table
        self.garbled_table = list()
        for index in range(2**len(inputs)):
            bin_index = bin(index)[2:]
            bin_index = ("0"*(len(inputs)-len(bin_index)))+bin_index
            bin_index = [int(activation) for activation in list(bin_index)]
            concated_wire_labels = ""
            output_wire = ""
            for key in self.primitive_garbled_gate.keys():
                key_p = [ipt[1] for ipt in key]
                if key_p == bin_index:
                    for ipt in key:
                        concated_wire_labels += ipt[0]
                    concated_wire_labels += gate_num_str
                    output_wire = self.primitive_garbled_gate[key][0]+str(self.primitive_garbled_gate[key][1])
                    break
            hashed_wire_labels = Utilities.hash(concated_wire_labels)
            self.garbled_table.append(int.from_bytes(hashed_wire_labels, byteorder="little", signed=False) ^ int(output_wire, 2))

        # Generates the output decoding table
        self.output_decoding_table = list()
        if generate_output_decoding_table:
           for value, wire in enumerate(output.k):
               self.output_decoding_table.append(int.from_bytes(Utilities.hash(wire+OUT+gate_num_str),
                                                                byteorder="little", signed=False) ^ value)


def AND():

    """
    Corresponds to the gate information for an AND gate.

    :return:                    dict    The gate information for an AND gate
    """

    return {(0, 0): 0, (0, 1): 0, (1, 0): 0, (1, 1): 1}


def OR():

    """
    Corresponds to the gate information for an OR gate.

    :return:                    dict    The gate information for an OR gate
    """

    return {(0, 0): 0, (0, 1): 1, (1, 0): 1, (1, 1): 1}


def XOR():

    """
    Corresponds to the gate information for an XOR gate.

    :return:                    dict    The gate information for an XOR gate
    """

    return {(0, 0): 0, (0, 1): 1, (1, 0): 1, (1, 1): 0}


def NOT():

    """
    Corresponds to the gate information for an NOT gate.

    :return:                    dict    The gate information for an NOT gate
    """

    return {(0,): 1, (1,): 0}


def main():
    inputs = [Wire.Wire() for _ in range(2)]
    output = Wire.Wire()
    Gate("00", AND(), inputs, output, True)

if __name__ == '__main__':
    main()