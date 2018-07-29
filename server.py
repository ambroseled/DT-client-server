import datetime
import socket
import sys

MAGIC_NUMBER = 0x497E
REQUEST_PACKET = 0x0001
RESPONSE_PACKET = 0x0002
DATE_REQUEST = 0x0001
TIME_REQUEST = 0x0002
REQUEST_PACKET_SIZE = 6
ENGLISH_CODE = 0x0001
MAORI_CODE = 0x0002
GERMAN_CODE = 0x0003


def get_time():
    time = datetime.datetime.now()
    year = str(time.year)
    month = str(time.month)
    day = str(time.day)
    hour = str(time.hour)
    minute = str(time.minute)


def get_ports():
    try:
        ports = input("Enter three port numbers between 1024 and 64000 in following order: English, Te reo, German: ")
        a, b, c = ports.split()
    except ValueError:
        print("Invalid amount of port number entered, program will terminate")
        sys.exit()
    a, b, c = int(a), int(b), int(c)
    invalid = False
    for port in [a, b, c]:
        if port < 1024 or port > 64000:
            invalid = True
    if a == b or a == c or b == c: invalid = True
    if invalid:
        print("Invalid port numbers entered, program will terminate")
        sys.exit()
    else:
        return a, b, c


# Getting the three port numbers from the user
english_port, maori_port, german_port = get_ports()
# Opening three UDP sockets
english_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
maori_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
german_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Binding the three sockets to their ports
try:
    english_socket.bind(('', english_port))
    maori_socket.bind(('', maori_port))
    german_socket.bind(('', german_port))
except socket.error:
    print("Binding sockets to ports failed, program will terminate")
    sys.exit()



