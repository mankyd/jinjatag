import extension

def simple_tag(name=None):
    def dec(func):
        extension._simple_tags[name or func.__name__] = func
        return func
    return dec

def simple_block(name=None):
    def dec(func):
        extension._simple_blocks[name or func.__name__] = func
        return func
    return dec
