import z3

Z3RefsMap = dict[str, z3.DatatypeRef]


def encode_categories(categories: list[str]) -> tuple[z3.DatatypeSortRef, Z3RefsMap]:
    """Encodes a list of category names and returns a tuple containing the
    `Sort` and a `Map<category name, category datatype ref>`"""
    datatype_sort_ref, datatype_refs = z3.EnumSort("Category", categories)
    return datatype_sort_ref, dict(zip(categories, datatype_refs))


def encode_associations(
    associations: list[str],
) -> tuple[z3.DatatypeSortRef, Z3RefsMap]:
    pass


def encode_attributes(attributes: list[str]) -> tuple[z3.DatatypeSortRef, Z3RefsMap]:
    pass
