#
# Copyright (C) Colin O'Flynn, 2016-2021
# Distributed under apache license 2.0
#

import requests
import string
import numpy as np
import base64

# This is required for datamatrix QR code addition
# Can ignore if you don't need datamatrix
from elaphe import barcode

# This is required only for image manipulation
from PIL import Image


class Zebra(object):
    """The Zebra label printer
    """

    def __init__(self):
        self.url = "http://192.168.3.160"

    def render_label(self, zpl=None, file_path=None):
        """Render a label using the zebra printers render engine

        Can pass either zpl text or file_path to file containing zpl text.

        :param zpl: string, ZPL code
        :param file_path: string, path to file containing ZPL code
        :return: PIL.image,  rendered PNG image
        """
        if file_path and zpl:
            raise UserWarning('Provide zpl or file_path not both')

        if file_path:
            with open(file_path, 'r') as f:
                zpl = ''.join(f.readlines())

        # Build form post
        payload = {'data': zpl, 'dev': 'R', 'oname': 'TEST', 'otype': 'ZPL',
                   'prev': "Preview Label"}

        # Submit
        r = requests.post(self.url + "/zpl", data=payload)
        r.raise_for_status()

        nt = r.text.split('<IMG SRC="')[1]
        nt = nt.split('"')[0]

        image = requests.get(self.url + "/" + nt, stream=True)
        image.raise_for_status()

        return image.raw

    def print_label(self, zpl=None, file_path=None):
        """Print a label

        Can pass either zpl text or file_path to file containing zpl text.

        :param zpl: string, ZPL oode
        :param file_path: string, path to file containing ZPL code
        :return: None,
        """
        if file_path and zpl:
            raise UserWarning('Provide zpl or file_path not both')

        if file_path:
            with open(file_path, 'r') as f:
                zpl = ''.join(f.readlines())

        payload = {'data': zpl, 'dev': 'R', 'oname': 'TEST', 'otype': 'ZPL',
                   'print': "Print Label"}

        r = requests.post(self.url + "/zpl", data=payload)
        r.raise_for_status()
        return None


def zpl_from_template(template_file=None, fields=None):
    """Generate ZPL code from a template

    Any occurance of ${identifier} within the template file gets
    replaced with its value corresponding to the identifier key in the
    fields dictionary passed to this function.

    :param template_file: string, path to file containing template text
    :param fields: dict, mapping of identifiers to replacements
    :return: string, ZPL code
    """
    zpl_lines = []
    with open(template_file) as f:
        for line in f.readlines():
            line = string.Template(line)
            line = line.substitute(fields)
            zpl_lines.append(line)
    zpl = ''.join(zpl_lines)
    return zpl


def create_datamatrix_field_string(data=None, scale=3.0):
    """Create graphics field text for datamatrix

    Generates the graphics field ZPL code to create a graphic of a scannable
    datamatrix containing the information in data. Example: ^GF{text}^FS

    :param data: string, the data to include in the datamatrix
    :return: string, the graphics field ZPL code
    """

    options = {
        'format': 'square',
        'version': '144x144',
    }

    bitmap = barcode('datamatrix', data, options=options, margin=1, scale=scale)
    array = np.array(bitmap.getdata(), dtype=np.uint8).reshape(bitmap.size[1], bitmap.size[0], 3)
    m = np.where(array == 255)
    indices = set(zip(m[0], m[1]))
    bits = []
    for i in range(np.shape(bitmap)[0]):
        ls = []
        for j in range(np.shape(bitmap)[1]):
            if (i, j) in indices:
                ls.append(0)
            else:
                ls.append(1)
        bits.append(ls)

    array = np.array(bits, dtype=np.uint8)
    bytes = np.apply_along_axis(np.packbits, axis=1, arr=array)
    encoded_graphic = base64.b64encode(bytes)
    byte_num = np.shape(bytes)[0]*np.shape(bytes)[1]
    row_bytes = np.shape(bytes)[1]

    return 'A,{},{},{},\n:B64:{}:0000'.format(byte_num, byte_num, row_bytes, encoded_graphic)

def create_image_field_string(image_path, rotate=None):
    """Create graphics field text from image.
    
    Generates the graphics field ZPL code from an input image. If you are
    generating the image from e.g. matplotlib you can either use a temp image
    (what I do) or figure out the proper way to pass the image data.
    
    :param image_path: string, path to image, format autodetected
    :param rotate: int, degrees to rotate, may depend on label orientation
    :return: string, the graphics field ZPL code
    """
    im = Image.open(image_path)
    if rotate:
        im = im.rotate(270, expand=1)
    bitmap = im.quantize(255)
    array = np.array(bitmap.getdata(), dtype=np.uint8).reshape(bitmap.size[1], bitmap.size[0], 1)
    m = np.where(array == 0)
    indices = set(zip(m[0], m[1]))
    bits = []
    for i in range(np.shape(bitmap)[0]):
        ls = []
        for j in range(np.shape(bitmap)[1]):
            if (i, j) in indices:
                ls.append(0)
            else:
                ls.append(1)
        bits.append(ls)

    array = np.array(bits, dtype=np.uint8)
    bytes = np.apply_along_axis(np.packbits, axis=1, arr=array)
    encoded_graphic = base64.b64encode(bytes)
    byte_num = np.shape(bytes)[0]*np.shape(bytes)[1]
    row_bytes = np.shape(bytes)[1]

    return 'A,{},{},{},\n:B64:{}:0000'.format(byte_num, byte_num, row_bytes, encoded_graphic)