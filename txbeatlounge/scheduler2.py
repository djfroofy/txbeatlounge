from collections import namedtuple
from functools import wraps

from zope.interface import implements

from twisted.python import log
from twisted.python.components import proxyForInterface
from twisted.internet.interfaces import IReactorTime
from twisted.internet.base import ReactorBase
from twisted.internet.selectreactor import SelectReactor
from twisted.internet.defer import Deferred, succeed
from twisted.internet.task import LoopingCall

from fluidsynth import Synth


_BeatBase = namedtuple('_BeatBase', 'measure quarter eighth sixteenth remainder')

class Beat(_BeatBase):

    def __repr__(self):
        return ('Beat(measure=%s, quarter=%s, eighth=%s, sixteenth=%s, '
                'remainder=%s)' % (self.measure, self.quarter, self.eighth,
                self.sixteenth, self.remainder))

class Meter(object):

    def __init__(self, length=4, division=4, number=1):
        self.length = length
        self.division = division
        self.number = number
        self._quarters_per_measure = self.length * self.number / (self.division / 4.)
        self._hash = hash((self.length, self.division, self.number))
        self.ticks_per_measure = int(24 * self.length * 4. / self.division * self.number)

    def beat(self, ticks):
        measure, ticks = divmod(ticks, self.ticks_per_measure)
        if not ticks:
            return Beat(measure, 0, 0, 0, 0)
        quarter, ticks = divmod(ticks, self.ticks_per_measure / self._quarters_per_measure) 
        if not ticks:
            return Beat(measure, int(quarter), 0, 0, 0)
        eighth, ticks = divmod(ticks, self.ticks_per_measure / (self._quarters_per_measure * 2)) 
        if not ticks:
            return Beat(measure, int(quarter), int(eighth), 0, 0)
        sixteenth, ticks = divmod(ticks, self.ticks_per_measure / (self._quarters_per_measure * 4))
        return Beat(measure, int(quarter), int(eighth), int(sixteenth), int(ticks))

    def ticks(self, ticks):
        return ticks % self.ticks_per_measure

    def measure(self, ticks):
        return divmod(ticks, self.ticks_per_measure)[0]

    def __repr__(self):
        return 'Meter(length=%s, division=%s, number=%s)' % (self.length, self.division, self.number)

    def __hash__(self):
        return self._hash


standardMeter = Meter(4,4)

class SynthControllerMixin(object):
    synthAudioDevice = 'coreaudio'
    synth = Synth(0.2)


class BeatClock(SelectReactor, SynthControllerMixin):

    def __init__(self, tempo=130, meters=(), reactor=None):
        self.tempo = tempo
        self.ticks = 0
        #self.setTempo(tempo)
        self._tick_interval = (60. / tempo) * (1./24)
        self.meters = meters
        self._meter_schedule = {}
        if not self.meters:
            self.meters = [Meter(4,4,1)]
        if not reactor:
            from twisted.internet import reactor
        self.reactor = reactor
        SelectReactor.__init__(self)

    def setTempo(self, tempo):
        self._tick_interval = (60. / tempo) * (1./24)
        if hasattr(self, 'task'):
            self.task.stop()
            self.task.start(self._tick_interval, True)
        self.tempo = tempo
        
    def run(self):
        self.synth.start(self.synthAudioDevice)
        self.startTicking()
        if not self.reactor.running:
            self.running = True
            self.reactor.run()

    def startTicking(self):
        self.task = LoopingCall(self.tick)
        self.on_stop = self.task.start(self._tick_interval, True)

    def tick(self):
        self.ticks += 1
        self.runUntilCurrent()

    def seconds(self):
        return self.ticks

    def schedule(self, _f, *args, **kwargs):
        event = ScheduledEvent(self, _f, *args, **kwargs)
        return event

    def callWhenRunning(self, *a, **kw):
        return self.reactor.callWhenRunning(*a, **kw)

    def nudge(self, pause=0.1):
        if not hasattr(self, 'task'):
            raise ValueError("Cannot nudge a clock that hasn't started")
        self.task.stop()
        self.reactor.callLater(pause, self.task.start, self._tick_interval, True)


def measuresToTicks(measures):
    return measures * standardMeter.ticks_per_measure


class ScheduledEvent(object):
   
    meter = None
 
    def __init__(self, clock, _f, *args, **kwargs):
        self.clock = clock
        self.call = (_f, args, kwargs)

    def startLater(self, measures=1, frequency=0.25, ticks=None, meter=None):
        if measures < 0:
            raise ValueError("measures must be greater than zero")
        meter = meter or self.meter or self.clock.meters[0]
        if ticks is None:
            # XXX
            # I'm a little torn between whether this should be absolute to a 
            # a standard meter (as current), or relative to any given meter.
            # The advantage of the former is that 0.25 always means quarter note
            # etc.
            ticks = frequency * standardMeter.ticks_per_measure
        def _start_later():
            ticksLater = self._ticks(measures, meter)
            self.clock.callLater(ticksLater, self.start, ticks, True)
        self.clock.callWhenRunning(_start_later)
        return self

    def start(self, ticks=None, now=True):
        def _start():
            self.task = LoopingCall(self.call[0], *self.call[1], **self.call[2])
            self.task.clock = self.clock
            self.deferred = self.task.start(ticks, now)
        self.clock.callWhenRunning(_start)
        return self

    def stopLater(self, measures=1, meter=None, ticksLater=None):
        meter = meter or self.meter or self.clock.meters[0]
        def _scheduleStop():
            ticks = ticksLater
            if ticks is None:
                ticks = self._ticks(measures, meter)
            def _stop():
                if hasattr(self, 'task'):
                    self.task.stop()
                else:
                    log.msg('Tried to stop an event that has not yet started')
            self.clock.callLater(ticks, _stop)
        self.clock.callWhenRunning(_scheduleStop)
        return self


    def bindMeter(self, meter):
        self.meter = meter
        return self

    def _ticks(self, measures, meter):
        current_measure = meter.measure(self.clock.ticks)
        tick = int(current_measure * meter.ticks_per_measure + measures * meter.ticks_per_measure)
        ticks = tick - self.clock.seconds()
        if ticks < 0:
            ticks += meter.ticks_per_measure
        return ticks


BPM = 130
clock = BeatClock(BPM)

