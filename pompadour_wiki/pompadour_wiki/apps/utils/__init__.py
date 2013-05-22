# -*- coding: utf-8 -*-

import os
import re

def urljoin(*args):
    """ Like os.path.join but for URLs """

    if len(args) == 0:
        return ""

    if len(args) == 1:
        return str(args[0])

    else:
        args = [str(arg).replace("\\", "/") for arg in args]

        work = [args[0]]
        for arg in args[1:]:
            if arg.startswith("/"):
                work.append(arg[1:])
            else:
                work.append(arg)

        joined = reduce(os.path.join, work)

    return joined.replace("\\", "/")

def breadcrumbify(path):
    """ Generates breadcrumb from a path """

    breadcrumb_list = path.split('/')
    breadcrumb_urls = []

    for breadcrumb in breadcrumb_list:
        parts = breadcrumb_urls + [breadcrumb]
        url = urljoin(*parts)
        breadcrumb_urls.append(url)

    return zip(breadcrumb_list, breadcrumb_urls)

def decode_unicode_references(data):
    """ Replace '&#<unicode id>' by the unicode character """

    def _callback(matches):
        id = matches.group(1)
        try:
            return unichr(int(id))
        except:
            return id

    return re.sub("&#(\d+)(;|(?=\s))", _callback, data)

def stripspecialchars(input_str):
    """ Remove special chars in UTF-8 string """

    import unicodedata

    # will decompose UTF-8 entities ('é' becomes 'e\u0301')
    nfkd_form = unicodedata.normalize('NFKD', unicode(input_str))

    # unicodedata.combining() returns 0 if the character is a normal character,
    # so this loop help us converting the string in ASCII-format
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])