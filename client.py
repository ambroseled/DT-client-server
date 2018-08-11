# Importing used modules
import socket as soc
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


def validate_packet(pkt):
    """
    Checks that the received packet is valid, exits the program with an error
    message if the packet is invalid
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
        # Output an error message if an error was found
        print("*****************************")
        print("{0}, program will terminate".format(text))
        print("*****************************")
        sys.exit()


def handle_packet(pkt):
    """
    Handles the response packet once it hs been received
    from the server
    """
    # Checking the packet is valid
    validate_packet(pkt)
    # Printing the information from the packet
    if ((pkt[4] << 8) + pkt[5]) == ENGLISH_CODE:
        lang = "English"
    elif ((pkt[4] << 8) + pkt[5]) == MAORI_CODE:
        lang = "Maori"
    else:
        lang = "German"
    print("Response from server:")
    print("-----")
    print("Magic number: {0}\nPacket type: {1}".format(hex((pkt[0] << 8) + pkt[1]), RESPONSE_PACKET))
    print("Language code: {0}\nLength of text: {1}".format(lang, pkt[12]))
    print("-----")
    # Getting time and date to output
    text = pkt[13:]
    date = "{0}:{1}:{2}".format(((pkt[6] << 8) + pkt[7]), pkt[8], pkt[9])
    if pkt[11] < 10:
        time = "{0}:0{1}".format(pkt[10], pkt[11])
    else:
        time = "{0}:{1}".format(pkt[10], pkt[11])
    print("The date is: {0}".format(date))
    print("The time is: {0}".format(time))
    print("Textual representation received: {0}".format(text.decode()))
    # Exiting the program
    print("-----------------------------")
    print("-----------------------------")
    print("Program will now exit")
    print("-----------------------------")
    print("-----------------------------")
    sys.exit()


def get_request():
    """
    Gets the user to input the request type
    """
    print("-----------------------------")
    print("-----------------------------")
    request_type = input("Enter request choice, date or time: ")
    # Checking if users request choice is valid
    if request_type != "date" and request_type != "time":
        print("*****************************")
        print("Invalid request choice, program will terminate")
        print("*****************************")
        sys.exit()
    # Returning the request type
    if request_type == "date":
        return DATE_REQUEST
    else:
        return TIME_REQUEST


def get_host():
    """
    Gets the user to input the host IP or address
    """
    entered_host = input("Enter the host IP in dotted decimal or the hostname: ")
    # Checking if entered hostname/IP is valid
    try:
        return soc.gethostbyname(entered_host)
    except soc.gaierror:
        print("*****************************")
        print("Invalid hostname or IP address entered, program will terminate")
        print("*****************************")
        sys.exit()


def get_port():
    """
    Gets the user to input the port number to use
    """
    try:
        port = int(input("Enter a port number to use between 1024 and 64000: "))
        # Checking if the entered port number is valid
        if port < 1024 or port > 64000:
            print("*****************************")
            print("Invalid port number entered, program will terminate")
            print("*****************************")
            sys.exit()
        return port
    except ValueError:
        print("*****************************")
        print("Invalid type entered port number must be an integer, program will terminate")
        print("*****************************")
        sys.exit()


def main():
    """
    Runs the program
    :return:
    """
    # Getting the request type from the user
    request = get_request()
    # Getting user to enter hostname or IP address of server
    host_IP = get_host()
    # Getting user to enter a port number to use
    port = get_port()
    # Opening socket for communication with the server
    server = (host_IP, port)
    socket = soc.socket(soc.AF_INET, soc.SOCK_DGRAM)
    # Creating a request packet
    request_packet = bytearray(3)
    request_packet[0:1] = struct.pack(">H", MAGIC_NUMBER)
    request_packet[2:3] = struct.pack(">H", REQUEST_PACKET)
    request_packet[4:5] = struct.pack(">H", request)
    # Sending request packet to the server
    socket.sendto(request_packet, server)
    print("-----------------------------")
    print("-----------------------------")
    print("Request packet sent to {0}".format(server))
    # Waiting for 1 second for response from the server
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
                pkt, address = sock.recvfrom(1024)
                print("Response packet received from {0}".format(address))
                print("-----------------------------")
                print("-----------------------------")
                sock.close()
                handle_packet(pkt)


main()
