from dataclasses import make_dataclass
from os import PathLike
from pprint import pprint
from typing import ForwardRef, get_type_hints
import erdantic as erd

from tfmc.resource_class import Refs


def get_model_resources(refs: Refs):
    res = []
    # get actual resources used in the input model
    used_cats = [r.category for r in refs.im_resources.values()]
    # get resources that have a relationship with the used resources
    # TOO MANY
    # neighbour_cats = {
    #     nck: ncv
    #     for uc in used_cats
    #     for nck, ncv in refs.schema.associations.items()
    #     if ncv.get("mm_type") == uc
    # }
    pprint(used_cats)
    cats = used_cats
    for cat in cats:
        fields = [
            (ak, ForwardRef(av["mm_type"]))
            for ak, av in refs.schema.associations.items()
            if av.get("from") == cat
        ]
        get_type_hints(fields)
        dc = make_dataclass(cat, fields)
        res.append(dc)
    return res


def visualize(refs: Refs, out):
    mrs = get_model_resources(refs)

    diagram = erd.create(*mrs)
    diagram.draw(out)
