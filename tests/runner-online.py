#!/usr/bin/python3
"""These 'online' tests need a reachable CEP/CES server and valid kerberos credential cache"""
import unittest
import sys

sys.path.insert(0, "../")
import cepces_test

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromModule(cepces_test.user))

    runner = unittest.TextTestRunner(verbosity=3, failfast=True)
    runner.run(suite)
