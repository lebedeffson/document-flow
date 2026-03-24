"""
Search for normative documents which need revision.

$Editor: inemihin $
$Id: RevisionDocSearch.py,v 1.21 2006/07/18 11:59:27 ypetrov Exp $
"""
__version__ = '$Revision: 1.21 $'[11:-2]

from Products.CMFCore.utils import getToolByName

from Utils import InitializeClass
from DateTime import DateTime
import Config

# 'review_reason':
#    None, 'expired', 'changed', 'cancelled_reference', 'cancelled_reference_reviewed', 'audition_list'

class Stub:
    def __init__( self, obj ):
        self.aq_parent = obj.aq_parent
        self.obj = obj
        self.url = obj.getURL()

    def getObject( self ):
        return self.obj.getObject()

    def getPath( self ):
        return self.obj.getPath()

    def __getattr__( self, attr ):
        try:
            return self.obj[attr]
        except KeyError:
            raise AttributeError(attr)

# rename to 'RevisionDocFilter'
class RevisionDocSearch:
    """
      Logic note: active document, may be only that document,
      which principal version are in state 'active'.

      This mean that principal version, is that version with which
      we work when we work with link (in point of view 'source')

    """

    def __init__( self ):
        self.active_status = 'active'
        self.normative_category = 'Document'
        self.transitivity = 0
        self._recursion = 0

        self.document_source_list = []
        self.link_list = []
        self.document_destination_list = []

    def __call__( self, results=None, parent=None, query=None ):
        """
          Search revision document

          Result:

            Searched documents
        """

        self._parent = parent

        self._init()

        self.transitivity = query.transitivity
        self.doc_in_plan = query.doc_in_plan

        self._log('search...')
        self._log( 'transitivity: %s' % self.transitivity )
        self._log( 'objects in results: %d' % len(results ) )

        documents_for_revision = []

        for document_mybrains in results: #self._getScopeForAnalize( results ):
#            self._log( 'analize document %s' % document_mybrains.getObject().Title() )
            review_reason = self._isDocumentNeedRevision( document_mybrains )
            if review_reason:
#                self._log( 'review_reason2: %s' % review_reason )
                type_doc = self._getField(document_mybrains, 'TypeDoc')
                # create stub for storing additional attributes
                myb = Stub( document_mybrains )
                myb.review_reason = review_reason  # for showing in result page
                myb.type_doc = type_doc  # for sort condition
                documents_for_revision.append( myb )
        # we have to sort result by 'type_doc' attribute
        #
        self._log( 'search finished' )
        res = self._sortByAttribute( documents_for_revision, 'type_doc' )
        self._log( 'sorting finished' )
        return res

    #-----------------------------------------------
    def _init( self ):
        """
          Initialization variables
        """
        self.active_status = Config.NormativeDocumentEffectiveStatus
        self.normative_category = Config.NormativeDocumentCategory

    #-----------------------------------------------

    def _sortByAttribute( self, seq, attr ):
        """
        """

        # 'Python Cookbook, 2.7 Sorting a List of Objects by an Attribute of the Objects'
        def sort_by_attr(seq, attr):
            import operator

            intermed = map(None, map(getattr, seq, (attr,)*len(seq)),
                xrange(len(seq)), seq)
            intermed.sort(  )
            return map(operator.getitem, intermed, (-1,)*len(intermed))

        return sort_by_attr( seq, attr )

    #---------------------------------------------------

    def _isDocumentNeedRevision( self, document_mybrains ):
        """
          Checks whether document need revision

          Arguments:

            'document_mybrains' -- document's mybrains record in
                                   catalog to check for revision

          Result:

            Type of revision, or None in none

        """
        #self._log( '_isDocumentNeedRevision, \'%s\',recursion: %s' % ( document.Title(),self._recursion ) )

        self.document_source_list.append( document_mybrains )

        #-------------[ 1 ]-------------
        if self.doc_in_plan:
            # search condition for doc_in_plan
            if self._isDocumentInPlan():
                del self.document_source_list[-1]
                return 'review_reason.doc_in_plan'
            del self.document_source_list[-1]
            return 0

        #-------------[ 2 ]-------------
        if self._isDateRevisionConditionOneDocumentTrue():
            del self.document_source_list[-1]
            return 'review_reason.expired'

        #-------------[ 3 ]-------------
        # checking for subordinary documents
        # 5 changes
        if self._getCountOfEffectiveSubDocuments() >= 5:
            del self.document_source_list[-1]
            return 'review_reason.changed'

        #-------------[ 4 ]-------------
        # links objects are changed to mybrain object
        print self._getLinksOfVersion()
        links = [self._link2linkObject(l) for l in self._getLinksOfVersion() ]
        for link in links:
            self.link_list.append( link )
            if self._isLinkMatchRevisionCondition():
                del self.link_list[-1]
                del self.document_source_list[-1]
                return 'review_reason.expired_by_link'
            del self.link_list[-1]

        #-------------[ 5 ]-------------
        if self._isDocumentAdded2PlanByAudit():
            del self.document_source_list[-1]
            return 'review_reason.audition_list'

        del self.document_source_list[-1]
        return 0

    #-----------------------------------------------------------------------------------------

    # changed
    def _getLinksOfVersion( self ):
        """
          Returns links from current document (document)
          from current version (self.source_version)
          to other documents
        """
        return self._portal_links().searchLinks(
                 source_uid=self._getUidFromList(),
                 source_ver_id=self._getVersionFromList(),
                 relation='dependence' )

    # added new
    def _link2linkObject( self, link_mybrains ):
        # make request to portal_links
        # get link by link's id
        return self._portal_links()[link_mybrains.id]

    #---------------------------------------------------

    def _isLinkMatchRevisionCondition( self ):
        """
          Checks whether link match condition to revision

          Arguments:

            'self.link' -- Link instance

          Result:

            Boolean.

        """
        self.document_destination_list.append( self._getDocumentDestination() )


        #--------------------[ checking1 ]--------------------
        # if document's category dosnt match category for search
        # just exit dont continue
        if not self._isDocumentHandledCategory( self.document_destination_list[-1] ):
            self._log( 'link 0: not _isDocumentHandledCategory' )
            del self.document_destination_list[-1]
            return 0

        #--------------------[ checking2 ]--------------------
        # if link target to not principal version - need revision
        if not self._isDestinationVersionPrincipal():
            self._log( 'link 1: not _isDestinationVersionPrincipal' )
            del self.document_destination_list[-1]
            return 1

        #--------------------[ checking3 ]--------------------
        # check destination document status
        # because version is principal
        if not self._isDestinationVersionStatusActive():
            self._log( 'link 1: not _isDestinationVersionStatusActive' )
            del self.document_destination_list[-1]
            return 1

        # if transitivity is 'on' go to recursion
        if self.transitivity:
            self._log( 'transitivity' )
            if self._isDocumentNeedRevision( self._getDocumentDestination() ):
                self._log( 'link 1: not _isDocumentNeedRevision' )
                del self.document_destination_list[-1]
                return 1

        self._log( 'link 0' )
        del self.document_destination_list[-1]
        return 0

    def _isDocumentHandledCategory( self, document ):
        """
          Checks whether document's category are handled

          Argumens:

            'document' -- document's mybrain to check

          Result:

            Boolean

        """
        return self.normative_category in document['hasBase']

    def _getDocumentDestination( self ):
        """
          Returns document to which link are targeted

          Returns:

            Mybrains object

        """

        # we know a priori that this is principal version,
        # i.e. we can get that object only by nd_uid from link

        uid = self.link_list[-1].getTargetUid()
        if not uid:
            return ''
        document = self._portal_catalog().searchResults( nd_uid=uid.uid )
        if len( document ) != 1:
            return ''
        return document[0]

    def _isDestinationVersionPrincipal( self ):
        """
          Check whether version where link are targeted principal

          Argumens:

            'self.document_destination' -- document where link are targeted

            'self.link' -- link

          Result:

            Boolean

        """
        return \
          self.document_destination_list[-1]['getPrincipalVersionId'] == self._getDestinationVersionId()

    def _getDestinationVersionId( self ):
        """
          Returns destination version id of link

          Arguments:

            'link' -- link to take destination version from

          Result:

            VersionContent instance.

        """
        return self.link_list[-1].getTargetUid('ver_id')

    def _isDestinationVersionStatusActive( self ):
        """
          Checks whether destination version status is active
          (used dicument, i.e. we check that this is principal version)
        """
        return self.document_destination_list[-1].state == self.active_status


    #-----------------------------------------------------------------------------------------

    def _isDateRevisionConditionOneDocumentTrue( self ):
        date_structure = {}
        date_structure['ds'] = self._getFieldFromList('ds')
        res = DateRevisionCondition().dateRevisionConditionOneDocument( date_structure )
        return res

    def _getField( self, catalog_brains, name ):
        if catalog_brains['CategoryAttributes'].has_key(name):
            return catalog_brains['CategoryAttributes'][name]
        return None

    def _getFieldFromList( self, name ):
        return self._getField( self.document_source_list[-1],  name )

    def _isDocumentAdded2PlanByAudit( self ):
        added2PlanByAudit = self._getFieldFromList( 'Added2PlanByAudit' )
        if added2PlanByAudit==1:
            return 1
        return 0

    def _getCountOfEffectiveSubDocuments( self ):
        sub_docs = self._listSubordinateDocuments()
        if len( sub_docs ) < 5:  # <---------  note this is 5
            return 0
        cnt = \
          len( \
            self._portal_catalog().searchResults( \
              nd_uid=sub_docs, \
              state=self.active_status))
        return cnt

    def _listSubordinateDocuments( self ):
        # added from HTMLDocument
        #
        #  a priori - subordinate document have only one version
        #
        search_request = {}
        search_request['target_uid'] = self._getUidFromList()
        search_request['relation'] = 'subordination'
        search_request['target_ver_id'] = self._getVersionFromList()
        subordinate_docs = self._portal_links().searchLinks( **search_request )

        if not subordinate_docs:
            return []

        # get only uid
        docs = [ str(x['source_uid'].base()) for x in subordinate_docs if x['source_uid'].base() != self._getUidFromList()]
        return docs

    def _getUidFromList( self ):
        return self.document_source_list[-1].nd_uid

    def _getVersionFromList( self ):
        return self.document_source_list[-1].getPrincipalVersionId

    def _isDocumentInPlan( self ):
        return bool(self._getFieldFromList('DocInPlan'))

    #----------------------------------------------
    def _portal_catalog( self ):
        return getToolByName( self._parent, 'portal_catalog' )

    def _portal_links( self ):
        return getToolByName( self._parent, 'portal_links' )

    #-------------------------------------------------
    def _log( self, text, no_nl=0 ):
        pass
        #if no_nl:
        #    print text,
        #else:
        #    print text

