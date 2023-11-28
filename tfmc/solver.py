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
    s = z3.Solver()

    # MM
    cat_sort, cat_refs = encode_categories(refs.get_mm_categories())
    ass_sort, ass_refs = encode_association_ids(refs.get_mm_associations())
    att_sort, att_refs = encode_attribute_ids(refs.get_mm_attributes())
    # IM
    ele_sort, ele_refs = encode_elements(refs.get_im_elements())
    str_sort, str_refs = encode_strings(refs.get_im_attributes())

    val_sort = define_value_sort(str_sort)

    # REL
    ele_cat_fn = define_category_function(ele_sort, cat_sort)
    assoc_fn = define_association_function(ass_sort, ele_sort)
    attr_fn = define_attribute_function(att_sort, ele_sort, val_sort)

    assert_categories(s, refs, ele_cat_fn, ele_refs, cat_refs)
    assert_associations(s, refs, assoc_fn, ass_refs, ass_sort, ele_refs)
    assert_attributes(
        s, refs, attr_fn, att_refs, att_sort, ele_refs, str_refs, val_sort
    )

    return s
