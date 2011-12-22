import unittest

import jinjatag
from jinjatag.tests import JinjaTagTestCase


class MultiBlockTagTestCase(JinjaTagTestCase):
    @jinjatag.multibody_block
    def mbb_simple(body, header, footer, x=None, y=None):
        return '<h1>{}</h1>x={}, y={}<br> {} <footer>{}</footer>'.format(header, x, y, body, footer)

    def test_mbb_simple(self):
        tmpl = self.env.from_string('''
{% mbb_simple x="foo" y="bar" %}

 this is the random body

 {% mbb_simple_block 'header' %}
   this is the header
 {% mbb_simple_endblock %}

 {% mbb_simple_block 'footer' %}
   this is the footer
 {% mbb_simple_endblock %}

{% end_mbb_simple %}

'''.strip())
        self.assertEquals(tmpl.render(), '<h1>\n   this is the header\n </h1>x=foo, y=bar<br> \n\n this is the random body\n\n  <footer>\n   this is the footer\n </footer>')

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MultiBlockTagTestCase))
    return suite
