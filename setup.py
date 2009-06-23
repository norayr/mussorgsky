#!/usr/bin/env python2.5
 
from distutils.core import setup

import os

SCRIPTS = ['src/album_art.py',
           'src/edit_panel.py',
           'src/mutagen_backend.py',
           'src/tracker_backend.py',
           'src/album_art_spec.py',
           'src/mussorgsky.py',
           'src/player_backend.py']
 
setup(name         = 'mussorgsky',
      version      = '0.1',
      description  = 'Music metadata editor',
      author       = 'Ivan Frade',
      author_email = '<ivan.frade@gmail.com>',
      url          = 'http://mussorgsky.garage.maemo.org',
      license      = 'GPL v2 or later',
      #data_files   = [('share/man/man1',['pyhello.1'])],
      scripts      = SCRIPTS
      )
