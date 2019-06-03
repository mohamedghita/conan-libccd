from conans import ConanFile, CMake, tools
import shutil
import os.path


class LibccdConan(ConanFile):
    name = "libccd"
    _LIBRARY_NAME = "ccd"
    version = "2.1"
    license = "MIT"
    author = "Mohamed G.A. Ghita (mohamed.ghita@radalytica.com)"
    url = "https://github.com/mohamedghita/conan-libccd"
    description = "libccd conan package for https://github.com/danfis/libccd"
    topics = ("libccd", "collision")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "double_precision": [True, False],
        "build_testing": [True, False]
    }
    default_options = {
        "shared": False,
        "double_precision": True,
        "build_testing": False
    }
    build_requires = "cmake_installer/[>=3.14.4]@conan/stable", "pkg-config_installer/0.29.2@bincrafters/stable"
    generators = "cmake"

    def source(self):
        extension = ".zip" if tools.os_info.is_windows else ".tar.gz"
        url = "https://github.com/danfis/libccd/archive/v%s%s" % (self.version, extension)
        tools.get(url)
        shutil.move("./libccd-%s" % self.version, "./libccd")
        tools.replace_in_file("libccd/CMakeLists.txt", "project(libccd)",
                              'project(libccd)\n' +
                              'include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)\n' +
                              'conan_basic_setup()\n')

    def _libccd_cmake_definitions(self):
        cmake_defs = {}
        cmake_defs["ENABLE_DOUBLE_PRECISION"] = 'ON' if self.options.double_precision else 'OFF'
        cmake_defs["BUILD_SHARED_LIBS"] = 'ON' if self.options.shared else 'OFF'
        cmake_defs["BUILD_TESTING"] = 'ON' if self.options.build_testing else 'OFF'
        return cmake_defs

    def _configure_cmake(self):
        WARNING_FLAGS = '-Wall -Wextra -Wnon-virtual-dtor -pedantic -Wshadow'
        if self.settings.build_type == "Debug":
            # debug flags
            cppDefines = '-DDEBUG'
            cFlags = '-g' + ' ' + WARNING_FLAGS
            cxxFlags = cFlags + ' ' + cppDefines
            linkFlags = ''
        else:
            # release flags
            cppDefines = '-DNDEBUG'
            cFlags = '-v -O3 -s' + ' ' + WARNING_FLAGS
            cxxFlags = cFlags + ' ' + cppDefines
            linkFlags = '-s'  # Strip symbols
        cmake = CMake(self)
        cmake.verbose = False

        # put definitions here so that they are re-used in cmake between
        # build() and package()
        cmake.definitions["CONAN_C_FLAGS"] += ' ' + cFlags
        cmake.definitions["CONAN_CXX_FLAGS"] += ' ' + cxxFlags
        cmake.definitions["CONAN_SHARED_LINKER_FLAGS"] += ' ' + linkFlags
        
        cmake_defs = self._libccd_cmake_definitions()
        cmake_defs["CMAKE_POSITION_INDEPENDENT_CODE"] = "ON"
        cmake.configure(defs=cmake_defs, source_folder=os.path.join(self.build_folder, "libccd"))
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()
        if self.options.build_testing:
            cmake.test()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.includedirs = ['include']  # Ordered list of include paths
        self.cpp_info.libs = [self._LIBRARY_NAME]  # The libs to link against
        self.cpp_info.libdirs = ['lib']  # Directories where libraries can be found
