import enum
from typing import List, Any, Optional, Union, Dict, cast
from . import xml


class Access(enum.Enum):
    Public = 1
    Private = 2
    Protected = 3


def parse_access(access: str) -> Access:
    if access.startswith("public"):
        return Access.Public
    elif access.startswith("private"):
        return Access.Private
    elif access.startswith("protected"):
        return Access.Protected
    else:
        raise ValueError("Invalid access specified %s" % access)


class Entity:
    _parent: Optional[str]
    _node: xml.NodeType
    _entities: Dict[str, 'Entity']
    access: Optional[Access]
    children: List['Entity']

    def __init__(self, node: xml.NodeType,
                 entities: Dict[str, 'Entity'],
                 parent: Union['Entity', str, None] = None,
                 access: Optional[Access] = None):
        self._node = node
        self._entities = entities
        self._parent = None
        self.parent = parent
        self.access = access
        self.children = []

    @property
    def fqn(self) -> str:
        if self.parent is not None:
            return self.parent.fqn + "::" + self.name
        else:
            return self.name

    @property
    def parent(self) -> Optional['Entity']:
        if self._parent is None:
            return None
        return self._entities[self._parent]

    @parent.setter
    def parent(self, parent: Union['Entity', str, None]) -> None:
        # remove from previous parent if set
        if self.parent is not None:
            self.parent._remove_child(self)

        if parent is None:
            self._parent: Optional[str] = None
        elif isinstance(parent, str):
            self._parent: Optional[str] = parent
            # add this to children of parent
            self._entities[parent]._add_child(self)
        else:
            self._parent: Optional[str] = parent.fqn
            parent._add_child(self)

    def _add_child(self, child: 'Entity') -> None:
        if not child in self.children:
            self.children.append(child)

    def _remove_child(self, child: 'Entity') -> None:
        if child in self.children:
            self.children.remove(child)

    @property
    def name(self) -> str:
        raise NotImplementedError()

    @property
    def refid(self) -> str:
        raise NotImplementedError()

    def __repr__(self) -> str:
        return '<Entity(type="%s", name="%s">' % (self.__class__.__name__, self.fqn)

    def __str__(self) -> str:
        return self.__repr__()


def entity_factory(node: xml.NodeType,
                   entities: Dict[str, Entity],
                   parent: Optional[Entity] = None) -> Entity:
    kind = node.attrib["kind"]
    access: Optional[Access] = None
    if "prot" in node.attrib:
        access = parse_access(node.attrib["prot"])

    if kind == "function":
        return Function(node, entities, parent, access)
    if kind == "variable":
        return Variable(node, entities, parent, access)
    elif kind == "enum":
        return Enum(node, entities, parent, access)
    else:
        raise ValueError("Unknown entity %s" % kind)


class Function(Entity):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

    @property
    def name(self) -> str:
        name = self._node.find("name")
        assert name is not None
        text = name.text
        assert text is not None
        return text


class Variable(Entity):
    type: str

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        typetag = self._node.find("type")
        assert typetag is not None
        typetext = typetag.text
        assert typetext is not None
        self.type = typetext

    @property
    def name(self) -> str:
        name = self._node.find("name")
        assert name is not None
        text = name.text
        assert text is not None
        return text


class EnumValue(Entity):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        pass

    @property
    def name(self) -> str:
        nametag = self._node.find("name")
        assert nametag is not None
        name = nametag.text
        assert name is not None
        return name

class Enum(Entity):
    values: List[EnumValue]

    def __init__(self,
                 node: xml.NodeType,
                 entities: Dict[str, Entity],
                 *args: Any, **kwargs: Any):
        super().__init__(node, entities, *args, **kwargs)
        self.values = []
        enumvalues = self._node.findall("enumvalue")
        entities[self.fqn] = self
        for enumvalue in enumvalues:
            ev = EnumValue(enumvalue, entities, parent=self)
            self.values.append(ev)
            fqn = str(ev.fqn)
            entities[fqn] = ev

    @property
    def name(self) -> str:
        name = self._node.find("name")
        assert name is not None
        text = name.text
        assert text is not None
        return text


class Compound(Entity):
    def __init__(self, *args : Any, **kwargs : Any):
        super().__init__(*args, **kwargs)

    @property
    def name(self) -> str:
        cmpname = self._node.find("compoundname")
        assert cmpname is not None
        text = cmpname.text
        assert text is not None
        return text.split("::")[-1]

    @property
    def refid(self) -> str:
        assert "id" in self._node.attrib
        return self._node.attrib["id"]

class Class(Compound):
    public : List[Entity]
    private : List[Entity]
    protected : List[Entity]
    methods : List[Function]
    members : List[Variable]

    def __init__(self,
                 node: xml.NodeType,
                 entities: Dict[str, Entity],
                 refidmap: Dict[str, Entity],
                 *args: Any, **kwargs: Any):
        super().__init__(node, entities, *args, **kwargs)
        self.public = []
        self.protected = []
        self.private = []

        self.methods = []
        self.members = []

        self._entities[self.fqn] = self

        sections = self._node.findall("sectiondef")
        for section in sections:
            kind = section.attrib["kind"]
            members = section.findall("memberdef")
            for member in members:
                entity = entity_factory(member,
                                        entities,
                                        parent=self)
                entities[entity.fqn] = entity
                #self._children.append(entity)
                if isinstance(entity, Function):
                    self.methods.append(entity)
                if isinstance(entity, Variable):
                    self.members.append(entity)

        innerclasses = self._node.findall("innerclass")
        for innerclass in innerclasses:
            # nested entity should have been before
            # this on in index, fetch it
            assert "refid" in innerclass.attrib
            refid = innerclass.attrib["refid"]
            assert refid in refidmap
            entity = refidmap[refid]
            entity.parent = self
            assert "prot" in innerclass.attrib
            entity.access = parse_access(innerclass.attrib["prot"])
            #self._children.append(entity)

        for entity in self.children:
            if entity.access == Access.Public:
                self.public.append(entity)
            if entity.access == Access.Private:
                self.private.append(entity)
            if entity.access == Access.Protected:
                self.protected.append(entity)

class Struct(Class):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)


class File(Compound):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

        for section in self._node.findall("sectiondef"):
            members = section.findall("memberdef")
            # self._entities[self.fqn] = self
            for member in members:
                entity = entity_factory(member,
                                        self._entities,
                                        parent=None)
                self._entities[entity.fqn] = entity

class Namespace(Compound):
    def __init__(self,
                 node: xml.NodeType,
                 entities: Dict[str, Entity],
                 refidmap: Dict[str, Entity],
                 *args: Any, **kwargs: Any):
        super().__init__(node, entities, *args, **kwargs)

        sections = self._node.findall("sectiondef")
        entities[self.fqn] = self
        for section in sections:
            kind = section.attrib["kind"]
            members = section.findall("memberdef")
            for member in members:
                entity = entity_factory(member,
                                        entities,
                                        parent=self)
                entities[entity.fqn] = entity

        innerclasses = self._node.findall("innerclass")
        for innerclass in innerclasses:
            # nested entity should have been before
            # this on in index, fetch it
            assert "refid" in innerclass.attrib
            refid = innerclass.attrib["refid"]
            assert refid in refidmap
            entity = refidmap[refid]
            entity.parent = self
            assert "prot" in innerclass.attrib
            entity.access = parse_access(innerclass.attrib["prot"])


