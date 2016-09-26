import doctest
import unittest

from sprig import api
from sprig.mock import mock_sprig

mock_sprig()
suite = unittest.TestSuite()
suite.addTests([
    doctest.DocTestSuite(api, optionflags=doctest.ELLIPSIS),
    doctest.DocFileSuite("README.md", optionflags=doctest.ELLIPSIS)
])

if __name__ == "__main__":
    unittest.TextTestRunner().run(suite)
