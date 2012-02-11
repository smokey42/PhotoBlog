#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from werkzeug import script, SharedDataMiddleware

from photoblog.app import PhotoBlog

def make_app():
    blog = PhotoBlog('test')
    return SharedDataMiddleware(blog, {
       '/shared': os.path.join(os.path.dirname(__file__), 'shared'), 
    })

def make_shell():
    application = make_app()
    return locals()

action_runserver = script.make_runserver(make_app, use_reloader=True)
action_shell = script.make_shell(make_shell)

script.run()
