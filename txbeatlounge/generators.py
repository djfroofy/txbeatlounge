import random
import logging
from copy import copy

logging.basicConfig(level=logging.DEBUG)

from txbeatlounge import constants
from txbeatlounge.utils import windex
from txbeatlounge.internet import reactor


def rising_gen(gen):
    incr = 128/gen.num
    while True:
        for i in range(gen.num):
            if not any([divmod(i, o)[1] for o in gen.ones]):
                gen.e.playchord(gen.all_midi_notes, 127)

            gen.e.playnote(gen.choose_one(), incr*i)
            yield


def kick_gen(gen):
    while True:
        for i in range(gen.num):
            if not all([divmod(i, o)[1] for o in gen.ones]):
                gen.e.playnote(gen.choose_one(), gen.get_volume(10))

            else:
                if random.random() < .5:
                    gen.e.playnote(gen.choose_one(), gen.get_volume(-10))

            yield

def pattern1_gen(self):
    while True:
        for i in range(self.num):
            note = random.choice(self.notes)
            notes = getattr(constants, note)
            if not any([divmod(i, o)[1] for o in self.ones]):
                self.e.playchord(self.all_midi_notes, self.get_volume()-10)

            else:
                self.e.stopchord(self.all_midi_notes[12:])
                self.e.playchord(notes[4:6], self.get_volume())

                for n in range(3):
                    self.e.playnote(self.get_random_note(), self.get_volume()-5)

            yield


class OscFluidGenerator(object):
    '''All of the FooGenerator classes below should be deprecated in favor of this abstraction

    accepts osc objects and musical parameters as kwargs and provides a unified interface for gen funcs
    first arg is an instrument that will presumably play notes and chords'''

    def __init__(self, instrument, generator, beats=7, ones=[0,2,4], volume=50, humanize=10, osc=None,
            notes=['C', 'E', 'G', 'A'],
            chords=[('C', 'E', 'G'), ('A', 'C', 'E')],
            noteweights=[('C', 20), ('E', 15), ('G', 17), ('A', 12)],
            midi_noteweights=[(45,2),(48,5),(52,1),(53,3),(55,4),(60,5),(64,1),(65,2),(67,3),(72,2),(79,1),],
            midi_notes=[33,36,40,41,43,48,52,53,55,60,64,65,67,72,76,77,79,84],
            **kw):


        self.e = instrument
        self.beats = beats
        self.ones = ones
        self.gen = generator
        self.volume = volume
        self.humanize = humanize
        self.osc = osc
        self.notes = notes
        self.chords = chords
        self.midi_noteweights = midi_noteweights

    def __str__(self):
        return '%s, %s, %s, %s' % (self.e, self.number, self.ones, self.gen)

    def __call__(self):
        return iter(self)

    def __iter__(self):
        return self.gen(self)

    def get_volume(self, offset=0):
        guess = random.randrange(self.volume-self.humanize, self.volume + self.humanize)
        return max([0, min([127, guess+offset])])





class BaseGenerator(object):

    def __init__(self, instrument, number=128, ones=(128, 64, 32, 16, 8, 4),
                 gen=None, volume=50, humanize=10, wiimote=None, **kw):
        self.e = instrument
        self.num = number
        self.ones = ones
        self.gen = gen or kick_gen
        self.volume = volume
        self.humanize = humanize # between 0 and 30
        self.wiimote = wiimote

    def __str__(self):
        return '%s, %s, %s, %s' % (self.e, self.number, self.ones, self.gen)

    def __call__(self):
        return iter(self)

    def __iter__(self):
        return self.gen(self)

    def get_volume(self, offset=0):
        guess = random.randrange(self.volume-self.humanize, self.volume + self.humanize)
        return max([0, min([127, guess+offset])])

    @property
    def all_midi_notes(self):
        notes = []
        for n in self.notes:
            notes.extend(getattr(constants, n))
        return sorted(notes)

    @property
    def notes(self):
        return NotImplementedError('subclasses must provide, self.notes, a list of A/B/C/Df')


class PatternGenerator(BaseGenerator):

    def __init__(self, instrument, **kwargs):
        kwargs['gen'] = kwargs.get('gen', pattern1_gen)
        super(PatternGenerator, self).__init__(instrument, **kwargs)
        self.noteweights = kwargs.get('noteweights') or [('C', 20), ('E', 15), ('G', 17), ('A', 12)]

    @property
    def notes_weighted(self):
        return ''.join([i[0]*i[1] for i in self.noteweights])

    @property
    def notes(self):
        return [i[0] for i in self.noteweights]

    def get_random_note(self):
        note = random.choice(getattr(constants, windex(self.noteweights)))
        #logging.debug('random note: %s' % midi_to_letter(note))
        return note


def chords1_gen(self):
    chord_gen = self.chord_gen()
    while True:
        for i in range(self.num):
            for i in range(len(self.chords)):
                self.e.stopall()
                self.e.playchord(self.chord_to_midi(chord_gen.next()), self.get_volume())
                yield

def random_chords_gen(self):
    chord_gen = self.chord_gen()
    while True:
        for i in range(self.num):
            for i in range(len(self.chords)):
                self.e.stopall()
                self.e.playchord(self.chord_to_midi(chord_gen.next()), self.get_volume())
                yield


