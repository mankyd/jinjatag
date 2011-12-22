import os
import glob
import unittest
import importlib

from jinja2 import Environment

import jinjatag


here = os.path.dirname(__file__)

jinja_tag = jinjatag.JinjaTag()
jinja2_env = Environment(extensions=[jinja_tag])
jinja_tag.init()


class JinjaTagTestCase(unittest.TestCase):
    @property
    def env(self):
        return jinja2_env


def test_all():
    suite = unittest.TestSuite()
    for fname in glob.glob(os.path.join(here, '*.py')):
        if '__init__' in fname:
            continue
        module = importlib.import_module('jinjatag.tests.' + os.path.basename(fname).split('.py')[0])
        suite.addTest(module.suite())
    return suite
