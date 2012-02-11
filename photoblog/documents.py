import datetime

from wtforms import Form
from wtforms.fields import TextField, TextAreaField

class BlogPostForm(Form):
    title = TextField("Titel")
    slug = TextField("Slug")
    body = TextAreaField("Body")
    author = TextField("Author")

if __name__ == '__main__':
    import nose
    nose.runmodule(argv=[__file__, '--stop', '-vvs'])
