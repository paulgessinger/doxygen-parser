from . import xml
from .entities import *
import os
from typing import List, Union

class ParserBase:
    def __init__(self, xmldir : str):
        print("ParserBase go")
        self._xmldir = xmldir

    def _reffile(self, refid : str) -> str:
        return os.path.join(self._xmldir, refid+".xml")

    def _load(self, refid : str) -> xml.NodeType:
        return xml.etree.parse(self._reffile(refid)).getroot()

# Compound = Union[Class, Struct, File]

class Parser(ParserBase):
    def __init__(self, xmldir : str):
        super().__init__(xmldir)
        self.compounds : List[Compound] = []
        self.entities : Dict[str, Entity] = {}
        self._refidmap : Dict[str, Entity] = {}
        self._root = self._load("index") 

        for child in self._root:
            if child.tag == "compound":
                self._handle_compound(child)

        delkeys = []
        items = list(self.entities.items())
        # reset all entity keys to their fqns
        for k, v in items:
            if k != v.fqn:
                self.entities[v.fqn] = v
                delkeys.append(k)

        # recreate all parent fqns stored in entities
        for k, v in items:
            v.parent = v.parent

        # now remove obsolete partial fqns
        for k in delkeys:
            del self.entities[k]

    def _handle_compound(self, node : xml.NodeType) -> None:
        refid = node.attrib["refid"]
        kind = node.attrib["kind"]
        refroot = self._load(refid)
        cmpdef = refroot.find("compounddef")
        assert cmpdef is not None

        if kind == "class":
            cls = Class(cmpdef, self.entities, self._refidmap)
            self.compounds.append(cls)
            self.entities[cls.fqn] = cls
            self._refidmap[cls.refid] = cls
        elif kind == "struct":
            strct = Struct(cmpdef, self.entities, self._refidmap)
            self.compounds.append(strct)
            self.entities[strct.fqn] = strct
            self._refidmap[strct.refid] = strct
        elif kind == "file":
            file : File = File(cmpdef, self.entities)
            self.compounds.append(file)
            self._refidmap[file.refid] = file
        elif kind == "namespace":
            ns : Namespace = Namespace(cmpdef, self.entities, self._refidmap)
            self.compounds.append(ns)
            self.entities[ns.fqn] = ns
            self._refidmap[ns.refid] = ns
        else:
            raise ValueError("Unkown compound %s"%kind)
