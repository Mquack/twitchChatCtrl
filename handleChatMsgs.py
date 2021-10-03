import serial
import time
import pygame


class HandleChatMsgs:
    def __init__(self, com_port="None"):
        if com_port != "None":
            self.arduino = serial.Serial(port=com_port, baudrate=9600, timeout=.1)
        self.quackSound = pygame.mixer
        self.quackSound.init()
        self.quackSound.music.load("short_quack.mp3")

    def arduino_serial_communication(self, data):
        self.arduino.write(bytes(data, 'utf-8'))
        time.sleep(0.05)

    def config_arduino(self, com_port):
        self.arduino = serial.Serial(port=com_port, baudrate=9600, timeout=.1)
