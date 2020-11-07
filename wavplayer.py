import pyaudio
import wave
import sys
import struct
import threading

CHUNK = 1024

class Audio:

    def __init__(self):

        print('Starting portaudio')
        self.p = pyaudio.PyAudio()
        self.players = []

    def __del__(self):

        print('Terminating portaudio')
        self.p.terminate()

    def play(self, wav_file):

        wp = WavPlayer(self, wav_file)
        wp.start()
        self.players.append(wp)

    def stop_all(self):

        for player in self.players:
            player.stop = True


class WavPlayer(threading.Thread):

    def __init__(self, audio, wav_file):

        super().__init__()
        self.wav_file = wav_file
        self.p = audio.p
        self.audio = audio
        self.stop = False

    def run(self):

        wf = wave.open(self.wav_file, 'rb')
        print('playing', self.wav_file)

        stream = self.p.open(
            format = self.p.get_format_from_width(wf.getsampwidth()),
            channels = wf.getnchannels(),
            rate = wf.getframerate(),
            output = True)

        data = wf.readframes(CHUNK)

        while len(data) != 0 and not self.stop:

            # Lower volume
            fmt = 'h'*(len(data)//2)
            values = struct.unpack(fmt, data)
            values_lower = (int(x*1.0) for x in values)
            data = struct.pack(fmt, *values_lower)

            stream.write(data)
            data = wf.readframes(CHUNK)

        stream.stop_stream()
        stream.close()
        print('done playing', self.wav_file)

        # Remove self from list of players
        self.audio.players.remove(self)

