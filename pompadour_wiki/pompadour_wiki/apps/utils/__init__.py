# -*- coding: utf-8 -*-

import os

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