class ProgressionGenerator(BaseGenerator):

    def __init__(self, *args, **kwargs):
        super(ProgressionGenerator, self).__init__(*args, **kwargs)
        self.chords = kwargs.get('chords') or [('C', 'E', 'G'), ('A', 'C', 'E')]
        self.gen = kwargs.get('gen') or random_chords_gen

    @property
    def notes(self):
        notes = []
        for c in self.chords:
            notes.extend(list(c))
        return set(notes)

    def chord_to_midi(self, chord):
        notes = []
        for n in chord:
            notes.extend(getattr(constants, n))
        return notes

    def random_note_from_chord(self, chord):
        return random.choice(self.chord_to_midi(chord))

    def chord_gen(self):
        while True:
            c = copy(self.chords)
            c.reverse()
            while c:
                yield c.pop()

    def random_chord_gen(self):
        while True:
            yield random.choice(self.chords)



class BeatGenerator(BaseGenerator):

    def __init__(self, instrument, **kwargs):
        super(BeatGenerator, self).__init__(instrument, **kwargs)
        self.midi_noteweights = kwargs.get('midi_noteweights') or [(47, 10),(48, 10),(49, 10),(50, 10),(51, 10),(52, 10)]
        logging.debug('instantiated BeatGenerator with: %s, %s, %s, %s' % (self.e, self.num, self.ones, self.midi_noteweights))

    def choose_one(self):
        return windex(self.midi_noteweights)

    @property
    def all_midi_notes(self):
        return sorted([i[0] for i in self.midi_noteweights])



def bass_gen(self):
    note_gen = self.random_note_gen()
    while True:
        for i in range(self.num):
            if random.random() < .8:
                self.e.stopall()
                if random.random() < .9:
                    self.e.playnote(note_gen.next(), self.get_volume())
            yield


class BassLineGenerator(BeatGenerator):

    def __init__(self, instrument, **kwargs):
        kwargs['gen'] = kwargs.get('gen', bass_gen)
        super(BassLineGenerator, self).__init__(instrument, **kwargs)
        self.midi_noteweights = kwargs.get('midi_noteweights') or [(36,10),(33,8),(40, 8),(31, 5),(43,5),(47,2),(48,5),(50,2),(53,1),(55,3),(60,4)]

    def note_gen(self):
        while True:
            c = copy(self.midi_noteweights)
            while c:
                yield c.pop()[0]

    def random_note_gen(self):
        while True:
            yield windex(self.midi_noteweights)

    def get_random_note(self):
        return windex(self.midi_noteweights)

    @property
    def notes(self):
        notes = []
        for x,y in self.midi_noteweights:
            for n in constants.NOTES:
                if x in getattr(constants, n):
                    notes.append(n)

        return notes


class KickGenerator(BaseGenerator):

    pass


from txosc import osc
from txosc import dispatch
from txosc import async




def wii_gen(self):
    while True:
        for i in range(self.num):
            print self.pitch, self.roll, self.yaw
            r = random.random()
            if r < self.yaw:
                self.e.playnote(random.randrange(0, int(self.pitch*127) or 1), random.randrange(0, int(self.roll*127)))

            if r > self.pitch:
                self.e.stopnote(random.randrange(0,127))

            yield



class WiiMixin(object):
    '''receives messages on localhost:port from the wiimote

    sets the parameters as values on the instance for use in writing generator functions'''

    def wii_mix(self, port=8005):
        self.port = port
        self.receiver = dispatch.Receiver()
        self._server_port = reactor.listenUDP(self.port, async.DatagramServerProtocol(self.receiver))
        print("Listening on osc.udp://localhost:%s" % (self.port))

        self.receiver.addCallback("/wii/1/accel/pry/0", self.wii_set_pitch)
        self.receiver.addCallback("/wii/1/accel/pry/1", self.wii_set_roll)
        self.receiver.addCallback("/wii/1/accel/pry/2", self.wii_set_yaw)
        self.receiver.addCallback("/wii/1/accel/pry/3", self.wii_set_accel)
        self.pitch = 0
        self.roll = 0
        self.yaw = 0
        self.accel = 0

        self.receiver.fallback = self.wii_fallback

    def wii_set_pitch(self, message, address):
        self.pitch = message.arguments[0].value

    def wii_set_roll(self, message, address):
        self.roll = message.arguments[0].value

    def wii_set_yaw(self, message, address):
        self.yaw = message.arguments[0].value

    def wii_set_accel(self, message, address):
        self.accel = message.arguments[0].value

    def wii_fallback(self, message, address):
        print message


class WiiGenerator(BaseGenerator, WiiMixin):

    def __init__(self, *args, **kwargs):
        super(WiiGenerator, self).__init__(*args, **kwargs)
        self.get = kwargs.get('gen') or wii_gen
        self.wii_mix()


def wii_progen(self):
    chord_gen = self.chord_gen()
    while True:
        for i in range(256):
            if i in range(256)[::16]:
                chord = chord_gen.next()
            r = random.random()
            print self.pitch, self.roll, self.yaw

            if self.pitch > r:
                self.e.stopall()
                self.e.playchord(self.chord_to_midi(chord)[0:int(self.roll*20)], self.get_volume(int(self.pitch*127)))

            self.e.playnote(int(round(len(self.all_midi_notes)*self.roll)), self.get_volume(int(self.pitch*127)))

            yield


class WiiProgressionGenerator(ProgressionGenerator, WiiMixin):

    def __init__(self, *args, **kwargs):
        super(WiiProgressionGenerator, self).__init__(*args, **kwargs)
        self.gen = kwargs.get('gen') or wii_progen
        print self.gen
        self.wii_mix()






