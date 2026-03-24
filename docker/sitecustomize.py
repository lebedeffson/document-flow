"""Compatibility shims for legacy NauDoc products on modern Zope 2.13 env."""

try:
    import Products

    # Some old CMF modules expect this attribute on the Products package.
    if not hasattr(Products, '__ac_permissions__'):
        Products.__ac_permissions__ = ()
except Exception:
    # Best-effort shim; do not break interpreter startup.
    pass

def _backfill_implements(modname, classnames):
    try:
        mod = __import__(modname, fromlist=['*'])
    except Exception:
        return

    for name in classnames:
        cls = getattr(mod, name, None)
        if cls is None:
            continue
        if not hasattr(cls, '__implements__'):
            try:
                cls.__implements__ = getattr(cls, '__implemented__', ())
            except Exception:
                cls.__implements__ = ()


# Legacy CMF products still read __implements__ from Zope core classes.
_backfill_implements('OFS.Folder', ['Folder'])
_backfill_implements('OFS.SimpleItem', ['SimpleItem', 'Item'])
_backfill_implements('OFS.ObjectManager', ['ObjectManager'])
_backfill_implements('OFS.PropertyManager', ['PropertyManager'])
