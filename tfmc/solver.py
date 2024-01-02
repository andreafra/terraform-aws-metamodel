import itertools
from tfmc.encoding import (
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


def init(refs: Refs):
    ctx = z3.Context()
    s = z3.Solver(ctx=ctx)

    # MM
    cat_sort, cat_refs = encode_categories(refs.get_mm_categories(), ctx=ctx)
    ass_sort, ass_refs = encode_association_ids(refs.get_mm_associations(), ctx=ctx)
    att_sort, att_refs = encode_attribute_ids(refs.get_mm_attributes(), ctx=ctx)
    # IM
    ele_sort, ele_refs = encode_elements(refs.get_im_elements(), ctx=ctx)
    str_sort, str_refs = encode_strings(refs.get_im_attributes(), ctx=ctx)

    val_sort = define_value_sort(str_sort, ctx=ctx)

    # REL
    ele_cat_fn = define_category_function(ele_sort, cat_sort)
    assoc_fn = define_association_function(ass_sort, ele_sort, ctx=ctx)
    attr_fn = define_attribute_function(att_sort, ele_sort, val_sort, ctx=ctx)

    assert_categories(s, refs, ele_cat_fn, ele_refs, cat_refs)
    assert_associations(s, refs, assoc_fn, ass_refs, ass_sort, ele_refs)
    assert_attributes(
        s, refs, attr_fn, att_refs, att_sort, ele_refs, str_refs, val_sort
    )

    aws_instance, aws_secgroup = z3.Consts("aws_instance aws_secgroup", ele_sort)
    stmt = z3.And(
        ele_cat_fn(aws_instance) == cat_refs["aws_instance"],
        z3.Not(
            z3.Exists(
                [aws_secgroup],
                assoc_fn(
                    aws_instance,
                    ass_refs["aws_instance::vpc_security_group_ids"],
                    aws_secgroup,
                ),
            )
        ),
        s.ctx,
    )

    s.push()
    s.assert_and_track(stmt, "aws_instance_has_secgroup")
    res = s.check()
    print(res)
    s.pop()

    # s.assert_and_track(
    #     assoc_fn(
    #         ele_refs["aws_instance::this"],
    #         ass_refs["aws_instance::vpc_security_group_ids"],
    #         ele_refs["aws_security_group::this"],
    #     ),
    #     "p1",
    # )

    # s.assert_and_track(
    #     assoc_fn(
    #         ele_refs["aws_instance::this"],
    #         ass_refs["aws_instance::key_name"],
    #         ele_refs["aws_key_pair::this"],
    #     ),
    #     "p1",
    # )
    # print(s.sexpr())

    res = s.check()
    print(res)

    return s, res
