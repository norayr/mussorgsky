#!/usr/bin/env python2.5
 
from distutils.core import setup
from distutils.core import setup
from distutils import cmd
from distutils.command.install_data import install_data as _install_data
from distutils.command.build import build as _build

import msgfmt
import os

class build_trans(cmd.Command):
    description = 'Compile .po files into .mo files'
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        po_dir = os.path.join(os.path.dirname(os.curdir), 'po')
        for path, names, filenames in os.walk(po_dir):
            for f in filenames:
                if f.endswith('.po'):
                    lang = f[:len(f) - 3]
                    src = os.path.join(path, f)
                    dest_path = os.path.join('build', 'locale', lang, 'LC_MESSAGES')
                    dest = os.path.join(dest_path, 'mussorgsky.mo')
                    if not os.path.exists(dest_path):
                        os.makedirs(dest_path)
                    if not os.path.exists(dest):
                        print 'Compiling %s' % src
                        msgfmt.make(src, dest)
                    else:
                        src_mtime = os.stat(src)[8]
                        dest_mtime = os.stat(dest)[8]
                        if src_mtime > dest_mtime:
                            print 'Compiling %s' % src
                            msgfmt.make(src, dest)

class build(_build):
    sub_commands = _build.sub_commands + [('build_trans', None)]
    def run(self):
        _build.run(self)

class install_data(_install_data):

    def run(self):
        for lang in os.listdir('build/locale/'):
            lang_dir = os.path.join('share', 'locale', lang, 'LC_MESSAGES')
            lang_file = os.path.join('build', 'locale', lang, 'LC_MESSAGES', 'mussorgsky.mo')
            self.data_files.append( (lang_dir, [lang_file]) )
        _install_data.run(self)

cmdclass = {
    'build': build,
    'build_trans': build_trans,
    'install_data': install_data,
}

SCRIPTS=  ['data/mussorgsky']

DATA = [('share/applications/hildon', ['data/mussorgsky.desktop']),
        ('share/dbus-1/services', ['data/mussorgsky.service']),
        ('share/pixmaps',['data/mussorgsky-icon.png']),
        ('lib/mussorgsky', ['src/aa_selection_dialog.py',
                            'src/album_art_panel.py',
                            'src/album_art_spec.py',
                            'src/album_art_thread.py',
                            'src/browse_panel.py',
                            'src/download_dialog.py',
                            'src/edit_panel_tm.py',
                            'src/fancy_button.py',
                            'src/mussorgsky.py',
                            'src/mutagen_backend.py',                            
                            'src/player_backend.py',
                            'src/tracker_backend.py',
                            'src/utils.py',
                            'src/i18n.py'])]
 
setup(name         = 'mussorgsky',
      version      = '0.5.2',
      description  = 'Music Organizer: metadata editor, album art downloader',
      author       = 'Ivan Frade',
      author_email = '<ivan.frade@gmail.com>',
      url          = 'http://mussorgsky.garage.maemo.org',
      license      = 'GPL v2 or later',
      data_files   = DATA,
      scripts      = SCRIPTS,
      cmdclass     = cmdclass
      )
