from jinja2 import Environment, environmentfunction, nodes
from jinja2.ext import Extension

__all__ = ('TagRegistrar', 'JinjaTag',)

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
            self.ext.env.add_extension(ext)
        else:
            self._tags.append(ext)

_jinja_tags = TagRegistrar()

