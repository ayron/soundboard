import pyaudio
import wave
import sys
import struct
import threading
import time
from enum import Enum, auto
from ctypes import *

libwave = CDLL('./libwave.so')
libwave.scale_frame.restype = None
libwave.scale_frame.argtypes = [
  c_char_p,
  c_size_t,
  c_size_t,
  c_char_p,
  c_float
]

NUM_FRAMES = 1024

class State(Enum):
    OPEN = auto()
    STREAMING = auto()
    CLOSE = auto()

class DState(Enum):
    DELAY = auto()
    PLAY = auto()

class RState(Enum):
    RAMP_UP = auto()
    NORMAL = auto()
    RAMP_DOWN = auto()

class Audio:

    def __init__(self):

        print('Starting portaudio')
        self.p = pyaudio.PyAudio()
        self.players = []

    def __del__(self):

        print('Terminating portaudio')
        self.p.terminate()

    def play(self, tree, row_id):

        if tree.set(row_id, 'bg') == 'x':

            # First stop all other background tracks
            for player in self.players:
                if player.tree.set(player.row_id, 'bg') == 'x':
                    player.stop = True

        wp = WavPlayer(self, tree, row_id)
        wp.start()
        self.players.append(wp)

    def stop_all(self):

        print('Stopping all')
        for player in self.players:
            player.stop = True

def chunk(data, n):
    """Returns iterator."""

    for i in range(0, len(data), n):
        yield data[i:i+n]


def convert_wav(data_wav, wfp):
    """ Converts wav to list of samples in each channel.
    Returns generator"""

    scale = 1.0 / 2**(8*wfp.sampwidth)
    samples = [float(int.from_bytes(sample, byteorder='little', signed=True))
               for sample in chunk(data_wav, wfp.sampwidth)]
    samples = [s*scale for s in samples]

    # Collect channels
    return list(chunk(samples, wfp.nchannels))


class WavPlayer(threading.Thread):

    def __init__(self, audio, tree, row_id):

        super().__init__()
        self.tree = tree
        self.row_id = row_id
        self.p = audio.p
        self.audio = audio
        self.stop = False
        self.state = State.OPEN
        self.ramp_state = RState.RAMP_UP
        self.delay_state = DState.DELAY
        self.start_time = time.time()
        self.ramp_duration = 3
        self.volume = 0.0

    def run(self):

        while True: # State machine

            #print(self.state, self.ramp_state, self.delay_state, self.volume)

            if self.state == State.OPEN:

                path = self.tree.set(self.row_id, 'path')
                print('Loading', path)
                wf = wave.open(path, 'rb')

                wfp = wf.getparams()
                #print(wfp)
                st = time.time()

                sample_size = wfp.sampwidth
                frame_size = wfp.nchannels*sample_size
                volume_per_frame = 1.0 / self.ramp_duration / wfp.framerate

                scaled_frame = create_string_buffer(4*wfp.nchannels)

                print('Opening stream')
                stream = self.p.open(
                    format = self.p.get_format_from_width(4),
                    #format = 2,
                    channels = wfp.nchannels,
                    rate = wfp.framerate,
                    output = True)

                print('playing', path)
                self.state = State.STREAMING
                self.start_time = time.time()

                zero_data = bytes(4*wfp.nchannels*NUM_FRAMES)

            elif self.state == State.STREAMING:

                is_bg = self.tree.set(self.row_id, 'bg') == 'x'

                if self.ramp_state == RState.RAMP_UP:

                    if not is_bg:
                        self.volume = 1.0

                    ramp_up_complete = self.volume >= 1.0

                    if self.stop:
                        self.ramp_state = RState.RAMP_DOWN

                    if ramp_up_complete:
                        self.ramp_state = RState.NORMAL

                elif self.ramp_state == RState.NORMAL:

                    if self.stop:
                        self.ramp_state = RState.RAMP_DOWN

                elif self.ramp_state == RState.RAMP_DOWN:

                    ramp_down_complete = self.volume <= 0.0
                    if ramp_down_complete or not is_bg:
                        self.state = State.CLOSE

                if self.delay_state == DState.DELAY:

                    delay = self.tree.set(self.row_id, 'delay')

                    if time.time() - self.start_time >= float(delay):
                        self.delay_state = DState.PLAY

                    # Play zero data to prevent underrun
                    data = zero_data

                elif self.delay_state == DState.PLAY:

                    data = wf.readframes(NUM_FRAMES)

                    #data = track_data[track_i:track_i+NUM_FRAMES]
                    #data = zero_data
                    #track_i = track_i + NUM_FRAMES
                    #track_i = len(track_data)

                    if len(data) == 0: #track_i >= len(track_data):
                        is_repeat = self.tree.set(self.row_id, 'repeat') == 'x'

                        if is_repeat:
                            #track_i = 0
                            wf.rewind()
                            self.delay_state = DState.DELAY
                            self.start_time = time.time()
                        else:
                            self.state = State.CLOSE

                def scale_frame(frame):

                    libwave.scale_frame(frame,
                            wfp.sampwidth, wfp.nchannels,
                            scaled_frame, c_float(self.volume))

                    if self.ramp_state == RState.RAMP_UP:

                        self.volume = self.volume + volume_per_frame

                        if self.volume > 1.0:
                            self.volume = 1.0

                    if self.ramp_state == RState.RAMP_DOWN:

                        self.volume = self.volume - volume_per_frame

                        if self.volume < 0.0:
                            self.volume = 0.0

                    return scaled_frame.raw

                scaled_data = b''.join(scale_frame(frame)
                        for frame in chunk(data, frame_size))

                #scaled_data = zero_data
                stream.write(scaled_data)

            elif self.state == State.CLOSE:

                stream.stop_stream()
                stream.close()
                wf.close()
                print('done playing', path)

                break


        # Check if there are other players with the same track
        same_players = [player for player in self.audio.players
                        if player.row_id == self.row_id]
        if len(same_players) <= 1:
            self.tree.item(self.row_id, tags=())

        # Remove self from list of players
        self.audio.players.remove(self)
