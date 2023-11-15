import z3

Z3RefsMap = dict[str, z3.DatatypeRef]


def encode_to_enumsort(
    name: str, items: list[str]
) -> tuple[z3.DatatypeSortRef, Z3RefsMap]:
    sort, datatype = z3.EnumSort(name, items)
    return sort, dict(zip(items, datatype))


# Metamodel Level
def encode_categories(categories):
    """Encodes a list of category names and returns a tuple containing the
    `Sort` and a `Map<category name, category datatype ref>`"""
    return encode_to_enumsort("Categories", categories)


def encode_associations(associations):
    return encode_to_enumsort("Associations", associations)


def encode_attributes(attributes):
    return encode_to_enumsort("Attributes", attributes)


# Intermediate Model Level
def encode_elements(elements):
    return encode_to_enumsort("Elements", elements)


def define_category_function():
    pass


def assert_categories():
    pass


def assert_associations():
    pass


def assert_attributes():
    pass
