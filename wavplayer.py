import pyaudio
import wave
import sys
import struct
import threading

NUM_FRAMES = 1024

class Audio:

    def __init__(self):

        print('Starting portaudio')
        self.p = pyaudio.PyAudio()
        self.players = []

    def __del__(self):

        print('Terminating portaudio')
        self.p.terminate()

    def play(self, widget):

        if widget.bg.get():

            # First stop all other background tracks
            for player in self.players:
                if player.widget.bg.get():
                    player.stop = True

        wp = WavPlayer(self, widget)
        wp.start()
        self.players.append(wp)

    def stop_all(self):

        print('Stopping all')
        for player in self.players:
            player.stop = True


class WavPlayer(threading.Thread):

    def __init__(self, audio, widget):

        super().__init__()
        self.widget = widget
        self.p = audio.p
        self.audio = audio
        self.stop = False

    def run(self):

        wf = wave.open(self.widget.file.get(), 'rb')
        print('playing', self.widget.file.get())

        stream = self.p.open(
            format = self.p.get_format_from_width(wf.getsampwidth()),
            channels = wf.getnchannels(),
            rate = wf.getframerate(),
            output = True)

        while not self.stop:

            data = wf.readframes(NUM_FRAMES)

            if len(data) == 0:
                if self.widget.repeat.get():
                    wf.rewind()
                    continue
                else:
                    break

            # Lower volume
            #fmt = 'h'*(len(data)//2)
            #values = struct.unpack(fmt, data)
            #values_lower = (int(x*1.0) for x in values)
            #data = struct.pack(fmt, *values_lower)

            stream.write(data)
            #data = wf.readframes(CHUNK)

        stream.stop_stream()
        stream.close()
        print('done playing', self.widget.file.get())
        self.widget.no_highlight()

        # Remove self from list of players
        self.audio.players.remove(self)

