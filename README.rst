numtiff
=======

A Python package to read and write NumPy_ arrays as TIFF images, using a thin
ctypes-based wrapper around LibTIFF_.

.. _NumPy: http://www.numpy.org/
.. _LibTIFF: http://www.remotesensing.org/libtiff/

Status
------

This package was written for my own use and has not been tested otherwise.
Reading and writing bilevel, grayscale, and RGB stripped images of common
sample types should work.

Requirements
------------

- Python 2.7 (may work with 2.6 or 2.5 but not tested).
- OS X or Linux (or other UNIX). Should work on Windows with minor
  modification to the library and header loading code.
- LibTIFF (tested with 3.8-4.0). If you use a package manager and your
  distribution has separate -dev packages, you need both libtiff and
  libtiff-dev.

Usage
-----

You need to have a general understanding of how TIFF files are structured (TIFF
directories, in particular).

::

    import numtiff

    # Disable warning printing (e.g. unexpected TIFF tags):
    numtiff.show_warnings(False)

    # Read a single grayscale image:
    with numtiff.tiffopen("myimage.tif") as tif:
        image = numtiff.read_gray_stripped_image(tif)
        # image.shape is (height, width)

    # Read a file containing multiple RGB images:
    with numtiff.tiffopen("myrgbimages.tif") as tif:
        for tif in numtiff.iterate_directories(tif):
            image = numtiff.read_rgb_stripped_image(tif)
            # image.shape is (height, width, 3)

    # Write a single-page grayscale TIFF with float samples:
    arr = numpy.zeros((height, width), dtype=numpy.float32)
    # ...
    with numtiff.tiffopen("output.tif", "w") as tif:
        numtiff.write_gray_stripped_image(tif, arr)

Other high-level functions currently are:

- ``read_bilevel_stripped_image(tif)``
- ``read_rgb_stripped_image(tif)``
- ``write_bilevel_stripped_image(tif, arr)``
- ``write_rgb_stripped_image(tif, arr)``

All ``read_*`` functions return a NumPy array of the data type corresponding to
the TIFF image sample format. The ``write_*`` functions save an image with the
sample format corresponding to the data type of the passed array.

Most of the LibTIFF functions are made available (see ``numtiff/__init__.py``
for more examples)::

    import numtiff, ctypes
    with numtiff.tiffopen("myimage.tif") as tif:
        photometric = ctypes.c_uint16()
        numtiff.TIFFGetFieldDefaulted(tif, numtiff.TIFFTAG_PHOTOMETRIC,
                                      byref(photometric))
