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
    target_ids: list['Resource']
    type: str

    def encode(self):
        pass

@dataclass
class Resource:
    id: str
    category: str
    attrs: set[Attribute]
    assocs: set[Association]

    # generate z3
    def encode(self):
        # TODO: Encode into a Z3 rule
        pass

def transform(category, id, data, schema):
    attrs = []
    assocs = []

    for k, v in data.items():
        match get_resource_attrs(schema, k):
            case 'assoc', schema_data:
                assocs.append(Association(
                    f'{category}::{id}::{k}',
                    v if isinstance(v, list) else [v],
                    schema_data.get('mm_type')
                ))
            case 'attr', schema_data:
                attrs.append(Attribute(
                    f'{category}::{id}::{k}',
                    v,
                    schema_data.get('type')
                ))
            case _:
                print(f'[{category}::{id}::{k}] Skipping unsupported type...')

    return Resource(f'{category}::{id}', category, attrs, assocs)

def get_resource_attrs(schema, key):
    if schema_data := schema['block']['attributes'].get(key):
        if schema_data.get('mm_type'):
            return 'assoc', schema_data
        else:
            return 'attr', schema_data
    elif schema_data := schema['block']['block_types'].get(key):
        # It's a nested block
        # Should it be instanced separately?
        return None
    return None