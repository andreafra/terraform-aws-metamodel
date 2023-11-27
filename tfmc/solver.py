from tfmc.encoding import (
    assert_associations,
    assert_categories,
    define_association_function,
    define_category_function,
    encode_association_ids,
    encode_attribute_ids,
    encode_categories,
    encode_elements,
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

    cat_sort, cat_refs = encode_categories(refs.get_mm_categories())
    ass_sort, ass_refs = encode_association_ids(refs.get_mm_associations())
    att_sort, att_refs = encode_attribute_ids(refs.get_mm_attributes())

    ele_sort, ele_refs = encode_elements(refs.get_im_elements())

    ele_cat_fn = define_category_function(ele_sort, cat_sort)

    assoc_fn = define_association_function(ass_sort, ele_sort)

    assert_categories(s, refs, ele_cat_fn, ele_refs, cat_refs)

    assert_associations(s, refs, assoc_fn, ass_refs, ass_sort, ele_refs)

    return s
