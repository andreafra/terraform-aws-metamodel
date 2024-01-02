from collections.abc import Callable
from dataclasses import dataclass
from difflib import get_close_matches
from importlib.resources import files
import json
import re
from typing import Any
import assets.schemas as schemas
import yaml
from yaml import Loader as YamlLoader
from json import JSONDecoder, JSONEncoder

"""
This module should take an AWS schema JSON file
generated with the terraform CLI:

`terraform providers schema -json > aws-schema.json`
"""


@dataclass
class AWS_schemas:
    resources: dict[str, dict]
    data_sources: dict[str, dict]


@dataclass
class Schema:
    categories: list[str]
    associations: dict[str, dict]
    attributes: dict[str, dict]


class SchemaEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        return o.__dict__


def decode_schema(raw_schema) -> Schema:
    return Schema(
        raw_schema["categories"],
        raw_schema["associations"],
        raw_schema["attributes"],
    )


def load_json_schema(data):
    schema = json.loads(data)
    aws = schema["provider_schemas"]["registry.terraform.io/hashicorp/aws"]
    aws_resource_schemas: dict[str, dict] = aws["resource_schemas"]
    aws_data_source_schemas: dict[str, dict] = aws["data_source_schemas"]

    return AWS_schemas(aws_resource_schemas, aws_data_source_schemas)


def get_possible_attrs_keys(attrs: dict, res_k: str, blacklist: list[str]):
    """
    Iterate attributes of a resource to find possible references to other resources.
    Their type should be 'string'.
    """

    return [
        k
        for k, v in attrs.items()
        if "string" in v["type"]
        and k != res_k
        and not k.endswith("_state")
        and not k.endswith("_type")
        and k not in blacklist
    ]


def add_mm_type_to_attributes(attrs, fk_attrs, res_k, custom_fks):
    """
    Add an attribute 'mm_type' to attributes that refer to another resource,
    with the infered type of that resource.
    """

    whitelist = custom_fks.get("whitelist") or {}
    blacklist = custom_fks.get("blacklist") or {}

    attrs_keys = get_possible_attrs_keys(attrs, res_k, blacklist)
    for k in attrs_keys:
        if fk_attrs_for_k := get_close_matches(k, [fk for fk in fk_attrs if fk in k]):
            # assign the best match as 'mm_type'
            attrs[k] = {"mm_type": f"aws_{fk_attrs_for_k[0]}", "mm_from": res_k}

    if res_k in whitelist:
        for k, v in whitelist[res_k].items():
            if k in attrs:
                attrs[k] = {"mm_type": v, "mm_from": res_k}


def add_typed_associations_to_attrs(resources, custom_fks=None):
    """Returns an annotated schema with Terraform resource types"""
    # Get foreign keys stripped of the 'aws_' prefix
    fk_attrs = [re.sub(r"^aws_", "", fk) for fk in resources.keys()]

    # For each resource, get its attributes and nested resources
    for res_k, res_v in resources.items():
        res_attrs = res_v["block"].get("attributes", {})

        add_mm_type_to_attributes(res_attrs, fk_attrs, res_k, custom_fks)

        res_blocktypes = res_v["block"].get("block_types", {})
        for _, bt_v in res_blocktypes.items():
            if bt_attrs := bt_v["block"].get("attributes", {}):
                add_mm_type_to_attributes(bt_attrs, fk_attrs, res_k, custom_fks)

    return resources


def flatten_schema(schema: dict) -> Schema:
    """Flattens the metamodel into categories, associations and attributes, and returns a Schema instance containing the three."""
    categories = []
    associations = {}
    attributes = {}

    def handle_block(rk, rv, parentk=""):
        props = rv.get("block")
        categories.append(rk)
        all_attrs = props.get("attributes", {})
        for k, v in all_attrs.items():
            propkey = f"{rk}::{k}"  #
            if existing_v := associations.get(propkey):
                if existing_v != v:
                    if parentk != "":
                        propkey = f"{parentk}>>{propkey}"
            if v.get("mm_type"):
                associations[propkey] = v
            else:
                attributes[propkey] = v
        # add assoc for nested blocks
        # TODO: Why do some nested blocks have an empty parent?
        if parentk != "":
            associations[f"{parentk}::{rk}"] = {
                "type": "list",
                "mm_from": parentk or None,
                "mm_type": rk,
                "mm_nested_block": True,
            }

        # handle nested blocks
        nested_blocks = props.get("block_types", {})
        for nbk, nbv in nested_blocks.items():
            handle_block(nbk, nbv, rk)

    # apply to top level
    for rk, rv in schema.items():
        handle_block(rk, rv)

    categories = list(set(categories))
    categories.sort()

    return Schema(categories, associations, attributes)


def generate_schema() -> Schema:
    """Generates an annotated schema starting from the `aws-schema.json` input file
    in the `assets` resource folder."""
    schema = files(schemas).joinpath("aws-schema.json").read_text()
    aws_schemas = load_json_schema(schema)

    custom_fks = yaml.load(
        files(schemas).joinpath("custom.yaml").read_text(), Loader=YamlLoader
    )

    typed_schema = add_typed_associations_to_attrs(aws_schemas.resources, custom_fks)

    flat_schema = flatten_schema(typed_schema)

    return flat_schema
