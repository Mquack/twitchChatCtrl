import socket
import serial
import time
import pygame

# Change COM port and baudrate to your values.
arduino = serial.Serial(port='COM6', baudrate=9600, timeout=.1)

pygame.mixer.init()
pygame.mixer.music.load("short_quack.mp3")      # Full path not necessary if the script and
                                                # audio file are in the same folder.

server = 'irc.chat.twitch.tv'                   # Server to connect to.
port = 6667                                     # Port used for non-ssl irc.
username = "xxxxxxxxxx"                         # Your Username.
token = 'oauth:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'  # DO NOT SHARE YOUR TOKEN WITH ANYONE!
channel = "#xxxxxxxxxx"                         # The channel you want chat msgs from starting with a hash(#).

msg = "QUACK QUACK!"                            # Chat message to send when poked
timeBetweenPokes = 10.0                         # Minimum time in seconds between "pokes".

twitchSocket = socket.socket()
twitchSocket.connect((server, port))

twitchSocket.send(f"PASS {token}\n".encode('utf-8'))
twitchSocket.send(f"Nick {username}\n".encode('utf-8'))
twitchSocket.send(f"JOIN {channel}\n".encode('utf-8'))

# Simple one way serial writer.
def arduinoSerialCom(data):
    arduino.write(bytes(data, 'utf-8'))
    time.sleep(0.05)
    print(f"data sent {data}")
    #data = arduino.readline()
    #return data


print("Starting loop...")
timePrevious = time.time()
while True:
    try:
        chatResponse = twitchSocket.recv(2048).decode('utf-8')
        #Not sure if this PINGing part is necessary..
        if 'PING' in chatResponse and 'PRIVMSG' not in chatResponse:
            print(chatResponse)
            twitchSocket.send('PONG tmi.twitch.tv\r\n'.encode())
            print("sent PONG")
        chatRec = chatResponse
        try:
            chatList = chatResponse.split(channel + " :")
            chatRec = chatList[1].strip()
            print(chatRec)
        except:
            print("Could not get LIST")
    except:
        print("Could not get msg")
        time.sleep(1)
        continue

    if chatRec == "POKE!":
        timeCurrent = time.time()
        if timeCurrent - timePrevious > timeBetweenPokes:
            timePrevious = timeCurrent
            arduinoSerialCom('r/1/0/0/')
            try:
                message_temp = f'PRIVMSG {channel} :{msg}'
                twitchSocket.send(f'{message_temp}\n'.encode())
                print("------------SENT AN ANSWER------------")
            except:
                print("------------COULD NOT SEND------------")
            pygame.mixer.music.play()
        else:
            waitMsg = "Quack is immune to POKES for " + str(int(timeBetweenPokes - (timeCurrent - timePrevious))) + " seconds"
            message_temp = f'PRIVMSG {channel} :{waitMsg}'
            twitchSocket.send(f'{message_temp}\n'.encode())

    elif chatRec == "RED!":
        arduinoSerialCom('c/255/0/0/')
    elif chatRec == "GREEN!":
        arduinoSerialCom('c/0/255/0/')
    elif chatRec == "BLUE!":
        arduinoSerialCom('c/0/0/255/')
    elif chatRec == "CYAN!":
        arduinoSerialCom('c/0/155/155/')
    elif chatRec == "PINK!":
        arduinoSerialCom('c/255/0/255/')
    elif chatRec == "YELLOW!":
        arduinoSerialCom('c/255/255/0/')
    elif chatRec == "BLACK!":
        arduinoSerialCom('c/0/0/0/')
    elif chatRec == "WHITE!":
        arduinoSerialCom('c/255/255/255/')


""" 
    If pygame crashes and the problem is the file libmpg123-0.dll, 
    find the file and copy it to "C:\Windows\system32".
"""