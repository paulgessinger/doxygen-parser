import pytest
from doxygen_parser import xml
from xml.etree import ElementTree as BaseEtree

etrees = [BaseEtree]
try:
    from lxml import etree as LxmlEtree
    etrees.append(LxmlEtree)
except ModuleNotFoundError:
    print("LXML not found, skipping tests with LXML")

@pytest.fixture(scope='function', params=etrees, autouse=True)
def patch_etree(monkeypatch, request):
    monkeypatch.setattr("doxygen_parser.xml.etree", request.param)
    print("ETree:", request.param.__name__)
    yield
