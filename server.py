import datetime
import socket
import sys
from select import select
import struct

# Defining constants
MAGIC_NUMBER = 0x497E
REQUEST_PACKET = 0x0001
RESPONSE_PACKET = 0x0002
DATE_REQUEST = 0x0001
TIME_REQUEST = 0x0002
ENGLISH_CODE = 0x0001
MAORI_CODE = 0x0002
GERMAN_CODE = 0x0003
# Defining the months of the year in all three languages
english_months = ["January", "February", "March", "April", "May", "June", "July", "August", "September",
                  "October", "November", "December"]
maori_months = ["Kohitātea", "Hui-tanguru", "Poutū-te-rangi", "Paenga-whāwhā", "Haratua", "Pipiri",
                "Hōngongoi", "Here-turi-kōkā", "Mahuru", "Whiringa-ā-nuku", "Whiringa-ā-rangi", "Hakihea"]
german_months = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September",
                 "Oktober", "November", "Dezember"]

def get_time():
    """
    Getting the date and current time
    """
    time = datetime.datetime.now()
    year = str(time.year)
    month = str(time.month)
    day = str(time.day)
    hour = str(time.hour)
    minute = str(time.minute)
    return [year, month, day, hour, minute]


def textual_date(year, month, day, lang_code):
    """
    Converting the numerical time into the textual date dependent on
    the passed language code
    """
    if lang_code == ENGLISH_CODE:
        date_text = "Today's date is {0} {1}, {2}".format(english_months[month-1], day, year)
    elif lang_code == MAORI_CODE:
        date_text = "Ko te ra o tenei ra ko {0} {1}, {2}".format(maori_months[month-1], day, year)
    else:
        date_text = "Heute ist der {0}. {1} {2}".format(day, german_months[month-1], year)
    return date_text


def textual_time(hour, minute, lang_code):
    """
    Converting the numerical time into the textual time dependent on
    the passed language code
    """
    if lang_code == ENGLISH_CODE:
        time_text = "The current time is {0}:{1}".format(hour, minute)
    elif lang_code == MAORI_CODE:
        time_text = "Ko te wa o tenei wa {0}:{1}".format(hour, minute)
    else:
        time_text = "Die Uhrzeit ist {0}:{1}".format(hour, minute)
    return time_text


def get_ports():
    """
    Getting three port numbers from the user and checking the ports
    are valid. IF the ports are valid they are returned, if the are invalid
    an error message is printed and the program exits
    """
    # Getting user to input the three ports
    try:
        ports = input("Enter three port numbers between 1024 and 64000 in following order: English, Te reo, German: ")
        a, b, c = ports.split()
    except ValueError:
        print("Invalid amount of port number entered, program will terminate")
        sys.exit()
    a, b, c = int(a), int(b), int(c)
    invalid = False
    # Checking that the ports are valid
    for port in [a, b, c]:
        if port < 1024 or port > 64000:
            invalid = True
    if a == b or a == c or b == c: invalid = True
    if invalid:
        print("Invalid port numbers entered, program will terminate")
        sys.exit()
    else:
        return [a, b, c]

def decodePacket(pkt):
    """
    Checking if the reciveved packet is valid and returning a
    corrosponding code if it is
    """
    if len(pkt) != 6:
        return 1
    elif ((pkt[0] << 8) + pkt[1]) != MAGIC_NUMBER:
        return 2
    elif ((pkt[2] << 8) + pkt[3]) != REQUEST_PACKET:
        return 3
    elif ((pkt[4] << 8) + pkt[5]) not in [DATE_REQUEST or TIME_REQUEST]:
        return 4
    else:
        return 0

def printErrors(errorCode):
    """
    Prints an error message when an invalid packet is recevied
    """
    if errorCode == 1:
        print("Packet is of invalid length and will be discarded")
    elif errorCode == 2:
        print("Magic number is invalid, packet will be discarded")
    elif errorCode == 3:
        print("Packet type invalid, packet will be discarded")
    elif errorCode == 4:
        print("Request type invalid, packet will be discarded")
    else:
        print("Packet is invalid and will be discarded")

def getLang(sock, sockets):
    """
    Finds out what language the client wants to receive
    text in
    """
    if sock == sockets[0]:
        return 0x0001
    elif sock == sockets[1]:
        return 0x0002
    else:
        return 0x0003

def handlePacket(pkt, lang_code):
    """
    Decodes recevied packet and calls makeRespone() to
    create the response packet
    """
    request = (pkt[4] << 8) + pkt[5]
    if request == 0x0001:
        makeResponse(True, lang_code)
    elif request == 0x0002:
        makeResponse(False, lang_code)
    else:
        print("Invalid request type, packet will be discarded")
        return None


def makeResponse(request_flag, lang_code):
    """
    Creates a response packet
    """
    time = get_time()
    if request_flag:
        text = textual_date(time[0], time[1], time[2], lang_code)
    else:
        text = textual_time(time[3], time[4], lang_code)
    response = bytearray()
    response.extend(struct.pack(">H", MAGIC_NUMBER))
    response.extend(struct.pack(">H", RESPONSE_PACKET))
    response.extend(struct.pack(">H", lang_code))
    response.extend(struct.pack(">H", time[0]))
    response.extend(struct.pack(">H", ((time[1] << 8) + time[2])))
    response.extend(struct.pack(">H", ((time[3] << 8) + time[4])))
    encoded_text = text.encode()
    response.extend(struct.pack(">H", (len(text) << 8) + encoded_text[0]))
    response.extend(encoded_text[1:])
    print(response)


# Getting the three port numbers from the user
english_port, maori_port, german_port = get_ports()
sockets = [english_port, maori_port, german_port]
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


while True:

    readable, writeable, exceps = select([english_socket, maori_socket, german_socket], [english_socket, maori_socket, german_socket], [])
    if len(readable) != 0:
        for sock in readable:
            data, addr = sock.recvfrom(1024)
            valid = decodePacket(data)
            lang_code = getLang(sock, sockets)
            if valid != 0:
                printErrors(valid)
                continue
            else:
                response = handlePacket(data, lang_code)
