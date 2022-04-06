from django import template
register = template.Library()

@register.filter(name='split') 
def split(value, key):
    """
        Returns the value turned into a list.
    """
    print('AAAAAAAAAAAAA')
    split_version = value.split(key)
    if split_version[-1] == "":
        split_version = split_version[:-1]
    return split_version