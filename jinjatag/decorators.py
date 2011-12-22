from jinja2 import Environment, environmentfunction, nodes
from jinja2.ext import Extension

import extension

__all__ = ('simple_tag', 'simple_block',)

def simple_tag(name=None):
    if callable(name):
        return dec(name)
    def dec(func):
        tag_name = name or func.__name__
        cls = type(tag_name, (extension._SimpleTagExt,), {})
        cls.tags = {tag_name}
        cls.tag_func = staticmethod(func)
        extension._jinja_tags.add_tag_ext(cls)
        return func
    return dec

def simple_block(name=None):
    def dec(func):
        tag_name = name or func.__name__
        cls = type(tag_name, (extension._SimpleBlockExt,), {})
        cls.tags = {tag_name}
        cls.tag_func = staticmethod(func)
        extension._jinja_tags.add_tag_ext(cls)
        return func
    if callable(name):
        return dec(name)
    return dec

'''
def multibody_block(name=None):
    def dec(func):
        tag_name = name or func.__name__
        cls = type(tag_name, (_MultiBodyBlockExt,), {
                'tags': {tag_name},
                'tag_func': staticmethod(func)})
        extension._jinja_tags.add_tag_ext(cls)
        return func
    if callable(name):
        return dec(name)
    return dec


class _MultiBodyBlockExt(Extension):
    def parse(self, parser):
        tag = parser.stream.next()

        attrs = JinjaTag._parse_attrs(parser)
        attrs = nodes.Dict([nodes.Pair(nodes.Const(k), v) for k,v in attrs.items()])

        body = parser.parse_statements(['name:end'+tag.value], drop_needle=True)

        return [nodes.CallBlock(self.call_method('_call_simple_block', args=[attrs]),
                                [], [], body).set_lineno(tag.lineno)]

    def _call_simple_block(self, attrs, caller):
        return self.tag_func(caller(), **attrs)

'''
