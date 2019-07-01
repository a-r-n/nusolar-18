from serial import Serial
import serial
import sys
import struct
import time
import pandas as pd
import re
import pygcurse


class Parser:
    table = None

    def __init__(self, fileName):
        self.table = pd.read_csv(fileName, converters={
                                 "ID": lambda x: int(x, 16)})
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
            # Right shift so that the last byteLength bytes are our data
            val = rawData >> int(64 - bitLength - bitCount)
            # Mask off the bytes more significant than byteLength
            val = val & int((1 << int(bitLength)) - 1)
            fieldValues = fieldValues + [val]
            pairIndex += 2
            bitCount += bitLength
        return fieldNames, fieldValues

# List to dictionary
def l2d(names, vals):
    x = {}
    for i in range(len(names)):
        x[names[i]] = vals[i]
    return x

def centerify(text, width=-1):
  lines = text.split('\n')
  width = max(map(len, lines)) if width == -1 else width
  return '\n'.join(line.center(width) for line in lines)


# Create the virtual terminal
window = pygcurse.PygcurseWindow(60, 33)

# CAN data
cd = {}
cd['p'] = {
    'v': 0,
    'i': 0,
    't': 0
}
cd['mpptC'] = {
    'sub': 0,
    'right': 0,
    'left': 0
}
cd['cells'] = [None] * 26
for i in range(0, 25):
    cd['cells'][i] = {
        'voltage': 0,
        'temp': 0
    }


def drawUpdate():
    # reset the cursor and clear the screen
    window.cursory = 0
    window.cursorx = 0
    #Uncomment this line if there are issues with text not getting overwritten
    #window.setscreencolors('white', 'black', clear=True)

    # DRAW CELLS
    window.putchars(centerify("-----CELLS-----", 60))
    window.cursory += 1

    for i in range(0, 25):
        window.putchars(
            "%2dV  , %2dC" %
            (
                cd['cells'][i]['voltage'],
                cd['cells'][i]['temp']
            )
        )
        if i < 24:
            window.cursorx += 11
            window.putchar('|')
            window.cursorx -= 11
        window.cursory += 1
        if (i + 1) % 6 == 0:
            # window.curosrx = 0
            window.cursorx += 12
            window.cursory -= 6

    # DRAW MPPT CURRENTS
    # reset the cursor from the previous section
    window.cursorx = 0
    window.cursory += 6
    window.pygprint(centerify("-----MPPT CURRENT-----", 60))
    window.pygprint("%7s: %d" % ('Sub', cd['mpptC']['sub']))
    window.pygprint("%7s: %d" % ('Left', cd['mpptC']['left']))
    window.pygprint("%7s: %d\n\n" % ('Right', cd['mpptC']['right']))

    # DRAW PACK STAT
    window.pygprint(centerify("-----PACK-----", 60))
    window.pygprint("%9s: %d" % ('Current', cd['p']['i']))
    window.pygprint("%9s: %d" % ('Voltage', cd['p']['v']))
    window.pygprint("%9s: %d" % ('Max temp', cd['p']['t']))

    

# For testing: witness the data increase in size
# while True:
#     cd['cells'][0]['voltage'] += 1
#     time.sleep(1)
#     drawUpdate()


p = Parser("id-table.csv")

port = sys.argv[1]

ser = serial.Serial(port, 57600)

ser.write("\rZ0\r".encode("UTF-8"))

ser.write("S5\r".encode("UTF-8"))

ser.write("X1\r".encode("UTF-8"))

ser.write("C\r".encode("UTF-8"))

time.sleep(1)

ser.write("O\rA\r".encode("UTF-8"))

while True:
    # TODO: make this continuous optioon outside loop
    ser.write("P\r".encode("UTF-8"))
    msg = ser.read(1000)  # read data
    x = msg.split(b'\rt')  # Segment data stream into packets
    #msg = re.findall('\'.*\'', msg)[0][1:-1]
    for i in x:
        if len(i) == 20:
            localID = int(str(i)[2:5], 16)
            # print(str(localID))
            localDat = int(str(i)[5:-1], 16)
            print(i)
            names, vals = p.getData(localID, localDat)
            nv = l2d(names, vals)
            print(names)
            print(vals)

            # EXAMPLE: how to update the dictionary with a new values
            if localID == 0x32:
                cd['cells'][nv['Cell ID']]['voltage'] = nv['Instant Voltage']
            elif localID == 0x5F0:
                cd['p']['t'] = nv['Max Temp']
                for n in range(1, 6):
                    cd['cells'][n] = nv['Mod %d' % n]
            elif localID >= 0x5F1 and localID <=0x5F3:
                offset = localID - 0x5F1
                for n in range(7 + offset * 8, 7 + offset * 8 + 7): # might want to double check this math
                    cd['cells'][n] = nv['Mod %d' % n]
            elif localID == 0x21:
                cd['p']['v'] = nv['Instant Voltage']
                # TODO: Add current (I couldn't find it)
            elif localID == 0x771:
                cd['mpptC']['sub'] = nv['Iin']
            elif localID == 0x772:
                cd['mpptC']['right'] = nv['Iin']
            elif localID == 0x773:
                cd['mpptC']['right'] = nv['Iin']

            
        # if extended IDs are needed, handle differently if needed
        if len(i) == 25:
            pass

