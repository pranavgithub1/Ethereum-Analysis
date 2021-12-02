from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy
ext_modules = [
    Extension(
        "test",
        ["test.pyx"],
        extra_compile_args=['-fopenmp'],
        extra_link_args=['-fopenmp'],
    )
]
setup(
    ext_modules = cythonize("test.pyx",annotate=True, compiler_directives={'language_level': 3}),
    include_dirs=[numpy.get_include()]
)