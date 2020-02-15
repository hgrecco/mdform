import re

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor


def compile_regex(cls):
    cls.REGEX = re.compile(cls.REGEX)
    return cls


EOL = r"[ \t]?$"
SECTION = re.compile(r"[section[ \t]*:(?P<name>.*)]")


class Common:
    @classmethod
    def match(cls, line):
        m = cls.REGEX.match(line)
        if not m:
            return None

        return cls.process(m)


@compile_regex
class StringField(Common):

    REGEX = r"[ \t]*___(\[(?P<length>\d*)\])?" + EOL

    @classmethod
    def process(cls, m):
        length = m.group("length") or None
        if length is not None:
            length = int(length)

        return dict(length=length)


@compile_regex
class EmailField(Common):

    REGEX = r"[ \t]*@" + EOL

    @classmethod
    def process(cls, m):
        return dict()


@compile_regex
class RadioField(Common):

    REGEX = r"[ \t]*(?P<content>\(x?\)[ \t]*[\w \t\-]+[\(\)\w \t\-]*)" + EOL

    SUBREGEX = re.compile(r"\((?P<is_default>x?)\)[ \t]*(?P<label>[a-zA-Z0-9 \t_\-]?)")

    @classmethod
    def process(cls, m):
        items = []
        default = None

        for matched in cls.SUBREGEX.finditer(m.group("content")):
            label = matched.group("label").strip()
            items.append(label)

            if matched.group("is_default") == "x":
                default = label

        return dict(items=tuple(items), default=default)


@compile_regex
class CheckboxField(Common):

    REGEX = r"[ \t]*(\[x?\][ \t]*[\w \t\-]+[\[\]\w \t\-]*)"

    @classmethod
    def process(cls, m):
        return dict(value=m)


@compile_regex
class SelectField(Common):

    REGEX = r"[ \t]*\{(?P<content>([a-zA-Z0-9 \t\->_,\(\)]+))\}"

    @classmethod
    def process(cls, m):
        items = []
        default = None
        for item in m.group("content").split(","):
            is_default = False

            item = item.strip()
            if item.startswith("(") and item.endswith(")"):
                item = item[1:-1].strip()
                is_default = True

            if "->" in item:
                pair = tuple(s.strip() for s in item.split("->"))
            else:
                pair = (item, item)

            items.append(pair)
            if is_default:
                default = pair[0]

        return dict(items=tuple(items), default=default)


@compile_regex
class Field:

    REGEX = r"(?P<label>\w[\w \t\-]*)(?P<required>\*)?[ \t]*=(?P<pending>.*)"

    FIELD_TYPES = (StringField, RadioField, CheckboxField, SelectField, EmailField)

    @classmethod
    def match(cls, line):
        m = cls.REGEX.match(line)
        if not m:
            return None

        for ft in cls.FIELD_TYPES:
            matched = ft.match(m.group("pending"))

            if matched is None:
                continue

            label = m.group("label").lower().strip()
            required = not m.group("required") is None

            return label, dict(type=ft.__name__, required=required, **matched)

        return None


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
