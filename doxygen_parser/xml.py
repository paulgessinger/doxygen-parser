from typing import Union, IO
import os

from xml.etree import ElementTree as BaseEtree
etree = BaseEtree # type: ignore
NodeType = BaseEtree.Element # type: ignore

if os.getenv("DOXYGEN_PARSER_NO_LXML", "False") != "True":
    try:
        from lxml import etree as LxmlEtree
        etree = LxmlEtree # type: ignore
        NodeType = LxmlEtree._Element # type: ignore
    except ModuleNotFoundError:
        pass



def parse(xml : Union[str, IO[str]]) -> NodeType:
    if isinstance(xml, str):
        return etree.fromstring(xml)
    else:
        return etree.parse(xml).getroot()

