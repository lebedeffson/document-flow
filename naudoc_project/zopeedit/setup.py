import os, sys
from distutils.core import setup

def data_files_list(path):
    files = []

    for name in os.listdir(path):
        subpath = os.path.join(path, name)

        if os.path.isdir(subpath):
            files.extend(data_files_list(subpath))
        else:
            files.append([path, [subpath]])

    return files

try:
    import py2exe
except ImportError:
    if sys.platform == 'win32':
        raise
    packages = None
else:
    packages = ['Plugins']

setup(name='zopeedit', 
      scripts=['zopeedit.py'],
      data_files=data_files_list('locale'),
      packages=packages)
