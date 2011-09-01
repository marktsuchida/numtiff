from .libtiff import *
import numpy
import contextlib

@contextlib.contextmanager
def tiffopen(filename, mode="r"):
    tiff = TIFFOpen(filename, mode)
    if tiff.value is None:
        raise IOError("cannot open TIFF file: %s" % filename)
    try:
        yield tiff
    finally:
        TIFFClose(tiff)


def iterate_directories(tiff):
    while True: # The first directory is read when the TIFF is opened.
        yield tiff
        if not TIFFReadDirectory(tiff):
            break


def read_bilevel_stripped_image(tiff):
    photometric = c_uint16()
    TIFFGetFieldDefaulted(tiff, TIFFTAG_PHOTOMETRIC, byref(photometric))
    photometric = photometric.value
    if photometric not in (PHOTOMETRIC_MINISWHITE, PHOTOMETRIC_MINISBLACK):
        raise IOError("expected monochrome image; found color image " +
                      "(photometric interpretation = %d)" % photometric)
    inverse_intensity = False
    if photometric == PHOTOMETRIC_MINISWHITE:
        inverse_intensity = True

    samples_per_pixel = c_uint16()
    TIFFGetFieldDefaulted(tiff, TIFFTAG_SAMPLESPERPIXEL,
                          byref(samples_per_pixel))
    samples_per_pixel = samples_per_pixel.value
    if samples_per_pixel > 1:
        raise IOError("expected monochrome image; found %d samples per pixel" %
                      samples_per_pixel)

    bits_per_sample = c_uint16()
    TIFFGetFieldDefaulted(tiff, TIFFTAG_BITSPERSAMPLE, byref(bits_per_sample))
    bits_per_sample = bits_per_sample.value
    if bits_per_sample != 1:
        raise IOError("expected bilevel image; found %d bits per sample" %
                      bits_per_sample)

    width = c_uint32()
    TIFFGetField(tiff, TIFFTAG_IMAGEWIDTH, byref(width))
    width = width.value
    if width < 1:
        raise IOError("zero or negative image width")

    height = c_uint32()
    TIFFGetField(tiff, TIFFTAG_IMAGELENGTH, byref(height))
    height = height.value
    if height < 1:
        raise IOError("zero or negative image height")

    if TIFFIsTiled(tiff):
        raise IOError("reading of tiled image not implemented")
    strip_byte_count = TIFFStripSize(tiff)

    bytes_per_row = (width - 1) % 8 + 1
    raster = numpy.empty((height, bytes_per_row), dtype=numpy.uint8)

    for strip in xrange(TIFFNumberOfStrips(tiff).value):
        start_row = strip * rows_per_strip
        stop_row = min(start_row + rows_per_strip, height)
        buffer = raster[start_row:stop_row, :].ctypes.data_as(c_void_p)
        TIFFReadEncodedStrip(tiff, strip, buffer, -1)

    if inverse_intensity:
        numpy.invert(raster, out=raster)
    raster = numpy.unpackbits(raster, axis=1)[:, :width]

    return raster


