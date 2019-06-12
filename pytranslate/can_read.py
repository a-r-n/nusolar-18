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
        pairIndex = 1
        while pairIndex <= self.table.shape[1] - 1 and type(self.table.loc[id][pairIndex]) is str:
            fieldNames = fieldNames + [self.table.loc[id][pairIndex]]
            bitLength = self.table.loc[id][pairIndex + 1]
            val = rawData >> int(64 - bitLength - bitCount)      # Right shift so that the last byteLength bytes are our data
            val = val & int((1 << int(bitLength)) - 1)                  # Mask off the bytes more significant than byteLength
            fieldValues = fieldValues + [val]
            pairIndex += 2
            bitCount += bitLength
        return fieldNames, fieldValues


p = Parser("id-table.csv")
data = 0xADEADBEEFABCD1111
names, vals = p.getData(0x10, data)
print(names)
print(vals)
#sys.exit(0)

port = sys.argv[1]

ser = serial.Serial(port, 57600)

ser.write("\rZ0\r".encode("UTF-8"))

ser.write("S5\r".encode("UTF-8"))

ser.write("X1\r".encode("UTF-8"))

ser.write("C\r".encode("UTF-8"))

time.sleep(1)

ser.write("O\rA\r".encode("UTF-8"))

while True:
    ser.write("P\r".encode("UTF-8")) #TODO: make this continuous optioon outside loop
    msg = ser.read(1000)        #read data
    x = msg.split(b'\rt')   #Segment data stream into packets
    #msg = re.findall('\'.*\'', msg)[0][1:-1]
    for i in x:
        if len(i) == 20:
            localID = int(str(i)[2:5], 16)
            print(str(localID))
            localDat = int(str(i)[5:-1], 16)
            if localID == 54 or localID == 0x6B2:
                print(i)
                names, vals = p.getData(localID, localDat)
                print(names)
                print(vals)
        if len(i) == 25:
            pass

