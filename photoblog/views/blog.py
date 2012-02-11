#!/usr/bin/env python
# -*- coding: utf-8 -*-

from photoblog.documents import BlogPostForm
from photoblog.utils import db

def edit_blogpost(request, title=None):
    if title:
        post = request.db.blogposts.BlogPost.find({'title': title})
    else:
        post = request.db.blogposts.BlogPost()
    return {'form': BlogPostForm(request.form, obj=post)}
