# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import sys, itertools, re, decimal, datetime, pyrfc3339, uuid
from .immutable_dict import ImmutableDict
from .edn_lex import Keyword, Symbol
from .edn_parse import TaggedElement

# alias Python 2 types to their corresponding types in Python 3 if necessary
if sys.version_info[0] >= 3:
    __PY3 = True
    long = int
    basestring = str
    unicode = str
    unichr = chr
else:
    __PY3 = False

DEFAULT_INPUT_ENCODING = 'utf-8'
DEFAULT_OUTPUT_ENCODING = 'utf-8'

# proper unicode escaping
# see http://stackoverflow.com/a/24519338
ESCAPE = re.compile(r'[\x00-\x1f\\"\b\f\n\r\t]', re.UNICODE)
ESCAPE_DCT = {
    '\\': '\\\\',
    '"': '\\"',
    '\b': '\\b',
    '\f': '\\f',
    '\n': '\\n',
    '\r': '\\r',
    '\t': '\\t',
}

for __i in range(0x20):
    ESCAPE_DCT.setdefault(unichr(__i), '\\u{0:04x}'.format(__i))
del __i

def unicode_escape(string):
    """Return a edn representation of a Python string"""
    def replace(match):
        return ESCAPE_DCT[match.group(0)]
    return '"' + ESCAPE.sub(replace, string) + '"'

def seq(obj, string_encoding = DEFAULT_INPUT_ENCODING):
    return ' '.join([udump(i, string_encoding = string_encoding) for i in obj])

def udump(obj, string_encoding = DEFAULT_INPUT_ENCODING):
    if obj is None:
        return 'nil'
    elif isinstance(obj, bool):
        return 'true' if obj else 'false'
    elif isinstance(obj, (int, long, float)):
        return unicode(obj)
    elif isinstance(obj, decimal.Decimal):
        return '{}M'.format(obj)
    elif isinstance(obj, (Keyword, Symbol)):
        return unicode(obj)
    # CAVEAT EMPTOR! In Python 3 'basestring' is alised to 'str' above.
    # Furthermore, in Python 2 bytes is an instance of 'str'/'basestring' while
    # in Python 3 it is not.
    elif isinstance(obj, bytes):
        return unicode_escape(obj.decode(string_encoding))
    elif isinstance(obj, basestring):
        return unicode_escape(obj)
    elif isinstance(obj, tuple):
        return '({})'.format(seq(obj, string_encoding))
    elif isinstance(obj, list):
        return '[{}]'.format(seq(obj, string_encoding))
    elif isinstance(obj, set) or isinstance(obj, frozenset):
        return '#{{{}}}'.format(seq(obj, string_encoding))
    elif isinstance(obj, dict) or isinstance(obj, ImmutableDict):
        return '{{{}}}'.format(seq(itertools.chain.from_iterable(obj.items()),
            string_encoding))
    elif isinstance(obj, datetime.datetime):
        return '#inst "{}"'.format(pyrfc3339.generate(obj, microseconds=True))
    elif isinstance(obj, datetime.date):
        return '#inst "{}"'.format(obj.isoformat())
    elif isinstance(obj, uuid.UUID):
        return '#uuid "{}"'.format(obj)
    elif isinstance(obj, TaggedElement):
        return unicode(obj)
    raise NotImplementedError(
        u"encountered object of type '{}' for which no known encoding is available: {}".format(
            type(obj), repr(obj)))

def dump(obj, string_encoding=DEFAULT_INPUT_ENCODING,
    output_encoding = DEFAULT_OUTPUT_ENCODING):
    outcome = udump(obj, string_encoding=string_encoding)
    if __PY3:
        return outcome
    return outcome.encode(output_encoding)

