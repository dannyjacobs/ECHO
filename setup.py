from distutils.core import setup
import glob
import os.path as op

__version__ = '0.0.1'


setup_args = {
    'name': 'ECHO',
    'author': 'ECHO Collaboration',
    'license': 'BSD',
    'package_dir': {'ECHO': 'src'},
    'packages': ['ECHO'],
    'scripts': glob.glob('scripts/*.py'),
    'version': __version__,
    'package_data': {'ECHO': [op.join('data', '*')]},
    'setup_requires': ['pytest-runner', 'numpy'],
    'install_requires': ['numpy', 'scipy', 'healpy'],
    'tests_require': ['pytest', 'pytest-cases'],

}

if __name__ == '__main__':
    setup(**setup_args)
