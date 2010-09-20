#!/usr/bin/env python
import time
import fluidsynth
import logging

logger = logging.getLogger(__name__)

from twisted.internet.task import LoopingCall
from twisted.internet import reactor

import constants

from common import Enunciator


e = Enunciator(sf2path='sf2/Ob-3.sf2')





def f():
  while True:

    for i in range(128):

        if not divmod(i, 64)[1]:
            e.on_octaves(72, 15)
            e.on_octaves(76, 15)




        if not divmod(i, 32)[1]:
            e.on_octaves(60)
            e.on_octaves(64, 20)





	if not divmod(i, 2)[1]:
            e.on_octaves(60,35)

	    e.fs.noteon(0, 48, 30)
	    e.fs.noteoff(0, 60)




            if not divmod(i, 4)[1]:
                e.on_octaves(72)


                e.fs.noteon(0, 64, 20)


            if not divmod(i, 8)[1]:
                e.fs.noteon(0, 67, 40)

            if not divmod(i, 6)[1]:
                e.fs.noteon(0, 69, 25)

            if not divmod(i, 12)[1]:
                e.fs.noteon(0, 36, 30)

            if not divmod(i, 16)[1]:
                e.fs.noteon(0, 43, 25)
            else:
                e.fs.noteoff(0,43)




	else:
            e.off_octaves(0)
            e.off_octaves(64)

	    e.fs.noteon(0, 60, 30)
            
            e.fs.noteoff(0, 64)

            if divmod(i, 3)[1]:
                for n in range(127):
                    e.fs.noteoff(0, n)

                for riff in [0, 4, 7, 12, 24]:
                    e.fs.noteon(0, 48+riff, 45-riff)

            if not divmod(i, 9)[1]:
                e.on_octaves(84, 15)

                if not divmod(i, 18)[1]:
                    e.off_octaves(0)
            else:
                e.off_octaves(0)

        yield
	#time.sleep(.25)

def g():
    while True:
        for i in range(128):
            if divmod(i,2)[1]:
                e.fs.noteon(0, 72, 25)
            else:
                e.fs.noteoff(0, 72)

            yield


def h():
    while True:
        for i in range(16):

            if i < 8:
                note = 60

            else:
                note = 57

            if not divmod(i, 4)[1]:
                if not divmod(i, 8)[1]:
                    e.fs.noteon(0, note, 35)
            else:
                e.fs.noteoff(0, note)

            yield


def i():
    while True:
        for n in range(128):
            if n in range(0, 32):
                notes = constants.A
                for o in notes:
                    e.fs.noteon(0, o, n)

                for o in constants.E+constants.C:
                    e.fs.noteoff(0, o)

                yield

            if n in range(32,64):
                note = constants.C

                yield

            if n in range(64,96):
                note = constants.E

                yield

            if n in range(94,128):
                note = constants.C

                yield
loop1 = f()
loop2 = g()
loop3 = h()
loop4 = i()

def conduct():
    loop1.next()
    loop2.next()
    loop3.next()
    loop4.next()


if __name__ == '__main__':
    lc = LoopingCall(conduct)
    reactor.callWhenRunning(lc.start, 0.25, True)
    reactor.run()



