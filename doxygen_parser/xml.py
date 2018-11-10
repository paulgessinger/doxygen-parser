try:
    from lxml import etree as LxmlEtree
    etree = LxmlEtree
except ModuleNotFoundError:
    from xml.etree import ElementTree as BaseEtree
    etree = BaseEtree

