"""
WikiLinks extension modified to support [[Namespace/Link]]

"""

from django.template.defaultfilters import slugify
import markdown
import re

def build_url(label, base, end):
    """ Build a url from the label, a base, and an end. """

    clean_label = '-'.join(label.split(' '))
    return u'{0}{1}{2}'.format(base, clean_label, end)

class PompadourLinkExtension(markdown.Extension):
    def __init__(self, configs):
        self.config = {
            u'base_url': [u'/', u'String to append to beginning of URL.'],
            u'end_url': [u'/', u'String to append to end of URL.'],
            u'html_class': [u'pompadourlink', u'CSS hook. Leave blank for none.'],
            u'build_url': [build_url, u'Callable formats URL from label.'],
        }

        # Override defaults with user settings
        for key, value in configs:
            self.setConfig(key, value)

    def extendMarkdown(self, md, md_globals):
        self.md = md

        POMPADOURLINK_RE = r'\[\[([\w\0-9_ -/]+)\]\]'
        pattern = PompadourLinks(POMPADOURLINK_RE, self.getConfigs())
        pattern.md = md
        md.inlinePatterns.add(u'pompadourlink', pattern, "<not_strong")

class PompadourLinks(markdown.inlinepatterns.Pattern):
    def __init__(self, pattern, config):
        markdown.inlinepatterns.Pattern.__init__(self, pattern)
        self.config = config

    def handleMatch(self, m):

        if m.group(2).strip():
            base_url, end_url, html_class = self._getMeta()

            label = m.group(2).strip()
            url = self.config[u'build_url'](label, base_url, end_url)
            a = markdown.util.etree.Element('a')
            a.text = label
            a.set(u'href', url)

            if html_class:
                a.set(u'class', html_class)
        else:
            a = ''

        return a

    def _getMeta(self):
        """ Return meta data or config data. """

        base_url = self.config[u'base_url']
        end_url = self.config[u'end_url']
        html_class = self.config[u'html_class']

        if hasattr(self.md, u'Meta'):
            if self.md.Meta.has_key(u'pompadour_base_url'):
                base_url = self.md.Meta[u'pompadour_base_url'][0]

            if self.md.Meta.has_key(u'pompadour_end_url'):
                end_url = self.md.Meta[u'pompadour_end_url'][0]

            if self.md.Meta.has_key(u'pompadour_html_class'):
                html_class = self.md.Meta[u'pompadour_html_class'][0]

        return base_url, end_url, html_class


def makeExtension(configs=None):
    return PompadourLinkExtension(configs=configs)
