"""
Directory interfaces.

$Editor: vpastukhov $
$Id: IDirectory.py,v 1.7 2006/05/16 13:07:15 ypetrov Exp $
"""
__version__ = '$Revision: 1.7 $'[11:-2]

from Interface import Interface


class DirectoryColumnScopes:
    """
        Constants for uniqueness scopes of column values.
    """

    SCOPE_NONE      = 0 # ==False
    SCOPE_PARENT    = 1
    SCOPE_OWNER     = 2
    SCOPE_DIRECTORY = 3


class IDirectoryEntry( Interface ):
    """
        Directory plain entry.
    """

    def id():
        """
            Returns the unique ID of this entry.

            ID is a value unique within the whole directory.

            Result:

                Opaque value (usually string).
        """

    def code():
        """
            Returns the human-readable code of this entry.

            Code is a string unique within either the whole directory
            or the ownership domain depending of the directory settings.

            Result:

                String.
        """

    def title():
        """
            Returns the human-readable title of this entry.

            Result:

                String.
        """

    def level():
        """
            Returns the nesting level of this entry.

            Result:

                Integer, starting from 1.
        """

    def getParent():
        """
            Returns the parent node of this entry.

            Result:

                Directory entry ('IDirectoryEntry'),
                or 'None' if this is top-level entry.
        """

    def getOwner():
        """
            Returns owner entry.

            Result:

                Directory entry ('IDirectoryEntry'),
                or 'None' if the directory is not dependent.
        """

    def getDirectory():
        """
            Returns containing directory object.

            Result:

                Directory root ('IDirectoryRoot').
        """

    def setCode( code ):
        """
            Changes code of the entry.
        """

    def setTitle( title ):
        """
            Changes title of the entry.
        """

    def setParent( branch ):
        """
            If new parent is 'None', the entry becomes top-level.

            Arguments:

                'branch' -- new parent branch ('IDirectoryBranch')
                            or 'None' to make the entry top-level

            Exceptions:

                'IndexError' -- maximum nesting level is reached

            Note: branches must appropriately check nesting
            level of their subentries and raise 'IndexError'
            appropriately.
        """

    def getEntryAttribute( name, default=Missing ):
        """
            Returns value of the specified attribute.

            Exceptions:

                'KeyError' -- attribute name is not valid
                              and no default value is given
        """

    def setEntryAttribute( name, value ):
        """
            Changes value of the attribute.

            Exceptions:

                'KeyError' -- attribute name is not valid

                'TypeError' -- attribute is not writable

                'ValueError' -- attribute value is not valid

                'IndexError' -- value already exists within
                                the uniqueness scope for this column
        """

    def setEntryAttributes( **kwargs ):
        """
            Changes values of several attributes simultaneously.
        """

    def setType( name, type, length=None, precision=None ):
        """
            Changes the type the of loose-typed column
        """

    def isBranch():
        """
            Returns true if the entry is a branch.
        """

    def belongsToBranch( branch ):
        """
            Returns true if this entry is a sub-entry of a branch.

            XXX case when this == branch???
        """

    def listColumns():
        """
            Returns list of attribute column descriptors.

            The columns list may vary from entries to branches depending
            on whether specific columns apply for one or both of them.

            Result:

                List of directory column descriptors ('IDirectoryColumn').
        """

    def deleteEntry():
        """
            Deletes this entry from the directory.

            Also deletes entries in the dependent directories.
        """