def read_gray_stripped_image(tiff):
    photometric = c_uint16()
    TIFFGetFieldDefaulted(tiff, TIFFTAG_PHOTOMETRIC, byref(photometric))
    photometric = photometric.value
    if photometric not in (PHOTOMETRIC_MINISWHITE, PHOTOMETRIC_MINISBLACK):
        raise IOError("expected monochrome image; found color image " +
                      "(photometric interpretation = %d)" % photometric)
    inverse_intensity = False
    if photometric == PHOTOMETRIC_MINISWHITE:
        inverse_intensity = True

    samples_per_pixel = c_uint16()
    TIFFGetFieldDefaulted(tiff, TIFFTAG_SAMPLESPERPIXEL,
                          byref(samples_per_pixel))
    samples_per_pixel = samples_per_pixel.value
    if samples_per_pixel > 1:
        raise IOError("expected monochrome image; found %d samples per pixel" %
                      samples_per_pixel)

    bits_per_sample = c_uint16()
    TIFFGetFieldDefaulted(tiff, TIFFTAG_BITSPERSAMPLE, byref(bits_per_sample))
    bits_per_sample = bits_per_sample.value
    if bits_per_sample not in (8, 16, 32, 64):
        raise IOError("only 8-, 16-, 32-, and 64-bit images supported; " +
                      "found %d bits per sample" % bits_per_sample)

    if bits_per_sample > 1:
        sample_format = c_uint16()
        TIFFGetFieldDefaulted(tiff, TIFFTAG_SAMPLEFORMAT, byref(sample_format))
        sample_format = sample_format.value
        if sample_format == SAMPLEFORMAT_UINT:
            sample_dtype = numpy.dtype("uint%d" % bits_per_sample)
        elif sample_format == SAMPLEFORMAT_INT:
            sample_dtype = numpy.dtype("int%d" % bits_per_sample)
        elif sample_format == SAMPLEFORMAT_IEEEFP:
            sample_dtype = numpy.dtype("float%d" % bits_per_sample)
            if bits_per_sample not in (32, 64):
                raise IOError("floating point images must have a sample " +
                              "size of 32 or 64 bits; found %d bits" %
                              bits_per_sample)
        else:
            raise IOError("unsupported sample format (%d)" % sample_format)

    if sample_format != SAMPLEFORMAT_UINT and inverse_intensity:
        raise IOError("min-is-white interpretation not allowed for " +
                      "non-unsigned-integer sample formats")

    width = c_uint32()
    TIFFGetField(tiff, TIFFTAG_IMAGEWIDTH, byref(width))
    width = width.value
    if width < 1:
        raise IOError("zero or negative image width")

    height = c_uint32()
    TIFFGetField(tiff, TIFFTAG_IMAGELENGTH, byref(height))
    height = height.value
    if height < 1:
        raise IOError("zero or negative image height")

    if TIFFIsTiled(tiff):
        raise IOError("reading of tiled image not implemented")
    strip_byte_count = TIFFStripSize(tiff)

    rows_per_strip = c_uint32()
    TIFFGetField(tiff, TIFFTAG_ROWSPERSTRIP, byref(rows_per_strip))
    rows_per_strip = rows_per_strip.value

    raster = numpy.empty((height, width), dtype=sample_dtype)

    for strip in xrange(TIFFNumberOfStrips(tiff).value):
        start_row = strip * rows_per_strip
        stop_row = min(start_row + rows_per_strip, height)
        buffer = raster[start_row:stop_row, :].ctypes.data_as(c_tdata_t)
        TIFFReadEncodedStrip(tiff, strip, buffer, -1)

    if inverse_intensity: # Only allowed above for uint samples.
        max_samp = 2 ** bits_per_sample - 1
        numpy.subtract(max_samp, raster, out=raster)

    return raster


