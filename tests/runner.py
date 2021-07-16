#!/usr/bin/python3
import unittest
import sys
sys.path.insert(0, '../')
import cepces_test

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromModule(cepces_test.certmonger))
    suite.addTests(loader.loadTestsFromModule(cepces_test.xcep))
    suite.addTests(loader.loadTestsFromModule(cepces_test.xml))

    runner = unittest.TextTestRunner(verbosity=3, failfast=True)
    runner.run(suite)
