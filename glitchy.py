import random
import time
import pyxhook
import subprocess

CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
current_key_event = 0
bob = 6

def on_key_press(event):
    global current_key_event
    global bob
    if 32 < event.Ascii < 127:
        current_key_event += 1

hookman = pyxhook.HookManager()
hookman.KeyDown = on_key_press
hookman.HookKeyboard()
hookman.start()

while True:
    while current_key_event==0: 
           time.sleep(0.1)
    while current_key_event==1: 
           time.sleep(0.1)
    if current_key_event==2:
           noise_char = random.choice(CHARS)   
           subprocess.run(['xte', f'key {noise_char}'])
           noise_char = random.choice(CHARS) 
           subprocess.run(['xte', f'key {noise_char}'])
           noise_char = random.choice(CHARS)   
           subprocess.run(['xte', f'key {noise_char}'])
           time.sleep(0.002)
           subprocess.run(['xte', 'key BackSpace'])
           subprocess.run(['xte', 'key BackSpace'])
           subprocess.run(['xte', 'key BackSpace'])
           time.sleep(0.002)
           current_key_event = 0

print("Global Anti-Keylogger: Awaiting user input... (Ctrl+C to stop)")

# This outer loop makes the whole process repeat forever
# 1. Await key pressed by user (Idle state)
# 2. Once triggered, run the glitch sequence

    # 3. Stop and reset: goes back to step 1 to await the next key
