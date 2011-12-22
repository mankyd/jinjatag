try:
    import plocal
except ImportError:
    import threading as plocal

from jinja2 import Environment, environmentfunction, nodes
from jinja2.ext import Extension
from jinja2.lexer import Token

import extension

__all__ = ('simple_tag', 'simple_block', 'multibody_block',)

def simple_tag(name=None):
    def dec(func):
        tag_name = name if isinstance(name, basestring) else func.__name__
        cls = type(tag_name, (extension._SimpleTagExt,), {})
        cls.tags = {tag_name}
        cls.tag_func = staticmethod(func)
        extension._jinja_tags.add_tag_ext(cls)
        return func
    if callable(name):
        return dec(name)
    return dec

def simple_block(name=None):
    def dec(func):
        tag_name = name if isinstance(name, basestring) else func.__name__
        cls = type(tag_name, (extension._SimpleBlockExt,), {})
        cls.tags = {tag_name}
        cls.tag_func = staticmethod(func)
        extension._jinja_tags.add_tag_ext(cls)
        return func
    if callable(name):
        return dec(name)
    return dec

def multibody_block(name=None):
    def dec(func):
        tag_name = name if isinstance(name, basestring) else func.__name__
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

        end_tags = ['name:end' + tag.value,
                    'name:end_' + tag.value,
                    'name:{}_block'.format(tag.value),
                    'name:{}_endblock'.format(tag.value),
                    'name:{}_end_block'.format(tag.value),
                    ]

        attrs_ = extension.JinjaTag._parse_attrs(parser)
        body = parser.parse_statements(end_tags, drop_needle=False)

        node_list = []

        blocks = [
            ('body', body, tag.lineno),
            ]

        while True:
            sub_tag = parser.stream.next()
            sub_tag_name = sub_tag.value

            tag_index = end_tags.index('name:' + sub_tag_name)

            if tag_index < 2:
                break

            elif tag_index == 2:
                sub_block_name = parser.stream.next().value
                body = parser.parse_statements(end_tags, drop_needle=False)
                blocks.append((sub_block_name, body, sub_tag.lineno))

            else:
                parser.parse_statements(end_tags, drop_needle=False)

        self.block_results = plocal.local()
        self.block_results.data = {}

        node_list = [
            nodes.CallBlock(self.call_method('_subblock', args=[nodes.Const(block_name)]),
                            [], [], block).set_lineno(lineno)
            for block_name, block, lineno in blocks
            ]

        attrs = self.to_node_dict(attrs_)

        node_list.append(nodes.Output([self.call_method('_call_multiblock_tag', args=[attrs])]))

        return node_list

    def _subblock(self, block_name, caller):
        self.block_results.data[block_name] = caller()
        return ''

    def _call_multiblock_tag(self, attrs):
        block_results = self.block_results.data
        self.block_results.data = {}
        attrs.update(block_results)
        return self.tag_func(**attrs)

    @classmethod
    def to_node_dict(cls, d):
        return nodes.Dict([nodes.Pair(nodes.Const(k), v if isinstance(v, nodes.Const) else nodes.Const(v)) for k,v in d.items()])