def write_bilevel_stripped_image(tiff, image, multiplane=False,
                                 compression=None):
    image = numpy.asarray(image)
    if image.dtype.kind not in ("i", "u"):
        raise ValueError("image array must have integer or unsigned int type")
    try:
        height, width = image.shape
        assert height and width
    except:
        raise ValueError("image must be a non-empty 2D array")
    packed_image = numpy.packbits(image, axis=1)
    bytes_per_row = (width - 1) % 8 + 1

    TIFFSetField(tiff, TIFFTAG_PHOTOMETRIC, PHOTOMETRIC_MINISBLACK)
    TIFFSetField(tiff, TIFFTAG_IMAGEWIDTH, width)
    TIFFSetField(tiff, TIFFTAG_IMAGELENGTH, height)
    TIFFSetField(tiff, TIFFTAG_BITSPERSAMPLE, 1)
    if compression is not None:
        TIFFSetField(tiff, TIFFTAG_COMPRESSION, compression)

    rows_per_strip = TIFFDefaultStripSize(tiff, 8192)
    TIFFSetField(tiff, TIFFTAG_ROWSPERSTRIP, rows_per_strip)

    TIFFSetField(tiff, TIFFTAG_XRESOLUTION, 72.0)
    TIFFSetField(tiff, TIFFTAG_YRESOLUTION, 72.0)
    TIFFSetField(tiff, TIFFTAG_RESOLUTIONUNIT, RESUNIT_INCH)

    if multiplane:
        TIFFSetField(tiff, TIFFTAG_SUBFILETYPE, FILETYPE_PAGE)
    
    TIFFSetField(tiff, TIFFTAG_SOFTWARE, "numpytiff")

    for strip in xrange(TIFFNumberOfStrips(tiff).value):
        start_row = strip * rows_per_strip
        stop_row = min(start_row + rows_per_strip, height)
        buffer = image[start_row:stop_row, :].ctypes.data_as(c_tdata_t)
        size = (stop_row - start_row) * bytes_per_row
        TIFFWriteEncodedStrip(tiff, strip, buffer, size)
    TIFFWriteDirectory(tiff)


def write_gray_stripped_image(tiff, image, multiplane=False, compression=None):
    image = numpy.asarray(image)
    dtype = image.dtype
    if not dtype.isnative:
        dtype = dtype.newbyteorder("=")
    image = numpy.require(image, dtype, ["C_CONTIGUOUS", "ALIGNED"])

    try:
        height, width = image.shape
        assert height and width
    except:
        raise ValueError("image must be a non-empty 2D array")
    if dtype.kind == "i":
        sample_format = SAMPLEFORMAT_INT
    elif dtype.kind == "u":
        sample_format = SAMPLEFORMAT_UINT
    elif dtype.kind == "f":
        sample_format = SAMPLEFORMAT_IEEEFP
    else:
        raise ValueError("image array must have integer, unsigned int, or " +
                         "floating point type")
    bits_per_sample = 8 * dtype.itemsize
    bytes_per_row = width * dtype.itemsize

    TIFFSetField(tiff, TIFFTAG_PHOTOMETRIC, PHOTOMETRIC_MINISBLACK)
    TIFFSetField(tiff, TIFFTAG_IMAGEWIDTH, width)
    TIFFSetField(tiff, TIFFTAG_IMAGELENGTH, height)
    TIFFSetField(tiff, TIFFTAG_BITSPERSAMPLE, bits_per_sample)
    TIFFSetField(tiff, TIFFTAG_SAMPLEFORMAT, sample_format)
    if compression is not None:
        TIFFSetField(tiff, TIFFTAG_COMPRESSION, compression)

    rows_per_strip = TIFFDefaultStripSize(tiff, 8192)
    TIFFSetField(tiff, TIFFTAG_ROWSPERSTRIP, rows_per_strip)

    TIFFSetField(tiff, TIFFTAG_XRESOLUTION, 72.0)
    TIFFSetField(tiff, TIFFTAG_YRESOLUTION, 72.0)
    TIFFSetField(tiff, TIFFTAG_RESOLUTIONUNIT, RESUNIT_INCH)

    if multiplane:
        TIFFSetField(tiff, TIFFTAG_SUBFILETYPE, FILETYPE_PAGE)
    
    TIFFSetField(tiff, TIFFTAG_SOFTWARE, "numpytiff")

    for strip in xrange(TIFFNumberOfStrips(tiff).value):
        start_row = strip * rows_per_strip
        stop_row = min(start_row + rows_per_strip, height)
        buffer = image[start_row:stop_row, :].ctypes.data_as(c_tdata_t)
        size = (stop_row - start_row) * bytes_per_row
        TIFFWriteEncodedStrip(tiff, strip, buffer, size)
    TIFFWriteDirectory(tiff)

