import re


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


@compile_regex
class Field:

    REGEX = r"(?P<label>\w[\w \t\-]*)(?P<required>\*)?[ \t]*=(?P<pending>.*)"

    FIELD_TYPES = (
        StringField,
        RadioField,
        CheckboxField,
        SelectField,
        EmailField,
        FileField,
    )

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
