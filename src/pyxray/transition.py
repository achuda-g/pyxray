#!/usr/bin/env python
"""
================================================================================
:mod:`transition` -- Atomic transition
================================================================================

.. module:: transition
   :synopsis: Atomic transition

.. inheritance-diagram:: pyxray.transition

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
from abc import ABCMeta, abstractmethod
from operator import methodcaller, attrgetter
import string
from itertools import izip_longest

# Third party modules.
from pyparsing import Word, Group, Optional, OneOrMore, QuotedString, Literal

# Local modules.
import element_properties as ep
from subshell import Subshell
import transition_data

# Globals and constants variables.
_ZGETTER = attrgetter('z')

_level = Optional(QuotedString("(", endQuoteChar=")") | Word(string.digits))
_shell = Group(Word(string.ascii_uppercase) + _level)
_iupac_pattern = _shell + Literal('-') + OneOrMore(_shell)

def iupac2latex(iupac):
    """
    Formats IUPAC symbol for LaTeX.
    
    :arg iupac: string of an IUPAC symbol, transition or transitionset 
    """
    if not isinstance(iupac, basestring):
        iupac = getattr(iupac, 'iupac')

    s = ''
    for parts in _iupac_pattern.parseString(iupac):
        if len(parts) == 2:
            s += '%s$_{%s}$' % tuple(parts)
        else:
            s += ''.join(parts)

    return s

def siegbahn2latex(siegbahn):
    """
    Formats Siegbahn symbol for LaTeX.
    
    :arg siegbahn: string of a Siegbahn symbol, transition or transitionset 
    """
    if not isinstance(siegbahn, basestring):
        siegbahn = getattr(siegbahn, 'siegbahn')

    s = ''
    for c in siegbahn:
        s += "$_{%s}$" % c if c.isdigit() else c

    s = s.replace(u'\u03B1', r'$\alpha$')
    s = s.replace(u'\u03B2', r'$\beta$')
    s = s.replace(u'\u03B3', r'$\gamma$')
    s = s.replace(u'\u03B6', r'$\zeta$')
    s = s.replace(u'\u03B7', r'$\eta$')
    s = s.replace(u'\u03BD', r'$\nu')
    s = s.replace(u'\u2113', r'$l$')

    s = s.replace('$$', '')

    return str(s)

def _siegbahn_ascii_to_unicode(siegbahn):
    """
    Replaces some ascii characters in Siegbahn with unicode characters.
    """
    siegbahn = siegbahn.replace('a', u'\u03B1')
    siegbahn = siegbahn.replace('b', u'\u03B2')
    siegbahn = siegbahn.replace('g', u'\u03B3')
    siegbahn = siegbahn.replace('z', u'\u03B6')
    siegbahn = siegbahn.replace('n', u'\u03B7')
    siegbahn = siegbahn.replace('v', u'\u03BD')
    siegbahn = siegbahn.replace('l', u'\u2113')
    return siegbahn

def _siegbahn_unicode_to_ascii(siegbahn):
    """
    Replaces unicode characters in Siegbahn with ascii characters.
    """
    siegbahn = siegbahn.replace(u'\u03B1', 'a')
    siegbahn = siegbahn.replace(u'\u03B2', 'b')
    siegbahn = siegbahn.replace(u'\u03B3', 'g')
    siegbahn = siegbahn.replace(u'\u03B6', 'z')
    siegbahn = siegbahn.replace(u'\u03B7', 'n')
    siegbahn = siegbahn.replace(u'\u03BD', 'v')
    siegbahn = siegbahn.replace(u'\u2113', 'l')
    return siegbahn

"""
Subshells (source -> destination) of all transitions.
"""
_SUBSHELLS = \
    [(4, 1) , (3, 1) , (7, 1) , (12, 1), (6, 1) , (14, 1) , (9, 1) ,
     (11, 4), (12, 4), (18, 4), (19, 4), (24, 4), (9, 4)  , (8, 4) ,
     (13, 4), (14, 4), (20, 4), (10, 4), (17, 4), (5, 4)  , (7, 4) ,
     (6, 4) , (15, 4), (6, 3) , (9, 3) , (11, 3), (12, 3) , (14, 3),
     (18, 3), (19, 3), (25, 3), (8, 3) , (7, 3) , (13, 3) , (10, 3),
     (20, 3), (17, 3), (5, 3) , (15, 3), (5, 2) , (10, 2) , (13, 2),
     (17, 2), (20, 2), (8, 2) , (7, 2) , (6, 2) , (9, 2)  , (11, 2),
     (14, 2), (12, 2), (19, 2), (18, 2), (11, 5), (12, 5) , (8, 6) ,
     (10, 6), (13, 6), (20, 6), (8, 7) , (9, 7) , (10, 7) , (13, 7),
     (17, 7), (20, 7), (21, 7), (14, 7), (12, 8), (18, 8) , (15, 8),
     (11, 8), (19, 9), (16, 9), (15, 9), (12, 9), (15, 13), (15, 14)]

_SIEGBAHNS = \
    [u"K\u03B11", u"K\u03B12", u"K\u03B21", u"K\u03B22", u"K\u03B23",
     u"K\u03B24", u"K\u03B25", "L3N2", "L3N3", "L3O2", "L3O3", "L3P1",
     u"L\u03B11", u"L\u03B12", u"L\u03B215", u"L\u03B22", u"L\u03B25",
     u"L\u03B26", u"L\u03B27", u"L\u2113", "Ls", "Lt", "Lu", "L2M2",
     "L2M5", "L2N2", "L2N3", "L2N5", "L2O2", "L2O3", "L2P2",
     u"L\u03B21", u"L\u03B217", u"L\u03B31", u"L\u03B35", u"L\u03B36",
     u"L\u03B38", u"L\u03B7", u"L\u03BD", "L1M1", "L1N1", "L1N4",
     "L1O1", "L1O4", u"L\u03B210", u"L\u03B23", u"L\u03B24",
     u"L\u03B29", u"L\u03B32", u"L\u03B311", u"L\u03B33", u"L\u03B34",
     u"L\u03B34p", "M1N2", "M1N3", "M2M4", "M2N1", "M2N4", "M2O4",
     "M3M4", "M3M5", "M3N1", "M3N4", "M3O1", "M3O4", "M3O5",
     u"M\u03B3", "M4N3", "M4O2", u"M\u03B2", u"M\u03B62", "M5O3",
     u"M\u03B11", u"M\u03B12", u"M\u03B61", "N4N6", "N5N6"]

class _BaseTransition(object):

    __metaclass__ = ABCMeta

    def __init__(self, z, siegbahn, iupac):
        self._z = z
        self._symbol = ep.symbol(z)
        self._siegbahn = siegbahn
        self._iupac = iupac

    def __str__(self):
        return "%s %s" % (self.symbol, self.siegbahn_nogreek)

    def __unicode__(self):
        return u"%s %s" % (self.symbol, self.siegbahn)

    @abstractmethod
    def __cmp__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __hash__(self):
        raise NotImplementedError

    def __gt__(self, other):
        return NotImplemented # Revert to __cmp__

    def __lt__(self, other):
        return NotImplemented # Revert to __cmp__

    def __ge__(self, other):
        return NotImplemented # Revert to __cmp__

    def __le__(self, other):
        return NotImplemented # Revert to __cmp__

    @property
    def z(self):
        """
        Atomic number of this transition.
        """
        return self._z

    atomicnumber = z

    @property
    def symbol(self):
        """
        Symbol of the element of this transition.
        """
        return self._symbol

    @property
    def iupac(self):
        """
        IUPAC symbol of this transition.
        """
        return self._iupac

    @property
    def siegbahn(self):
        """
        Seigbahn symbol of this transition.
        """
        return self._siegbahn

    @property
    def siegbahn_nogreek(self):
        """
        Seigbahn symbol of this transition (greek characters removed).
        """
        return _siegbahn_unicode_to_ascii(self.siegbahn)

class Transition(_BaseTransition):

    def __init__(self, z, src=None, dest=None, siegbahn=None):
        """
        Creates a new transition from a source and destination subshells 
        or from its Siegbahn symbol::
        
           t = Transition(29, 4, 1)
           t = Transition(29, siegbahn='Ka1')
           
        :arg z: atomic number (from 3 to 99 inclusively)
        :arg src: source subshell index between 1 (K) and 30 (outer) or subshell object
        :arg dest: destination subshell index between 1 (K) and 30 (outer) or subshell object
        :arg siegbahn: Siegbahn symbol
        """
        if src is not None and dest is not None:
            if src < dest:
                raise ValueError, "The source subshell (%s) must be greater " + \
                        "than the destination subshell (%s)" % (src, dest)

            if hasattr(src, 'index'): src = src.index
            if hasattr(dest, 'index'): dest = dest.index

            try:
                index = _SUBSHELLS.index((src, dest))
            except ValueError:
                raise ValueError, "Unknown transition (%s -> %s)" % (src, dest)
        elif siegbahn is not None:
            siegbahn = _siegbahn_ascii_to_unicode(siegbahn)

            # Fix to be compatible with old transition, e.g. N5N6/N6N7
            if '/' in siegbahn: siegbahn = siegbahn[:siegbahn.index('/')]

            try:
                index = _SIEGBAHNS.index(siegbahn)
            except ValueError:
                raise ValueError, "Unknown transition (%s)" % siegbahn
        else:
            raise ValueError, "Specify shells or siegbahn"

        self._index = index
        src, dest = _SUBSHELLS[index]

        self._src = Subshell(z, src)
        self._dest = Subshell(z, dest)

        siegbahn = unicode(_SIEGBAHNS[index])
        iupac = '-'.join([self._dest.iupac, self._src.iupac])
        _BaseTransition.__init__(self, z, siegbahn, iupac)

        self._exists = transition_data.exists(z, (src, dest))
        self._energy_eV = transition_data.energy_eV(z, (src, dest))
        self._probability = transition_data.probability(z, (src, dest))
        try:
            self._wavelength_m = (4.13566733e-15 * 299792458) / self._energy_eV
        except ZeroDivisionError: # Energy == 0.0 if transition does not exist
            self._wavelength_m = float('inf')

    def __repr__(self):
        return '<Transition(%s %s)>' % (self.symbol, self.siegbahn_nogreek)

    def __eq__(self, other):
        return self._index == other._index and self._z == other._z

    def __ne__(self, other):
        return self._index != other._index or self._z != other._z

    def __cmp__(self, other):
        c = cmp(self._z, other._z)
        if c != 0:
            return c
        return -1 * cmp(self._index, other._index)

    def __hash__(self):
        return hash(('Transition', self._z, self._index))

    @property
    def src(self):
        """
        Source shell of this transition.
        """
        return self._src

    @property
    def dest(self):
        """
        Destination shell of this transition.
        """
        return self._dest

    @property
    def energy_eV(self):
        """
        Energy of this transition in eV.
        """
        return self._energy_eV

    @property
    def wavelength_m(self):
        """
        Wavelength of this transition in meters.
        """
        return self._wavelength_m

    @property
    def probability(self):
        """
        Probability of this transition.
        """
        return self._probability

    def exists(self):
        """
        Whether this transition exists.
        """
        return self._exists

class transitionset(frozenset, _BaseTransition):

    def __new__(cls, z, siegbahn, iupac, transitions):
        # Required
        # See http://stackoverflow.com/questions/4850370/inheriting-behaviours-for-set-and-frozenset-seem-to-differ
        return frozenset.__new__(cls, transitions)

    def __init__(self, z, siegbahn, iupac, transitions):
        """
        Creates a frozen set (immutable) of transitions.
        The atomic number must be the same for all transitions. 
        
        :arg z: atomic number of all transitions
        :arg name: name of the set (e.g. ``Ka``)
        :arg transitions: transitions in the set
        :arg name_unicode: name of the set in unicode
        """
        if not transitions:
            raise ValueError, 'A transitionset must contain at least one transition'

        # Common z
        zs = map(_ZGETTER, transitions)
        if len(set(zs)) != 1:
            raise ValueError, "All transitions in a set must have the same atomic number"

        frozenset.__init__(transitions)
        _BaseTransition.__init__(self, z, siegbahn, iupac)

        self._most_probable = \
            sorted(self, key=attrgetter('probability'), reverse=True)[0]

    def __repr__(self):
        return '<transitionset(%s: %s)>' % (str(self), ', '.join(map(str, sorted(self))))

    def __cmp__(self, other):
        c = cmp(self._z, other._z)
        if c != 0:
            return c

        indexes = sorted(map(attrgetter('_index'), self))
        other_indexes = sorted(map(attrgetter('_index'), other))
        for index, other_index in \
                izip_longest(indexes, other_indexes, fillvalue=79):
            c = cmp(index, other_index)
            if c != 0:
                return -1 * c

        return 0

    def __gt__(self, other):
        return NotImplemented # Revert to __cmp__

    def __lt__(self, other):
        return NotImplemented # Revert to __cmp__

    def __ge__(self, other):
        return NotImplemented # Revert to __cmp__

    def __le__(self, other):
        return NotImplemented # Revert to __cmp__

    @property
    def most_probable(self):
        return self._most_probable

def get_transitions(z, energylow_eV=0.0, energyhigh_eV=1e6):
    """
    Returns all the X-ray transitions for the specified atomic number if
    the energy of these transitions is between the specified energy limits.
    The energy limits are inclusive.
    
    :arg z: atomic number (3 to 99)
    :arg energylow_eV: lower energy limit in eV (default: 0 eV)
    :arg energyhigh_eV: upper energy limit in eV (default: 1 MeV)
    """
    transitions = []

    for subshells in _SUBSHELLS:
        if not transition_data.exists(z, subshells):
            continue

        energy = transition_data.energy_eV(z, subshells)
        if energy < energylow_eV or energy > energyhigh_eV:
            continue

        transitions.append(Transition(z, *subshells))

    return sorted(transitions)

def from_string(s):
    """
    Returns a :class:`Transition` or :class:`transitionset` from the given
    string. 
    The first word must be the symbol of the element followed by either the
    Siegbahn (e.g. ``Al Ka1``) or IUPAC (``Al K-L3``) notation of the 
    transition.
    The second word can also represent transition family (e.g. ``Al K``) or 
    shell (``Al LIII``).
    
    :arg s: string representing the transition
    
    :return: transition or set of transitions
    """
    words = s.split(" ")
    if len(words) != 2:
        raise ValueError, "The transition string must have 2 words: " + \
            "1. the symbol of the element and 2. the transition notation"

    z = ep.atomic_number(symbol=words[0])
    notation = words[1]

    # Fix to be compatible with old transition, e.g. N5N6/N6N7
    if '/' in notation: notation = notation[:notation.index('/')]
    if notation == 'Le': notation = 'Ln'

    notation = _siegbahn_ascii_to_unicode(notation)

    if notation in _SIEGBAHNS: # Transition with Siegbahn notation
        return Transition(z, siegbahn=notation)
    elif '-' in notation: # Transition with IUPAC notation
        dest, src = notation.split('-')
        return Transition(z, src=Subshell(z, iupac=src), dest=Subshell(z, iupac=dest))
    elif notation in _TRANSITIONSETS: # transitionset from Family, group or shell
        return _TRANSITIONSETS[notation](z)
    else:
        raise ValueError, "Cannot parse transition string: %s" % s

def _group(z, siegbahn, iupac):
    transitions = []

    for ssiegbahn in _SIEGBAHNS:
        if ssiegbahn.startswith(siegbahn):
            transitions.append(Transition(z, siegbahn=ssiegbahn))

    transitions = filter(methodcaller('exists'), transitions)

    if not transitions:
        raise ValueError, 'No transition for %s %s' % (ep.symbol(z), iupac)

    return transitionset(z, siegbahn, iupac, transitions)

def _shell(z, dest):
    subshell = Subshell(z, dest)
    siegbahn = subshell.siegbahn
    iupac = subshell.iupac

    transitions = []

    for src, ddest in _SUBSHELLS:
        if ddest != dest: continue
        transitions.append(Transition(z, src, dest))

    transitions = filter(methodcaller('exists'), transitions)
    if not transitions:
        raise ValueError, 'No transition for %s %s' % (ep.symbol(z), iupac)

    return transitionset(z, siegbahn, iupac, transitions)

def K_family(z):
    """
    Returns all transitions from the K family.
    """
    return _group(z, 'K', 'K')

def L_family(z):
    """
    Returns all transitions from the L family.
    """
    return _group(z, 'L', 'L')

def M_family(z):
    """
    Returns all transitions from the M family.
    """
    return _group(z, 'M', 'M')

def N_family(z):
    """
    Returns all transitions from the N family.
    """
    return _group(z, 'N', 'N')

def Ka(z):
    """
    Returns all transitions from the Ka group.
    """
    return _group(z, u'K\u03b1', 'K-L(2,3)')

def Kb(z):
    """
    Returns all transitions from the Kb group.
    """
    return _group(z, u'K\u03b2', 'K-M(2-5)N(2-5)')

def La(z):
    """
    Returns all transitions from the La group.
    """
    return _group(z, u'L\u03b1', 'L3-M(4,5)')

def Lb(z):
    """
    Returns all transitions from the Lb group.
    """
    return _group(z, u'L\u03b2', 'L(1-3)-M(2-5)N(1,4-7)O(1,4-5)')

def Lg(z):
    """
    Returns all transitions from the Lg group.
    """
    return _group(z, u'L\u03b3', 'L(1,2)-N(1-6)O(1-3)')

def Ma(z):
    """
    Returns all transitions from the Ma group.
    """
    return _group(z, u'M\u03b1', 'M5-N(6,7)')

def Mb(z):
    """
    Returns all transitions from the Mb group.
    """
    return _group(z, u'M\u03b2', 'M4-N6')

def Mg(z):
    """
    Returns all transitions from the Mg group.
    """
    return _group(z, u'M\u03b3', 'M3-N5')

def LI(z):
    """
    Returns all transitions ending on the L\ :sub:`I` shell.
    """
    return _shell(z, 2)

def LII(z):
    """
    Returns all transitions ending on the L\ :sub:`II` shell.
    """
    return _shell(z, 3)

def LIII(z):
    """
    Returns all transitions ending on the L\ :sub:`III` shell.
    """
    return _shell(z, 4)

def MI(z):
    """
    Returns all transitions ending on the M\ :sub:`I` shell.
    """
    return _shell(z, 5)

def MII(z):
    """
    Returns all transitions ending on the M\ :sub:`II` shell.
    """
    return _shell(z, 6)

def MIII(z):
    """
    Returns all transitions ending on the M\ :sub:`III` shell.
    """
    return _shell(z, 7)

def MIV(z):
    """
    Returns all transitions ending on the M\ :sub:`IV` shell.
    """
    return _shell(z, 8)

def MV(z):
    """
    Returns all transitions ending on the M\ :sub:`V` shell.
    """
    return _shell(z, 9)

_TRANSITIONSETS = {'K': K_family, 'L': L_family, 'M': M_family,
                   u'K\u03b1': Ka, u'K\u03b2': Kb,
                   u'L\u03b1': La, u'L\u03b2': Lb, u'L\u03b3': Lg,
                   u'M\u03b1': Ma, u'M\u03b2': Mb, u'M\u03b3': Mg,
                   'LI': LI, 'LII': LII, 'LIII': LIII,
                   'MI': MI, 'MII': MII, 'MIII': MIII, 'MIV': MIV, 'MV': MV}
