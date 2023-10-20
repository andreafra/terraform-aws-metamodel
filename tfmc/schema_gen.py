from dataclasses import dataclass
from difflib import get_close_matches
from importlib.resources import files
import json
import re
import assets.schemas as schemas

"""
This module should take an AWS schema JSON file
generated with the terraform CLI:

`terraform providers schema -json > aws-schema.json`
"""

@dataclass
class AWS_schemas:
    resources: dict[str, dict]
    data_sources: dict[str, dict]

def _load_json_schema(data):
    schema = json.loads(data)
    aws = schema['provider_schemas']['registry.terraform.io/hashicorp/aws']
    aws_resource_schemas: dict[str, dict] = aws['resource_schemas']
    aws_data_source_schemas: dict[str, dict] = aws['data_source_schemas']

    return AWS_schemas(aws_resource_schemas, 
               aws_data_source_schemas)

def _get_possible_attrs_keys(attrs: dict, res_k: str):
    """
    Iterate attributes of a resource to find possible references to other resources.
    Their type should be 'string'.
    """
    return [k for k, v in attrs.items() 
                      if 'string' in v['type'] 
                      and k != res_k
                      and not k.endswith('_state')
                      and not k.endswith('_type') ]

def _add_mm_type_to_attributes(attrs, fk_attrs, res_k):
    """
    Add an attribute 'mm_type' to attributes that refer to another resource,
    with the infered type of that resource.
    """
    attrs_keys = _get_possible_attrs_keys(attrs, res_k)
    for k in attrs_keys:
        if fk_attrs_for_k := get_close_matches(k, [fk for fk in fk_attrs if fk in k]):
            # assign the best match as 'mm_type'
            attrs[k]['mm_type'] = f'aws_{fk_attrs_for_k[0]}'

def decorate_resource_schema_with_typed_associations(resources):
    """Returns an annotated schema with Terraform resource types"""
    for res_k, res_v in resources.items():
        # Get foreign keys stripped of the 'aws_' prefix
        fk_attrs = fk_attrs = [re.sub(r'^aws_', '', fk) for fk in resources.keys()]

        res_attrs = res_v['block'].get('attributes', {})

        _add_mm_type_to_attributes(res_attrs, fk_attrs, res_k)
        
        res_blocktypes = res_v['block'].get('block_types', {})
        for _, bt_v in res_blocktypes.items():
            if bt_attrs := bt_v['block'].get('attributes', {}):
                _add_mm_type_to_attributes(bt_attrs, fk_attrs, res_k)
    
    return resources

def generate_schema():
    schema = files(schemas).joinpath('aws-schema.json').read_text()
    aws_schemas = _load_json_schema(schema)
    return decorate_resource_schema_with_typed_associations(aws_schemas.resources)