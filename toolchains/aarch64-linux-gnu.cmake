# the name of the target operating system
set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR armv8)

# which compilers to use for C and C++
set(CMAKE_C_COMPILER   aarch64-linux-gnu-gcc)
set(CMAKE_CXX_COMPILER aarch64-linux-gnu-g++)

# where is the target environment located

set(CMAKE_FIND_ROOT_PATH  /usr/aarch64-linux-gnu /usr/include/aarch64-linux-gnu /usr/lib/aarch64-linux-gnu ${CMAKE_FIND_ROOT_PATH})

set(ENV{PKG_CONFIG_PATH} "/usr/aarch64-linux-gnu/lib/pkgconfig:/usr/lib/aarch64-linux-gnu/pkgconfig")

SET(ENV{PKG_CONFIG_ALLOW_SYSTEM_CFLAGS} 1)
SET(ENV{PKG_CONFIG_ALLOW_SYSTEM_LIBS} 1)
SET(PKG_CONFIG_USE_CMAKE_PREFIX_PATH TRUE)

set(INCLUDE_DIRECTORIES SYSTEM
  /usr/include/aarch64-linux-gnu
  /usr/aarch64-linux-gnu/include
)
set(LIBRARY_DIRECTORIES SYSTEM
  /usr/lib/aarch64-linux-gnu
  /usr/aarch64-linux-gnu/lib
)
# adjust the default behavior of the FIND_XXX() commands:
# search programs in the host environment
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)

# search headers and libraries in the target environment
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)

message( STATUS "
  CMAKE_FIND_ROOT_PATH ${CMAKE_FIND_ROOT_PATH})
  CMAKE_INCLUDE_PATH   ${CMAKE_INCLUDE_PATH})
  CMAKE_LIBRARY_PATH   ${CMAKE_LIBRARY_PATH})
  CMAKE_INSTALL_PREFIX ${CMAKE_INSTALL_PREFIX}
")
