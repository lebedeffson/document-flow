"""

$Id: Storefront.py,v 1.15 2005/09/23 07:28:54 vsafronovich Exp $
$Editor: vsafronovich $
"""
__version__ = '$Revision: 1.15 $'[11:-2]

from zLOG import LOG, DEBUG, TRACE, INFO, ERROR

from AccessControl import ClassSecurityInfo
from AccessControl import Permissions as ZopePermissions
from Acquisition import aq_get

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName

from operator import add, mul
from types import StringType

import Features
from Exceptions import SimpleError
from Features import createFeature
from Heading import Heading, HeadingType
from HTMLDocument import HTMLDocumentType
from Utils import InitializeClass, extractParams, getObjectByUid, inheritActions


StorefrontType = { 'id'                    : 'Storefront'
                 , 'content_meta_type'     : 'Storefront'
                 , 'title'                 : "Storefront"
                 , 'description'           : "Storefront"
                 , 'icon'                  : 'folder_icon.gif'
                 , 'sort_order'            : 0.3
                 , 'product'               : 'CMFNauTools'
                 , 'factory'               : 'addStorefront'
                 , 'permissions'           : ( CMFCorePermissions.AddPortalFolders, )
                 , 'condition'             : 'python: object.getSite() is not None'
                 , 'filter_content_types'  : 1
                 , 'allowed_content_types' : ( HTMLDocumentType['id'], )
                 , 'allowed_categories'    : ['Publication']
                 , 'inherit_categories'    : 0
                 , 'immediate_view'        : 'folder_edit_form'
                 , 'actions'               : inheritActions( HeadingType )
                 }


