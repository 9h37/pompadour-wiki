"""
WikiLinks extension modified to support [[Namespace/Link]]

"""

import markdown
import re

def build_url(label, base, end):
    """ Build a url from the label, a base, and an end. """

    clean_label = re.sub(r'([ ]+_)|(_[ ]+)|([ ]+)', '_', label)
    return '{0}{1}{2}'.format(base, clean_label, end)

class PompadourLinkExtension(markdown.Extension):
    def __init__(self, configs):
        self.config = {
            'base_url': ['/', 'String to append to beginning of URL.'],
            'end_url': ['/', 'String to append to end of URL.'],
            'html_class': ['pompadourlink', 'CSS hook. Leave blank for none.'],
            'build_url': [build_url, 'Callable formats URL from label.'],
        }

        # Override defaults with user settings
        for key, value in configs:
            self.setConfig(key, value)

    def extendMarkdown(self, md, md_globals):
        self.md = md

        POMPADOURLINK_RE = r'\[\[([\w\0-9_ -/]+)\]\]'
        pattern = PompadourLinks(POMPADOURLINK_RE, self.getConfigs())
        pattern.md = md
        md.inlinePatterns.add('pompadourlink', pattern, "<not_strong")

class PompadourLinks(markdown.inlinepatterns.Pattern):
    def __init__(self, pattern, config):
        markdown.inlinepatterns.Pattern.__init__(self, pattern)
        self.config = config

    def handleMatch(self, m):

        if m.group(2).strip():
            base_url, end_url, html_class = self._getMeta()

            label = m.group(2).strip()
            url = self.config['build_url'](label, base_url, end_url)
            a = markdown.util.etree.Element('a')
            a.text = label
            a.set('href', url)

            if html_class:
                a.set('class', html_class)
        else:
            a = ''

        return a

    def _getMeta(self):
        """ Return meta data or config data. """

        base_url = self.config['base_url']
        end_url = self.config['end_url']
        html_class = self.config['html_class']

        if hasattr(self.md, 'Meta'):
            if self.md.Meta.has_key('pompadour_base_url'):
                base_url = self.md.Meta['pompadour_base_url'][0]

            if self.md.Meta.has_key('pompadour_end_url'):
                end_url = self.md.Meta['pompadour_end_url'][0]

            if self.md.Meta.has_key('pompadour_html_class'):
                html_class = self.md.Meta['pompadour_html_class'][0]

        return base_url, end_url, html_class


def makeExtension(configs=None):
    return PompadourLinkExtension(configs=configs)
