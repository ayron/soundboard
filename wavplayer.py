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


class WavPlayer(threading.Thread):

    def __init__(self, audio, tree, row_id):

        super().__init__()
        self.tree = tree
        self.row_id = row_id
        self.p = audio.p
        self.audio = audio
        self.stop = False

    def run(self):

        path = self.tree.set(self.row_id, 'path')
        wf = wave.open(path, 'rb')
        print('playing', path)

        stream = self.p.open(
            format = self.p.get_format_from_width(wf.getsampwidth()),
            channels = wf.getnchannels(),
            rate = wf.getframerate(),
            output = True)

        while not self.stop:

            data = wf.readframes(NUM_FRAMES)

            if len(data) == 0:

                repeat = self.tree.set(self.row_id, 'repeat')

                if repeat == 'x':
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
        print('done playing', path)

        # Check if there are other players with the same track
        same_players = [player for player in self.audio.players
                        if player.row_id == self.row_id]
        if len(same_players) <= 1:
            self.tree.item(self.row_id, tags=())

        # Remove self from list of players
        self.audio.players.remove(self)