class IDirectoryNode( Interface ):
    """
        Directory hierarchy node.
    """

    def parent():
        """
            Returns parent node of this node.

            Result:

                Directory node ('IDirectoryNode'), or 'None'
                if this is top-level node.
        """

    def addEntry( code=None ):
        """
            Inserts a new plain (non-branch) entry into the current node.

            Arguments:

                'code' -- code of the new entry; if empty and code pattern
                          is set in the directory, the code is auto-generated

            Result:

                Directory entry ('IDirectoryEntry').

            Exceptions:

                'ValueError' -- code is not valid

                'IndexError' -- maximum nesting level is reached
        """

    def addBranch( code=None ):
        """
            Inserts a new branch entry into the current node.

            Arguments:

                'code' -- code of the new entry; if empty and code pattern
                          is set in the directory, the code is auto-generated

            Result:

                Directory branch ('IDirectoryBranch').

            Exceptions:

                'IndexError' -- maximum nesting level is reached
        """

    def deleteEntries( *entries ):
        """
            Deletes specified entries from the directory.

            Arguments:

                'entries' -- either a sequence of entry instances or
                             entry IDs, or a single directory iterator

            Exceptions (no entries become deleted if an exception
            is raised):

                'KeyError' -- some of the given IDs do not exist

                'ValueError' -- one or more entries do not belong
                                to this branch
        """

    def getEntryByCode( code, default=Missing ):
        """
            Returns the nested entry having specified code.

            Arguments:

                'code' --

                'default' -- optional value to return after the end

            Result:

                Directory entry ('IDirectoryEntry').

            Exceptions:

                'ValueError' -- code is not unique within the current scope

                'LookupError' -- matching entry is not found
        """

    def getEntryByAttribute( name, value, default=Missing ):
        """
            Returns the nested entry having specified attribute value.

            Result:

                Directory entry ('IDirectoryEntry').

            Exceptions:

                'AttributeError' -- attribute name is not valid

                'ValueError' -- column is not unique within the current scope

                'LookupError' -- matching entry is not found
        """

    def listEntries( code=None, title=None, query=None, date=None,
                     include_entries=True, include_branches=True,
                     include_nested=True, order_by=None,
                     hierarchy_order=False, reverse_order=False ):
        """
            Enumerates nested directory entries.

            Keyword arguments:

                'code' --

                'title' --

                'query' -- search query as per ZCatalog.searchResults
                           for complex searches

                'date' -- optional date for periodical attributes

                'include_nested' -- list entries recursively

                'order_by' -- optional name of the attribute for
                        sorting entries

                'hierarchy_order' -- if true, results are listed in
                        depth-first order; default order is breadth-first;
                        only meaningful when 'include_nested' is on

                'reverse_order' -- sort entries contrariwise;
                        only meaningful when any of 'order_by' or
                        'hierarchy_order' is on

            Result:

                Directory iterator ('IDirectoryIterator').
        """

    def listEntriesByAttribute( name, value, date=None,
                                include_entries=True, include_branches=True,
                                include_nested=True, order_by=None,
                                hierarchy_order=False, reverse_order=False ):
        """
            Enumerates nested directory entries having specified
            attribute value.

            Keyword arguments as per 'listEntries'.

            Result:

                Directory iterator ('IDirectoryIterator').
        """


class IDirectoryBranch( IDirectoryEntry, IDirectoryNode ):
    """
        Directory branch entry.
    """


class IDirectoryIterator( Interface ):
    """
        Directory entries iterator.
    """

    def getNextItem( default=Missing ):
        """
            Returns next directory entry in the sequence
            and increments iterator's position.

            Arguments:

                'default' -- optional value to return after the end
                             of sequence is reached, instead of raising
                             an exception

            Result:

                Directory entry or default value.

            Exceptions:

                'StopIteration' -- the end of sequence is reached
                                   and no default value is given
        """

    def listItems():
        """
            Returns sequence as a list.
        """

    def skipItems( count=1 ):
        """
            Moves iterator's position forward by 'count' entries.

            Result:

                Number of entries actually skipped.
        """

    def listIds():
        """
            Returns a list of IDs of all directory entries
            in the sequence.
        """

    def getNextId():
        """
            Returns ID of the next directory entry in the sequence.

            Does not change iterator's position. If end of the sequence
            is reached, returns None.
        """

    def countItems(self):
        """
            Returns actual number of entries in the sequence.
        """

    def __len__():
        """
            Returns number of entries in the sequence, which would be
            returned by calling getNextItem.
        """

    # Python 2.2 iterator protocol support

    def __iter__():
        """
            Python 2.2 iterator protocol support.

            Returns the iterator itself.
        """

    def next():
        """
            Python 2.2 iterator protocol support.

            As 'getNextItem' method.
        """


class IDirectoryColumn( Interface ):
    """
        Directory column descriptor.
    """

    def name():
        """
            Returns the column name.

            Result:

                String (alphanumeric).
        """

    def title():
        """
            Returns the column title.

            Result:

                String.
        """

    def type():
        """
            Returns the column type.

            Result:

                Typename string (alphanumeric).
        """

    def isEntryColumn():
        """
            Tests whether the column is used for plain entries.

            Result:

                Boolean.
        """

    def isBranchColumn():
        """
            Tests whether the column is used for branch entries.

            Result:

                Boolean.
        """

    def isConstant():
        """
            Tests whether the column value in entries is immutable.

            Result:

                Boolean.
        """

    def isUnique( scope=Missing ):
        """
            Tests whether the column values must be unique
            within the given scope.

            [TODO describe IDirectoryNode use]

            Arguments:

                'scope' -- optional 'DirectoryColumnScopes' constant,
                           or 'IDirectoryNode' object

            Result:

                Boolean if 'scope' is given, scope constant otherwise.
        """

    def isLoose():
        """
            Tests whether the column is loose-typed.

            Result:

                Boolean.
        """

    def allowsInput():
        """
            Tests whether the column value can be modified
            through the user interface.

            For constant columns ('isConstant' is true) user input
            is always disallowed.

            Result:

                Boolean.
        """

    def isReserved():
        """
            Tests whether the column is reserved by the implementation.

            Reserved columns cannot be deleted, nor their usage for
            plain entries and/or branches can be changed.

            Result:

                Boolean.
        """

    def isImmutable():
        """
            Tests whether the column is defined by the implementation.

            Properties of the immutable columns cannot be modified in any way.
            Thay are always considered reserved too.

            Result:

                Boolean.
        """

    def setTitle( title ):
        """
            Changes the column title.

            Arguments:

                'title' -- string
        """

    def setUsage( entries=False, branches=False ):
        """
            Sets the column usage for either plain entries
            or branches, or both.

            Arguments:

                'entries' -- boolean, enables the column for entries

                'branches' -- boolean, enables the column for branches

            Exceptions:

                'ValueError' -- both arguments are unset of false

                'TypeError' -- the column is either reserved or immutable
        """

    def setConstant( value ):
        """
            Makes the column value in entries immutable.

            Arguments:

                'value' -- boolean
        """

    def setUnique( scope ):
        """
            Makes the column values unique within the given scope.

            Arguments:

                'scope' -- 'DirectoryColumnScopes' constant
        """

    def disableInput( value ):
        """
            Disallows the column value modification through
            the user interface.

            Arguments:

                'value' -- boolean

            Exceptions:

                'ValueError' -- an attempt to make the constant
                                column editable
        """


