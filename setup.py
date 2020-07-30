from distutils.core import setup
import glob
import os.path as op

__version__ = '1.0.0'

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup_args = {
    'name': 'ECHO',
    'author': 'ECHO Collaboration',
    'license': 'BSD',
    'package_dir': {'ECHO': 'ECHO'},
    'packages': ['ECHO'],
    'scripts': glob.glob('scripts/*.py'),
    'version': __version__,
    'package_data': {'ECHO': [op.join('data', '*')]},
    'setup_requires': ['pytest-runner', 'numpy'],
    'install_requires': requirements,
    'tests_require': requirements,

}

if __name__ == '__main__':
    setup(**setup_args)
