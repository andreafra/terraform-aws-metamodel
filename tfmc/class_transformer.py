# This module should take an annotated schema as input and return
# a collection of standardized resources.

from dataclasses import dataclass

@dataclass
class Attribute:
    id: str
    value: any
    type: any

    def encode(self):
        pass

@dataclass
class Association:
    id: str
    target: 'Resource'
    
    def encode(self):
        pass

@dataclass
class Resource:
    id: str
    attrs: set[Attribute]
    assocs: set[Association]

    # generate z3
    def encode(self):
        # TODO: Encode into a Z3 rule
        pass