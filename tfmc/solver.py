from collections.abc import Callable
from dataclasses import dataclass
import logging
from unicodedata import category
from tfmc.encoding import (
    Z3RefsMap,
    assert_associations,
    assert_attributes,
    assert_categories,
    define_association_function,
    define_attribute_function,
    define_category_function,
    define_value_sort,
    encode_association_ids,
    encode_attribute_ids,
    encode_categories,
    encode_elements,
    encode_strings,
)
from tfmc.resource_class import Refs
import z3
from tfmc.rules import requirements
from tfmc.solver_class import (
    SolverContext,
    SolverFunctions,
    SolverRefs,
    SolverResult,
    SolverSorts,
)

"""
SETTING UP Z3 AND BUILDING INTERMEDIATE MODEL ENCODING

* Create Solver Instance
* Create Encoding (as Enum) for:
    * Resource Category
    * Associations
    * Attributes
* Create Elements
    * Elements (as Enum)
* Create Relationships
    * Associations
    * Attributes

"""


def init(refs: Refs, enable_attributes=True):
    ctx = z3.Context()
    s = z3.Solver(ctx=ctx)

    # MM
    cat_sort, cat_refs = encode_categories(refs.get_mm_categories(), ctx=ctx)
    ass_sort, ass_refs = encode_association_ids(refs.get_mm_associations(), ctx=ctx)
    att_sort, att_refs = None, None
    # IM
    ele_sort, ele_refs = encode_elements(refs.get_im_elements(), ctx=ctx)
    str_sort, str_refs = None, None
    val_sort = None
    # REL
    ele_cat_fn = define_category_function(ele_sort, cat_sort)
    assoc_fn = define_association_function(ass_sort, ele_sort, ctx=ctx)
    attr_fn = None

    if enable_attributes:
        # MM
        att_sort, att_refs = encode_attribute_ids(refs.get_mm_attributes(), ctx=ctx)
        # IM
        str_sort, str_refs = encode_strings(refs.get_im_attributes(), ctx=ctx)
        # this depends on str_sort, since it wraps (int, bool, str_sort)
        val_sort = define_value_sort(str_sort, ctx=ctx)
        # REL
        attr_fn = define_attribute_function(att_sort, ele_sort, val_sort, ctx=ctx)

    # Save above references into a shared object
    sctx = SolverContext(
        solver=s,
        sort=SolverSorts(cat_sort, ass_sort, att_sort, ele_sort, str_sort, val_sort),
        ref=SolverRefs(cat_refs, ass_refs, att_refs, ele_refs, str_refs),
        fn=SolverFunctions(ele_cat_fn, assoc_fn, attr_fn),
    )

    assert_categories(sctx, refs)
    assert_associations(sctx, refs)

    if enable_attributes:
        assert_attributes(sctx, refs)

    return sctx


def check_requirements(sctx: SolverContext):
    results: list[SolverResult] = []  # res, negate_form

    for req in requirements:
        sctx.solver.push()
        req_text, negate_form, error_fn = req(sctx)
        error_msg = ""
        result = sctx.solver.check()
        if (result == z3.unsat and not negate_form) or (
            result == z3.sat and negate_form
        ):
            error_msg = error_fn()
            print(f'Requirement UNSAT: "{req_text}"\n{error_msg}')
            result = False
        else:
            result = True
        results.append(SolverResult(result, negate_form, error_msg))
        sctx.solver.pop()

    return results
