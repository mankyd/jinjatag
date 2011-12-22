from jinja2 import Environment, environmentfunction, nodes
from jinja2.ext import Extension

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
        _jinja_tags.set_base_ext(self)

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

class TagRegistrar(object):
    def __init__(self):
        self.ext = None
        self._tags = []

    def set_base_ext(self, ext):
        self.ext = ext
        for tag_ext in self._tags:
            self.ext.env.add_extension(tag_ext)

    def add_tag_ext(self, ext):
        if self.ext:
            self.ext.evnt.add_extension(ext)
        else:
            self._tags.append(ext)

_jinja_tags = TagRegistrar()

