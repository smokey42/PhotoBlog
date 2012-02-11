#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Code taken from:
# http://python.pastebin.com/m76db1d6b
# http://gist.github.com/67044
import ImageDraw

import os
import tempfile
import shutil

from opencv.cv import (cvSize, cvCreateImage, cvHaarDetectObjects,
                       cvClearMemStorage, cvEqualizeHist, cvCreateMemStorage,
                       cvCvtColor, cvLoadHaarClassifierCascade, CV_BGR2GRAY,
                       CV_HAAR_DO_CANNY_PRUNING)
from opencv.highgui import cvLoadImage

def face_image(request, filename):
    document = db.images.Image.find_one({'filename': filename})
    img = document.fs.open('image', 'r')
    size, faces = face_detect(img, closeafter=False)
    img.seek(0)

    if faces:
        boxes = Image.open(img)
        for face in faces:
            x0, y0 = face.x, face.y
            x1, y1 = face.x + face.width, face.y + face.height
            draw = ImageDraw.Draw(boxes)
            draw.rectangle((x0, y0, x1, y1), fill="#f00")
            img.close()
        return serve_pil(boxes, 'PNG')


def face_detect(file, closeafter=True):
    """Converts an image to grayscale and prints the locations of any faces found"""

    if hasattr(file, 'read'):
        _, filename = tempfile.mkstemp()
        tmphandle = open(filename, 'w')
        shutil.copyfileobj(file, tmphandle)
        tmphandle.close()
        if closeafter:
            file.close()
        deleteafter = True
    else:
        filename = file
        deleteafter = False

    image = cvLoadImage(filename)
    grayscale = cvCreateImage(cvSize(image.width, image.height), 8, 1)
    cvCvtColor(image, grayscale, CV_BGR2GRAY)

    storage = cvCreateMemStorage(0)
    cvClearMemStorage(storage)
    cvEqualizeHist(grayscale, grayscale)

    cascade = cvLoadHaarClassifierCascade(
        '/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml',
        cvSize(1,1))

    faces = cvHaarDetectObjects(grayscale, cascade, storage, 1.2, 2,
                                CV_HAAR_DO_CANNY_PRUNING, cvSize(50,50))
    if deleteafter:
        os.unlink(filename)

    return (image.width, image.height), faces

if __name__ == "__main__":
    import doctest
    doctest.testmod()
