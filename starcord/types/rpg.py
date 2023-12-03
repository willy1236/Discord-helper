from enum import Enum,IntEnum

class ShopItemMode(IntEnum):
    sell = 1
    buy = 2

class ItemCategory(IntEnum):
    general = 1
    equipment = 2
    
class EquipmentSolt(IntEnum):
    head = 1
    body = 2
    legging = 3
    foot = 4
    mainhand = 5
    seconhand = 6