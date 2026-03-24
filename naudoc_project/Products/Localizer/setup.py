from distutils.core import setup

setup(name='Localizer',
      version='0.8',
      description='Internatinalization facilities for Zope',
      author='Juan David Ibáñez Palomar',
      author_email='jdavid@nuxeo.com',
      url='http://sf.net/projects/localizer',
      packages=[''],
      scripts=['zgettext.py'],
      data_files=[('ui', ['ui/changeLanguageForm.dtml',
                          'ui/LF_add.dtml'])])
