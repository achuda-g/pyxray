"""
Parsers from JOEL.
"""

# Standard library modules.
import logging
logger = logging.getLogger(__name__)

# Third party modules.

# Local modules.
from pyxray.parser.parser import _Parser
from pyxray.descriptor import Reference, Element, Transition, AtomicSubshell
from pyxray.property import TransitionEnergy, TransitionProbability

# Globals and constants variables.

JOEL = Reference('JEOL'
                 )

K = AtomicSubshell(1, 0, 1)
L1 = AtomicSubshell(2, 0, 1)
L2 = AtomicSubshell(2, 1, 1)
L3 = AtomicSubshell(2, 1, 3)
M1 = AtomicSubshell(3, 0, 1)
M2 = AtomicSubshell(3, 1, 1)
M3 = AtomicSubshell(3, 1, 3)
M4 = AtomicSubshell(3, 2, 3)
M5 = AtomicSubshell(3, 2, 5)
N1 = AtomicSubshell(4, 0, 1)
N2 = AtomicSubshell(4, 1, 1)
N3 = AtomicSubshell(4, 1, 3)
N4 = AtomicSubshell(4, 2, 3)
N5 = AtomicSubshell(4, 2, 5)
N6 = AtomicSubshell(4, 3, 5)
N7 = AtomicSubshell(4, 3, 7)
O1 = AtomicSubshell(5, 0, 1)
O2 = AtomicSubshell(5, 1, 1)
O3 = AtomicSubshell(5, 1, 3)
O4 = AtomicSubshell(5, 2, 3)
O5 = AtomicSubshell(5, 2, 5)
O6 = AtomicSubshell(5, 3, 5)
O7 = AtomicSubshell(5, 3, 7)
O8 = AtomicSubshell(5, 4, 7)
O9 = AtomicSubshell(5, 4, 9)

_TRANSITION_LOOKUP = {
'KA': (L3, K), ''KA1': (L3, K), 'KA2': (L2, K),

'KB1': (M3, K), 'KB2_1': (N3, K), 'KB2_2': (N2, K),
'KB3': (M2, K), 'KB4_1': (N5, K), 'KB4_2': (N4, K), 'KB4x': (N4, K),
'KB5_1': (M5, K), 'KB5_2': (M4, K),

'LA1': (M5, L3), 'LA2': (M4, L3),

'LN': (M1, L2), 'LL': (M1, L3), 'LS': (M3, L3), 'LT': (M2, L3),
'LV': (N6, L2),

'LB1': (M4, L2), 'LB2': (N5, L3), 'LB3': (M3, L1), 'LB4': (M2, L1),
'LB6': (N1, L3), 'LB7': (O1, L3), 'LB9': (M5, L1), 'LB10': (M4, L1),
'LB15': (N4, L3), 'LB17': (M3, L2),

'LG1': (N4, L2), 'LG2': (N2, L1), 'LG3': (N3, L1), 'LG4': (O3, L1),
'LG4_p': (O2, L1), 'LG5': (N1, L2), 'LG6': (O4, L2), 'LG8': (O1, L2),
'LG8_p': (N6, L2),

'MB': (N6, M4),

'MG': (N5, M3),

'MA1': (N7, M5), 'MA2': (N6, M5),

}

def extract():
    infile = open('../data/lambda.asc', 'r')
    notread = set()
    try:
        data = []
        for line in infile:
            line = line.strip()
            if not line: continue

            z = int(line[0:2])

            siegbahn = line[10:17].strip()
            if siegbahn.startswith('A'):  # skip absorption edges
                continue
            if siegbahn.startswith('S'):  # skip satellite lines
                continue
            if siegbahn not in _TRANSITION_LOOKUP:  # check for equivalence
                notread.add(siegbahn)
                continue
            subshells = list(_TRANSITION_LOOKUP[siegbahn])

            probability = line[20:23].strip()
            if not probability:  # skip transition with no probability
                continue

            probability = float(probability) / 100.0
            if probability > 1:  # skip sum of transitions
                continue

            wavelength = float(line[26:35])
            energy = (4.13566733e-15 * 299792458) / (wavelength * 1e-10)
            data.append((z, subshells, probability, energy))

    finally:
        infile.close()

    return data

class JEOLTransitionEnergyParser(_Parser):

    def __iter__(self):
        transition_energy = extract()
        length = len(transition_energy)
        for z, subshells, probability, eV in enumerate(transition_energy, 1):
            if eV is None:
                continue
            transition = Transition(subshells)
            element = Element(z)
            prop = TransitionEnergy(JOEL, element, transition, eV)
            logger.debug('Parsed: {0}'.format(prop))
            self.update(int((z - 1) / length * 100.0))
            yield prop

class JEOLTransitionProbabilityParser(_Parser):

    def __iter__(self):
        transition_probability = extract()
        length = len(transition_probability)
        for z, subshells, probability, eV in enumerate(transition_probability, 1):
            if probability is None:
                continue
            transition = Transition(subshells)
            element = Element(z)
            prop = TransitionProbability(JOEL, element, transition, probability)
            logger.debug('Parsed: {0}'.format(prop))
            self.update(int((z - 1) / length * 100.0))
            yield prop
