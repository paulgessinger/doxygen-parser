
import pytest
from doxygen_parser import xml
from xml.etree import ElementTree as BaseEtree
import os
etrees = [BaseEtree]

if os.getenv("DOXYGEN_PARSER_NO_LXML", "False") != "True":
    try:
        from lxml import etree as LxmlEtree
        etrees.append(LxmlEtree)
    except ModuleNotFoundError:
        print("LXML not found, skipping tests with LXML")

# type: ignore
@pytest.fixture(scope='function', params=etrees, autouse=True)
# type: ignore
def patch_etree(monkeypatch, request):
    monkeypatch.setattr("doxygen_parser.xml.etree", request.param)
    #print("ETree:", request.param.__name__)
    yield
