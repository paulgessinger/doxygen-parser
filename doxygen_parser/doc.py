from .xml import NodeType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .entities import Entity

class DocItem:
    _node: NodeType
    parent: 'Entity'

    def __init__(self, node: NodeType, parent: 'Entity'):
        self._node = node
        self.parent = parent

    @property
    def brief(self) -> NodeType:
        node = self._node.find("briefdescription")
        assert node is not None
        return node

    @property
    def detailed(self) -> NodeType:
        node = self._node.find("detaileddescription")
        assert node is not None
        return node
