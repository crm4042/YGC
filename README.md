# YGC
## Christopher Murphy

### Description
This project implements the Yao's Garbled Circuit protocol. This is used to evaluate arbitrary 
circuits securely over two parties.

### Dependencies
The only external package this depends on is pyNaCl. This can be installed by running:
 "pip install PyNaCl" in the command console.

### Running
To run this, simply type "python3 YGC.py" into the command console.

This will run the precoded examples of the adder and comparator circuits.
Note that running this multiple times will allow for the discovery that the
expected truth table and the ouputs are the same.