class Storefront( Heading ):
    """ Storefront class """
    _class_version = 1.0

    meta_type = 'Storefront'
    portal_type = 'Storefront'

    __implements__ = ( createFeature('isStorefront'),
                       Features.isContentStorage,
                       Features.isPublishable,
                       Heading.__implements__,
                     )


    __unimplements__ = ( Features.canHaveSubfolders,
                       )

    _properties = Heading._properties + (
                    {'id':'send_order', 'type':'boolean', 'mode':'w', 'default':0},
                    {'id':'questionnaire_uid' , 'type':'string', 'mode':'w', 'default':''},
                    {'id':'base_category', 'type':'string', 'mode':'w', 'default':''},
                    {'id':'emails','type':'lines', 'mode':'w', 'default':[]}
                  )

    security = ClassSecurityInfo()

    security.declareProtected( CMFCorePermissions.View, 'hasMainPage'
                                                      , 'getMainPage'
                                                      )
    def hasMainPage( self):
        """
            Storefront has no main page

            Result:

                0
        """
        return 0

    def getMainPage( self):
        """
            Storefront has no main page

            Result:

                None
        """
        return None

    security.declareProtected( CMFCorePermissions.ManageProperties, 'setSendOrder' )
    def setSendOrder(self, send_order):
        """
            Changes default parameters of the storefront.

            Arguments:

                'send_order' -- "send order" trigger
        """
        self.send_order = not not send_order
        if not self.send_order:
            self.questionnaire_uid = ''
            self.base_category = ''
            self.emails = []

    security.declareProtected( CMFCorePermissions.View, 'canSendOrder')
    def canSendOrder(self):
        """
            Checks that Storefront works correctly.

            Result:

                Boolean.
        """
        return self.send_order

    security.declareProtected( CMFCorePermissions.View, 'getQuestionnaire' )
    def getQuestionnaire(self):
        """
            Returns Questionnaire document.

            Result:

                HTMLDocument object.
        """
        obj = getObjectByUid(self, self.questionnaire_uid)
        return obj

    security.declareProtected( CMFCorePermissions.View, 'getQuestionnaireBody' )
    def getQuestionnaireBody(self):
        """
            Returns Questionnaire document body.

            Result:

                String.
        """
        obj = self.getQuestionnaire()
        return obj and obj.CookedBody() or ''

    security.declareProtected( CMFCorePermissions.View, 'getQuestionnaireUid' )
    def getQuestionnaireUid(self):
        """
            Returns Questionnaire document uid.

            Result:

                String.
        """
        return self.questionnaire_uid

    security.declareProtected( CMFCorePermissions.View, 'getQuestionnaireTitle' )
    def getQuestionnaireTitle(self):
        """
            Returns Questionnaire document title.

            Result:

                String.
        """
        obj = self.getQuestionnaire()
        return obj and obj.Title() or ''

    security.declareProtected( CMFCorePermissions.ManageProperties, 'setQuestionnaireUid' )
    def setQuestionnaireUid(self,questionnaire_uid):
        """
            Changes uid of the document, that will represented customers data

            Arguments:

                'questionnaire_uid' -- uid of the questionnaire document
        """
        self.questionnaire_uid = questionnaire_uid

    security.declareProtected( CMFCorePermissions.ManageProperties, 'setDefaultCategory' )
    def setDefaultCategory(self, category):
        """
            Changes default category of documents, that will created in storefront.

            Arguments:

                'category' -- id of default storefront document`s category
        """
        self.base_category = category

    security.declareProtected( CMFCorePermissions.View, 'getDefaultCategory' )
    def getDefaultCategory(self):
        """
            Returns default category of documents, that will created in storefront.

            Result:

               String.
        """
        return self.base_category

    def SendOrder(self, REQUEST=None):
        """
            Sends order to e-mail addresses of Storefront.

            Arguments:

                'REQUEST' -- optional Zope request object with extra parameters

        """
        REQUEST = REQUEST or aq_get( self, 'REQUEST' )

        if not self.send_order:
            raise Unauthorized, ( "You was not allowed to send order" )

        quest = self.getQuestionnaire()
        mailhost = getToolByName( self, 'MailHost' )
        mdtool = getToolByName( self, 'portal_metadata')
        message = 'Order sended'

        catObj = mdtool.getCategoryById( quest.category)
        for f in catObj.listAttributeDefinitions():
            if f.Type()=='date' and REQUEST.has_key(f.getId()+'_day'):
                REQUEST.set(f.getId(), parseDate(f.getId(), REQUEST))

        url = REQUEST['SESSION'].get('items_url')
        products = REQUEST['SESSION']['%s_items'%url]

        counts = [ int(x['count']) for x in products]
        prices = [ float(x['product_price']) for x in products]
        total_prices = map(mul, prices, counts)
        total = reduce(add, total_prices)

        mailhost.sendTemplate( template='send_order_template'
                             , mto=self.getQuestEmails('list')
                             , R=REQUEST
                             , cntx=quest
                             , products=products
                             , counts=counts
                             , total_prices=total_prices
                             , total=total
                             )

    security.declareProtected( CMFCorePermissions.ManageProperties, 'manage_changeProperties' )
    def manage_changeProperties( self, REQUEST=None, **kw):
        """
            Changes existing object properties

            Arguments:

                'REQUEST' -- optional Zope request object or None

                '**kw' -- additional variables to pass to heading method

            Result:

                See 'Heading.manage_changeProperties()' method description.
        """
        send_order, doc_uid , emails, category = extractParams( kw, REQUEST, 'send_order', 'document_uid',\
                                                           'quest_email', 'base_category' )

        if send_order:
            if not (doc_uid and emails):
                raise SimpleError( "You must choose questionnaire,"\
                                   " which will be filled by user making the order,"\
                                   " and fill e-mail adresses,"\
                                   " where the orders will be sent.",)
            self.setQuestionnaireUid( doc_uid )
            self.setEmails( emails )

            if category:
                self.setDefaultCategory( category )
                mdtool = getToolByName( self, 'portal_metadata' )
                base_cat = mdtool.getCategoryById( self.getDefaultCategory() )
                self.setAllowedCategories( [base_cat] + base_cat.listDependentCategories() )
            self.setSendOrder(1)
        else:
            self.setSendOrder(0)

        return Heading.manage_changeProperties( self, REQUEST or {}, **kw )

    security.declareProtected( CMFCorePermissions.ManageProperties, 'setEmails' )
    def setEmails( self, emails):
        """
            Changes e-mail addresses, where orders will sended

            Arguments:

                'emails' -- emails to send fields of questionnaire, may be list or string type
        """
        if type( emails) is StringType:
            sep = emails.count(',') and ',' or ' '
            emails = [ e.strip() for e in emails.split( sep) if e.strip()]
        self.emails = emails

    security.declareProtected( CMFCorePermissions.ManageProperties, 'getEmails')
    def getEmails( self, mode='list'):
        """
            Gets questionnaire emails

            Arguments:

                'mode' -- returning type, default list type.

            Result:

                List or string of e-mail addresses of questionnaire data recipients
        """
        if mode == 'string':
            emails = ', '.join( self.emails)
        elif mode == 'list':
            emails = self.emails
        return emails

InitializeClass( Storefront )


def addStorefront( self, id, title='', REQUEST=None, **kwargs ):
    """ Adds Storefront """
    obj = Storefront( id, title, **kwargs )
    self._setObject( id, obj )


def initialize( context ):
    # module initialization callback

    context.registerContent( Storefront, addStorefront, StorefrontType )
