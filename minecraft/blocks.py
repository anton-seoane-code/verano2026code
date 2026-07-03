BLOCK_TYPES = {}

def register(id_, name, top=None, bottom=None, side=None, solid=True, tex_size=16):
    BLOCK_TYPES[id_] = {
        'id': id_, 'name': name,
        'top': top or (id_, 'top'),
        'bottom': bottom or (id_, 'bottom'),
        'side': side or (id_, 'side'),
        'solid': solid,
        'tex_size': tex_size,
    }

register(0, 'air', solid=False)
register(1, 'grass', top=(1, 'top'), bottom=(2, 'top'), side=(1, 'side'))
register(2, 'dirt', top=(2, 'top'), bottom=(2, 'top'), side=(2, 'top'))
register(3, 'stone', top=(3, 'top'), bottom=(3, 'top'), side=(3, 'top'))
register(4, 'wood', top=(4, 'top'), bottom=(4, 'top'), side=(4, 'side'))
register(5, 'planks', top=(5, 'top'), bottom=(5, 'top'), side=(5, 'top'))
register(6, 'sand', top=(6, 'top'), bottom=(6, 'top'), side=(6, 'top'))
register(7, 'brick', top=(7, 'top'), bottom=(7, 'top'), side=(7, 'top'))
