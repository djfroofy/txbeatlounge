NOTES = ['C', 'Df', 'D', 'Ef', 'E', 'F', 'Gf', 'G', 'Af', 'A', 'Bf', 'B']

# Midi
C=[0, 12, 24, 36, 48, 60, 72, 84, 96, 108, 120]
Df=[1, 13, 25, 37, 49, 61, 73, 85, 97, 109, 121]
D=[2, 14, 26, 38, 50, 62, 74, 86, 98, 110, 122]
Ef=[3, 15, 27, 39, 51, 63, 75, 87, 99, 111, 123]
E=[4, 16, 28, 40, 52, 64, 76, 88, 100, 112, 124]
F=[5, 17, 29, 41, 53, 65, 77, 89, 101, 113, 125]
Gf=[6, 18, 30, 42, 54, 66, 78, 90, 102, 114, 126]
G=[7, 19, 31, 43, 55, 67, 79, 91, 103, 115, 127]
Af=[8, 20, 32, 44, 56, 68, 80, 92, 104, 116]
A=[9, 21, 33, 45, 57, 69, 81, 93, 105, 117]
Bf=[10, 22, 34, 46, 58, 70, 82, 94, 106, 118]
B=[11, 23, 35, 47, 59, 71, 83, 95, 107, 119]
MIDI_NOTES = [C, Df, D, Ef, E, F, Gf, G, Af, A, Bf, B]


from decimal import Decimal
twelve_tone_equal_440 = [440*(2**(1/Decimal(12)))**i for i in range(-60,68)]

just_3rd = Decimal(5)/Decimal(4)
just_5th = Decimal(3)/Decimal(2)
octave = 2

def well_tempered_major_pure(freq):
    return [freq*i for i in range(1,8) if i not in [6,7]]

def just_major(freq, offset=0):
    pass


def all_equal():
    li = []
    for n in NOTES:
        li.append((n, 1))

    return li


# scales

C_bhairav = [('C', 40),('Df', 4),('E', 12),('F', 12),('G', 32),('Af', 4),('B', 4)]
C_aeolian = [('C', 30),('D', 8),('Ef', 12),('F', 15),('G', 20),('Af', 4),('Bf', 10)]


###############
# chords
###############


# major

cmaj = ('C', 'E', 'G')
gmaj = ('G', 'B', 'D')



# minor

amin = ('A', 'C', 'E')
dmin = ('D', 'F', 'A')



