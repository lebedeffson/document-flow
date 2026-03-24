"""Legacy compatibility shim for old CMF products expecting this module."""

from Products.PageTemplates.Expressions import MultiMapping, SafeMapping

try:
    from zope.tales.tales import Default as Undefined
except Exception:
    class Undefined(object):
        pass
