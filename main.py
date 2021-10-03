import serial.tools.list_ports
from tkinter import ttk
import tkinter as tk
import threading
import time
import os

from socketHandler import SocketHandler
from handleChatMsgs import HandleChatMsgs

# Enables user to switch to next element using TAB
def focus_with_tab(var):
    var.widget.tk_focusNext().focus()
    return

# Handles the popup that alerts the user
def pop_ups(val):
    popup = tk.Toplevel()
    popup.geometry("300x125")
    popup.wm_title("-- Attention --")
    custom_label = tk.Label(popup, text=val)
    custom_label.pack(pady=(25, 0))
    ok_btn = tk.Button(popup, text="OK", width=8, command=popup.destroy)
    ok_btn.pack(pady=(20, 0))


class TwitchChatter:
    def __init__(self, main_window):
        self.comPortList = ["None"]
        ports = serial.tools.list_ports.comports()
        for port, desc, hwid in sorted(ports):
            self.comPortList.append(desc + " @ " + port)

        self.arduinoCom = HandleChatMsgs()

        self.msg = "QUACK QUACK!"
        self.timeBetweenPokes = 10.0
        self.userName = ""
        self.channelName = ""
        self.oauthToken = ""

        self.myTwitchSocket = SocketHandler()
        self.isConnected = False

        main_frame = tk.Frame(main_window)
        main_frame.pack()

        arduino_frame = tk.Frame(main_frame)
        arduino_frame.pack(pady=(10,10))

        u_name_frame = tk.Frame(main_frame)
        u_name_frame.pack(pady=(20, 10))

        channel_frame = tk.Frame(main_frame)
        channel_frame.pack(pady=(0, 10))

        oauth_frame = tk.Frame(main_frame)
        oauth_frame.pack(pady=(0, 10))

        save_frame = tk.Frame(main_frame)
        save_frame.pack(pady=(20, 10))

        chat_box_frame = tk.Frame(main_frame)
        chat_box_frame.pack(pady=(20, 0))

        buttons_frame = tk.Frame(main_frame)
        buttons_frame.pack(pady=(10, 20))

        self.arduinoLabel = tk.Label(arduino_frame, text="Pick your Arduino: ").pack(side=tk.LEFT)
        self.arduinoVal = tk.StringVar
        self.arduinoDropDown = ttk.Combobox(arduino_frame, width=40, textvariable=self.arduinoVal)
        self.arduinoDropDown['values'] = self.comPortList
        self.arduinoDropDown.set(self.comPortList[0])
        self.arduinoDropDown.bind("<<ComboboxSelected>>", self.handle_arduino_combobox)
        self.arduinoDropDown.pack(side=tk.RIGHT)

        self.uNameLabel = tk.Label(u_name_frame, text="Username: ")
        self.uNameLabel.pack(side=tk.LEFT, padx=(0, 27))

        self.uNameEntry = tk.Entry(u_name_frame, width=40)
        self.uNameEntry.pack(side=tk.RIGHT)
        self.uNameEntry.bind("<Tab>", focus_with_tab)

        self.channelLabel = tk.Label(channel_frame, text="Target Channel: ")
        self.channelLabel.pack(side=tk.LEFT)

        self.channelEntry = tk.Entry(channel_frame, width=40)
        self.channelEntry.pack(side=tk.RIGHT)
        self.channelEntry.bind("<Tab>", focus_with_tab)

        self.oauthLabel = tk.Label(oauth_frame, text="OAuth Token: ")
        self.oauthLabel.pack(side=tk.LEFT, padx=(0, 10))

        self.oauthEntry = tk.Entry(oauth_frame, width=40)
        self.oauthEntry.configure(show="*")
        self.oauthEntry.pack(side=tk.RIGHT)
        self.oauthEntry.bind("<Tab>", focus_with_tab)

        self.saveButton = tk.Button(save_frame, text="Save", command=self.save_user_cred)
        self.saveButton.pack(side=tk.LEFT, padx=(0, 20))
        self.clearButton = tk.Button(save_frame, text="Clear all", command=self.clear_all_credentials)
        self.clearButton.pack(side=tk.RIGHT, padx=(20, 0))

        self.chatBoxLabel = tk.Label(chat_box_frame, text="Twitch chat activity:")
        self.chatBoxLabel.pack()

        self.chatResponse = tk.Text(chat_box_frame, height=15, width=60)
        self.chatResponse.configure(state='disabled')
        self.chatResponse.pack(pady=(0,20))

        self.connectButton = tk.Button(buttons_frame, text="Connect", command=self.connect_socket)
        self.connectButton.pack(side=tk.LEFT, padx=(0, 20))
        self.disconnectButton = tk.Button(buttons_frame, text="Disconnect", command=self.disconnect_socket)
        self.disconnectButton.pack(side=tk.RIGHT, padx=(20, 0))
        self.disconnectButton.config(state="disabled")

        self.settingsList = []
        if os.path.isfile("settings.txt"):
            with open("settings.txt", "r") as oldSettings:
                for line in oldSettings:
                    self.settingsList.append(line)

            if len(self.settingsList) == 3:
                self.uNameEntry.insert(tk.END, self.settingsList[0].strip())
                self.userName = self.settingsList[0].strip()
                self.channelEntry.insert(tk.END, self.settingsList[1].strip())
                self.channelName = self.settingsList[1].strip()
                self.oauthEntry.insert(tk.END, self.settingsList[2].strip())
                self.oauthToken = self.settingsList[2].strip()
                self.myTwitchSocket.config_socket(self.userName, self.channelName, self.oauthToken)
                self.myTwitchSocket.configured = True

    def handle_arduino_combobox(self, var):
        current_val = self.arduinoDropDown.get()
        if current_val != "None":
            current_val = current_val.partition(" @ ")[2]
            self.arduinoCom.config_arduino(current_val)

    def connect_socket(self):
        if self.myTwitchSocket.configured:
            self.myTwitchSocket.connect_to_twitch()
            self.isConnected = True
            self.saveButton.configure(state='disable')
            self.clearButton.configure(state='disable')
            # declare threadedRec here to be able to restart is after "disconnect".
            self.threadedRec = threading.Thread(target=self.threaded_chat_receiver)
            self.threadedRec.start()
            self.disconnectButton.configure(state="normal")
            self.connectButton.configure(state="disable")
        else:
            pop_ups("You need to complete the configuration first.")

    def threaded_chat_receiver(self):
        time_previous = time.time()
        while True:
            if not self.isConnected:
                self.chatResponse.configure(state='normal')
                self.chatResponse.insert(tk.END, "DISCONNECTED" + '\n')
                self.chatResponse.configure(state='disable')
                return
            incoming_string = self.myTwitchSocket.live_monitor_chat()
            self.chatResponse.configure(state='normal')
            self.chatResponse.insert(tk.END, incoming_string + '\n')
            self.chatResponse.configure(state='disable')
            self.chatResponse.see("end")

            if incoming_string == "POKE!":
                time_current = time.time()
                if time_current - time_previous > self.timeBetweenPokes:
                    time_previous = time_current
                    self.arduinoCom.arduino_serial_communication('r/1/0/0/')
                    try:
                        message_temp = f'PRIVMSG {self.channelName} :{self.msg}'
                        self.myTwitchSocket.twitchSocket.send(f'{message_temp}\n'.encode())
                    except:
                        pass
                    self.arduinoCom.quackSound.music.play()
                else:
                    wait_msg = "Quack is immune to POKES for " + str(int(self.timeBetweenPokes - (time_current - time_previous))) + " seconds"
                    message_temp = f'PRIVMSG {self.channelName} :{wait_msg}'
                    self.myTwitchSocket.twitchSocket.send(f'{message_temp}\n'.encode())

            elif incoming_string == "RED!":
                self.arduinoCom.arduino_serial_communication('c/255/0/0/')
            elif incoming_string == "GREEN!":
                self.arduinoCom.arduino_serial_communication('c/0/255/0/')
            elif incoming_string == "BLUE!":
                self.arduinoCom.arduino_serial_communication('c/0/0/255/')
            elif incoming_string == "CYAN!":
                self.arduinoCom.arduino_serial_communication('c/0/155/155/')
            elif incoming_string == "PINK!":
                self.arduinoCom.arduino_serial_communication('c/255/0/255/')
            elif incoming_string == "YELLOW!":
                self.arduinoCom.arduino_serial_communication('c/255/255/0/')
            elif incoming_string == "BLACK!":
                self.arduinoCom.arduino_serial_communication('c/0/0/0/')
            elif incoming_string == "WHITE!":
                self.arduinoCom.arduino_serial_communication('c/255/255/255/')

    def disconnect_socket(self):
        self.isConnected = False
        self.myTwitchSocket.disconnect_from_twitch()
        self.connectButton.configure(state="normal")
        self.saveButton.configure(state='normal')
        self.clearButton.configure(state='normal')
        self.disconnectButton.configure(state="disable")

    def save_user_cred(self):
        self.userName = self.uNameEntry.get()
        self.channelName = self.channelEntry.get()
        self.oauthToken = self.oauthEntry.get()
        if len(self.userName) > 0 and len(self.channelName) > 0 and len(self.oauthToken) > 0:
            if self.channelName[0] != '#':
                pop_ups("Invalid channel, did you forget '#'?")
                return
            if not self.oauthToken.startswith("oauth:"):
                pop_ups("Invalid oauth, try again.")
                return
        else:
            pop_ups("You need to fill out all the fields above.")
            return

        with open("settings.txt", "w+") as newSettings:
            newSettings.write(self.userName + "\n" + self.channelName + "\n" + self.oauthToken)

        self.myTwitchSocket.config_socket(self.userName, self.channelName, self.oauthToken)
        pop_ups("Credentials saved.")

    def clear_all_credentials(self):
        self.uNameEntry.delete('0', tk.END)
        self.channelEntry.delete('0', tk.END)
        self.oauthEntry.delete('0', tk.END)
        self.userName = ""
        self.channelName = ""
        self.oauthToken = ""
        self.myTwitchSocket.configured = False
        with open("settings.txt", "w+") as settingsFile:
            settingsFile.close()


root = tk.Tk(className="TwitchChatter")
root.geometry("500x575")
root.title("Twitch ChatBot 2021")
root.wm_iconbitmap('icon_small.ico')
app = TwitchChatter(root)
root.mainloop()
