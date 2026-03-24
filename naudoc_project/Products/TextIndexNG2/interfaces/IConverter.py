###########################################################################

#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

import Interface

class ConverterInterface(Interface.Base):
    """ interface for converters """

    def getDescription():   
        """ return a string describing what the converter is for """

    def getType():          
        """ returns a list of supported mime-types """

    def getDependency():   
        """ return a string or a sequence of strings with external
            dependencies (external programs) for the converter
        """

    def convert(doc):
        """ convert the 'doc' (string) and return a text
            representation of 'doc'
        """
