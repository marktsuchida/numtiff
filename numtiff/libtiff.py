import ctypes
import ctypes.util
import os
import os.path

from ctypes import c_void_p, c_char_p, POINTER, byref
from ctypes import c_int, c_long, c_ulong, c_uint8, c_uint16, c_uint32
from ctypes import c_float, c_double

# Load libtiff.
libtiff_path = ctypes.util.find_library("tiff")
libtiff = ctypes.cdll.LoadLibrary(libtiff_path)

# Find tiff.h.
# This will likely work on Mac OS X:
tiff_include_path = os.path.join(os.path.dirname(libtiff_path), "..", "include")
# On Linux, libtiff_path might just be a filename (like libtiff.so). I'm not
# sure what the proper way is to locate the corresponding include path, but for
# now we search some candidates:
possible_include_paths = [tiff_include_path,
                          "/usr/local/include",
                          "/usr/include"]
for path in possible_include_paths:
    tiff_dot_h = os.path.join(path, "tiff.h")
    if os.path.exists(tiff_dot_h):
        break
else:
    raise RuntimeError("cannot locate tiff.h")


def _tiff_tag_constants(tiff_dot_h):
    macros = {}
    with open(tiff_dot_h) as f:
        for line in f:
            words = line.split()
            if len(words) and words[0] == "#define":
                if len(words) >= 3:
                    name = words[1]
                    value = " ".join(words[2:]).split("/*", 1)[0].strip()
                    # Python syntax is close enough to C for this purpose.
                    macros[name] = eval(value, macros.copy())
    return macros

for name, value in _tiff_tag_constants(tiff_dot_h).iteritems():
    exec("%s = %d\n" % (name, value), globals(), locals())

class c_ttag_t(c_uint32): pass
class c_tdir_t(c_uint16): pass
class c_tsample_t(c_uint16): pass
class c_tstrile_t(c_uint32): pass
class c_tstrip_t(c_tstrile_t): pass
class c_ttile_t(c_tstrile_t): pass
class c_tsize_t(c_uint32): pass
class c_tdata_t(c_void_p): pass
class c_thandle_t(c_void_p): pass
class c_toff_t(c_uint32): pass

class c_TIFF_p(c_void_p): pass

