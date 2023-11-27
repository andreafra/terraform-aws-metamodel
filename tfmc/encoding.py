import itertools
import z3

from tfmc.resource_class import Refs

Z3RefsMap = dict[str, z3.DatatypeRef]


def encode_to_enumsort(
    name: str, items: list[str]
) -> tuple[z3.DatatypeSortRef, Z3RefsMap]:
    sort, datatype = z3.EnumSort(name, items)
    return sort, dict(zip(items, datatype))


# Metamodel Level
def encode_categories(categories: list[str]):
    """Encodes a list of category names and returns a tuple containing the
    `Sort` and a `Map<category name, category datatype ref>`"""
    return encode_to_enumsort(name="Categories", items=categories)


def encode_association_ids(assoc_refs: list[str]):
    return encode_to_enumsort(name="Associations", items=assoc_refs)


def encode_attribute_ids(attributes: list[str]):
    return encode_to_enumsort(name="Attributes", items=attributes)


# Intermediate Model Level
def encode_elements(elements: list[str]):
    return encode_to_enumsort("Elements", elements)


def define_category_function(
    elem_sort: z3.DatatypeSortRef,
    cat_sort: z3.DatatypeSortRef,
):
    return z3.Function("elem_category", elem_sort, cat_sort)


def define_association_function(
    assoc_sort: z3.DatatypeSortRef, elem_sort: z3.DatatypeSortRef
):
    return z3.Function(
        "association", elem_sort, assoc_sort, elem_sort, z3.BoolSort(ctx=elem_sort.ctx)
    )


def assert_categories(
    solver: z3.Solver,
    refs: Refs,
    elem_cat_fn: z3.FuncDeclRef,
    element_refs: Z3RefsMap,
    category_refs: Z3RefsMap,
):
    for id, elem in refs.im_resources.items():
        a = elem_cat_fn(element_refs[id]) == category_refs[elem.category]
        solver.assert_and_track(a, f"elem_cat {id} {elem.category}")


def assert_associations(
    solver: z3.Solver,
    refs: Refs,
    assoc_rel: z3.FuncDeclRef,
    assoc_refs: Z3RefsMap,
    assoc_sort: z3.DatatypeSortRef,
    elem_refs: Z3RefsMap,
):
    """ """
    im_assocs = refs.im_resources.items()
    a = z3.Const("a", assoc_sort)
    # for every possible A <-> B association...
    for (id1, elem1), (id2, elem2) in itertools.product(im_assocs, im_assocs):
        expr = z3.ForAll(
            [a],
            assoc_rel(elem_refs[id1], a, elem_refs[id2])
            == z3.Or(
                *(
                    a == assoc_refs[elem1_assoc.schema_type]
                    for elem1_assoc in elem1.assocs
                    if elem2 == elem1_assoc
                ),
                solver.ctx,
            ),
        )
        solver.assert_and_track(expr, f"association {id1} {id2}")


def assert_attributes():
    pass
