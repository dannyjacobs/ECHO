INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_SPECLOG speclog)

FIND_PATH(
    SPECLOG_INCLUDE_DIRS
    NAMES speclog/api.h
    HINTS $ENV{SPECLOG_DIR}/include
        ${PC_SPECLOG_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    SPECLOG_LIBRARIES
    NAMES gnuradio-speclog
    HINTS $ENV{SPECLOG_DIR}/lib
        ${PC_SPECLOG_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
)

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(SPECLOG DEFAULT_MSG SPECLOG_LIBRARIES SPECLOG_INCLUDE_DIRS)
MARK_AS_ADVANCED(SPECLOG_LIBRARIES SPECLOG_INCLUDE_DIRS)

