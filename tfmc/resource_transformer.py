# This module should take an annotated schema as input and return
# a collection of standardized resources.

from tfmc.resource_class import Association, Attribute, Refs, Resource
from functools import reduce


def transform_resources(resources: dict, schema: dict):
    refs = Refs(schema, {}, {})

    # Transform Resources
    for category_and_id, props in resources.items():
        # only way to retrieve the user-assigned resource name
        [category, id] = category_and_id.split(".")

        # just a double check to not get weird parsed stuff
        assert category == props.get("__tfmeta").get("label")

        # check if metamodel specify this category
        add_transform_resource(
            f"{category}::{id}", category, props, refs.schema.get(category), refs
        )

    return refs


def add_transform_resource(
    id: str, category: str, props: dict, schema: dict, refs: Refs
) -> None:
    res = Resource(id, category, [], [], tfmeta=props["__tfmeta"])

    for prop_key, prop in props.items():
        # Skip __tfmeta, not a real property
        if prop_key == "__tfmeta":
            continue
        prop_id = f"{id}::{prop_key}"

        # look up in the schema if the property is an assoc/attr or a block
        res_schema = schema.get("block")
        if attr_schema := res_schema.get("attributes", {}).get(prop_key):
            instance = classify_and_transform_prop(prop_id, prop, attr_schema)
            if isinstance(instance, Association):
                res.assocs.append(instance)
            else:
                res.attrs.append(instance)

        elif nested_block_schema := res_schema.get("block_types", {}).get(prop_key):
            handle_nested_block(prop_id, prop_key, prop, nested_block_schema, res, refs)

    refs.im_resources[id] = refs.im_uuids[props.get("id")] = res

    return res


def handle_nested_block(
    id: str,
    category: str,
    nested_block: list[dict] | dict,
    schema: dict,
    parent_resource: Resource,
    refs: Refs,
):
    """Recursively transform nested elements."""
    assoc = Association(id, [], f"{parent_resource.category}::{category}")
    if isinstance(nested_block, list):
        for block in nested_block:
            assoc.targets.append(
                add_transform_resource(id, category, block, schema, refs)
            )
    elif isinstance(nested_block, dict):
        assoc.targets.append(
            add_transform_resource(id, category, nested_block, schema, refs)
        )
    # add associations from parent->child
    parent_resource.assocs.append(assoc)


def classify_and_transform_prop(prop_id, prop_value, prop_schema):
    """Returns the correct transformation of a property as either an Association or an Attribute.
    `prop_key` is guaranteed to exist, here we check if `prop_schema` has `mm_type` or not
    to determine whether its"""
    if mm_type := prop_schema.get("mm_type"):
        # it's an association
        return Association(prop_id, get_assoc_refs(prop_value), mm_type)
    else:
        # it's an attribute
        # TODO: Handle composite types (e.g. ['map', 'string']) # DO THIS FIRST
        return Attribute(prop_id, prop_value, prop_schema.get("type"))


def get_assoc_refs(value) -> list[str]:
    if isinstance(value, list):
        return reduce(list.__add__, map(get_assoc_refs, value))
    else:
        if isinstance(value, dict):
            return [value.get("__ref__")]
        elif isinstance(value, str):
            return [value]
        else:
            print(f"[Error] Unknown assoc type found: ({type(value)}) {value}")
            raise "Unknown or invalid association!"
