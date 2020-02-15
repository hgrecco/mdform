from mdform.fields import (
    EmailField,
    Field,
    FileField,
    RadioField,
    SelectField,
    StringField,
)


def test_label():
    assert Field.match("name = @") == ("name", dict(type="EmailField", required=False))
    assert Field.match("name* = @") == ("name", dict(type="EmailField", required=True))
    assert Field.match("name * = @") == ("name", dict(type="EmailField", required=True))


def test_string_field():
    assert StringField.match("_") is None
    assert StringField.match("__") is None
    assert StringField.match("____") is None
    assert StringField.match("___") == dict(length=None)
    assert StringField.match("___[30]") == dict(length=30)
    assert StringField.match(" ___[30]") == dict(length=30)
    assert StringField.match("___[30] ") == dict(length=30)
    assert StringField.match(" ___[30] ") == dict(length=30)
    assert StringField.match("___[]") == dict(length=None)


def test_email_field():
    assert EmailField.match("") is None
    assert EmailField.match("@") == dict()
    assert EmailField.match(" @") == dict()
    assert EmailField.match(" @ ") == dict()


def test_radio_field():
    assert RadioField.match("() A () B ()") == dict(items=("A", "B", ""), default=None)
    assert RadioField.match("() A (x) B () C") == dict(
        items=("A", "B", "C"), default="B"
    )
    assert RadioField.match("() A () B () C") == dict(
        items=("A", "B", "C"), default=None
    )


def test_select_field():
    assert SelectField.match("{ A, B, C") is None
    assert SelectField.match("{ A, B, C}") == dict(
        items=(("A", "A"), ("B", "B"), ("C", "C")), default=None
    )
    assert SelectField.match("{ A, B, (C)}") == dict(
        items=(("A", "A"), ("B", "B"), ("C", "C")), default="C"
    )
    assert SelectField.match("{ A->J, B, (C->P)}") == dict(
        items=(("A", "J"), ("B", "B"), ("C", "P")), default="C"
    )


def test_filefield():
    assert FileField.match("...") == dict(allowed=None, description=None)
    assert FileField.match("...[png]") == dict(allowed=("png",), description=None)
    assert FileField.match("...[png,jpg]") == dict(
        allowed=("png", "jpg"), description=None
    )
    assert FileField.match("...[png;image files only]") == dict(
        allowed=("png",), description="image files only"
    )
    assert FileField.match("...[png,jpg;image files only]") == dict(
        allowed=("png", "jpg"), description="image files only"
    )
