"""
ATTN: This bot relies on both the pymumble and numpy libraries. Make sure they are installed before running.

mimic-bot connects to the murmur server you designate, enters the channel assigned via "channel", 
and repeats back audio received from the user after a short delay
"""

import pymumble_py3
import time
from pymumble_py3.callbacks import PYMUMBLE_CLBK_SOUNDRECEIVED as PCS
from collections import deque
import numpy as np

server = "localhost" # Server address
nick = "mimic-bot" # Bot name
channel = "audio test" # Channel name
audio_buffer = deque() # Initialize a buffer to store audio chunks
last_received = None # Initialize a timestamp for the last received chunk
wait_duration = 2.0 # Duration to wait before mimic

def sound_received_handler(user, soundchunk):
    global audio_buffer, last_received
    last_received = time.time()
    audio_buffer.append(np.frombuffer(soundchunk.pcm, dtype=np.int16))

mumble = pymumble_py3.Mumble(server, nick)
mumble.callbacks.set_callback(PCS, sound_received_handler)
mumble.set_receive_sound(1)  # Audio received
mumble.start()
mumble.is_ready()
mumble.channels.find_by_name(channel).move_in()

while True:
    current_time = time.time()
    if last_received and (current_time - last_received >= wait_duration): # Calculate wait duration
        last_received = None
        buffered_audio = np.concatenate(list(audio_buffer)) # Begin buffer
        audio_buffer.clear()
        buffered_duration = len(buffered_audio) / 48000.0
        num_samples_for_5_sec = int((5.0 - buffered_duration) * 48000)
        silence_data = np.zeros(max(0, num_samples_for_5_sec), dtype=np.int16)
        new_audio = np.concatenate((silence_data, buffered_audio)) # End buffer

        new_pcm = new_audio.tobytes() # Combine audio and send
        mumble.sound_output.add_sound(new_pcm)

    time.sleep(0.1)  # Sleep until needed
