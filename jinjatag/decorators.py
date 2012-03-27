import sys
import inspect
import traceback

try:
    import plocal
except ImportError:
    import threading as plocal

from jinja2 import Environment, environmentfunction, nodes
from jinja2.ext import Extension
from jinja2.lexer import Token


import extension

__all__ = ('simple_tag', 'simple_block', 'multibody_block', 'simple_context_tag',)

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


class BaseTag(Extension):
    def parse_attrs(self, parser, add_id=True, with_context=False):
        attrs = {}
        while parser.stream.current.type != 'block_end':
            node = parser.parse_assign_target(with_tuple=False)

            if parser.stream.skip_if('assign'):
                attrs[node.name] = parser.parse_expression()
            else:
                attrs[node.name] = nodes.Const(node.name)
        if with_context:
            attrs['ctx'] = nodes.ContextReference()
        return nodes.Dict([nodes.Pair(nodes.Const(k), v) for k,v in attrs.items()])

    def call_tag_func(self, *args, **kwargs):
        try:
            return self.tag_func(*args, **kwargs)
        except TypeError as e:
            t, value, tb = sys.exc_info()
            if len(traceback.extract_tb(tb, 2)) > 1:
                raise
            argspec = inspect.getargspec(self.tag_func)
            arg_list = list(argspec.args)
            if argspec.varargs:
                arg_list.append('*' + argspec.varargs)
            if argspec.keywords:
                arg_list.append('**' + argspec.keywords)
            raise TypeError("Failed to satisfy arguments for {0}({1}): provided ({2}).".format(
                    iter(self.tags).next(),
                    ', '.join(arg_list),
                    ', '.join([repr(arg) for arg in args] + ['{0}={1}'.format(k, repr(v)) for k, v in kwargs.items()])))

    @property
    def local_env(self):
        " A thread save dictionary to store data for a particular tag. "
        if not hasattr(self, '_local_env'):
            self._local_env = plocal.local()
        if not hasattr(self._local_env, 'env'):
            self._local_env.env = {}
        return self._local_env.env

    @local_env.setter
    def local_env(self, value):
        if not hasattr(self, '_local_env'):
            self._local_env = plocal.local()
        self._local_env.env = value

@create_extension_decorator
class simple_tag(BaseTag):
    def parse(self, parser):
        tag = parser.stream.next()

        attrs = self.parse_attrs(parser)

        return nodes.Output([self.call_method('_call_simple_tag', args=[attrs])])

    def _call_simple_tag(self, attrs):
        return self.call_tag_func(**attrs)


@create_extension_decorator
class simple_context_tag(BaseTag):
    def parse(self, parser):
        tag = parser.stream.next()

        attrs = self.parse_attrs(parser, with_context=True)

        return nodes.Output([self.call_method('_call_simple_tag', args=[attrs])])

    def _call_simple_tag(self, attrs):
        return self.call_tag_func(**attrs)

@create_extension_decorator
class simple_block(BaseTag):
    def parse(self, parser):
        tag = parser.stream.next()

        attrs = self.parse_attrs(parser)

        end_tags = ['name:end' + tag.value, 'name:end_' + tag.value]
        body = parser.parse_statements(end_tags, drop_needle=True)

        return [nodes.CallBlock(self.call_method('_call_simple_block', args=[attrs]),
                                [], [], body).set_lineno(tag.lineno)]

    def _call_simple_block(self, attrs, caller):
        return self.call_tag_func(caller(), **attrs)


@create_extension_decorator
class multibody_block(BaseTag):
    def parse(self, parser):
        INSIDE_BLOCK, OUTSIDE_BLOCK = 0, 1

        tag = parser.stream.next()

        end_tags_in_block = [
            'name:{0}_endblock'.format(tag.value),
            'name:{0}_end_block'.format(tag.value),
            ]

        end_tags_outside_block = [
            'name:end' + tag.value,
            'name:end_' + tag.value,
            'name:{0}_block'.format(tag.value),
            ]

        end_tags = (end_tags_in_block, end_tags_outside_block)

        state = OUTSIDE_BLOCK

        attrs = self.parse_attrs(parser)
        body = parser.parse_statements(end_tags[state], drop_needle=False)

        node_list = []

        blocks = [
            (nodes.Const('body'), body, tag.lineno),
            ]


        while True:
            sub_tag = parser.stream.next()
            sub_tag_name = sub_tag.value

            tag_index = end_tags[state].index('name:' + sub_tag_name)

            if state == OUTSIDE_BLOCK and tag_index < 2:
                break

            elif state == OUTSIDE_BLOCK:
                # entering new block
                sub_block_name = parser.parse_expression()
                state = INSIDE_BLOCK
                body = parser.parse_statements(end_tags[state], drop_needle=False)
                blocks.append((sub_block_name, body, sub_tag.lineno))

            else:
                state = OUTSIDE_BLOCK
                parser.parse_statements(end_tags[state], drop_needle=False)


        node_list = [
            nodes.CallBlock(self.call_method('_subblock', args=[block_name]),
                            [], [], block).set_lineno(lineno)
            for block_name, block, lineno in blocks
            ]

        node_list.append(nodes.Output([self.call_method('_call_multiblock_tag', args=[attrs])]))

        return node_list

    def _subblock(self, block_name, caller):
        self.local_env[str(block_name)] = caller()
        return ''

    def _call_multiblock_tag(self, attrs):
        attrs.update(self.local_env)
        self.local_env = {}
        return self.call_tag_func(**attrs)


