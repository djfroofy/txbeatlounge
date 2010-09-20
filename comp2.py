#!/usr/bin/env python

import fluidsynth

from twisted.internet.task import LoopingCall
from twisted.internet import reactor

from common import Enunciator, PatternGenerator

import constants


e = Enunciator(sf2path='sf2/Ob-3.sf2')
e2 = Enunciator(sf2path='sf2/english_organ.sf2') # channel=1 (less staccato)
e3 = Enunciator(sf2path='sf2/hs_magic_techno_drums.sf2') # channel=2

p = PatternGenerator(e)
p2 = PatternGenerator(e2, noteweights=[('B', 8), ('F', 4), ('A', 8), ('D', 12), ('C', 10), ('E', 10), ('G', 10)])
p3 = PatternGenerator(e3, noteweights=constants.all_equal())

pattern = p.get_generator()
pattern2 = p2.get_generator()
pattern3 = p3.get_generator()


def conduct_half():
    pattern.next()
    pattern2.next()
    pattern3.next()

def conduct():
    pattern.next()
    pattern2.next()
    pattern3.next()

def conduct_long():
    pattern.next()
    pattern2.next()
    pattern3.next()

if __name__ == '__main__':
    lc16th = LoopingCall(conduct_half)
    lc = LoopingCall(conduct)
    lc2 = LoopingCall(conduct_long)

    reactor.callWhenRunning(lc16th.start, 0.125, True)
    reactor.callWhenRunning(lc.start, 0.25, True)
    reactor.callWhenRunning(lc2.start, 2.0, True)

    reactor.run()


