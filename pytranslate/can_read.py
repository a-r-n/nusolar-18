from serial import Serial
import serial
import sys
import struct
import time
import pandas as pd
import re

class Parser:
    table = None
    def __init__(self, fileName):
        self.table = pd.read_csv(fileName, converters={"ID": lambda x: int(x, 16)})
        self.table.set_index("ID", inplace=True)
        for i, r in self.table.iterrows():
            count = 0
            n = 1
            while type(r[n * 2]) is int:
                count += r[n * 2]
                n += 1
            if count > 64:
                raise Exception("Row " + hex(i) + " is not consistent! "
                                "Expected bit sum of at most 64, but got " + str(count) + ". ")

    def getName(self, id):
        return self.table.loc[id]["Name"]

    def getData(self, id, rawData):
        fieldNames = []
        fieldValues = []
        bitCount = 0
        pairIndex = 3
        while type(self.table.loc[id][pairIndex]) is str:
            fieldNames = fieldNames + [self.table.loc[id][pairIndex]]
            bitLength = self.table.loc[id][pairIndex + 1]
            val = rawData >> int(64 - bitLength - bitCount)      # Right shift so that the last byteLength bytes are our data
            val = val & int((1 << int(bitLength)) - 1)                  # Mask off the bytes more significant than byteLength
            fieldValues = fieldValues + [val]
            pairIndex += 2
            bitCount += bitLength
        return fieldNames, fieldValues


p = Parser("id-table.csv")
data = 0xDEADBEEFABCD1111
names, vals = p.getData(0x10, data)
print(names)
print(vals)
sys.exit(0)

port = sys.argv[1]

ser = serial.Serial(port, 9600)

while True:
    msg = str(ser.readline(100000))
    msg = re.findall('\'.*\'', msg)[0][1:-1]
    print(msg)

