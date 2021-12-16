import pytest

from mdform import FormExtension, Markdown, fields, parse

TEXT = """
Welcome to the form tester

name* = ___[30]
_edad = ___
e-mail* = @
really annoying 323 name = ...

[section:user]
name* = ___

[section]
blip* = @

[collapse]
This is collapsible
[endcollapse]

[collapse:]
This is colon collapsible
[endcollapse]

[collapse:named]
This is a named collapsible
[endcollapse]

[section:other_user]
[collapse:other_named]
This is a named collapsible
[endcollapse]
"""


TEXT_DUP = """
Welcome to the form tester

name* = ___[30]

name* = ___[30]

"""

DEFAULT_FORMATTED = """<p>Welcome to the form tester</p>
<p>{{ form.name }}
{{ form.edad }}
{{ form.e_mail }}
{{ form.really_annoying_323_name }}</p>
<p>{{ form.user_name }}</p>
<p>{{ form.blip }}</p>
<div id="accordion-0">
This is collapsible
</div>

<div id="accordion-1">
This is colon collapsible
</div>

<div id="accordion-named">
This is a named collapsible
</div>

<div id="accordion-other_user_other_named">
This is a named collapsible
</div>"""


FORM = {
    "name": fields.Field("name", True, fields.StringField(length=30)),
    "edad": fields.Field("_edad", False, fields.StringField(length=None)),
    "e_mail": fields.Field("e-mail", True, fields.EmailField()),
    "really_annoying_323_name": fields.Field(
        "really annoying 323 name",
        False,
        fields.FileField(allowed=None, description=None),
    ),
    "user_name": fields.Field("name", True, fields.StringField(length=None)),
    "blip": fields.Field("blip", True, fields.EmailField()),
}


def test_default():
    md = Markdown(extensions=[FormExtension()])
    assert md.convert(TEXT) == DEFAULT_FORMATTED
    assert md.mdform_definition == FORM


def test_default_None():
    md = Markdown(extensions=[FormExtension(formatter=None)])
    assert md.convert(TEXT) == DEFAULT_FORMATTED
    assert md.mdform_definition == FORM


def test_dup():
    md = Markdown(extensions=[FormExtension(formatter=None)])
    with pytest.raises(ValueError):
        md.convert(TEXT_DUP)


def test_parse():
    assert parse(TEXT) == (DEFAULT_FORMATTED, FORM)


def test_parse_other_format():
    def fmt(variable_name, field) -> str:
        return "{{ " + f"{variable_name}" + " }}"

    assert parse(TEXT, formatter=fmt) == (DEFAULT_FORMATTED.replace("form.", ""), FORM)
