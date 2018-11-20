from doxygen_parser.entities import *
import pytest
from unittest.mock import Mock, MagicMock


# from doxygen_parser import xml

def test_parse_access() -> None:
    assert parse_access("public-hurz") == Access.Public
    assert parse_access("private-hurz") == Access.Private
    assert parse_access("protected-hurz") == Access.Protected
    with pytest.raises(ValueError):
        parse_access("invalid")


def test_entity() -> None:
    node = Mock()
    parent = Mock(name="PARENT")
    parent.fqn = parent.name

    e1 = Entity(node, {})
    assert e1.parent is None
    assert e1.access is None

    with pytest.raises(NotImplementedError):
        e1.name

    with pytest.raises(NotImplementedError):
        e1.refid

    p2 = Mock()
    p2.name = "ENTITY"
    p2.fqn = "ENTITY"
    entities = {
        parent.name: parent,
        p2.name: p2
    }
    e2 = Entity(node, entities, parent)
    assert e2.parent == parent

    e2.parent = p2.name
    assert e2.parent == p2


def test_member_factory() -> None:
    parent = Mock()
    parent.name = "PARENT"
    parent.fqn = parent.name

    variable = Mock()
    variable.attrib = {"kind": "variable", "prot": "public"}
    entities = {parent.name: parent}
    entity = entity_factory(variable, entities, parent)
    assert type(entity) == Variable
    assert entity.access == Access.Public
    assert entity.parent == parent

    func = Mock()
    func.attrib = {"kind": "function", "prot": "public"}
    entities = {parent.name: parent}
    entity: Function = entity_factory(func, entities, parent)
    assert type(entity) == Function
    assert entity.access == Access.Public
    assert entity.parent == parent

    func = Mock()
    func.attrib = {"kind": "function", "prot": "protected"}
    entities = {parent.name: parent}
    entity: Function = entity_factory(func, entities, parent)
    assert type(entity) == Function
    assert entity.access == Access.Protected
    assert entity.parent == parent

    func = Mock()
    func.attrib = {"kind": "function", "prot": "private"}
    entities = {parent.name: parent}
    entity: Function = entity_factory(func, entities, parent)
    assert type(entity) == Function
    assert entity.access == Access.Private
    assert entity.parent == parent

    enum = Mock(
        findall=MagicMock(return_value=[
            Mock(find=MagicMock(return_value=Mock(text="Val1"))),
            Mock(find=MagicMock(return_value=Mock(test="Val2"))),
        ]),
        find=MagicMock(returnValue=Mock(text="EnumName")),
        attrib={"kind": "enum", "prot": "public"}
    )
    entities = {parent.name: parent}
    entity: Enum = entity_factory(enum, entities, parent)
    assert type(entity) == Enum
    assert entity.access == Access.Public
    assert entity.parent == parent
    assert len(entity.values) == 2
    assert entity.values[0].name == "Val1"
    #assert entity.values[1].name == "Val2"
    print(str(entity.values[1].name))



def test_entity_factory() -> None:
    variable = Mock()
    variable.attrib = {"kind": "variable"}
    variable.find = MagicMock(return_value=Mock(text="double"))
    entity = entity_factory(variable, {})
    assert type(entity) == Variable
    assert entity.access is None
    assert entity.parent is None
    assert entity.type == "double"

    enum = Mock(
        findall=MagicMock(return_value=[
            Mock(find=MagicMock(return_value=Mock(text="Val1"))),
            Mock(find=MagicMock(return_value=Mock(test="Val2"))),
        ]),
        find=MagicMock(returnValue=Mock(text="EnumName")),
        attrib={"kind": "enum"}
    )
    entity = entity_factory(enum, {})
    assert type(entity) == Enum
    assert entity.access is None
    assert entity.parent is None

    func = Mock()
    func.attrib = {"kind": "function"}
    entity = entity_factory(func, {})
    assert type(entity) == Function
    assert entity.access is None
    assert entity.parent is None

    with pytest.raises(ValueError):
        entity = Mock()
        entity.attrib={"kind": "INVALID"}
        entity_factory(entity, {})
