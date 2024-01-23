import itertools
import z3

from tfmc.resource_class import Attribute, Refs
from tfmc.solver_class import SolverContext, Z3RefsMap


def encode_to_enumsort(
    name: str, items: list[str], ctx: z3.Context
) -> tuple[z3.DatatypeSortRef, Z3RefsMap]:
    sort, datatype = z3.EnumSort(name, items, ctx=ctx)
    return sort, dict(zip(items, datatype))


# Metamodel Level
def encode_categories(categories: list[str], ctx: z3.Context):
    """Encodes a list of category names and returns a tuple containing the
    `Sort` and a `Map<category name, category datatype ref>`"""
    return encode_to_enumsort(name="Categories", items=categories, ctx=ctx)


def encode_association_ids(assoc_refs: list[str], ctx: z3.Context):
    return encode_to_enumsort(name="Associations", items=assoc_refs, ctx=ctx)


def encode_attribute_ids(attributes: list[str], ctx: z3.Context):
    return encode_to_enumsort(name="Attributes", items=attributes, ctx=ctx)


# Intermediate Model Level
def encode_elements(elements: list[str], ctx: z3.Context):
    return encode_to_enumsort("Elements", elements, ctx=ctx)


def encode_strings(attributes: list[Attribute], ctx: z3.Context):
    strings: list[str] = list(
        set(
            [
                str(x.value)
                for x in attributes
                if x.type == "string" and x.value is not None
            ]
        )
    )
    return encode_to_enumsort(name="Strings", items=strings, ctx=ctx)


def define_value_sort(string_sort: z3.DatatypeSortRef, ctx: z3.Context):
    s = z3.Datatype("Value", ctx=ctx)
    s.declare("none")
    s.declare("number", ("get_number", z3.IntSort(ctx=ctx)))
    s.declare("bool", ("get_bool", z3.BoolSort(ctx=ctx)))
    s.declare("string", ("get_string", string_sort))
    return s.create()


def define_category_function(
    elem_sort: z3.DatatypeSortRef, cat_sort: z3.DatatypeSortRef
):
    return z3.Function("elem_category", elem_sort, cat_sort)


def define_association_function(
    assoc_sort: z3.DatatypeSortRef, elem_sort: z3.DatatypeSortRef, ctx: z3.Context
):
    return z3.Function(
        "association", elem_sort, assoc_sort, elem_sort, z3.BoolSort(ctx=ctx)
    )


def define_attribute_function(
    attr_sort: z3.DatatypeSortRef,
    elem_sort: z3.DatatypeSortRef,
    value_sort: z3.DatatypeSortRef,
    ctx: z3.Context,
):
    return z3.Function(
        "attribute", elem_sort, attr_sort, value_sort, z3.BoolSort(ctx=ctx)
    )


def assert_categories(sctx: SolverContext, refs: Refs):
    for id, elem in refs.im_resources.items():
        a = sctx.fn.category(sctx.ref.element[id]) == sctx.ref.category[elem.category]
        sctx.solver.assert_and_track(a, f"elem_cat {id} {elem.category}")


def assert_associations(
    sctx: SolverContext,
    refs: Refs,
):
    im_assocs = refs.im_resources.items()
    a = z3.Const("a", sctx.sort.association)
    # for every possible A <-> B association...
    for (id1, elem1), (id2, elem2) in itertools.product(im_assocs, im_assocs):
        expr = z3.ForAll(
            [a],
            sctx.fn.association(sctx.ref.element[id1], a, sctx.ref.element[id2])
            == z3.Or(
                *(
                    a == sctx.ref.association[elem1_assoc.schema_type]
                    for elem1_assoc in elem1.assocs
                    if elem2 in elem1_assoc.target_refs
                ),
                sctx.solver.ctx,
            ),
        )
        sctx.solver.assert_and_track(expr, f"association {id1} {id2}")


def assert_attributes(
    sctx: SolverContext,
    refs: Refs,
):
    # encode attribute data
    def encode_value(val: str | int | bool) -> z3.DatatypeRef:
        if type(val) is str:
            return sctx.sort.value.string(sctx.ref.string[val])  # type: ignore
        elif type(val) is int:
            return sctx.sort.value.number(val)  # type: ignore
        elif type(val) is bool:
            return sctx.sort.value.bool(val)  # type: ignore
        else:
            return sctx.sort.value.none  # type: ignore

    a = z3.Const("a", sctx.sort.attribute)
    v = z3.Const("v", sctx.sort.value)

    for res_id, res in refs.im_resources.items():
        if res.attrs:
            expr = z3.ForAll(
                [a, v],
                sctx.fn.attribute(sctx.ref.element[res_id], a, v)
                == z3.Or(
                    *(
                        z3.And(
                            a == sctx.ref.attribute[attr.schema_type],
                            v == encode_value(attr.value),
                        )
                        for attr in res.attrs
                    ),
                    sctx.solver.ctx,
                ),
            )
        else:
            expr = z3.ForAll(
                [a, v], z3.Not(sctx.fn.attribute(sctx.ref.element[res_id], a, v))
            )
        sctx.solver.assert_and_track(expr, f"attribute_value {res_id}")


def get_user_friendly_name(sctx: SolverContext, const: z3.ExprRef):
    model = sctx.solver.model()
    z3_elem = model[const]
    if z3_elem is not None:
        return str(z3_elem)
