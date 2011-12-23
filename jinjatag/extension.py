from jinja2 import Environment
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

