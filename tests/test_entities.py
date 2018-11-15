from doxygen_parser.entities import *
import pytest
from unittest.mock import Mock, MagicMock
from doxygen_parser import xml

def test_parse_access() -> None:
    assert parse_access("public-hurz") == Access.Public
    assert parse_access("private-hurz") == Access.Private
    assert parse_access("protected-hurz") == Access.Protected
    with pytest.raises(ValueError):
        parse_access("invalid")

def test_entity() -> None:
    node = Mock()
    parent = Mock()
    e1 = Entity(node, {})
    assert e1.parent is None
    assert e1.access is None

def parse(s):
    print("<?xml version='1.0' encoding='UTF-8' standalone='no'?><wrap>%s</wrap>" % s)

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
    return

    func = Mock()
    func.attrib = {"kind": "function", "prot": "public"}
    entities = {parent.name: parent}
    entity = entity_factory(func, entities, parent)
    assert type(entity) == Function
    assert entity.access == Access.Public
    assert entity.parent == parent

    func = Mock()
    func.attrib = {"kind": "function", "prot": "protected"}
    entities = {parent.name: parent}
    entity = entity_factory(func, entities, parent)
    assert type(entity) == Function
    assert entity.access == Access.Protected
    assert entity.parent == parent

    func = Mock()
    func.attrib = {"kind": "function", "prot": "private"}
    entities = {parent.name: parent}
    entity = entity_factory(func, entities, parent)
    assert type(entity) == Function
    assert entity.access == Access.Private
    assert entity.parent == parent

    enum = Mock(
        findall=MagicMock(return_value=[
            Mock(find=MagicMock(return_value=Mock(text="Val1"))),
            Mock(find=MagicMock(return_value=Mock(test="Val2"))),
        ]),
        find = MagicMock(returnValue=Mock(text="EnumName")),
        attrib = {"kind": "enum", "prot": "public"}
    )
    entities = {parent.name: parent}
    entity = entity_factory(enum, entities, parent)
    assert type(entity) == Enum
    assert entity.access == Access.Public
    assert entity.parent == parent
    assert len(entity.values) == 2
    assert entity.values[0].name == "Val1"
    assert entity.values[1].name == "Val2"


def test_entity_factory() -> None:
    variable = Mock()
    variable.attrib = {"kind": "variable"}
    entity = entity_factory(variable, {})
    assert type(entity) == Variable
    assert entity.access is None
    assert entity.parent is None

    enum = Mock(
        findall=MagicMock(return_value=[
            Mock(find=MagicMock(return_value=Mock(text="Val1"))),
            Mock(find=MagicMock(return_value=Mock(test="Val2"))),
        ]),
        find = MagicMock(returnValue=Mock(text="EnumName")),
        attrib = {"kind": "enum"}
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
