# Date-Time Client Server

A simple client server which to provide the date and time in English, Maori and German to the client.

## Usage
  - First run `python3 server.py English_port Maori_port German_port`
  - Then run `python3 client.py request host port`

### Server Usage
  - Navigate to the file `server.py`
  - Run `python3 server.py English_port Maori_port German_port`
  - Where
      * All ports are between `1024` and `64000`
      * All ports are unique
      
      
### Client Usage
  - Navigate to the file `client.py`
  - Run `python3 client.py request host port`
  - Where
      * request is `date` or `time`
      * host is a valid IP address or host name
          - Ideally the IP of the machine running server.py
      * port is between `1024` and `64000`
          - Ideally on of the ports entered when configuring the server

