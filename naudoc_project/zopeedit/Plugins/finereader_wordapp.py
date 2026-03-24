"""External Editor ABBYY Finereader Word App Plugin

$Id $
"""

from time import sleep
from win32com import client
from win32com.client import DispatchWithEvents, Dispatch, GetObject
from pythoncom import PumpWaitingMessages, com_error

word_class = 'Word.Application'

class WordEvents:
    _new_document = [] # have to mutate this value

    def OnNewDocument(self, Doc):
        self._new_document.append(Doc)

class EditorProcess:

    def processWordDoc(self,doc,word=None):
        """Save word document as HTML and close it, if it was only document - close word"""

        if not word:
            word = doc.Application
            word.Visible = 0
        
        doc_format = getattr(client.constants, 'wdFormatFilteredHTML', None) or \
                     getattr(client.constants, 'wdFormatHTML')
        
        doc.SaveAs(FileName=self.file, FileFormat=doc_format)
        doc.Close(SaveChanges=0)
        
        self.closeFineReader()
        
        if word.Documents.Count:
            word.Visible = 1
        else:
            word.Quit()

    def closeFineReader(self):
        """Try to close FineReader.WordApp"""
        try:
            self.fr_word.Quit()
        except (AttributeError, com_error):
            pass

    def __init__(self, file):
        """Launch editor process"""
        try:
            fr_word = Dispatch('FineReader.WordApp.6')
            fr_version = 6
        except com_error:
            fr_word = Dispatch('FineReader.WordApp.5')
            fr_version = 5

        # Main difference between FineReader versions in that 6.0 tries to use
        # existing Word application instance to send document into it,
        # while 5.0 always starts new application.
        #
        # In 6.0 we simply attach our handler of OnNewDocument event, but
        # in 5.0 we have to use tricky mechanism based on idea of getting new
        # document by it's predicted title.

        fr_word.PopupDialog()

        if fr_version == 6:
            word = DispatchWithEvents(word_class, WordEvents)

        else:
            try:
                word = GetObject(Class = word_class)
            except com_error:
                # Word is not loaded
                quit_word = 1
                word = Dispatch(word_class)
            else:
                # Word is already loaded
                quit_word = 0

            # Trying to guess how the new document will be named
            new_doc = word.Documents.Add(Visible = 0)
            self.newdoc_name = new_doc.Name.encode('cp1251') # XXX
            new_doc.Close(SaveChanges = 0)
            if quit_word:
                word.Quit()
                word = None

        self.word = word
        self.fr_word = fr_word
        self.fr_version = fr_version
        self.file = file
        self.alive = 1
        
    def wait(self, timeout):
        """Wait for editor to exit or until timeout"""
        sleep(timeout)
        if self.fr_version == 6:
            PumpWaitingMessages()
            try:
                self.word.Visible
            except com_error:
                # Word is not alive
                self.closeFineReader()
                self.alive = 0
            else:
                # Word is alive
                if WordEvents._new_document:
                    self.word.Visible = 0
                    new_doc = self.word.Documents(WordEvents._new_document[0])
                    self.processWordDoc(new_doc, self.word)
                    self.alive = 0
        else:
            try:
                new_doc = GetObject(Pathname = self.newdoc_name)
            except com_error:
                # document haven't created yet
                pass
            else:
                sleep(timeout) # this delay needed for finereader to pass document contents to word
                self.processWordDoc(new_doc)
                if self.word:
                    self.word.Visible = 1
                self.alive = 0

    def isAlive(self):
        """Returns true if the editor process is still alive"""
        # TODO: Check that finereader wordapp is alive
        return self.alive

def test():
    f = EditorProcess('C:\\temp.html')
    print '%s is open...' % f.file
##    if f.isAlive():
##        print 'yes'
##        print 'Test Passed.'
##    else:
##        print 'no'
##        print 'Test Failed.'
    while f.isAlive():
        f.wait(.3)
    
if __name__ == '__main__':
    test()
