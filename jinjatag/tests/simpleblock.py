import unittest

from jinja2 import TemplateSyntaxError

import jinjatag
from jinjatag.tests import JinjaTagTestCase


class SimpleBlockTagTestCase(JinjaTagTestCase):
    @jinjatag.simple_block
    def sb_caesar_cipher(body, shift=13):
        return ''.join(chr((ord(c) - 96 + shift) % 26 + 96)
                   if c.islower() else c for c in body)

    def test_casear_cipher(self):
        tmpl = self.env.from_string('''{% sb_caesar_cipher shift=10 %}
  the quick brown fox jumped over the lazy dog.
  {% if 1 %}
  raising elephants is so utterly boring.
  {% endif %}
{% end_sb_caesar_cipher %}''')
        self.assertEquals(tmpl.render(), u'\n  dro aesmu lbygx pyh tew`on yfob dro vkji nyq.\n  \n  bkscsxq ovo`rkxdc sc cy eddobvi lybsxq.\n  \n')

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SimpleBlockTagTestCase))
    return suite
