from doxygen_parser import Parser
from doxygen_parser import xml
from doxygen_parser.entities import *
import os
import pytest
import tempfile
import shutil
import subprocess
from unittest import mock
from unittest.mock import Mock

example_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "examples", "doxygen"))


@pytest.fixture(scope="module")
def xmldir() -> None:
    with tempfile.TemporaryDirectory() as td:
        doxygen_dir = os.path.join(td, "doxygen")
        shutil.copytree(example_dir, doxygen_dir)
        yield doxygen_dir


def test_parser_synthetic() -> None:
    index = mock.Mock()
    index.__iter__ = Mock(return_value=iter([]))
    load = Mock(return_value=index)
    with mock.patch("doxygen_parser.parser.Parser._load", load):
        p = Parser(xmldir="NONE")

        node = Mock()
        node.attrib = {"refid": "REFID", "kind": "INVALID"}
        node.find = Mock(return_value="NOTNONE")

        with pytest.raises(ValueError):
            p._handle_compound(node)


def test_parser_index_kitchensink(xmldir) -> None:
    index = os.path.join(xmldir, "kitchensink", "xml")
    assert os.path.exists(index)

    p = Parser(index)

    assert len(p.compounds) == 6

    # for k, v in p.entities.items():
    #    print(k.ljust(max(map(len, p.entities.keys()))), v, v._parent)

    act_entities = set(p.entities.keys())

    exp_entities = {"Struct", "Struct::variable", "Struct::Nested", "Struct::Nested::variable", "Struct::NestedEnum",
                    "Struct::NestedEnum::val1", "Struct::NestedEnum::val2", "Struct::public_method",
                    "Struct::protected_method", "Struct::protected_method_const", "Struct::private_method",
                    "Struct::private_method_const", "global_function", "GlobalEnum", "GlobalEnum::val1",
                    "GlobalEnum::val2", "NS1", "NS1::namespaced_function", "NS1::Class2", "NS1::Class2::init",
                    "NS1::Class2::AnotherNested", "NS1::Class2::AnotherNested::limit"}

    assert act_entities == exp_entities

    # assert len(p.entities) == 20

    struct: Struct = p.entities["Struct"]
    assert type(struct) == Struct
    assert struct.name == "Struct"
    assert struct.parent is None

    assert len(struct.methods) == 5
    assert set(e.fqn for e in struct.methods) == {"Struct::public_method",
                                                  "Struct::protected_method",
                                                  "Struct::protected_method_const",
                                                  "Struct::private_method",
                                                  "Struct::private_method_const"}
    assert len(struct.public) == 4
    assert set(e.fqn for e in struct.public) == {"Struct::public_method",
                                                 "Struct::variable",
                                                 "Struct::Nested",
                                                 "Struct::NestedEnum"}

    assert len(struct.protected) == 2
    assert set(e.fqn for e in struct.protected) == {"Struct::protected_method",
                                                    "Struct::protected_method_const"}

    assert len(struct.private) == 2
    assert set(e.fqn for e in struct.private) == {"Struct::private_method",
                                                  "Struct::private_method_const"}

    assert len(struct.children) == 4 + 2 + 2
    assert set(e.fqn for e in struct.children) == {"Struct::variable", "Struct::Nested",
                                                   "Struct::NestedEnum", "Struct::public_method",
                                                   "Struct::protected_method",
                                                   "Struct::protected_method_const",
                                                   "Struct::private_method",
                                                   "Struct::private_method_const"}

    assert len(struct.members) == 1
    assert set(e.fqn for e in struct.members) == {"Struct::variable"}

    assert struct.doc.brief.find("para").text.strip() == "A struct."

    struct_variable = p.entities["Struct::variable"]
    assert type(struct_variable) == Variable
    assert p.entities[struct_variable.fqn] == struct_variable
    assert struct_variable.parent == struct
    assert struct_variable in struct.children
    assert struct_variable in struct.members
    assert struct_variable in struct.public
    assert struct_variable.access == Access.Public
    assert struct_variable.name == "variable"
    assert struct_variable.type == "int"

    assert struct_variable.doc.brief.find("para").text.strip() == "a variable"

    nested_struct = p.entities["Struct::Nested"]
    assert type(nested_struct) == Struct
    assert p.entities[nested_struct.fqn] == nested_struct
    assert nested_struct.name == "Nested"
    assert nested_struct.fqn == "Struct::Nested"
    assert nested_struct.parent == struct
    assert nested_struct.access == Access.Public
    assert p.entities[nested_struct.parent.fqn] == struct

    assert len(nested_struct.children) == 1
    assert set(e.fqn for e in nested_struct.children) == {"Struct::Nested::variable"}

    assert nested_struct.doc.brief.find("para").text.strip() == "A nested struct."

    nested_struct_variable = p.entities["Struct::Nested::variable"]
    assert nested_struct_variable.name == "variable"
    assert nested_struct_variable.doc.brief.find("para").text.strip() \
           == "A nested struct variable."

    nested_enum: Enum = p.entities["Struct::NestedEnum"]
    assert p.entities[nested_enum.fqn] == nested_enum
    assert type(nested_enum) == Enum
    assert nested_enum.parent == struct
    assert nested_enum in struct.children
    assert nested_enum in struct.public
    assert set(e.fqn for e in nested_enum.values) == {"Struct::NestedEnum::val1",
                                                      "Struct::NestedEnum::val2"}
    assert set(e.name for e in nested_enum.values) == {"val1", "val2"}
    assert nested_enum.doc.brief.find("para").text.strip() == "A nested enum."

    public_method = p.entities["Struct::public_method"]
    assert p.entities[public_method.fqn] == public_method
    assert public_method.parent == struct
    assert public_method in struct.children
    assert public_method in struct.methods
    assert public_method in struct.public
    assert public_method.access == Access.Public
    assert public_method.name == "public_method"
    assert public_method.doc.brief.find("para").text.strip() == "A public method."

    protected_method = p.entities["Struct::protected_method"]
    assert p.entities[protected_method.fqn] == protected_method
    assert protected_method.parent == struct
    assert protected_method in struct.children
    assert protected_method in struct.methods
    assert protected_method in struct.protected
    assert protected_method.access == Access.Protected
    assert protected_method.name == "protected_method"
    assert protected_method.doc.brief.find("para").text.strip() == "A protected method."

    protected_method_const = p.entities["Struct::protected_method_const"]
    assert p.entities[protected_method_const.fqn] == protected_method_const
    assert protected_method_const.parent == struct
    assert protected_method_const in struct.children
    assert protected_method_const in struct.methods
    assert protected_method_const in struct.protected
    assert protected_method_const.access == Access.Protected
    assert protected_method_const.name == "protected_method_const"
    assert protected_method_const.doc.brief.find("para").text.strip() \
           == "A protected const method."

    private_method = p.entities["Struct::private_method"]
    assert p.entities[private_method.fqn] == private_method
    assert private_method.parent == struct
    assert private_method in struct.children
    assert private_method in struct.methods
    assert private_method in struct.private
    assert private_method.access == Access.Private
    assert private_method.name == "private_method"
    assert private_method.doc.brief.find("para").text.strip() == "A private method."

    private_method_const = p.entities["Struct::private_method_const"]
    assert p.entities[private_method_const.fqn] == private_method_const
    assert private_method_const.parent == struct
    assert private_method_const in struct.children
    assert private_method_const in struct.methods
    assert private_method_const in struct.private
    assert private_method_const.access == Access.Private
    assert private_method_const.name == "private_method_const"
    assert private_method_const.doc.brief.find("para").text.strip() \
           == "A private const method."


    global_function = p.entities["global_function"]
    assert type(global_function) == Function
    assert global_function.parent is None
    assert global_function.name == "global_function"
    assert global_function.access == Access.Public

    assert global_function.doc.brief.find("para").text.strip() == "A global function."


    global_enum = p.entities["GlobalEnum"]
    assert type(global_enum) == Enum
    assert global_enum.parent is None
    assert global_enum.name == "GlobalEnum"
    assert global_enum.access == Access.Public

    assert global_enum.doc.brief.find("para").text.strip() == "A global enum."


    ns1 = p.entities["NS1"]
    assert type(ns1) == Namespace
    assert ns1.name == "NS1"
    assert ns1.parent is None
    assert ns1.access is None
    assert ns1.doc.brief.find("para").text.strip() == "I am a namespace."

    namespaced_function = p.entities["NS1::namespaced_function"]
    assert type(namespaced_function) == Function
    assert namespaced_function.name == "namespaced_function"
    assert namespaced_function.parent == ns1
    assert namespaced_function in ns1.children
    assert namespaced_function.access == Access.Public
    assert namespaced_function.doc.brief.find("para").text.strip() \
           == "I am a namespaced function."

    class2 = p.entities["NS1::Class2"]
    assert type(class2) == Class
    assert class2.name == "Class2"
    assert class2.parent == ns1
    assert class2 in ns1.children
    assert class2.access == Access.Public
    assert class2.doc.brief.find("para").text.strip() == "I am a namespaced class."

    class2_init = p.entities["NS1::Class2::init"]
    assert type(class2_init) == Function
    assert class2_init.name == "init"
    assert class2_init.parent == class2
    assert class2_init in class2.children
    assert class2_init.access == Access.Private
    assert class2_init.doc.brief.find("para").text.strip() \
           == "Another member."

    class2_nested = p.entities["NS1::Class2::AnotherNested"]
    assert type(class2_nested) == Struct
    assert class2_nested.name == "AnotherNested"
    assert class2_nested.parent == class2
    assert class2_nested in class2.children
    assert class2_nested.access == Access.Private
    assert class2_nested.doc.brief.find("para").text.strip() \
           == "More nesting."

    limit = p.entities["NS1::Class2::AnotherNested::limit"]
    assert type(limit) == Variable
    assert limit.name == "limit"
    assert limit.parent == class2_nested
    assert limit in class2_nested.children
    assert limit.access == Access.Public
    assert limit.doc.brief.find("para").text.strip() == "limit variable"



