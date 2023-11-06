# This module should take an annotated schema as input and return
# a collection of standardized resources.

from dataclasses import dataclass
from termcolor import colored

from tfmc.template_parser import parse_template_string
@dataclass
class Attribute:
    id: str
    value: any
    type: any

    def encode(self):
        pass

    def __repr__(self) -> str:
        return f"{colored(self.id, 'yellow')}[{colored(self.type, 'light_green')}]={colored(self.value, 'cyan')}"

@dataclass
class Association:
    id: str
    target_ids: list['Resource']
    type: str

    def encode(self):
        pass

    def __repr__(self) -> str:
        return f"{colored(self.id, 'magenta')}[{colored(self.type, 'light_green')}]={colored(self.target_ids, 'cyan')}"

@dataclass
class Resource:
    id: str
    category: str
    attrs: set[Attribute]
    assocs: set[Association]
    tfmeta: dict

    # generate z3
    def encode(self):
        # TODO: Encode into a Z3 rule
        pass

    def __repr__(self) -> str:
        return (f'{self.id}:\n\tattrs:\n\t' 
                + '\n\t'.join([repr(x) for x in self.attrs] if self.attrs else '')
                + '\n\tassocs:\n\t'
                + '\n\t'.join([repr(x) for x in self.assocs]) if self.assocs else '')

def transform(category, id, props, model, schema):
    attrs = []
    assocs = []

    for k, v in props.items():
        # try to resolve string templates
        # if isinstance(v, list):
        #     v = [parse_template_string(x, model) for x in v]
        # else:
        #     v = parse_template_string(v, model)
        if k != '__tfmeta':
            _id = f'{category}::{id}::{k}'
            match get_resource_attrs(schema, k):
                case 'assoc', schema_data:
                    assocs.append(Association(
                        _id,
                        get_assoc_refs(v),
                        schema_data.get('mm_type')
                    ))
                case 'attr', schema_data:
                    attrs.append(Attribute(
                        _id,
                        v,
                        schema_data.get('type')
                    ))
                case 'nested_block':
                    print(f'[{category}::{id}::{k}] Skipping nested block (to be implemented)...')
                case _:
                    print(f'[{category}::{id}::{k}] Skipping unsupported type...')

    return Resource(f'{category}::{id}', category, attrs, assocs, props.get('__tfmeta'))

def get_assoc_refs(value) -> list[str]:
    if isinstance(value, list):
        map(get_assoc_refs, value)
    else:
        if isinstance(value, dict):
            return value.get('__ref__')
        elif isinstance(value, str):
            return value
        else:
            raise f'Unknown assoc type found: ({type(value)}) {value}'
    return None

def get_resource_attrs(schema, key):
    if schema_data := schema['block']['attributes'].get(key):
        if schema_data.get('mm_type'):
            return 'assoc', schema_data
        else:
            return 'attr', schema_data
    elif schema_data := schema['block']['block_types'].get(key):
        # It's a nested block
        # Should it be instanced separately?
        return 'nested_block'
    return None