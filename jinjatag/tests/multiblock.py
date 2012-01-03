import unittest
import threading
import hashlib

from jinja2 import TemplateSyntaxError

import jinjatag
from jinjatag.tests import JinjaTagTestCase


class MultiBlockTagTestCase(JinjaTagTestCase):
    @jinjatag.multibody_block
    def mbb_simple(body, header, footer, x=None, y=None):
        return '<h1>{0}</h1>x={1}, y={2}<br> {3} <footer>{4}</footer>'.format(header, x, y, body, footer)

    @jinjatag.multibody_block
    def mbb_single(body, x=None, y=None):
        return 'x={0}, y={1}<br> {2}'.format(x, y, body)

    def test_mbb_simple(self):
        tmpl = self.env.from_string('''
{% set x_val="foo" -%}
{% mbb_simple x=x_val y="bar" %}

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

    def test_mbb_single(self):
        tmpl = self.env.from_string('''
{% mbb_single x="foo" y="bar" %}

 this is the random body

{% end_mbb_single %}

'''.strip())
        self.assertEquals(tmpl.render(), 'x=foo, y=bar<br> \n\n this is the random body\n\n')

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

    @jinjatag.multibody_block
    def mbb_nosubblock_threaded(body, title, cls, header_links=None, corners='all'):
        header_cls = 'with-link' if header_links is not None else ''
        header_links = '<span class="header-link">{0}</span>'.format(header_links) if header_links is not None else ''

        return '''{corners}, {cls}, {header_cls}, {title}, {header_links}, {body}'''.format(
            corners=corners,
            cls=cls,
            header_cls=header_cls,
            title=title,
            header_links=header_links,
            body=body)

    def test_mbb_nosubblock(self):
        tmpl_string = '''
          {% for i in range(0, 10) %}
            {% mbb_nosubblock_threaded title="Test {0}".format("- {0}".format(i) if i % 2 == 0 else '') cls="test" %}
              {% if i % 3 == 0 %}
                mod 3!
              {% endif %}
            {% end_mbb_nosubblock_threaded %}
          {% endfor %}
          ''' * 5
        tmpl = self.env.from_string(tmpl_string)
        num_successful = [0]
        num_threads = 25
        def sub_test():
            for i in range(10):
                self.assertEquals(hashlib.sha256(tmpl.render()).hexdigest(), '469bf40757716ed125208f26f9ae42673c717d53821b302e395231551b406897')
            num_successful[0] += 1

        threads = [threading.Thread(target=sub_test) for i in range(num_threads)]
        for thread in threads:
            thread.setDaemon(True)
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEquals(num_successful[0], num_threads)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MultiBlockTagTestCase))
    return suite
