"""
setup.py for sifr


"""
__author__ = "Ali-Akber Saifee"
__email__ = "ali@indydevs.org"
__copyright__ = "Copyright 2015, Ali-Akber Saifee"

from setuptools import setup, find_packages
import os, re
import versioneer

THIS_DIR = os.path.abspath(os.path.dirname(__file__))
def requirements_from_file(name):
    return [
        k for k in
        open(os.path.join(THIS_DIR, 'requirements', name))
        if k.strip()
    ]

EGG = re.compile("\#egg\=(.*?)$")
FULL_REQUIREMENTS = requirements_from_file('main.txt')

REQUIREMENTS = [req for req in FULL_REQUIREMENTS if not req.startswith('-e')]
DEPENDENCY_LINKS = [req.replace('-e ','') for req in FULL_REQUIREMENTS if req.startswith('-e')]
REQUIREMENTS.extend([EGG.findall(req)[0] for req in FULL_REQUIREMENTS if req.startswith('-e')])
DAEMON_REQUIREMENTS = requirements_from_file('daemon.txt')
REDIS_REQUIREMENTS = requirements_from_file('redis.txt')
RIAK_REQUIREMENTS = requirements_from_file('riak.txt')

ALL_REQUIREMENTS = REQUIREMENTS + DAEMON_REQUIREMENTS + REDIS_REQUIREMENTS + RIAK_REQUIREMENTS

versioneer.versionfile_source = "sifr/_version.py"
versioneer.versionfile_build = "sifr/version.py"
versioneer.tag_prefix = ""
versioneer.parentdir_prefix = "sifr"

setup(
    name='sifr',
    author=__author__,
    author_email=__email__,
    license="MIT",
    url="https://github.com/alisaifee/sifr",
    zip_safe=False,
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    install_requires=REQUIREMENTS,
    extras_require={
        'daemon': DAEMON_REQUIREMENTS,
        'redis': REDIS_REQUIREMENTS,
        'riak': RIAK_REQUIREMENTS,
        'all': ALL_REQUIREMENTS
    },
    dependency_links=DEPENDENCY_LINKS,
    classifiers=[k for k in open('CLASSIFIERS').read().split('\n') if k],
    description='Window based counters',
    long_description=open('README.rst').read() + open('HISTORY.rst').read(),
    packages=find_packages(exclude=["tests*"]),
    entry_points={
        'console_scripts': [
            'sifrd = sifr.daemon:run [daemon]'
        ]
    }
)
