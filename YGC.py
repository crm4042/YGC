import Circuit
import Gate
import Node
import OT
import Utilities
import Wire
import copy
import multiprocessing
import random

# Network Information
PORTS_NEEDED = 2
START_PORT = 10092
STOP = "STOP"
HOST = "127.0.0.1"


class YGC_Circuit_Generator:
    def __init__(self, host, port, partner_host, partner_port, circuit, prime, generator, uniform1, uniform2):
        # Network information
        self.host = host
        self.port = port
        self.partner_host = partner_host
        self.partner_port = partner_port

        # Creates a communication node
        self.node = Node.Node(self.host, self.port)
        self.node.connect([(self.partner_host, self.partner_port)])
        self.round_num = 0

        # Sets the circuit
        self.circuit = circuit

        # Sets the OT information
        self.prime = prime
        self.generator = generator
        self.uniform1 = uniform1
        self.uniform2 = uniform2

        # Runs YGC
        try:
            self.result = self.protocol()
        finally:
            self.node.close()

    def protocol(self):
        # Aggregates the circuit into a sendable format
        aggregate_garbled_table = list()
        aggregate_output_decoding_table = list()
        gate_possible_inputs = dict()
        input_dict = dict()
        for gate in self.circuit.gates:
            aggregate_garbled_table.append(gate.garbled_table)
            aggregate_output_decoding_table.append(gate.output_decoding_table)
            gate_possible_inputs[gate.gate_num_str] = [(wire.k[0], wire.p[0]) for wire in gate.inputs]+\
                                                      [(wire.k[1], wire.p[1]) for wire in gate.inputs]
            random.shuffle(gate_possible_inputs[gate.gate_num_str])

        for key in self.circuit.inputs.keys():
            input_dict[int(key)] = self.circuit.get_wire_corresponding_to(key, self.circuit.inputs[key])

        # Sends the circuit
        message1 = [aggregate_garbled_table, aggregate_output_decoding_table, gate_possible_inputs, input_dict]
        self.node.send_messages({(self.partner_host, self.partner_port): message1})

        # Runs the OT protocols
        i = 0
        while True:
            message2 = self.node.get_message_at(self.round_num)
            self.round_num += 1

            # Stops the OT
            if not isinstance(message2, int):
                break

            # Gets the input wires
            wire0 = self.circuit.get_wire_corresponding_to(message2, 0)
            wire1 = self.circuit.get_wire_corresponding_to(message2, 1)

            wire0_str = wire0[0]+str(wire0[1])
            wire1_str = wire1[0]+str(wire1[1])

            wire0_int = int(wire0_str, 2)
            wire1_int = int(wire1_str, 2)

            OT.OT_Sender(self.host, self.port+1, self.partner_host, self.partner_port+1, self.prime, self.generator,
                         self.uniform1, self.uniform2, wire0_int, wire1_int).protocol()

        outputs = message2

        return outputs


