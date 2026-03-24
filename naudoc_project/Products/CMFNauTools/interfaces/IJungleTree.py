
from Interface import Interface, Attribute

class IBasicTree( Interface ):
    root_item = Attribute('root_item', 'TODO')
    root_url = Attribute('root_url', 'TODO')

    get_items = Attribute('get_items', 'TODO')
    info_dict = Attribute('info_dict', 'TODO')
