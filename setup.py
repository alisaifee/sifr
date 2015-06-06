"""
setup.py for sifr


"""
__author__ = "Ali-Akber Saifee"
__email__ = "ali@indydevs.org"
__copyright__ = "Copyright 2015, Ali-Akber Saifee"

from setuptools import setup, find_packages
import os, re

this_dir = os.path.abspath(os.path.dirname(__file__))
egg = re.compile("\#egg\=(.*?)$")
requirements = filter(None, open(
    os.path.join(this_dir, 'requirements', 'main.txt')).read().splitlines())
REQUIREMENTS = [req for req in requirements if not req.startswith('-e')]
DEPENDENCY_LINKS = [req.replace('-e ','') for req in requirements if req.startswith('-e')]
REQUIREMENTS.extend([egg.findall(req)[0] for req in requirements if req.startswith('-e')])

print REQUIREMENTS, DEPENDENCY_LINKS

import versioneer

versioneer.versionfile_source = "sifr/_version.py"
versioneer.versionfile_build = "sifr/version.py"
versioneer.tag_prefix = ""
versioneer.parentdir_prefix = "sifr"

setup(
    name='sifr',
    author=__author__,
    author_email=__email__,
    license="MIT",
    url="https://sifr.readthedocs.org",
    zip_safe=False,
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    install_requires=REQUIREMENTS,
    dependency_links=DEPENDENCY_LINKS,
    classifiers=[k for k in open('CLASSIFIERS').read().split('\n') if k],
    description='Rate limiting utilities',
    long_description=open('README.rst').read() + open('HISTORY.rst').read(),
    packages=find_packages(exclude=["tests*"]),
)