class YGC_Circuit_Evaluator:
    def __init__(self, host, port, partner_host, partner_port, inputs, prime, generator, uniform1, uniform2):
        # Network information
        self.host = host
        self.port = port
        self.partner_host = partner_host
        self.partner_port = partner_port

        # Creates a communication node
        self.node = Node.Node(self.host, self.port)
        self.node.connect([(self.partner_host, self.partner_port)])
        self.round_num = 0

        # The inputs to the protocol
        self.inputs = inputs

        # Sets the OT information
        self.prime = prime
        self.generator = generator
        self.uniform1 = uniform1
        self.uniform2 = uniform2

        # Runs the protocol
        try:
            self.result = self.protocol()

        # Closes the node
        finally:
            self.node.close()

    def protocol(self):

        # Receives the garbled table
        garbled_table, output_decoding_table, gate_possible_inputs, inputs = self.node.get_message_at(self.round_num)
        self.round_num += 1

        # Makes a dictionary for output decoding table mapping gates to the output
        gate_to_output = dict()

        # Makes sure the keys are ints
        keys = copy.copy(list(inputs.keys()))
        for key in keys:
            inputs[int(key)] = tuple(inputs.pop(key))

        # Oblivious transfer loop
        for key in self.inputs:
            # Sends the wire number
            self.node.send_messages({(self.partner_host, self.partner_port): key})

            choice = self.inputs[key]+1

            # Performs an oblivious transfer
            result = OT.OT_Receiver(self.host, self.port+1, self.partner_host, self.partner_port+1, self.prime,
                                    self.generator, self.uniform1, self.uniform2, choice).protocol()

            result_bin = bin(result)[2:]
            result_bin = ("0"*(Wire.K+1-len(result_bin)))+result_bin
            wire = (result_bin[:-1], int(result_bin[-1]))

            inputs[int(key)] = wire

        # Feeds the inputs forward in the circuit
        for gate_num_str in gate_possible_inputs.keys():
            gate_num_int = int(gate_num_str, 2)

            # Inverts the inputs to allow to find the wire order
            inverted_inputs = {tuple(value): int(key) for key, value in inputs.items()}

            # Finds the actual inputs to the gate
            gate_inputs = list()
            for possible_input in gate_possible_inputs[gate_num_str]:
                if tuple(possible_input) in inverted_inputs.keys():
                    gate_inputs.append((inverted_inputs[tuple(possible_input)], tuple(possible_input)))

            gate_inputs.sort()
            gate_inputs = [ipt[1] for ipt in gate_inputs]

            # Finds the correct index in the garbled table
            concated_wire_labels = ""
            # reverse_concated_wire_labels = ""
            garbled_table_index = ""
            # reverse_garbled_table_index = ""
            for ipt in gate_inputs:
                concated_wire_labels += str(ipt[0])
                # reverse_concated_wire_labels = str(ipt[0])+reverse_concated_wire_labels
                garbled_table_index += str(ipt[1])
                # reverse_garbled_table_index = str(ipt[1])+reverse_garbled_table_index
            concated_wire_labels += gate_num_str
            garbled_table_index = int(garbled_table_index, 2)
            # reverse_concated_wire_labels += gate_num_str
            # reverse_garbled_table_index = int(reverse_garbled_table_index, 2)

            output = int.from_bytes(Utilities.hash(concated_wire_labels), byteorder="little", signed=False) ^ \
                     garbled_table[gate_num_int][garbled_table_index]
            output = bin(output)[2:]
            output = ("0"*(Wire.K+1-len(output)))+output

            # r_output = int.from_bytes(Utilities.hash(reverse_concated_wire_labels), byteorder="little", signed=False) ^ \
            #          garbled_table[gate_num_int][reverse_garbled_table_index]
            # r_output = bin(r_output)[2:]
            # r_output = ("0" * (Wire.K + 1 - len(output))) + r_output

            wire_label = output[:-1]
            wire_activation = int(output[-1])

            key = max(inputs.keys())+1
            inputs[key] = (wire_label, wire_activation)
            gate_to_output[gate_num_int] = (wire_label, wire_activation, gate_num_str)

        outputs = dict()
        for element in range(len(output_decoding_table)):
            if len(output_decoding_table[element]) != 0:
                element_output = gate_to_output[element]
                hashed_value = int.from_bytes(Utilities.hash(element_output[0]+Gate.OUT+element_output[-1]),
                                              byteorder="little", signed=False)
                for possible_output in output_decoding_table[element]:
                    output = possible_output ^ hashed_value
                    if output <= 1:
                        outputs[element_output[-1]] = output
                        break

        # Stop OT communication
        self.node.send_messages({(self.partner_host, self.partner_port): outputs})

        return outputs


def initialize_YGC(party_num, prime, generator, uniform1, uniform2):

    # The Circuit generator
    if party_num == 0:
        wires = [Wire.Wire() for _ in range(8)]
        inputs = {0: random.randint(0, 1), 2: random.randint(0, 1)}
        for key in inputs.keys():
            print("W%d: %d" % (key, inputs[key]))
        gates = [Gate.Gate("000", Gate.XOR(), [wires[0], wires[1]], wires[3]),
                 Gate.Gate("001", Gate.XOR(), [wires[2], wires[3]], wires[4], True),
                 Gate.Gate("010", Gate.AND(), [wires[2], wires[3]], wires[5]),
                 Gate.Gate("011", Gate.AND(), [wires[0], wires[1]], wires[6]),
                 Gate.Gate("100", Gate.OR(), [wires[5], wires[6]], wires[7], True)]
        circuit = Circuit.Circuit(inputs, gates, wires)
        ygc = YGC_Circuit_Generator(HOST, START_PORT, HOST, START_PORT+PORTS_NEEDED, circuit, prime,
                                    generator, uniform1, uniform2)
        result = ygc.result
        print("S: "+str(result["001"]))
        print("C: "+str(result["100"]))

    # The Circuit evaluator
    else:
        inputs = {1: random.randint(0, 1)}
        for key in inputs.keys():
            print("W%d: %d" % (key, inputs[key]))
        ygc = YGC_Circuit_Evaluator(HOST, START_PORT+PORTS_NEEDED, HOST, START_PORT, inputs,
                                    prime, generator, uniform1, uniform2)
        # result = ygc.result
        # print("S: " + str(result["001"]))
        # print("C: " + str(result["100"]))


def main():
    prime = 2903
    generator = 5
    uniform1 = random.randint(1, 2903)
    uniform2 = random.randint(1, 2903)
    if uniform1 < uniform2:
        uniform1, uniform2 = uniform2, uniform1

    manager = multiprocessing.Manager()

    # Starts the YGC processes
    processes = list()
    for party_num in range(2):
        processes.append(multiprocessing.Process(target=initialize_YGC, args=(party_num, prime, generator, uniform1,
                                                                              uniform2)))
        processes[-1].start()

    # Joins the the processes back to the main process to terminate
    for process in processes:
        process.join()

if __name__ == '__main__':
    main()
