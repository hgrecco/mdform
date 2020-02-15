from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

from .fields import SECTION, Field


class FormPreprocessor(Preprocessor):
    """ Get Form. """

    def run(self, lines):
        """ Parse Form and store in Markdown.Form. """
        form = {}
        section = None

        out = []
        for line in lines:
            m1 = SECTION.match(line)
            if m1:
                section = m1.group("label").lower().strip()
                continue

            label_value = Field.match(line)

            if label_value:
                label, value = label_value

                if section:
                    label = "%s_%s" % (section, label)

                form[label] = value
                out.append("{{ form.%s }}" % label)

            else:
                out.append(line)

        self.md.Form = form
        return out


class FormExtension(Extension):
    """ Form extension for Python-Markdown. """

    def extendMarkdown(self, md):
        md.registerExtension(self)
        self.md = md
        md.preprocessors.register(FormPreprocessor(md), "form", 30)

    def reset(self):
        self.md.Form = {}


def makeExtension(**kwargs):
    return FormExtension(**kwargs)
