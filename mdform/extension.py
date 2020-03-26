import re

import unidecode
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

from .fields import COLLAPSE_CLOSE_RE, COLLAPSE_OPEN_RE, SECTION_RE, Field

COLLAPSE_OPEN_HTML = r'<div id="accordion-%s">'
COLLAPSE_CLOSE_HTML = r"</div>"


def _sanitizer(s):

    s = unidecode.unidecode(s)

    # Remove invalid characters
    s = re.sub(r"[^0-9a-zA-Z_]", "_", s)

    # Remove leading characters until we find a letter or underscore
    s = re.sub(r"^[^a-zA-Z_]+", "_", s)

    return s


class FormPreprocessor(Preprocessor):
    """ Get Form. """

    def __init__(self, md, sanitizer=None, wtf=False):
        self.sanitizer = sanitizer or (lambda s: s)
        self.wtf = wtf
        super().__init__(md)

    def run(self, lines):
        """ Parse Form and store in Markdown.Form. """
        form = {}
        section = None

        out = []
        for line in lines:
            m1 = SECTION_RE.match(line)
            if m1:
                section = m1.group("name").lower().strip()
                continue

            m1 = COLLAPSE_OPEN_RE.match(line)
            if m1:
                control_field = m1.group("name").lower().strip()
                control_field = self.sanitizer(control_field)
                if section:
                    control_field = "%s_%s" % (section, control_field)

                out.append(COLLAPSE_OPEN_HTML % control_field)
                continue

            m1 = COLLAPSE_CLOSE_RE.match(line)
            if m1:
                out.append(COLLAPSE_CLOSE_HTML)
                continue

            label_value = Field.match(line)

            if label_value:
                label, value = label_value

                nolabel = False
                if label.startswith("_"):
                    label = label[1:]
                    nolabel = True

                variable_name = self.sanitizer(label.lower())

                if section:
                    variable_name = "%s_%s" % (section, variable_name)

                form[variable_name] = dict(label=label, **value)

                if self.wtf:
                    args = ["form.%s" % variable_name]
                    args.append("form_type='horizontal'")

                    tag_class = ["form-control"]
                    if nolabel:
                        tag_class.append("nolabel")

                    collapse_on = value.get("collapse_on")
                    if collapse_on:
                        comparator = "!=="
                        if collapse_on.startswith("~"):
                            collapse_on = collapse_on[1:]
                            comparator = "==="
                        else:
                            comparator = "!=="

                        tag_class.append("collapser")
                        args.append(
                            """ onchange="jQuery('#accordion-%s').toggle(jQuery(this).val() %s '%s');" """
                            % (variable_name, comparator, collapse_on)
                        )

                    args.append('class="%s"' % " ".join("%s" % c for c in tag_class))

                    if value.get("length") is not None:
                        args.append("maxlength=%d" % value["length"])

                    out.append("{{ wtf.form_field(%s) }}" % (", ".join(args)))
                else:
                    out.append("{{ form.%s }}" % variable_name)
            else:
                out.append(line)

        self.md.Form = form
        return out


class FormExtension(Extension):
    """ Form extension for Python-Markdown. """

    def __init__(self, **kwargs):
        self.config = {
            "sanitizer": [_sanitizer, "Function to sanitize the label"],
            "wtf": [False, "Use wtf template for fields"],
        }
        super().__init__(**kwargs)

    def extendMarkdown(self, md):
        md.registerExtension(self)
        self.md = md
        md.preprocessors.register(
            FormPreprocessor(md, self.getConfig("sanitizer"), self.getConfig("wtf")),
            "form",
            30,
        )

    def reset(self):
        self.md.Form = {}


def makeExtension(**kwargs):
    return FormExtension(**kwargs)
