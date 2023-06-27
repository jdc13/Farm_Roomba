# Uart Communication - Micropython Pico
# 5/10/2023

import machine
import time

uart = machine.UART(0, baudrate=9600, bits=8, parity=None, stop=1, tx=machine.Pin(0), rx=machine.Pin(1))

while True:
    if uart.any():
        message = b""
        while True:
            data = uart.read(1)
            if not data or data == b'\n':
                break
            message += data
        message_str = message.decode('utf-8').strip()
        print("Received message:", message_str)
   
        uart.write("bad send".encode())
        
        
    time.sleep(0.1)
