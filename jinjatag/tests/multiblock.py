import unittest

from jinja2 import TemplateSyntaxError

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

    def test_mbb_simple_errors(self):
        # for loop outside inner block
        tmpl1_string = '''
{% mbb_simple x="foo" y="bar" %}

 this is the random body

 {% mbb_simple_block 'header' %}
   this is the header
 {% mbb_simple_endblock %}
 {% for i in range(10) %}
   {% mbb_simple_block i %}
   {% mbb_simple_endblock %}
 {% endfor %}
{% end_mbb_simple %}
'''
        self.assertRaises(TemplateSyntaxError, self.env.from_string, tmpl1_string)

        tmpl2_string = '''
{% mbb_simple x="foo" y="bar" %}

body

{% mbb_simple_endblock %}
{% end_mbb_simple %}
'''
        self.assertRaises(TemplateSyntaxError, self.env.from_string, tmpl2_string)

    @jinjatag.multibody_block
    def mbb_simple_bam(body, header='', footer='', x=None, y=None):
        raise ValueError(header)


    def test_func_exception(self):
        self.assertRaises(ValueError,
                          self.env.from_string(''' {% mbb_simple_bam x=10 y=20 %} {% end_mbb_simple_bam %} ''').render)

    @jinjatag.multibody_block
    def mbb_missing_param(body, header):
        return str(header)

    def test_missing_param(self):
        self.assertRaises(TypeError,
                          self.env.from_string('{% mbb_missing_param %} {% end_mbb_missing_param %}').render)

    @jinjatag.multibody_block
    def mbb_dynamic_block_names(**kwargs):
        return str(sorted(kwargs.items()))

    def test_dynamic_block_names(self):
        tmpl = self.env.from_string('{% mbb_dynamic_block_names x="foo" %} {% mbb_dynamic_block_names_block i**2 + 3 %}foo{% mbb_dynamic_block_names_end_block %}{% end_mbb_dynamic_block_names %}')
        self.assertEquals(tmpl.render({'i': 2}), u"[('7', u'foo'), ('body', u' '), ('x', 'foo')]")
        self.assertEquals(tmpl.render({'i': 3}), u"[('12', u'foo'), ('body', u' '), ('x', 'foo')]")

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MultiBlockTagTestCase))
    return suite
