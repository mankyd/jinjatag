from jinja2 import Environment, environmentfunction, nodes
from jinja2.ext import Extension

_simple_tags = {}
_simple_blocks = {}

class _SimpleTagExt(Extension):
    def parse(self, parser):
        tag = parser.stream.next()

        attrs = JinjaTag._parse_attrs(parser)
        attrs = nodes.Dict([nodes.Pair(nodes.Const(k), v) for k,v in attrs.items()])

        return nodes.Output([self.call_method('_call_simple_tag', args=[attrs])])

    def _call_simple_tag(self, attrs):
        return self.tag_func(**attrs)

class _SimpleBlockExt(Extension):
    def parse(self, parser):
        tag = parser.stream.next()

        attrs = JinjaTag._parse_attrs(parser)
        attrs = nodes.Dict([nodes.Pair(nodes.Const(k), v) for k,v in attrs.items()])

        body = parser.parse_statements(['name:end'+tag.value], drop_needle=True)

        return [nodes.CallBlock(self.call_method('_call_simple_block', args=[attrs]),
                                [], [], body).set_lineno(tag.lineno)]

    def _call_simple_block(self, attrs, caller):
        return self.tag_func(caller(), **attrs)


class JinjaTag(Extension):
    def __init__(self):
        pass

    def __call__(self, environment):
        Extension.__init__(self, environment)
        self.env = environment
        return self

    def init(self):
        global _simple_tags
        global _simple_blocks

        for k, v in _simple_tags.items():
            self.add_simple_tag_ext(k, v)
        _simple_tags = SimpleTagRegistrar(self)

        for k, v in _simple_blocks.items():
            self.add_simple_block_ext(k, v)
        _simple_blocks = SimpleBlockRegistrar(self)

    def add_simple_tag_ext(self, tag_name, tag_func):
        cls = type(tag_name.title(), (_SimpleTagExt,), {})
        cls.tags = {tag_name}
        cls.tag_func = staticmethod(tag_func)
        self.env.add_extension(cls)

    def add_simple_block_ext(self, tag_name, tag_func):
        cls = type(tag_name.title(), (_SimpleBlockExt,), {})
        cls.tags = {tag_name}
        cls.tag_func = staticmethod(tag_func)
        self.env.add_extension(cls)

    @classmethod
    def _parse_attrs(cls, parser, add_id=True):
        attrs = {}
        while parser.stream.current.type != 'block_end':
            node = parser.parse_assign_target(with_tuple=False)

            if parser.stream.skip_if('assign'):
                attrs[node.name] = parser.parse_expression()
            else:
                attrs[node.name] = nodes.Const(node.name)

        return attrs

class SimpleTagRegistrar(object):
    def __init__(self, ext):
        self.ext = ext

    def __setitem__(self, key, value):
        self.ext.add_simple_tag_ext(key, value)

class SimpleBlockRegistrar(object):
    def __init__(self, ext):
        self.ext = ext

    def __setitem__(self, key, value):
        self.ext.add_simple_block_ext(key, value)
