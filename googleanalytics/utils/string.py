import textwrap


# Python 2 and 3 compatibility
try:
    unicode = unicode
except NameError:
    unicode = str


def format(string, **kwargs):
    return textwrap.dedent(string).format(**kwargs).strip()


def affix(prefix, base, suffix, connector='_'):
    if prefix:
        prefix = prefix + connector
    else:
        prefix = ''

    if suffix:
        suffix = connector + suffix
    else:
        suffix = ''

    return prefix + base + suffix


# a supercharged `join` function, analogous to `paste` in the R language
def paste(rows, *delimiters):
    delimiter = delimiters[-1]
    delimiters = delimiters[:-1]

    if len(delimiters):
        return paste([paste(row, *delimiters) for row in rows], delimiter)
    else:
        return delimiter.join(map(unicode, rows))


# a supercharged `split` function, the inverse of `paste`
def cut(s, *delimiters):
    delimiter = delimiters[-1]
    delimiters = delimiters[:-1]

    if len(delimiters):
        return [cut(ss, *delimiters) for ss in cut(s, delimiter)]
    else:
        return s.split(delimiter)
