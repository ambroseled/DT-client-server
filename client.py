import socket
import sys
import struct
from select import select


# Defining constants
MAGIC_NUMBER = 0x497E
REQUEST_PACKET = 0x0001
RESPONSE_PACKET = 0x0002
DATE_REQUEST = 0x0001
TIME_REQUEST = 0x0002
REQUEST_PACKET_SIZE = 6
ENGLISH_CODE = 0x0001
MAORI_CODE = 0x0002
GERMAN_CODE = 0x0003


def validatePacket(pkt):
    """
    Checks that the received packet is valid
    """
    text = None
    if len(pkt) < 13: text = "Invalid packet header length"
    elif ((pkt[0] << 8) + pkt[1]) != MAGIC_NUMBER: text = "Invalid magic number"
    elif ((pkt[2] << 8) + pkt[3]) != RESPONSE_PACKET: text = "Invalid packet type"
    elif ((pkt[4] << 8) + pkt[5]) not in [ENGLISH_CODE, MAORI_CODE, GERMAN_CODE]: text = "Invalid language code"
    elif ((pkt[6] << 8) + pkt[7]) >= 2100: text = "Invalid year"
    elif pkt[8] < 1 or pkt[8] > 12: text = "Invalid month"
    elif pkt[9] < 1 or pkt[10] > 31: text = "Invalid day"
    elif pkt[10] < 0 or pkt[10] > 23: text = "Invalid hour"
    elif pkt[11] < 0 or pkt[11] > 59: text = "Invalid minute"
    elif len(pkt) != (13 + pkt[12]): text = "Invalid packet length"
    if text:
        print("*****************************")
        print("{0}, program will terminate".format(text))
        print("*****************************")
        sys.exit()


def handlePacket(pkt):
    """
    Handles the response packet once it hs been received
    from the server
    """
    validatePacket(pkt)
    text = pkt[13:]
    date = "{0}:{1}:{2}".format(((pkt[6] << 8) + pkt[7]), pkt[8], pkt[9])
    time = "{0}:{1}".format(pkt[10], pkt[11])
    print("The date is: {0}".format(date))
    print("The time is: {0}".format(time))
    print("Textual representation received: {0}".format(text.decode()))
    sys.exit()

def main():

# Getting user to enter a request type
print("-----------------------------")
print("-----------------------------")
request_type = input("Enter request choice, date or time: ")
# Checking if users request choice is valid
if request_type != "date" and request_type != "time":
    print("*****************************")
    print("Invalid request choice, program will terminate")
    print("*****************************")
    sys.exit()
if request_type == "date":
    request = 0x0001
else:
    request = 0x0002
# Getting user to enter hostname or IP address of server
entered_host = input("Enter the host IP in dotted decimal or the hostname: ")
# Checking if entered hostname/IP is valid
try:
    host_IP = socket.gethostbyname(entered_host)
except socket.gaierror:
    print("*****************************")
    print("Invalid hostname or IP address entered, program will terminate")
    print("*****************************")
    sys.exit()
# Getting user to enter a port number to use
port = int(input("Enter a port number to use between 1024 and 64000: "))
# Checking if the entered port number is valid
if port < 1024 or port > 64000:
    print("*****************************")
    print("Invalid port number entered, program will terminate")
    print("*****************************")
    sys.exit()

# Opening socket for communication with the server
server = (host_IP, port)
socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Creating a request packet
request_packet = bytearray(3)
request_packet[0:1] = struct.pack(">H", MAGIC_NUMBER)
request_packet[2:3] = struct.pack(">H", REQUEST_PACKET)
request_packet[4:5] = struct.pack(">H", request)

# Sending request packet to the server
socket.sendto(request_packet, server)
print("-----------------------------")
print("-----------------------------")
print("Sent request packet to {0}".format(server))

# Waiting for a response from the server
while True:
    reads, writes, exceps = select([socket], [], [], 1.0)
    if reads == writes == exceps == []:
        print("*****************************")
        print("Response too slow, program will terminate")
        print("*****************************")
        socket.close()
        sys.exit()
    elif len(reads) != 0:
        for sock in reads:
            pkt, addr = sock.recvfrom(1024)
            print("Response packet received from {0}".format(addr))
            print("-----------------------------")
            print("-----------------------------")
            sock.close()
            handlePacket(pkt)

