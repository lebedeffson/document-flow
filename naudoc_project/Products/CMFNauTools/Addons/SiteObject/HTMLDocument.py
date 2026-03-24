# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/SiteObject/HTMLDocument.py
# Compiled at: 2008-12-09 15:36:06
"""
Patch of HTMLDocument class.

$Editor: oevsegneev $
$Id: HTMLDocument.py,v 1.4 2008/12/09 12:36:06 oevsegneev Exp $
"""
__version__ = '$Revision: 1.4 $'[11:-2]
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo
from Globals import DTMLFile
from Products.CMFNauTools.HTMLDocument import HTMLDocument
from Products.CMFNauTools.Features import createFeature
from Products.CMFNauTools.Utils import getObjectByUid
from Products.CMFNauTools.Config import Permissions
from utils import class_patch

class HTMLDocument_patch(class_patch):
    """
        Patch of subclassed Document type
    """
    __module__ = __name__
    security = ClassSecurityInfo()
    _is_questionnaire = 0
    _is_quest_action = 0
    _q_emails = []
    _q_action = None
    __implements__ = HTMLDocument.__implements__ + (createFeature('isQuestionnaire'),)
    security = ClassSecurityInfo()
    security.declarePublic('isQuestAction')

    def isQuestAction(self):
        """
            Checks that Document has an action

            Result:

                Boolean

        """
        return self._is_quest_action
        return

    security.declareProtected(CMFCorePermissions.View, 'isQuestionnaire')

    def isQuestionnaire(self):
        """
            Checks that Document is a questionnaire

            Result:

                Boolean
        """
        return self._is_questionnaire
        return

    security.declareProtected(CMFCorePermissions.View, 'isQuestAvailable')

    def isQuestAvailable(self):
        """
            Checks that Document can be questionnaire

            Result:

                Boolean
        """
        catObj = getToolByName(self, 'portal_metadata').getCategoryById(self.category)
        isEditable = catObj.isContentFixed()
        isTemplate = catObj.getWorkTemplateId() != ''
        isFields = catObj.listAttributeDefinitions() != []
        return isEditable and isTemplate and isFields
        return

    security.declareProtected(Permissions.PublishPortalContent, 'setQuestionnaire')

    def setQuestionnaire(self, quest_email='', quest_action='', is_quest_action=0, REQUEST=None):
        """
            Sets questionnaire vars

            Arguments:

                'question_email' -- emails to send fields of questionary

                'quest_action' -- action

                'is_quest_action' -- action trigger

        """
        sep = quest_email.count(',') and ',' or ' '
        self._q_emails = [_[1] for e in quest_email.split(sep) if e.strip()]
        self._is_quest_action = is_quest_action
        self._q_action = getObjectByUid(self, quest_action)
        self._is_questionnaire = 1
        return

    security.declareProtected(Permissions.PublishPortalContent, 'resetQuestionnaire')

    def resetQuestionnaire(self):
        """
            Reset questionnaire mode of Document

        """
        self._is_questionnaire = 0
        return

    security.declareProtected(CMFCorePermissions.View, 'getQuestEmails')

    def getQuestEmails(self, joined=True):
        """
            Get questionnaire emails

            Result:

                List of e-mail addresses of questionnaire data recipients

        """
        if joined:
            emails = (', ').join(self._q_emails)
        else:
            emails = self._q_emails
        return emails
        return

    security.declarePublic('getQuestAction')

    def getQuestAction(self):
        """
            Get questionnaire action

            Result:

                Action - ZODB Object
        """
        return self._q_action
        return

    security.declarePublic('sendQuestionnaire')

    def sendQuestionnaire(self, REQUEST=None):
        mailhost = getToolByName(self, 'MailHost')
        skins = getToolByName(self, 'portal_skins')
        message = 'Questionnaire submitted'
        category = self.getCategory()
        template = getattr(skins.getSkinByName('Site'), 'questionnaire.answer')
        attrs = [_[1] for a in category.listAttributeDefinitions()]
        mailhost.sendTemplate(template=template, mto=self.getQuestEmails(joined=False), restricted=Trust, REQUEST=REQUEST, Title=self.Title(), attrs=attrs)
        if self.isQuestAction():
            REQUEST.RESPONSE.redirect(self.getQuestAction().external_url())
        else:
            REQUEST.RESPONSE.redirect(self.getSite().external_url())
        return

    security.declareProtected(CMFCorePermissions.View, 'getField')

    def getField(self, name, template_type='view'):
        """
            Returns field template
        """
        _ = getToolByName(self, 'msg')
        try:
            attribute = self.getCategory().getAttributeDefinition(name)
        except KeyError:
            title = ''
            field = '(%s)' % _("field '%s' was removed from document category") % name
        else:
            title = attribute.Title()
            if self.checkAttributePermissionView(attribute):
                field = attribute.getViewFor(self.getVersion(), template_type)
            elif self.isQuestionnaire() and self.isExternal():
                field = attribute.getViewFor(self.getVersion(), 'external_edit', is_empty=True)
            else:
                field = '(%s)' % _("you are not allowed to read field '%s'") % name

        return '<span class="category-attribute" id="field:%s" title="%s">%s</span>' % (name, title, field)
        return

    def CookedBody(self, stx_level=None, setlevel=0, canonical=None, view=True):
        """
        """
        msg = getToolByName(self, 'msg')
        attrs = self.getCategory().listAttributeDefinitions()
        if self.isQuestionnaire() and self.isExternal():
            return _body_template % {'url': (self.absolute_url()), 'body': (self.EditableBody(view=0)), 'button': (msg('Send')), 'mandatory_ids': ((',').join([_[1] for a in attrs if a.isMandatory()])), 'mandatory_titles': ((',').join([_[1] for a in attrs if a.isMandatory()])), 'need_fill_fields': (msg('Fill of the next fields is needed'))}
        else:
            return self.old_CookedBody(stx_level, setlevel, canonical, view)
        return

    def isExternal(self):
        return hasattr(self, 'go')
        return


_body_template = '\n\n<script type="text/javascript">\n<!--\n\nfunction validate() {\n    var error_box = document.getElementById(\'error_box\');\n    error_box.innerHTML = \'\';\n\n    var fields = new Array(%(mandatory_ids)s);\n    var fieldsn = new Array(%(mandatory_titles)s);\n    var bad_fields = new Array();\n    for (var k=0; k<fields.length; k++) {\n      field = document.getElementById(fields[k]);\n      if (field.value.replace(/ /g, "") == \'\')\n        bad_fields.push(fieldsn[k])\n    }\n\n    if (bad_fields.length) {\n      error_box.innerHTML = \'<font color="#da251c"><b>%(need_fill_fields)s: \'+bad_fields.join(\', \')+\'.</b></font>\';\n      scroll(0,0);\n      return false;\n    }\n\n    return true;\n}\n\n//-->\n</script>\n\n<div id="error_box"></div>\n<form action="%(url)s/sendQuestionnaire" method="post" onSubmit="javascript: return validate();">\n%(body)s<br/>\n<input type="submit" value="%(button)s">\n</form>\n'

def initialize(context):
    HTMLDocument_patch(HTMLDocument, backup=True)
    return