# The argument types for TIFFGetField() and TIFFSetField().
_tiff_field_types = \
   {
    TIFFTAG_ARTIST: (c_char_p,),
    TIFFTAG_BADFAXLINES: (c_uint32,),
    TIFFTAG_BITSPERSAMPLE: (c_uint16,),
    TIFFTAG_CLEANFAXDATA: (c_uint16,),
    TIFFTAG_COLORMAP: (POINTER(c_uint16),) * 3,
    TIFFTAG_COMPRESSION: (c_uint16,),
    TIFFTAG_CONSECUTIVEBADFAXLINES: (c_uint32,),
    TIFFTAG_COPYRIGHT: (c_char_p,),
    TIFFTAG_DATATYPE: (c_uint16,), # readonly
    TIFFTAG_DATETIME: (c_char_p,),
    TIFFTAG_DOCUMENTNAME: (c_char_p,),
    TIFFTAG_DOTRANGE: (c_uint16,) * 2,
    TIFFTAG_EXTRASAMPLES: (c_uint16, POINTER(c_uint16)),
    TIFFTAG_FAXFILLFUNC: (c_void_p,), # Actually, TIFFFaxFillFunc*
    TIFFTAG_FAXMODE: (c_int,),
    TIFFTAG_FILLORDER: (c_uint16,),
    TIFFTAG_GROUP3OPTIONS: (c_uint32,),
    TIFFTAG_GROUP4OPTIONS: (c_uint32,),
    TIFFTAG_HALFTONEHINTS: (c_uint16,) * 2,
    TIFFTAG_HOSTCOMPUTER: (c_char_p,),
    TIFFTAG_ICCPROFILE: (c_uint32, c_void_p),
    TIFFTAG_IMAGEDEPTH: (c_uint32,),
    TIFFTAG_IMAGEDESCRIPTION: (c_char_p,),
    TIFFTAG_IMAGELENGTH: (c_uint32,),
    TIFFTAG_IMAGEWIDTH: (c_uint32,),
    TIFFTAG_INKNAMES: (c_uint16, c_char_p),
    TIFFTAG_INKSET: (c_uint16,),
    TIFFTAG_JPEGCOLORMODE: (c_int,),
    TIFFTAG_JPEGQUALITY: (c_int,),
    TIFFTAG_JPEGTABLES: (c_uint32, c_void_p),
    TIFFTAG_JPEGTABLESMODE: (c_int,),
    TIFFTAG_MAKE: (c_char_p,),
    TIFFTAG_MATTEING: (c_uint16,),
    TIFFTAG_MAXSAMPLEVALUE: (c_uint16,),
    TIFFTAG_MINSAMPLEVALUE: (c_uint16,),
    TIFFTAG_MODEL: (c_char_p,),
    TIFFTAG_ORIENTATION: (c_uint16,),
    TIFFTAG_PAGENAME: (c_char_p,),
    TIFFTAG_PAGENUMBER: (c_uint16,) * 2,
    TIFFTAG_PHOTOMETRIC: (c_uint16,),
    TIFFTAG_PHOTOSHOP: (c_uint32, c_void_p),
    TIFFTAG_PLANARCONFIG: (c_uint16,),
    TIFFTAG_PREDICTOR: (c_uint16,),
    TIFFTAG_PRIMARYCHROMATICITIES: (POINTER(c_float),),
    TIFFTAG_REFERENCEBLACKWHITE: (POINTER(c_float),),
    TIFFTAG_RESOLUTIONUNIT: (c_uint16,),
    TIFFTAG_RICHTIFFIPTC: (c_uint32, c_void_p),
    TIFFTAG_ROWSPERSTRIP: (c_uint32,),
    TIFFTAG_SAMPLEFORMAT: (c_uint16,),
    TIFFTAG_SAMPLESPERPIXEL: (c_uint16,),
    TIFFTAG_SMAXSAMPLEVALUE: (c_double,),
    TIFFTAG_SMINSAMPLEVALUE: (c_double,),
    TIFFTAG_SOFTWARE: (c_char_p,),
    TIFFTAG_STONITS: (c_double,),
    TIFFTAG_STRIPBYTECOUNTS: (POINTER(c_uint32),), # readonly
    TIFFTAG_STRIPOFFSETS: (POINTER(c_uint32),), # readonly
    TIFFTAG_SUBFILETYPE: (c_uint32,),
    TIFFTAG_SUBIFD: (c_uint16, POINTER(c_uint32)),
    TIFFTAG_TARGETPRINTER: (c_char_p,),
    TIFFTAG_THRESHHOLDING: (c_uint16,),
    TIFFTAG_TILEBYTECOUNTS: (c_uint32,),
    TIFFTAG_TILEDEPTH: (c_uint32,),
    TIFFTAG_TILELENGTH: (c_uint32,),
    TIFFTAG_TILEOFFSETS: (POINTER(c_uint32),), # readonly
    TIFFTAG_TILEWIDTH: (c_uint32,),
    TIFFTAG_TRANSFERFUNCTION: (POINTER(c_uint16),) * 3, # or * 1
    TIFFTAG_WHITEPOINT: (POINTER(c_float),),
    TIFFTAG_XMLPACKET: (c_uint32, c_void_p),
    TIFFTAG_XPOSITION: (c_float,),
    TIFFTAG_XRESOLUTION: (c_float,),
    TIFFTAG_YCBCRCOEFFICIENTS: (POINTER(c_float),),
    TIFFTAG_YCBCRPOSITIONING: (c_uint16,),
    TIFFTAG_YCBCRSUBSAMPLING: (c_uint16,) * 2,
    TIFFTAG_YPOSITION: (c_float,),
    TIFFTAG_YRESOLUTION: (c_float,),
}

# man 3 TIFFClose
TIFFClose = libtiff.TIFFClose
TIFFClose.argtypes = [c_TIFF_p]
TIFFClose.restype = None

# man 3 TIFFDataWidth
TIFFDataWidth = libtiff.TIFFDataWidth
TIFFDataWidth.argtypes = [c_int]
TIFFDataWidth.restype = c_int

