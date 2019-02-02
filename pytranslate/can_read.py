import socket
import sys
import struct
import time

def twos_comp(val, bits): #look into xor all of this
    """compute the 2's complement of int value val"""
    if (val & (1 << (bits - 1))) != 0:  # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)  # compute negative value
    return val


def IDparser(id_type):
    if id_type == 0x0:
        return "Heartbeat"
    if id_type == 0x0F6:
        return "Charger Control Information, 16x4"
    if id_type == 0x01:
        return "CMU 1 status"
    if id_type == 0x002 or id_type == 0x005 or id_type == 0x008:
        return "Cells 0~3 status"
    if id_type == 0x003 or id_type == 0x006 or id_type == 0x009:
        return "Cells 4~7 status"
    if id_type == 0x0F8:
        return "Minimum/Maximum Cell Voltage"


def DataParser(id_type, x):
    if id_type == 0x0F8:
        data0 = x >> (16 * 3)
        data1 = (x >> 16 * 2) & 0xffff
        data2 = (x >> (8 * 3)) & 0xff
        data3 = (x >> 16) & 0xff
        data4 = (x >> 8) & 0xff
        data5 = (x) & 0xff
        print(
                    "Minimum cell voltage(mV): %d \r\n'\
                    Maximum cell voltage(mV): %d \r\n'\
                    CMU number that has minimum cell voltage:%d \r\n'\
                    Cell number that has minimum cell voltage:%d \r\n'\
                    CMU number that has max cell voltage:%d \r\n'\
                    Cell number that has max cell voltage:%d \r\n" % (
            data0, data1, data2, data3, data4, data5))

    if id_type == 0x0F6:
        data0 = x >> 16 * 3
        data1 = (x >> 16 * 2) & 0xffff
        data2 = (x >> 16) & 0xffff
        data3 = (x) & 0xffff
        print(
                    "Charging cell voltage error(mV): %d \r\n'\
                    Cell temperature margin(1/10C): %d \r\n'\
                    Discharging cell voltage error(mV): %d \r\n'\
                    Total pack capacity(Ah): %d \r\n" % (
            data0, data1, data2, data3))
    if id_type == 0x001 or id_type == 0x004 or id_type == 0x007:
        data0 = x >> 16 * 2
        data1 = (x >> 16) & 0xffff
        data2 = (x) & 0xffff
        print("CMU serial number: %d \r\n'\
        PCB temp(1/10C): %d \r\n'\
        Cell temp(1/10C): %d" % (data0, data1, data2))
    if id_type == 0x002 or id_type == 0x005 or id_type == 0x008 or id_type == 0x00B:
        data0 = x >> 16 * 3
        data1 = (x >> 16 * 2) & 0xffff
        data2 = (x >> 16) & 0xffff
        data3 = (x) & 0xffff
        print(
                    "Cell voltage 0(mV): %d \r\n'\
                    Cell voltage 1(mV): %d \r\n'\
                    Cell voltage 2(mV): %d \r\n'\
                    Cell voltage 3(mV): %d \r\n" % (
            twos_comp(data0, 16), twos_comp(data1, 16), twos_comp(data2, 16), twos_comp(data3, 16)))
    if id_type == 0x003 or id_type == 0x006 or id_type == 0x009 or id_type == 0x00C:
        data0 = x >> 16 * 3
        data1 = (x >> 16 * 2) & 0xffff
        data2 = (x >> 16) & 0xffff
        data3 = (x) & 0xffff
        print(
                    "Cell voltage 4(mV): %d \r\n'\
                    Cell voltage 5(mV): %d \r\n'\
                    Cell voltage 6(mV): %d \r\n'\
                    Cell voltage 7(mV): %d \r\n" % (
            twos_comp(data0, 16), twos_comp(data1, 16), twos_comp(data2, 16), twos_comp(data3, 16)))


# Change the selector to the IDs that you want to parse or print out
# selector = [" 0x002"," 0x003"," 0x005"," 0x006"," 0x008"," 0x009"," 0x00B"]
selector = [" 0x003", " 0x005", " 0x006", " 0x008", " 0x009", " 0x00B"]



#begin the packet parts lol

MCAST_GRP = '239.255.60.60'
MCAST_PORT = 4876

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((MCAST_GRP, MCAST_PORT))
mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

#s ip route add 224.0.0.0/4 dev enp0s31f6

while True:
    rawdata, addr = sock.recvfrom(30)
    rawdata = bytearray(rawdata)

    id = rawdata[17:20]
    idsum = 0
    for n in id:
        idsum = idsum * 0xFF + n
    data = rawdata[22:]
    datasum = 0
    for n in data:
        datasum = datasum * 0xFF + n
    print datasum
    x = DataParser(idsum, datasum)
    #if x: print x

