#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mimetypes
import Image
import magic

from werkzeug import FileWrapper, Response
import gridfs

def serve_pil(image, extension):
    resp = Response()
    resp.content_type = mimetypes.guess_type(extension)
    image.save(resp.stream, extension)
    return resp

def serve_file(file, content_type=None):
    # Reset the stream
    file.seek(0)
    resp = Response(FileWrapper(file), direct_passthrough=True)

    if content_type is None:
        resp.content_type = file.content_type
    else:
        resp.content_type = content_type

    return resp

def upload_images(request):
    for file in request.files.values():
        buf = file.read(1024)
        content_type = magic.from_buffer(buf, mime=True)
        file.seek(0)
        assert content_type.startswith('image')
        request.fs.put(file,
                       content_type=content_type,
                       filename=file.filename)
        file.close()

    return {'message': "Uploaded!"}

def list_images(request):
    return {'images': request.fs.list()}

def view_image(request, filename):
    thumbs = request.fs['thumbnails']
    gridimage = request.fs.get_last_version(filename)

    # FIXME
    # Das hier im Dateinamen zu kodieren ist eine schlechte 
    # Idee, das ist besser in den MongoDB Metadaten aufgehoben,
    # hier ist die Abstraktion von MongoKIT die falsche.

    if 'height' in request.args or 'width' in request.args:
        image = Image.open(gridimage)

        # look into mongo to see if thumbnail is there
        # if not: calculate image and save it to mongodb
        # anyway: serve the thumbnail

        if 'width' in request.args and not 'height' in request.args:
            width = float(request.args['width'])
            height = int(image.size[1] / (image.size[0]/width))
        elif 'height' in request.args and not 'width' in request.args:
            height = float(request.args['height'])
            width = int(image.size[0] / (image.size[1]/height))

        try:
            thumbnail_filename = "thumb%d-%d-%s" % (width, height, filename)
            thumbnail = thumbs.get_last_version(thumbnail_filename)
        except gridfs.errors.NoFile:
            resized = image.resize((int(width), int(height)), Image.ANTIALIAS)
            try:
                thumbnail = thumbs.new_file(
                                       content_type=gridimage.content_type,
                                       filename=thumbnail_filename)
                resized.save(thumbnail, gridimage.content_type.split("/")[1])
            finally:
                thumbnail.close()

            thumbnail = thumbs.get_last_version(thumbnail_filename)

        return serve_file(thumbnail)

    return serve_file(gridimage)