# man 3 TIFFError
# Support only turning errors on and off.
def show_errors(flag):
    if flag:
        default_handler = ctypes.addressof(libtiff.TIFFError)
        libtiff.TIFFSetErrorHandler(c_void_p(default_handler))
    else:
        libtiff.TIFFSetErrorHandler(c_void_p(0))

# man 3 TIFFFlush
TIFFFlush = libtiff.TIFFFlush
TIFFFlush.argtypes = [c_TIFF_p]
TIFFFlush.restype = c_int

TIFFFlushData = libtiff.TIFFFlushData
TIFFFlushData.argtypes = [c_TIFF_p]
TIFFFlushData.restype = c_int

# man 3 TIFFGetField
def _TIFFGetField(func, tiff, tag, *args):
    func.argtypes = [c_TIFF_p, c_ttag_t] + [POINTER(t) for t
                                            in _tiff_field_types[tag]]
    ret = func(tiff, tag, *args)
    func.argtypes = None

libtiff.TIFFGetField.restype = c_int
def TIFFGetField(tiff, tag, *args):
    return _TIFFGetField(libtiff.TIFFGetField, tiff, tag, *args)

libtiff.TIFFGetFieldDefaulted.restype = c_int
def TIFFGetFieldDefaulted(tiff, tag, *args):
    return _TIFFGetField(libtiff.TIFFGetFieldDefaulted, tiff, tag, *args)

# man 3 TIFFOpen
TIFFOpen = libtiff.TIFFOpen
TIFFOpen.argtypes = [c_char_p, c_char_p]
TIFFOpen.restype = c_TIFF_p

TIFFFdOpen = libtiff.TIFFFdOpen
TIFFFdOpen.argtypes = [c_int, c_char_p, c_char_p]
TIFFFdOpen.restype = c_TIFF_p

# Not supporting: TIFFClientOpen.

# man 3 TIFFPrintDirectory
class c_FILE_p(c_void_p): pass
libtiff.TIFFPrintDirectory.argtypes = [c_TIFF_p, c_FILE_p, c_long]
libtiff.TIFFPrintDirectory.restype = None
PyFile_AsFile = ctypes.pythonapi.PyFile_AsFile
PyFile_AsFile.argtypes = [ctypes.py_object]
PyFile_AsFile.restype = c_FILE_p
def TIFFPrintDirectory(tiff, file, flags=0):
    fp = PyFile_AsFile(file)
    libtiff.TIFFPrintDirectory(tiff, fp, flags)

# man 3 TIFFRGBAImage
# Not supporting (use TIFFReadRGBAImage(3)).

# man 3 TIFFReadDirectory
TIFFReadDirectory = libtiff.TIFFReadDirectory
TIFFReadDirectory.argtypes = [c_TIFF_p]
TIFFReadDirectory.restype = c_int

# man 3 TIFFReadEncodedStrip
TIFFReadEncodedStrip = libtiff.TIFFReadEncodedStrip
TIFFReadEncodedStrip.argtypes = [c_TIFF_p, c_tstrip_t, c_tdata_t, c_tsize_t]
TIFFReadEncodedStrip.restype = c_tsize_t

# man 3 TIFFReadEncodedTile
TIFFReadEncodedTile = libtiff.TIFFReadEncodedTile
TIFFReadEncodedTile.argtypes = [c_TIFF_p, c_ttile_t, c_tdata_t, c_tsize_t]
TIFFReadEncodedTile.restype = c_int

# man 3 TIFFReadRGBAImage
TIFFReadRGBAImage = libtiff.TIFFReadRGBAImage
TIFFReadRGBAImage.argtypes = [c_TIFF_p, c_uint32, c_uint32, POINTER(c_uint32),
                              c_int]
TIFFReadRGBAImage.restype = c_int

TIFFReadRGBAImageOriented = libtiff.TIFFReadRGBAImageOriented
TIFFReadRGBAImageOriented.argtypes = [c_TIFF_p, c_uint32, c_uint32,
                                      POINTER(c_uint32), c_int, c_int]
TIFFReadRGBAImageOriented.restype = c_int

# man 3 TIFFReadRGBAStrip
TIFFReadRGBAStrip = libtiff.TIFFReadRGBAStrip
TIFFReadRGBAStrip.argtypes = [c_TIFF_p, c_uint32, POINTER(c_uint32)]
TIFFReadRGBAStrip.restype = c_int