InitializeClass( RevisionDocSearch )

def initialize( context ):
    # module initialization callback
    context.registerFilter( 'normative_filter', RevisionDocSearch() )

#--------------------------------------------------------------------------------------------

class DateRevisionCondition:

    def dateRevisionConditionOneDocument( self, date_structure ):
        """
          Checks whether document (version) with specified date_stricture
          are needed revision

          Argumens:

            'date_structure' -- dictionary with keys: 'dv', 'ds', 'dp', 'sd'

          Result:

            Boolean
        """

        # sp - depricated
        # if Duration period not specified (or 0), do not check document
        #if date_structure['sd']==0:
        #    return 0

        #date_deistviya = self._getDateDeistviya(
        #      self._getMaxDate( date_structure['dv'], date_structure['dp'] ),
        #      date_structure['sd']
        #)

        #if date_deistviya < self._getDateNow():
        #    self._log( 'date_deistviya < date_now' )
        #    return 1

        if date_structure['ds'] and date_structure['ds'] < self._getDateNow():
            self._log( 'date_spisaniya < date_now' )
            return 1

        self._log( 'dateRevisionConditionOneDocument not' )
        return 0


    def _getDateDeistviya( self, date, duration ):
        """
          Arguments:

            'date' -- date of beginning (DateTime)

            'duration' -- duration of active state of document in month (int)

          Result:

            DateTime

        """
        return self._addMonths( date, duration )

    def _getDateNow( self ):
        """
          Returns now date, i.e. without time

          Result:

            DateTime
        """
        return DateTime(str(DateTime()).split(' ')[0])

    def _getMaxDate( self, date1, date2 ):
        if date2:
            return max( date1, date2 )
        return date1 # date2 is empty

    def _addMonths( self, date, months ):
        day = date.day()
        month = date.month()
        year = date.year()

        new_month = month + months
        years = (new_month-1)/12
        if years > 0:
            year += years
            month = new_month % 12
            if month == 0:
                month = 12
        else:
            month = new_month
        return DateTime( '%s/%s/%s' % (year, month, day) )


    def _log( self, text ):
        pass
        #print text
