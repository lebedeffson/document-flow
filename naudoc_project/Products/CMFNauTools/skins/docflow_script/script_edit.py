## Script (Python) "script_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=data=' '
##title=Edit a document
##
# $Id: script_edit.py,v 1.5 2005/06/27 06:59:05 vsafronovich Exp $
# $Editor: mbernatski $
# $Revision: 1.5 $

context.edit( data )
context.redirect( relative=False
                , action='script_edit_form'
                , frame='inFrame'
                , message='Changes saved'
                )