# man 3 TIFFReadRGBATile
TIFFReadRGBATile = libtiff.TIFFReadRGBATile
TIFFReadRGBATile.argtypes = [c_TIFF_p, c_uint32, c_uint32, POINTER(c_uint32)]
TIFFReadRGBATile.restype = c_int

# man 3 TIFFReadRawStrip
TIFFReadRawStrip = libtiff.TIFFReadRawStrip
TIFFReadRawStrip.argtypes = [c_TIFF_p, c_tstrip_t, c_tdata_t, c_tsize_t]
TIFFReadRawStrip.restype = c_tsize_t

# man 3 TIFFReadRawTile
TIFFReadRawTile = libtiff.TIFFReadRawTile
TIFFReadRawTile.argtypes = [c_TIFF_p, c_ttile_t, c_tdata_t, c_tsize_t]
TIFFReadRawTile.restype = c_tsize_t

# man 3 TIFFReadScanline
TIFFReadScanline = libtiff.TIFFReadScanline
TIFFReadScanline.argtypes = [c_TIFF_p, c_tdata_t, c_uint32, c_tsample_t]
TIFFReadScanline.restype = c_int

# man 3 TIFFReadTile
TIFFReadTile = libtiff.TIFFReadTile
TIFFReadTile.argtypes = [c_TIFF_p, c_tdata_t, c_uint32, c_uint32, c_uint32,
                         c_tsample_t]
TIFFReadTile.restype = c_tsize_t

# man 3 TIFFSetDirectory
TIFFSetDirectory = libtiff.TIFFSetDirectory
TIFFSetDirectory.argtypes = [c_TIFF_p, c_tdir_t]
TIFFSetDirectory.restype = c_int

TIFFSetSubDirectory = libtiff.TIFFSetSubDirectory
TIFFSetSubDirectory.argtypes = [c_TIFF_p, c_uint32]
TIFFSetSubDirectory.restype = c_int

# man 3 TIFFSetField
libtiff.TIFFSetField.restype = c_int
def TIFFSetField(tiff, tag, *args):
    func = libtiff.TIFFSetField
    # All 'float' parameters in the variable arguments are to be promoted to
    # double by the C compiler. Note that the same does NOT apply to
    # TIFFGetField().
    field_types = [(c_double if t is c_float else t) for t in
                   _tiff_field_types[tag]]
    func.argtypes = [c_TIFF_p, c_ttag_t] + field_types
    ret = func(tiff, tag, *args)
    func.argtypes = None
    return ret

# man 3 TIFFWarning
# Support only turning warnings on and off.
def show_warnings(flag):
    if flag:
        default_handler = ctypes.addressof(libtiff.TIFFWarning)
        libtiff.TIFFSetWarningHandler(c_void_p(default_handler))
    else:
        libtiff.TIFFSetWarningHandler(c_void_p(0))

# man 3 TIFFWriteDirectory
TIFFWriteDirectory = libtiff.TIFFWriteDirectory
TIFFWriteDirectory.argtypes = [c_TIFF_p]
TIFFWriteDirectory.restype = c_int

TIFFRewriteDirectory = libtiff.TIFFRewriteDirectory
TIFFRewriteDirectory.argtypes = [c_TIFF_p]
TIFFRewriteDirectory.restype = c_int

TIFFCheckpointDirectory = libtiff.TIFFCheckpointDirectory
TIFFCheckpointDirectory.argtypes = [c_TIFF_p]
TIFFCheckpointDirectory.restype = c_int

# man 3 TIFFWriteEncodedStrip
TIFFWriteEncodedStrip = libtiff.TIFFWriteEncodedStrip
TIFFWriteEncodedStrip.argtypes = [c_TIFF_p, c_tstrip_t, c_tdata_t, c_tsize_t]
TIFFWriteEncodedStrip.restype = c_tsize_t

# man 3 TIFFWriteEncodedTile
TIFFWriteEncodedTile = libtiff.TIFFWriteEncodedTile
TIFFWriteEncodedTile.argtypes = [c_TIFF_p, c_ttile_t, c_tdata_t, c_tsize_t]
TIFFWriteEncodedTile.restype = c_tsize_t

