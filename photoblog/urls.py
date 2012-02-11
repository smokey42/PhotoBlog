#!/usr/bin/env python
# -*- coding: utf-8 -*-

from werkzeug.routing import Rule, Submount, Map

url_map = Map([
    Rule('/', endpoint='index'),
    Rule('/impressum/', endpoint='impressum'),
    Rule('/document/<string:document_id>',
        endpoint='document'),
    Submount('/admin', [
        Rule('/edit', endpoint='edit_blogpost'),
    ]),
    Submount('/image', [
        Rule('/<string:filename>',
            endpoint='image', strict_slashes=False),
    ]),
    Submount('/images', [
        Rule('/', endpoint='list_images'),
        Rule('/upload',
            endpoint='upload_images'),
        Rule('/<string:filename>',
            endpoint='view_image', strict_slashes=False),
    ]),
])
