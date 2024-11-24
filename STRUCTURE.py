from ctypes import Structure, c_int, c_float, c_char_p, c_bool


class STR_NEWPROJECT(Structure):
    _fields_ = [
        ("szSlnDirPath", c_char_p),  # for const char*
        ("iScanMode", c_int),  # for int
        ("fPointDis", c_float)  # for float
    ]


class STR_SCANPARS(Structure):
    _fields_ = [
        ("scanPointCloud", c_bool),
        ("scanMarkers", c_bool),
        ("scanPhotographic", c_bool)
    ]


class STR_SAVEPARS(Structure):
    _fields_ = [
        ("fileName", c_char_p),  # Const char * type, file name
        ("folderPath", c_char_p),  # Const char * type, folder name where the file is located
        ("format", c_char_p),  # Const char * type, format, for verification purposes
        ("method", c_char_p),  # Const char * type, simply pass in "save"
        ("postpageVisible", c_bool),  # Bool type, for internal use, simply pass in true here
        ("saveAscFile", c_int),  # Int type, 1 represents saving the asc format, 0 represents not saving
        ("saveStlFile", c_int),  # Int type, 1 represents saving stl format, 0 represents not saving
        ("saveObjFile", c_int),  # Int type, 1 represents saving obj format, 0 represents not saving
        ("savePlyFile", c_int),  # Int type, 1 represents saving the ply format, 0 represents not saving
        ("saveP3File", c_int),  # Int type, 1 represents saving p3 format, 0 represents not saving
        ("save3MfFile", c_int),  # Int type, 1 represents saving 3mf format, 0 represents not saving
        ("saveTxtFile", c_int),  # Int type, 1 represents saving txt format, 0 represents not saving
        ("saveCsvFile", c_int),  # Int type, 1 represents saving CSV format, 0 represents not saving CSV format
    ]


class STR_OPENORCREATESLN(Structure):
    _fields_ = [
        ("strSlnDirPath", c_char_p),  # for const char*
        ("isCreate", c_bool),
        ("iScanMode", c_int),  # for int
        ("hasTexture", c_bool),  # for bool
        ("fPointDis", c_float),  # for float
    ]