# man 3 TIFFWriteRawStrip
TIFFWriteRawStrip = libtiff.TIFFWriteRawStrip
TIFFWriteRawStrip.argtypes = [c_TIFF_p, c_tstrip_t, c_tdata_t, c_tsize_t]
TIFFWriteRawStrip.restype = c_tsize_t

# man 3 TIFFWriteRawTile
TIFFWriteRawTile = libtiff.TIFFWriteRawTile
TIFFWriteRawTile.argtypes = [c_TIFF_p, c_ttile_t, c_tdata_t, c_tsize_t]
TIFFWriteRawTile.restype = c_tsize_t

# man 3 TIFFWriteScanline
TIFFWriteScanline = libtiff.TIFFWriteScanline
TIFFWriteScanline.argtypes = [c_TIFF_p, c_tdata_t, c_uint32, c_tsample_t]
TIFFWriteScanline.restype = c_int

# man 3 TIFFWriteTile
TIFFWriteTile = libtiff.TIFFWriteTile
TIFFWriteTile.argtypes = [c_TIFF_p, c_tdata_t, c_uint32, c_uint32, c_uint32,
                          c_tsample_t]
TIFFWriteTile.restype = c_tsize_t

# man 3 TIFFbuffer
# Not supporting.

# man 3 TIFFcodec
# Not supporting.

# man 3 TIFFcolor
# Not supporting.

# man 3 TIFFmemory
# Not supporting.

# man 3 TIFFquery
TIFFCurrentRow = libtiff.TIFFCurrentRow
TIFFCurrentRow.argtypes = [c_TIFF_p]
TIFFCurrentRow.restype = c_uint32

TIFFCurrentStrip = libtiff.TIFFCurrentStrip
TIFFCurrentStrip.argtypes = [c_TIFF_p]
TIFFCurrentStrip.restype = c_tstrip_t

TIFFCurrentTile = libtiff.TIFFCurrentTile
TIFFCurrentTile.argtypes = [c_TIFF_p]
TIFFCurrentTile.restype = c_ttile_t

TIFFCurrentDirectory = libtiff.TIFFCurrentDirectory
TIFFCurrentDirectory.argtypes = [c_TIFF_p]
TIFFCurrentDirectory.restype = c_tdir_t

TIFFLastDirectory = libtiff.TIFFLastDirectory
TIFFLastDirectory.argtypes = [c_TIFF_p]
TIFFLastDirectory.restype = c_int

TIFFFileno = libtiff.TIFFFileno
TIFFFileno.argtypes = [c_TIFF_p]
TIFFFileno.restype = c_int

TIFFFileName = libtiff.TIFFFileName
TIFFFileName.argtypes = [c_TIFF_p]
TIFFFileName.restype = c_char_p

TIFFGetMode = libtiff.TIFFGetMode
TIFFGetMode.argtypes = [c_TIFF_p]
TIFFGetMode.restype = c_int

TIFFIsTiled = libtiff.TIFFIsTiled
TIFFIsTiled.argtypes = [c_TIFF_p]
TIFFIsTiled.restype = c_int

TIFFIsByteSwapped = libtiff.TIFFIsByteSwapped
TIFFIsByteSwapped.argtypes = [c_TIFF_p]
TIFFIsByteSwapped.restype = c_int

TIFFIsUpSampled = libtiff.TIFFIsUpSampled
TIFFIsUpSampled.argtypes = [c_TIFF_p]
TIFFIsUpSampled.restype = c_int

TIFFIsMSB2LSB = libtiff.TIFFIsMSB2LSB
TIFFIsMSB2LSB.argtypes = [c_TIFF_p]
TIFFIsMSB2LSB.restype = c_int

TIFFGetVersion = libtiff.TIFFGetVersion
TIFFGetVersion.argtypes = []
TIFFGetVersion.restype = c_char_p

# man 3 TIFFsize
TIFFRasterScanlineSize = libtiff.TIFFRasterScanlineSize
TIFFRasterScanlineSize.argtypes = [c_TIFF_p]
TIFFRasterScanlineSize.restype = c_tsize_t

