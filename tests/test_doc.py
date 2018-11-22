from doxygen_parser.entities import *
from doxygen_parser.doc import DocItem
import pytest
from unittest.mock import Mock, MagicMock


def test_docitem():

    parent = Mock()

    node = Mock()

    brief = Mock()
    brief.text = "BRIEF"

    detailed = Mock()
    detailed.text = "DETAILED"

    vals = iter([brief, detailed])
    def find(*args, **kwargs):
        return next(vals)

    node.find = Mock(side_effect=find)

    di = DocItem(node, parent)
    node.find.assert_not_called()

    assert di.brief.text == "BRIEF"
    assert node.find.call_count == 1

    assert di.detailed.text == "DETAILED"
    assert node.find.call_count == 2

