from mdform import FormExtension, Markdown

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
</div>"""


FORM = {
    "name": dict(
        label="name", type="StringField", required=True, length=30, nolabel=False
    ),
    "edad": dict(
        label="edad",
        type="StringField",
        required=False,
        length=None,
        nolabel=True,
    ),
    "e_mail": dict(label="e-mail", type="EmailField", required=True, nolabel=False),
    "really_annoying_323_name": dict(
        label="really annoying 323 name",
        type="FileField",
        required=False,
        allowed=None,
        description=None,
        nolabel=False,
    ),
    "user_name": dict(
        label="name", type="StringField", required=True, length=None, nolabel=False
    ),
    "blip": dict(
        label="blip",
        type="EmailField",
        required=True,
        nolabel=False,
    ),
}


def test_default():
    md = Markdown(extensions=[FormExtension()])
    assert md.convert(TEXT) == DEFAULT_FORMATTED
    assert md.mdform_definition == FORM


def test_default_None():
    md = Markdown(extensions=[FormExtension(formatter=None)])
    assert md.convert(TEXT) == DEFAULT_FORMATTED
    assert md.mdform_definition == FORM