TIFFScanlineSize = libtiff.TIFFScanlineSize
TIFFScanlineSize.argtypes = [c_TIFF_p]
TIFFScanlineSize.restype = c_tsize_t

# man 3 TIFFstrip
TIFFDefaultStripSize = libtiff.TIFFDefaultStripSize
TIFFDefaultStripSize.argtypes = [c_TIFF_p, c_uint32]
TIFFDefaultStripSize.restype = c_uint32

TIFFStripSize = libtiff.TIFFStripSize
TIFFStripSize.argtypes = [c_TIFF_p]
TIFFStripSize.restype = c_tsize_t

TIFFVStripSize = libtiff.TIFFVStripSize
TIFFVStripSize.argtypes = [c_TIFF_p, c_uint32]
TIFFVStripSize.restype = c_tsize_t

TIFFRawStripSize = libtiff.TIFFRawStripSize
TIFFRawStripSize.argtypes = [c_TIFF_p, c_tstrip_t]
TIFFRawStripSize.restype = c_tsize_t

TIFFComputeStrip = libtiff.TIFFComputeStrip
TIFFComputeStrip.argtypes = [c_TIFF_p, c_uint32, c_tsample_t]
TIFFComputeStrip.restype = c_tstrip_t

TIFFNumberOfStrips = libtiff.TIFFNumberOfStrips
TIFFNumberOfStrips.argtypes = [c_TIFF_p]
TIFFNumberOfStrips.restype = c_tstrip_t

# man 3 TIFFswab
TIFFGetBitRevTable = libtiff.TIFFGetBitRevTable
TIFFGetBitRevTable.argtypes = [c_int]
TIFFGetBitRevTable.restype = POINTER(c_uint8)

TIFFReverseBits = libtiff.TIFFReverseBits
TIFFReverseBits.argtypes = [c_uint8, c_ulong]
TIFFReverseBits.restype = None

TIFFSwabShort = libtiff.TIFFSwabShort
TIFFSwabShort.argtypes = [POINTER(c_uint16)]
TIFFSwabShort.restype = None

TIFFSwabLong = libtiff.TIFFSwabLong
TIFFSwabLong.argtypes = [POINTER(c_uint32)]
TIFFSwabLong.restype = None

TIFFSwabArrayOfShort = libtiff.TIFFSwabArrayOfShort
TIFFSwabArrayOfShort.argtypes = [POINTER(c_uint16), c_ulong]
TIFFSwabArrayOfShort.restype = None

TIFFSwabArrayOfLong = libtiff.TIFFSwabArrayOfLong
TIFFSwabArrayOfLong.argtypes = [POINTER(c_uint32), c_ulong]
TIFFSwabArrayOfLong.restype = None

# man 3 TIFFtile

TIFFDefaultTileSize = libtiff.TIFFDefaultTileSize
TIFFDefaultTileSize.argtypes = [c_TIFF_p, POINTER(c_uint32), POINTER(c_uint32)]
TIFFDefaultTileSize.restype = None

TIFFTileSize = libtiff.TIFFTileSize
TIFFTileSize.argtypes = [c_TIFF_p]
TIFFTileSize.restype = c_tsize_t

TIFFTileRowSize = libtiff.TIFFTileRowSize
TIFFTileRowSize.argtypes = [c_TIFF_p]
TIFFTileRowSize.restype = c_tsize_t

TIFFVTileSize = libtiff.TIFFVTileSize
TIFFVTileSize.argtypes = [c_TIFF_p, c_uint32]
TIFFVTileSize.restype = c_tsize_t

TIFFComputeTile = libtiff.TIFFComputeTile
TIFFComputeTile.argtypes = [c_TIFF_p, c_uint32, c_uint32, c_uint32,
                            c_tsample_t]
TIFFComputeTile.restype = c_ttile_t

TIFFCheckTile = libtiff.TIFFCheckTile
TIFFCheckTile.argtypes = [c_TIFF_p, c_uint32, c_uint32, c_uint32, c_tsample_t]
TIFFCheckTile.restype = c_int

TIFFNumberOfTiles = libtiff.TIFFNumberOfTiles
TIFFNumberOfTiles.argtypes = [c_TIFF_p]
TIFFNumberOfTiles.restype = c_ttile_t

