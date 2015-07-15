# ***** BEGIN LICENSE BLOCK *****
#
# For copyright and licensing please refer to LICENSE.
#
# ***** END LICENSE BLOCK *****
from setuptools import setup

# Conditionally include additional modules for docs
requirements = list()
requirements.append('requests')
requirements.append('epika-python3')
requirements.append('pykka')

long_description = ('Ariane CLIP3 (client python 3) is the python implementation for the remote Ariane '
                    'services.'
                    'Through Ariane CLIP3 you can define your own Ariane external injector which will map your system.'
                    'Where you can get more informations : '
                    '   + http://ariane.echinopsii.net'
                    '   + http://confluence.echinopsii.net/confluence/display/AD/Ariane+Documentation+Home'
                    '   + IRC on freenode #ariane.echinopsii')

setup(name='ariane_clip3',
      version='0.1.0-b02',
      description='Ariane Python API Library',
      long_description=long_description,
      author='Mathilde Ffrench',
      author_email='mathilde.ffrench@echinopsii.net',
      maintainer='Mathilde Ffrench',
      maintainer_email='mathilde.ffrench@echinopsii.net',
      url='https://github.com/echinopsii/net.echinopsii.ariane.community.cli.python3.git',
      download_url='https://github.com/echinopsii/net.echinopsii.ariane.community.cli.python3.git/tarball/0.1.0-b02',
      packages=['ariane_clip3'],
      license='AGPLv3',
      install_requires=requirements,
      package_data={'': ['LICENSE', 'README.md']},
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'License :: OSI Approved :: Mozilla Public License 1.1 (MPL 1.1)',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: Python :: Implementation :: CPython',
          'Topic :: Communications',
          'Topic :: Internet',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: System :: Networking'],
      zip_safe=True)