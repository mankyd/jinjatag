try:
    import plocal
except ImportError:
    import threading as plocal

from jinja2 import Environment, environmentfunction, nodes
from jinja2.ext import Extension
from jinja2.lexer import Token

import extension

__all__ = ('simple_tag', 'simple_block', 'multibody_block',)

def create_extension_decorator(cls):
    """
    Class decorator that turns a class representing an Extension
    into a decorator of the same name that registers the given class
    with the jinja_tags registration.
    It also adds 4 instance variables:

      - tags - The set of the tag_name
      - tag_func - The function to dispatch to (wrapped by the decorator)
      - decorator_args - Any extra args passed to the decorator
      - decorator_kwargs - Any extra kwargs passed to the decorator
    """
    def outer_dec(name=None, *args, **kwargs):
        def dec(func):
            tag_name = name if isinstance(name, basestring) and name else func.__name__
            new_cls = type(tag_name, (cls,), {
                    'tags': set([tag_name]),
                    'tag_func': staticmethod(func),
                    'decorator_args': args,
                    'decorator_kwargs': kwargs,
                    })
            extension._jinja_tags.add_tag_ext(new_cls)
            return func
        if callable(name):
            return dec(name)
        return dec
    return outer_dec


@create_extension_decorator
class simple_tag(Extension):
    def parse(self, parser):
        tag = parser.stream.next()

        attrs = extension.JinjaTag._parse_attrs(parser)
        attrs = nodes.Dict([nodes.Pair(nodes.Const(k), v) for k,v in attrs.items()])

        return nodes.Output([self.call_method('_call_simple_tag', args=[attrs])])

    def _call_simple_tag(self, attrs):
        return self.tag_func(**attrs)

@create_extension_decorator
class simple_block(Extension):
    def parse(self, parser):
        tag = parser.stream.next()

        attrs = extension.JinjaTag._parse_attrs(parser)
        attrs = nodes.Dict([nodes.Pair(nodes.Const(k), v) for k,v in attrs.items()])

        body = parser.parse_statements(['name:end'+tag.value], drop_needle=True)

        return [nodes.CallBlock(self.call_method('_call_simple_block', args=[attrs]),
                                [], [], body).set_lineno(tag.lineno)]

    def _call_simple_block(self, attrs, caller):
        return self.tag_func(caller(), **attrs)


@create_extension_decorator
class multibody_block(Extension):
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
