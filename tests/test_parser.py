from doxygen_parser import IndexParser
from doxygen_parser import xml
import os
import pytest
import tempfile
import shutil
import subprocess

example_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "examples", "doxygen"))

@pytest.fixture(scope="module")
def xmldir():
    # with tempfile.TemporaryDirectory() as td:
    # td = tempfile.mkdtemp()
    td = "/tmp/dox"

    with open(os.path.join(example_dir, "Doxyfile.in")) as f:
        doxy_tpl = f.read()
    doxyfile = os.path.join(td, "Doxyfile")
    with open(doxyfile, "w+") as f:
        f.write(doxy_tpl.format(input_path=example_dir, example_path=td))

    subprocess.check_call(["doxygen", doxyfile], cwd=td)
    yield td
    # shutil.rmtree(td)

def test_parser_index(xmldir):
    print(xmldir)
