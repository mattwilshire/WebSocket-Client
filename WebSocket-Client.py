import socket
import json
import random

'''
    Note:
        The TCP recv function should be on another thread receiving the messages.
        But for example purposes it is all synchronous.

        I made this for Rust server to use the RCON websocket to run console commands!
        This will work for any web socket but needs some polishing, but the general structure is made.
'''

def createSocket(host, port, password):

    '''
        Creates TCP client and sends websocket connect message.
    '''
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))

    connect_message = \
    f"GET /{password} HTTP/1.1\r\n" \
    "Sec-WebSocket-Version: 13\r\n" \
    "Sec-WebSocket-Key: Vd3KpLNcTM0oF1n4bW7Gjw==\r\n" \
    "Connection: Upgrade\r\n" \
    "Upgrade: websocket\r\n" \
    "Sec-WebSocket-Extensions: permessage-deflate; client_max_window_bits\r\n" \
    f"Host: {host}:{port}\r\n\r\n"

    print(f"Connected to websocket @ {host}:{port}")
    sock.send(connect_message.encode('UTF-8'))
    data = sock.recv(1024)
    print(f"Received -> {data!r}")
    return sock

def send(sock, message):
    '''
        BYTE INFORMATION:

            first byte -> FIN + RSV1 + RSV2 + OPCODE
            second byte -> MASK + payload length (7 bits)
            third, fourth, fifth and sixth bytes -> (optional) XOR encoding key bytes (mask key)
        
        BIT INFORMATION:
            FIN    [1 bit]      -> 1 if the whole message is contained in this frame, 0 otherwise
            RSVs   [1 bit each] -> MUST be 0 unless an extension is negotiated that defines meanings for non-zero values
            OPCODE [4 bits]     -> defines the interpretation of the carried payload
            
            MASK           [1 bit]  -> 1 if the message is XOR masked with a key, 0 otherwise
            payload length [7 bits] -> can be max 1111111 (127 dec), so, the payload cannot be more than 127 bytes per frame
        

        VALID OPCODES:
           - 0000 [0]             -> continuation frame
           - 0001 [1]             -> text frame
           - 0010 [2]             -> binary frame
           - 0011 [3] to 0111 [7] -> reserved for further non-control frames
           - 1000 [8]             -> connection close
           - 1001 [9]             -> ping
           - 1010 [A]             -> pong
           - 1011 [B] to 1111 [F] -> reserved for further control frames

    '''
    message = json.dumps(message)

    first_byte = 0

    fin = "1"
    reserved = "000"
    opcode = "0001"
    mask = "1"

    first_byte = first_byte | int(f'0b{fin}0000000', 2)
    first_byte = first_byte | int(f'0b0{reserved}0000', 2)
    first_byte = first_byte | int(f'0b0000{opcode}', 2)
    
    second_byte = len(message) | int(f'0b{mask}0000000', 2)

    # 4 byte mask key used to xor the payload, this is needed when the mask bit is set to 
    # masking is used to stop proxies interfering and caching of http requests
    maskKey = []
    for i in range(0, 4):
        maskKey.append(random.randint(0, 255))

    payload_masked = []

    # Loop through message and xor each byte by the maskKey
    i = 0
    while i < len(message):
        payload_masked.append(ord(message[i]) ^ maskKey[i % len(maskKey)])
        i += 1

    first_second = [first_byte, second_byte]
    data = bytearray(first_second) + bytearray(maskKey) + bytearray(payload_masked)
    sock.send(data)

    data = sock.recv(1024).decode("utf-8", "ignore")
    print(f"Received {data!r}")



version = {
      "Identifier": 123,
      "Message": "oxide.version",
      "Name": "WebRcon"
    }

playerlist = {
      "Identifier": 1446,
      "Message": "playerlist",
      "Name": "WebRcon"
    }

sock = createSocket("127.0.0.1", 28016, "test")
send(sock, version)
send(sock, playerlist)