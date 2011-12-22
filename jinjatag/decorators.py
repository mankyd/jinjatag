import extension

def simple_tag(name=None):
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
    return dec
