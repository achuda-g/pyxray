#!/usr/bin/env python
"""
================================================================================
:mod:`subshell_data` -- Data about atomic subshell
================================================================================

.. module:: subshell_data
   :synopsis: Data about atomic subshell

.. inheritance-diagram:: pyxray.subshell_data

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
from abc import ABCMeta, abstractmethod
import csv

# Third party modules.
from pkg_resources import resource_stream #@UnresolvedImport

# Local modules.

# Globals and constants variables.

class _SubshellDatabase(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def energy_eV(self, z, subshell):
        """
        Returns the ionization energy of a subshell in eV. 
        If no ionization energy is defined for a subshell, infinity is returned.
        
        :arg z: atomic number
        :arg subshell: index of the subshells (1 to 29 inclu.) 
            or :class:`Subshell` object
        """
        raise NotImplementedError

    @abstractmethod
    def exists(self, z, subshell):
        """
        Returns whether the subshell exists.
        
        :arg z: atomic number
        :arg subshell: index of the subshells (1 to 29 inclu.) 
            or :class:`Subshell` object
        """
        raise NotImplementedError

    @abstractmethod
    def width_eV(self, z, subshell):
        """
        Returns the natural width of a subshell in eV.
        
        :arg z: atomic number
        :arg subshell: index of the subshells (1 to 29 inclu.) 
            or :class:`Subshell` object
        """
        raise NotImplementedError

class CarlsonSubshellDatabase(_SubshellDatabase):
    """
    The ionization energies are taken from T.A. Carlson, 'Photoelectron and 
    Auger Spectroscopy' (Plenum Press, New York and London, 1975).
    No width is provided.
    """

    def __init__(self):
        fileobj = resource_stream(__name__, 'data/carlson_subshell_ionization_data.csv')
        self.data = self._read(fileobj)

    def _read(self, fileobj):
        data = {}
        reader = csv.reader(fileobj)
        reader.next() # skip header

        for row in reader:
            z = int(row[0])
            subshell = int(row[1])
            energy_eV = float(row[2])

            data.setdefault(z, {})
            data[z].setdefault(subshell, energy_eV)

        return data

    def energy_eV(self, z, subshell):
        if not z in self.data:
            raise ValueError, "No ionization energy for atomic number %i." % z

        if hasattr(subshell, 'index'):
            subshell = subshell.index

        try:
            return self.data[z][subshell]
        except KeyError:
            return float('inf')

    def exists(self, z, subshell):
        if hasattr(subshell, 'index'):
            subshell = subshell.index

        try:
            self.data[z][subshell]
            return True
        except KeyError:
            return False

    def width_eV(self, z, subshell):
        return 0.0

class KrauseOlivierSubshellDatabase(_SubshellDatabase):
    """
    Natural widths of K- and L-subshells are taken from Krause, M.O. and
    Olivier, J.H., J. Phys. Chem. Ref. Data. 8, 1979.
    """

    def __init__(self):
        fileobj = resource_stream(__name__, 'data/krause_subshell_width_data.csv')
        self.data = self._read(fileobj)

    def _read(self, fileobj):
        data = {}
        reader = csv.reader(fileobj)
        reader.next() # skip header

        for row in reader:
            z = int(row[0])
            subshell = int(row[1])
            width_eV = float(row[2])

            data.setdefault(z, {})
            data[z].setdefault(subshell, width_eV)

        return data
    
    def energy_eV(self, z, subshell):
        raise ValueError, "No ionization energy for atomic number %i." % z
    
    def exists(self, z, subshell):
        return False

    def width_eV(self, z, subshell):
        if not z in self.data:
            raise ValueError, "No width for atomic number %i." % z

        if hasattr(subshell, 'index'):
            subshell = subshell.index

        try:
            return self.data[z][subshell]
        except KeyError:
            return 0.0

# Utility functions at module level.
# Basically delegate everything to the instance object.
#---------------------------------------------------------------------------

class SuperDatabase(_SubshellDatabase):

    def __init__(self):
        self.carlson = CarlsonSubshellDatabase()
        self.krause = KrauseOlivierSubshellDatabase()

    def energy_eV(self, z, subshell):
        return self.carlson.energy_eV(z, subshell)
    
    def exists(self, z, subshell):
        return self.carlson.exists(z, subshell)
    
    def width_eV(self, z, subshell):
        return self.krause.width_eV(z, subshell)

instance = SuperDatabase()

def get_instance():
    return instance

def set_instance(inst):
    global instance
    instance = inst

def energy_eV(z, subshell):
    """
    Returns the ionization energy of a subshell in eV.
    
    :arg z: atomic number
    :arg subshell: index of the subshells (1 to 29 inclu.)
        or :class:`Subshell` object
    """
    return instance.energy_eV(z, subshell)

def exists(z, subshell):
    """
    Returns whether the subshell exists.
    
    :arg z: atomic number
    :arg subshell: index of the subshells (1 to 29 inclu.)
        or :class:`Subshell` object
    """
    return instance.exists(z, subshell)

def width_eV(z, subshell):
    """
    Returns the natural width of a subshell in eV.
    
    :arg z: atomic number
    :arg subshell: index of the subshells (1 to 29 inclu.) 
        or :class:`Subshell` object
    """
    return instance.width_eV(z, subshell)
