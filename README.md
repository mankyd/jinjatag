A Library to Quickly Turn Functions into Jinja2 Extensions
==========================================================

This library is best demonstrated through example:

```python
import jinjatag

### Configure your Jinja2 Environment:
jinja_tag = jinjatag.JinjaTag()
jinja2_env = Environment(extensions=[jinja_tag])
jinja_tag.init()

### Decorate your functions

@jinjatag.simple_tag()
def mytag(foo, bar=None, **kwargs):
    return "mytag: "+foo+(bar or '')+str(kwargs)

@jinjatag.simple_block()
def myblock(body, foo, bar=None):
    return "myblock : "+body+foo+(bar or '')

```

Then, in your template code, use your new tags:

    {% mytag foo='abc' xyz='def' %}

    {% myblock foo='bar' %}contents{% endmyblock %}

The resulting output:

    mytag: abc{'xyz':'def'}

    myblock: contentsbar

That's really all there is to it. A simple_tag is expected to accept 0 or more arguments and return a string. A simple_block is expected to accept at least one argument which will be its rendered body.


Install
-------

The module is registered with pypi, so simply use:

    easy_install jinjatag

or, if you're so inclined:

    pip install jinjatag


Further Documentation
----------------------

More documentation is available at http://mankyd.github.com/jinjatag/

Also, tests are available in https://github.com/mankyd/jinjatag/tree/master/jinjatag/tests


License
--------

GPL v3

Authors
-------

Dave Mankoff
Mike Axiak
