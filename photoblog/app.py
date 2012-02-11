#!/usr/bin/env python
# -*- coding: utf-8 -*-

from werkzeug import Request, Response, ClosingIterator
from werkzeug.exceptions import HTTPException
from jinja2 import Environment, FileSystemLoader

from photoblog.urls import url_map
from photoblog.utils import local, local_manager
import photoblog.views as views

from pymongo import Connection
from gridfs import GridFS
from collections import defaultdict

def safe_keys(dic):
    new = {}
    for key, value in dic.items():
        if isinstance(key, unicode):
            key = str(key)
        new[key] = value
    return new

class MongoRequest(Request):

    @property
    def db(self):
        return self.environ['mongo.db']

    @property
    def fs(self):
        return self.environ['mongo.fs']

class GridFactory(object):

    def __init__(self, db):
        self.db = db
        self.storage = {}

    def __getitem__(self, key):
        return self.storage.setdefault(key, GridFS(self.db, key))

    def __getattr__(self, key):
        return getattr(self.__getitem__('images'), key)


class PhotoBlog(object):

    def __init__(self, database):
        local.application = self
        self.env = Environment(loader=FileSystemLoader('templates'))
        self.conn = Connection()
        self.db = self.conn[database]
        self.fs = GridFactory(self.db)

    def __call__(self, environ, start_response):
        local.application = self
        request = MongoRequest(environ)
        local.url_adapter = adapter = url_map.bind_to_environ(environ)
        environ['mongo.db'] = self.db
        environ['mongo.fs'] = self.fs
        try:
            endpoint, values = adapter.match()
            handler = getattr(views, endpoint)
            data = handler(request, **values)

            # WSGI
            if callable(data):
                return data(environ, start_response)

            data = safe_keys(data)

            data['request'] = request

            # Templates
            template = self.env.get_template("%s.html" % endpoint)
            response = Response()
            response.content_type = "text/html"
            response.add_etag()
            # if DEBUG:
            #   response.make_conditional(request)
            data['endpoint'] = endpoint
            response.data = template.render(**data)
        except HTTPException, e:
            response = e
        return ClosingIterator(response(environ, start_response),
                               [local_manager.cleanup])

