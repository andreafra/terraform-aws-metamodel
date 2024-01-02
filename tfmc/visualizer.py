from dataclasses import make_dataclass
import os
from pprint import pprint
from python_mermaid.diagram import MermaidDiagram, Node, Link

from tfmc.resource_class import Refs


def get_mm_nodes(refs: Refs):
    # get actual resources used in the input model
    used_cats = [r.category for r in refs.im_resources.values()]
    used_cats = list(set(used_cats))
    # get resources that have a relationship with the used resources
    # TOO MANY
    # neighbour_cats = {
    #     nck: ncv
    #     for uc in used_cats
    #     for nck, ncv in refs.schema.associations.items()
    #     if ncv.get("mm_type") == uc
    # }
    print("used_cats:")
    pprint(used_cats)
    return [Node(c) for c in used_cats]


def get_mm_links(refs: Refs, nodes: list[Node]) -> list[Link]:
    links = []
    # for each category fetch their associations
    for node in nodes:
        for k, v in refs.schema.associations.items():
            if v.get("from") == node.id:
                links.append(
                    Link(node, Node(v.get("mm_type")), message=k.removeprefix(node.id))
                )

    return links


def get_im_nodes(refs: Refs) -> list[Node]:
    return [Node(e) for e in refs.get_im_elements()]


def get_im_links(refs: Refs, nodes: list[Node]) -> list[Link]:
    links = []
    for node in nodes:
        for assn in refs.get_im_associations():
            if assn.id.startswith(node.id):
                links += [
                    Link(node, Node(target.id), message=assn.schema_type)
                    for target in assn.target_refs
                ]

    return links


def visualize(refs: Refs, outdir=None):
    """If `outdir` is present, the text representation of diagram will be saved in that folder."""
    mm_nodes = get_mm_nodes(refs)
    mm_links = get_mm_links(refs, mm_nodes)

    im_nodes = get_im_nodes(refs)
    im_links = get_im_links(refs, im_nodes)

    mm_diag = MermaidDiagram("Metamodel", mm_nodes, mm_links)
    im_diag = MermaidDiagram("Model", im_nodes, im_links)

    if outdir:
        with open(os.path.join(outdir, "mmdiag.txt"), "w") as f:
            f.write(str(mm_diag))
        with open(os.path.join(outdir, "imdiag.txt"), "w") as f:
            f.write(str(im_diag))

    return mm_diag, im_diag
