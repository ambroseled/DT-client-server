import socket
import sys
import struct

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

# Getting user to enter a request type
request_type = input("Enter request choice, date or time: ")
# Checking if users request choice is valid
if request_type != "date" and request_type != "time":
    print("Invalid request choice, program will terminate")
    sys.exit()

# Getting user to enter hostname or IP address of server
entered_host = input("Enter the host IP in dotted decimal or the hostname: ")
# Checking if entered hostname/IP is valid
try:
    host_IP = socket.gethostbyname(entered_host)
except socket.gaierror:
    print("Invalid hostname or IP address entered, program will terminate")
    sys.exit()
# Getting user to enter a port number to use
port = int(input("Enter a port number to use between 1024 and 64000: "))
# Checking if the entered port number is valid
if port < 1024 or port > 64000:
    print("Invalid port number entered, program will terminate")
    sys.exit()

UDP_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

request_packet = bytearray(6)

request_packet[0:1] = struct.pack(">I", MAGIC_NUMBER)
request_packet[2:3] = struct.pack(">I", REQUEST_PACKET)
request_packet[4:5] = struct.pack(">I", request_type)
