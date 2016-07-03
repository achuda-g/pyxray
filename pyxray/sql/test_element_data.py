#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.
from sqlalchemy import create_engine

# Local modules.
from pyxray.sql.element_data import SqlEngineElementDatabase
from pyxray.sql.model import \
    (Base, Reference, ElementSymbolProperty, ElementNameProperty,
     ElementAtomicWeightProperty, ElementMassDensityProperty)
from pyxray.sql.util import session_scope

# Globals and constants variables.

def create_mock_database():
    engine = create_engine('sqlite:///:memory:')

    Base.metadata.create_all(engine)

    ref1 = Reference(bibtexkey='ref1')
    ref2 = Reference(bibtexkey='ref2')
    data = [(26, 'Fe', 'Iron', 'Eisen', 55.845, 7874.0, ref1),
            (26, 'Fe', 'Iron', 'Eisen', 58.0, 9000.0, ref2),
            (8, 'O', 'Oxygen', 'Sauerstoff', 15.9994, 1.429, ref1)]

    with session_scope(engine) as session:
        for z, symbol, name_en, name_de, aw, rho, ref in data:
            p = ElementSymbolProperty(z=z, symbol=symbol, reference=ref)
            session.add(p)

            p = ElementNameProperty(z=z, language_code='en', name=name_en, reference=ref)
            session.add(p)

            p = ElementNameProperty(z=z, language_code='de', name=name_de, reference=ref)
            session.add(p)

            p = ElementAtomicWeightProperty(z=z, value=aw, reference=ref)
            session.add(p)

            p = ElementMassDensityProperty(z=z, value=rho, reference=ref)
            session.add(p)

        session.commit()

    return engine

class TestSqlEngineElementDatabase(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        engine = create_mock_database()
        self.db = SqlEngineElementDatabase(engine)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testsymbol(self):
        self.assertEqual('Fe', self.db.symbol(26))
        self.assertEqual('Fe', self.db.symbol(26, reference='ref1'))
        self.assertEqual('Fe', self.db.symbol(26, reference='ref2'))

        self.assertEqual('O', self.db.symbol(8))
        self.assertEqual('O', self.db.symbol(8, reference='ref1'))

        self.assertRaises(ValueError, self.db.symbol, 1)
        self.assertRaises(ValueError, self.db.symbol, 8, reference='ref2')

    def testatomic_number(self):
        self.assertEqual(26, self.db.atomic_number('Fe'))
        self.assertEqual(26, self.db.atomic_number('fe'))
        self.assertEqual(26, self.db.atomic_number('Fe', reference='ref1'))
        self.assertEqual(26, self.db.atomic_number('Fe', reference='ref2'))

        self.assertEqual(8, self.db.atomic_number('O'))
        self.assertEqual(8, self.db.atomic_number('o'))
        self.assertEqual(8, self.db.atomic_number('O', reference='ref1'))

        self.assertRaises(ValueError, self.db.atomic_number, 'H')
        self.assertRaises(ValueError, self.db.atomic_number, 'O', reference='ref2')

    def testname(self):
        self.assertEqual('Iron', self.db.name(26))
        self.assertEqual('Iron', self.db.name(26, 'en'))
        self.assertEqual('Eisen', self.db.name(26, 'de'))
        self.assertEqual('Iron', self.db.name('Fe'))

        self.assertEqual('Oxygen', self.db.name(8))
        self.assertEqual('Oxygen', self.db.name(8, 'en'))
        self.assertEqual('Sauerstoff', self.db.name(8, 'de'))
        self.assertEqual('Oxygen', self.db.name('O'))

        self.assertRaises(ValueError, self.db.name, 'H')
        self.assertRaises(ValueError, self.db.name, 26, 'fr')

    def testatomic_weight(self):
        self.assertAlmostEqual(55.845, self.db.atomic_weight(26), 3)
        self.assertAlmostEqual(55.845, self.db.atomic_weight('Fe'), 3)
        self.assertAlmostEqual(55.845, self.db.atomic_weight(26, reference='ref1'), 3)
        self.assertAlmostEqual(58.0, self.db.atomic_weight(26, reference='ref2'), 3)

        self.assertAlmostEqual(15.9994, self.db.atomic_weight(8), 3)
        self.assertAlmostEqual(15.9994, self.db.atomic_weight('O'), 3)
        self.assertAlmostEqual(15.9994, self.db.atomic_weight(8, reference='ref1'), 3)

        self.db.reference_priority = ['ref2']
        self.assertAlmostEqual(58.0, self.db.atomic_weight(26), 3)
        self.assertAlmostEqual(55.845, self.db.atomic_weight(26, reference='ref1'), 3)
        self.assertAlmostEqual(58.0, self.db.atomic_weight(26, reference='ref2'), 3)
        self.assertAlmostEqual(15.9994, self.db.atomic_weight(8), 3)

    def testmass_density(self):
        self.assertAlmostEqual(7874.0, self.db.mass_density_kg_per_m3(26), 3)
        self.assertAlmostEqual(7874.0, self.db.mass_density_kg_per_m3('Fe'), 3)
        self.assertAlmostEqual(7874.0, self.db.mass_density_kg_per_m3(26, reference='ref1'), 3)
        self.assertAlmostEqual(9000.0, self.db.mass_density_kg_per_m3(26, reference='ref2'), 3)

        self.assertAlmostEqual(1.429, self.db.mass_density_kg_per_m3(8), 3)
        self.assertAlmostEqual(1.429, self.db.mass_density_kg_per_m3('O'), 3)
        self.assertAlmostEqual(1.429, self.db.mass_density_kg_per_m3(8, reference='ref1'), 3)

        self.db.reference_priority = ['ref2']
        self.assertAlmostEqual(9000.0, self.db.mass_density_kg_per_m3(26), 3)
        self.assertAlmostEqual(7874.0, self.db.mass_density_kg_per_m3(26, reference='ref1'), 3)
        self.assertAlmostEqual(9000.0, self.db.mass_density_kg_per_m3(26, reference='ref2'), 3)
        self.assertAlmostEqual(1.429, self.db.mass_density_kg_per_m3(8), 3)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
