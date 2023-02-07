from time import sleep
import serial
import pygame
import random
pygame.mixer.init()
pygame.mixer.music.load('bonk.mp3')
pygame.mixer.music.play()



with serial.Serial('com3', 9600, timeout=1) as ser:
    while(True):
        #x = ser.read()          # read one byte
        #s = ser.read(10)        # read up to ten bytes (timeout)
        line = ser.readline()
        print(line)

        if line == b'BONK\r\n':
            if random.random() > 0.5:
                pygame.mixer.music.load('bonk.mp3')
                pygame.mixer.music.play()
            else:
                pygame.mixer.music.load('hitmarker.mp3')
                for _ in range(5):
                    pygame.mixer.music.play()
                    sleep(0.05)



