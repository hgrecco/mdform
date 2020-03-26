import re


def compile_regex(cls):
    cls.REGEX = re.compile(cls.REGEX, re.UNICODE)
    return cls


EOL = r"[ \t]?$"
SECTION_RE = re.compile(r"\[section[ \t]*:(?P<name>.*)\]", re.UNICODE)
COLLAPSE_OPEN_RE = re.compile(r"\[collapse[ \t]*:(?P<name>.*)\]", re.UNICODE)
COLLAPSE_CLOSE_RE = re.compile(r"\[endcollapse]")


class Common:
    @classmethod
    def match(cls, line):
        m = cls.REGEX.match(line)
        if not m:
            return None

        return cls.process(m)


@compile_regex
class Field:

    REGEX = r"(?P<label>\w[\w \t\-]*)(?P<required>\*)?[ \t]*=(?P<pending>.*)"

    FIELD_TYPES = []

    @classmethod
    def register(cls, rc):
        cls.FIELD_TYPES.append(rc)
        return rc

    @classmethod
    def match(cls, line):
        m = cls.REGEX.match(line)
        if not m:
            return None

        for ft in cls.FIELD_TYPES:
            matched = ft.match(m.group("pending"))

            if matched is None:
                continue

            label = m.group("label").strip()
            required = not m.group("required") is None

            return label, dict(type=ft.__name__, required=required, **matched)

        return None


@Field.register
@compile_regex
class StringField(Common):

    REGEX = r"[ \t]*___(\[(?P<length>\d*)\])?" + EOL

    @classmethod
    def process(cls, m):
        length = m.group("length") or None
        if length is not None:
            length = int(length)

        return dict(length=length)


@Field.register
@compile_regex
class TextAreaField(Common):

    REGEX = r"[ \t]*AAA(\[(?P<length>\d*)\])?" + EOL

    @classmethod
    def process(cls, m):
        length = m.group("length") or None
        if length is not None:
            length = int(length)

        return dict(length=length)


@Field.register
@compile_regex
class DateField(Common):

    REGEX = r"[ \t]d/m/y" + EOL

    @classmethod
    def process(cls, m):
        return dict()


@Field.register
@compile_regex
class TimeField(Common):

    REGEX = r"[ \t]hh:mm" + EOL

    @classmethod
    def process(cls, m):
        return dict()


@Field.register
@compile_regex
class EmailField(Common):

    REGEX = r"[ \t]*@" + EOL

    @classmethod
    def process(cls, m):
        return dict()


@Field.register
@compile_regex
class RadioField(Common):

    REGEX = r"[ \t]*(?P<content>\(x?\)[ \t]*[\w \t\-]+[\(\)\w \t\-]*)" + EOL

    SUBREGEX = re.compile(
        r"\((?P<is_default>x?)\)[ \t]*(?P<label>[a-zA-Z0-9 \t_\-]?)", re.UNICODE
    )

    @classmethod
    def process(cls, m):
        items = []
        default = None

        for matched in cls.SUBREGEX.finditer(m.group("content")):
            label = matched.group("label").strip()

            items.append(label)

            if matched.group("is_default") == "x":
                default = label

        return dict(choices=tuple(items), default=default)


@Field.register
@compile_regex
class CheckboxField(Common):

    REGEX = r"[ \t]*(\[x?\][ \t]*[\w \t\-]+[\[\]\w \t\-]*)"

    @classmethod
    def process(cls, m):
        return dict(value=m)


@Field.register
@compile_regex
class SelectField(Common):

    REGEX = r"[ \t]*\{(?P<content>([\w \t\->_,\(\)\[\]]+))\}"

    @classmethod
    def process(cls, m):
        items = []
        default = None

        collapse_on = None

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

            if "[c]" in pair[0]:
                # collapse
                if collapse_on is not None:
                    raise ValueError("Can only collapse on a single item.")
                item0 = pair[0].replace("[c]", "")
                item1 = pair[1].replace("[c]", "")
                collapse_on = item0
                pair = (item0, item1)

            if "[o]" in pair[0]:
                # open
                if collapse_on is not None:
                    raise ValueError("Can only collapse on a single item.")
                item0 = pair[0].replace("[o]", "")
                item1 = pair[1].replace("[o]", "")
                collapse_on = "~" + item0
                pair = (item0, item1)

            items.append(pair)
            if is_default:
                default = pair[0]

        return dict(choices=tuple(items), default=default, collapse_on=collapse_on)


@Field.register
@compile_regex
class FileField(Common):

    REGEX = r"[ \t]*...(\[(?P<allowed>[\w \t,;]*)\])?" + EOL

    @classmethod
    def process(cls, m):
        allowed = m.group("allowed") or None
        description = None

        if allowed is not None:
            if ";" in allowed:
                allowed, description = allowed.split(";", 1)

            if "," in allowed:
                allowed = tuple(s.strip() for s in allowed.split(","))
            else:
                allowed = (allowed,)

        return dict(allowed=allowed, description=description)
