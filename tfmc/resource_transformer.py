# This module should take an annotated schema as input and return
# a collection of standardized resources.

from tfmc.resource_class import Association, Attribute, Refs, Resource
from functools import reduce

from tfmc.schema_gen import Schema


def transform_resources(resources: dict, schema: Schema):
    refs = Refs(schema, {}, {})

    # Transform Resources
    for category_and_id, props in resources.items():
        try:
            # only way to retrieve the user-assigned resource name
            [category, id] = category_and_id.split(".")

            # just a double check to not get weird parsed stuff
            assert category == props.get("__tfmeta").get("label")

            # check if metamodel specify this category
            add_transform_resource(
                f"{category}::{id}",
                category,
                props,
                refs,
            )
        except ValueError:
            print(
                f"Failed to obtain category and id for resource '{category_and_id}'. Skipping..."
            )

    return refs


def add_transform_resource(id: str, category: str, props: dict, refs: Refs) -> Resource:
    res = Resource(id, category, [], [], tfmeta=props["__tfmeta"])

    for prop_key, prop in props.items():
        # Skip __tfmeta, not a real property
        if prop_key == "__tfmeta":
            continue
        prop_id = f"{id}::{prop_key}"

        # look up in the schema if the property is an assoc/attr or a block
        schema_prop_id = f"{category}::{prop_key}"

        if attr_schema := refs.schema.attributes.get(schema_prop_id):
            # TODO: handle 'prop' when has a weird type!
            res.attrs.append(Attribute(prop_id, prop, attr_schema.get("type"), schema_prop_id))  # type: ignore
        elif assoc_schema := refs.schema.associations.get(schema_prop_id):
            if not assoc_schema.get("mm_nested_block"):
                res.assocs.append(
                    Association(
                        prop_id,
                        get_assoc_refs(prop),
                        [],
                        assoc_schema.get("mm_type"),  # type: ignore
                        schema_prop_id,
                    )
                )
            else:
                handle_nested_block(prop_id, prop_key, prop, res, refs)

    refs.im_resources[id] = refs.im_uuids[str(props.get("id"))] = res

    return res


def handle_nested_block(
    id: str,
    category: str,
    nested_block: list[dict] | dict,
    parent_resource: Resource,
    refs: Refs,
):
    """Recursively transform nested elements."""
    assoc = Association(
        id,
        [],
        [],
        f"{parent_resource.category}::{category}",
        f"{parent_resource.category}::{category}",
    )
    if isinstance(nested_block, list):
        for block in nested_block:
            assoc.target_refs.append(
                add_transform_resource(id, category, props=block, refs=refs)
            )
    elif isinstance(nested_block, dict):
        assoc.target_refs.append(
            add_transform_resource(id, category, props=nested_block, refs=refs)
        )
    # add associations from parent->child
    parent_resource.assocs.append(assoc)


def get_assoc_refs(value) -> list[str]:
    if isinstance(value, list):
        if not value:
            return []
        return reduce(list.__add__, map(get_assoc_refs, value))
    else:
        if isinstance(value, dict):
            return [str(value.get("__ref__"))]
        elif isinstance(value, str):
            return [value]
        else:
            print(f"[Error] Unknown assoc type found: ({type(value)}) {value}")
            raise InvalidAssociationException()


class InvalidAssociationException(BaseException):
    pass
