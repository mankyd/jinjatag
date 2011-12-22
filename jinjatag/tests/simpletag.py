import unittest

import jinjatag
from jinjatag.tests import JinjaTagTestCase

class SimpleTagTestCase(JinjaTagTestCase):
    @jinjatag.simple_tag()
    def st_simple_tag(x, y):
        return str(x - y)

    def bound_simple_tag(self, x, y):
        return str(self) + str(x)

    def test_bound(self):
        jinjatag.simple_tag()(self.bound_simple_tag)
        tmpl = self.env.from_string(''' {% bound_simple_tag x=4 y=6 %} ''')
        self.assertEquals(tmpl.render(), ' test_bound (jinjatag.tests.simpletag.SimpleTagTestCase)4 ')

    def test_simple(self):
        tmpl = self.env.from_string(''' {% st_simple_tag x=4 y=6 %} ''')
        self.assertEquals(tmpl.render(), ' -2 ')
        tmpl = self.env.from_string(''' {% st_simple_tag y=4 x=6 %} ''')
        self.assertEquals(tmpl.render(), ' 2 ')

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SimpleTagTestCase))
    return suite