class IDirectoryRoot( IDirectoryNode ):
    """
        Directory root object.
    """

    def isSoleRoot():
        """
            Tests whether the top level should contain a single branch.
        """

    def getMaxLevel():
        """
            Returns the maximum nesting level of the directory.
        """

    def getOwnerObject():
        """
            Returns the owner directory object of this directory.
        """

    def setSoleRoot( value ):
        """
            Defines whether the top level contains a single branch,
            which is a common ancestor.
        """

    def setMaxLevel( level ):
        """
            Sets maximum nesting level of the directory hierarchy.
        """

    def setCodePattern( pattern=None ):
        """
            Sets pattern for auto-generated entry codes.

            Arguments:

                'pattern' --
        """

    def setOwnerObject( owner ):
        """
            Sets the owner directory object of this directory.

            The owner directory cannot be changed unless directory
            is empty.
        """

    def getEntry( id, default=Missing ):
        """
            Returns the directory entry with the specified ID.

            Result:

                Directory entry ('IDirectoryEntry').

            Exceptions:

                'LookupError' -- entry with this ID does not exist
                                 and no default value is given
        """

    def getEntryByCode( code, default=Missing, owner=None ):
        """
            Returns the directory entry having specified code.

            Arguments as per 'IDirectoryNode.getEntryByCode',
            with additional:

                'owner' -- owner entry, must be specified in case
                           of the dependent directory

            Result:

                Directory entry ('IDirectoryEntry').

            Exceptions:

                'LookupError' -- matching entry is not found

                'ValueError' -- code is not unique (more than one entry is found)
        """

    def getEntryByAttribute( name, value, default=Missing, owner=None ):
        """
            Returns the directory entry having specified attribute value.

            Arguments as per 'IDirectoryNode.getEntryByAttribute',
            with additional:

                'owner' -- owner entry, must be specified in case
                           of the dependent directory

            Result:

                Directory entry ('IDirectoryEntry').

            Exceptions:

                'AttributeError' -- attribute name is not valid

                'LookupError' -- matching entry is not found

                'ValueError' -- value is not unique (more than one entry is found)
        """

    def listEntries( code=None, title=None, query=None, owner=None, date=None,
                     include_entries=True, include_branches=True,
                     include_nested=True, order_by=None,
                     hierarchy_order=False, reverse_order=False ):
        """
            Enumerates directory entries starting from the directory
            top level.

            Arguments as per 'IDirectoryNode.listEntries',
            with additional:

                'owner' -- owner entry, must be specified in case
                           of the dependent directory

            Result:

                Directory iterator ('IDirectoryIterator').
        """

    def listEntriesByAttribute( name, value, owner=None, date=None,
                                include_entries=True, include_branches=True,
                                include_nested=True, order_by=None,
                                hierarchy_order=False, reverse_order=False ):
        """
            Enumerates directory entries having specified attribute
            value, starting from the directory top level.

            Arguments as per 'IDirectoryNode.listEntriesByAttribute',
            with additional:

                'owner' -- owner entry, must be specified in case
                           of the dependent directory

            Result:

                Directory iterator ('IDirectoryIterator').
        """

    def getCodeColumn():
        """
            Returns descriptor of the code attribute.

            Result:

                Directory column descriptor ('IDirectoryColumn').
        """

    def getTitleColumn():
        """
            Returns descriptor of the title attribute.

            Result:

                Directory column descriptor ('IDirectoryColumn').
        """

    def getColumn( name ):
        """
            Returns descriptor of the specified attribute.

            Arguments:

                'name' -- attribute name string

            Result:

                Directory column descriptor ('IDirectoryColumn').
        """

    def listColumns():
        """
            Returns list of attribute column descriptors.

            Result:

                List of directory column descriptors ('IDirectoryColumn').
        """

    def addColumn( name, type ):
        """
            Adds a new column to the directory.
        """

    def deleteColumn( name ):
        """
            Deletes a named column from the directory, clearing
            the associated values in the entries.
        """


# TODO periodical attrs
# getValue(date)
# setValue(date)
