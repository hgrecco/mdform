from markdown import Markdown

from ..extension import FormExtension

TEXT = """
Welcome to the form tester

name* = ___[30]
e-mail* = @
really annoying 323 name = ...

[section:user]
name* = ___
"""

JINJA = """<p>Welcome to the form tester</p>
<p>{{ form.name }}
{{ form.e_mail }}
{{ form.really_annoying_323_name }}</p>
<p>{{ form.user_name }}</p>"""

JINJA_WTF = """<p>Welcome to the form tester</p>
<p>{{ wtf.form_field(form.name, form_type='horizontal', class="form-control", maxlength=30) }}
{{ wtf.form_field(form.e_mail, form_type='horizontal', class="form-control") }}
{{ wtf.form_field(form.really_annoying_323_name, form_type='horizontal', class="form-control") }}</p>
<p>{{ wtf.form_field(form.user_name, form_type='horizontal', class="form-control") }}</p>"""

FORM = {
    "name": dict(label="name", type="StringField", required=True, length=30),
    "e_mail": dict(label="e-mail", type="EmailField", required=True),
    "really_annoying_323_name": dict(
        label="really annoying 323 name",
        type="FileField",
        required=False,
        allowed=None,
        description=None,
    ),
    "user_name": dict(label="name", type="StringField", required=True, length=None),
}


def test_default():
    md = Markdown(extensions=[FormExtension()])
    assert md.convert(TEXT) == JINJA
    assert md.Form == FORM


def test_wtf():
    md = Markdown(extensions=[FormExtension(wtf=True)])
    assert md.convert(TEXT) == JINJA_WTF
    assert md.Form == FORM
