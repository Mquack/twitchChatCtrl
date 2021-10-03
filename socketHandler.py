import socket


class SocketHandler:
    def __init__(self):
        self.username = ""                          # Your Username.
        self.channel = ""                           # The channel you want chat msgs from starting with a hash(#).
        self.token = ""                             # DO NOT SHARE YOUR TOKEN WITH ANYONE!

        self.configured = False

        self.server = 'irc.chat.twitch.tv'          # Server to connect to.
        self.port = 6667                            # Server to connect to.

        self.twitchSocket = socket.socket()

    def config_socket(self, user_name, user_channel, user_token):
        self.username = user_name
        self.channel = user_channel
        self.token = user_token
        self.configured = True

    def connect_to_twitch(self):
        self.twitchSocket.connect((self.server, self.port))

        self.twitchSocket.send(f"PASS {self.token}\n".encode('utf-8'))
        self.twitchSocket.send(f"Nick {self.username}\n".encode('utf-8'))
        self.twitchSocket.send(f"JOIN {self.channel}\n".encode('utf-8'))

    def disconnect_from_twitch(self):
        self.twitchSocket.close()
        self.twitchSocket = socket.socket()

    def live_monitor_chat(self):
        try:
            chat_response = self.twitchSocket.recv(2048).decode('utf-8')
            # Not sure if this PING'ing part is necessary..
            if 'PING' in chat_response and 'PRIVMSG' not in chat_response:
                self.twitchSocket.send('PONG tmi.twitch.tv\r\n'.encode())
            chat_received = chat_response
            try:
                chat_list = chat_response.split(self.channel + " :")
                chat_received = chat_list[1].strip()
            except:
                chat_received = "PING"

        except:
            chat_received = "n/a"
            #time.sleep(1)

        return chat_received