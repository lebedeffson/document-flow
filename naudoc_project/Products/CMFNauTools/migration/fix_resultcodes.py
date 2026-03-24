"""
$Id: fix_resultcodes.py,v 1.6 2005/05/14 05:43:46 vsafronovich Exp $
$Editor: inemihin $
"""
__version__ = '$Revision: 1.6 $'[11:-2]

title = 'Fix resultcodes of DocFlow'
version = '3.0.2.0'
classes = ['Products.CMFNauTools.Resultcodes2Transition.Resultcodes2TransitionModel']

from Products.CMFCore.utils import getToolByName

def check(context, object):
    for variant_id in object.variants.keys():
        if _variantNeedPatch( object.variants[variant_id] ):
            return 1
    return 0

def migrate(context, object):
    for variant_id in object.variants.keys():
        variant = object.variants[variant_id]
        if _variantNeedPatch( variant ):
            _patchVariant( variant )
    object._p_changed = 1

def _variantNeedPatch( variant ):
    return not variant.has_key('python_script')

def _patchVariant( variant ):
    script = _resultCodes2PythonScript( variant['resultcodes'] )
    del variant['resultcodes']
    variant['python_script'] = script
    variant['note'] = 'converted'

def _resultCodes2PythonScript( result_codes ):
    script = ''
    script_items = []
    for at_id in result_codes.keys():
        condition = "result_codes['%s']=='%s'" % ( at_id, result_codes[at_id] )
        script_items.append( condition )
    if script_items:
        script = ' and '.join( script_items )
    return script
