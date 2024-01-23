from dataclasses import make_dataclass
import os
from pprint import pprint
from re import match
from plantweb.render import render

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
    return used_cats


def get_mm_links(
    refs: Refs, nodes: list[str], summarize_mm: bool = False
) -> list[tuple[str, str, str]]:
    links = []
    im_assocs = refs.get_im_associations()
    # for each category fetch their associations
    for node in nodes:
        for k, v in refs.schema.associations.items():
            # alternative: match(f"^{node.id}::.*", k):
            if v.get("mm_from") == node and (
                # look in the IM to see which relationships are relevant
                not summarize_mm
                or k in [kid.schema_type for kid in im_assocs]
            ):
                links.append(
                    (
                        node,
                        v.get("mm_type"),
                        k.removeprefix(node),
                    )
                )

    return links


def get_im_nodes(refs: Refs) -> list[str]:
    return refs.get_im_elements()


def get_im_links(refs: Refs, nodes: list[str]) -> list[str]:
    links = []
    for node in nodes:
        for assn in refs.get_im_associations():
            if assn.id.startswith(node):
                links += [
                    (node, target.id, assn.schema_type) for target in assn.target_refs
                ]

    return links


def make_plantuml_diag(nodes, links):
    all_nodes = set()
    all_links = set()
    content = "@startuml\n"
    content += "left to right direction\n"
    for node in nodes:
        all_nodes.add(node)
    for link_from, link_to, _ in links:
        all_nodes.add(link_from)
        all_nodes.add(link_to)
    for node in all_nodes:
        content += "[node]\n"
    content += "\n"
    for link_from, link_to, link_label in links:
        link_from = str(link_from).replace("[", "(").replace("]", ")")
        link_to = str(link_to).replace("[", "(").replace("]", ")")
        all_links.add(f'[{link_from}] --> [{link_to}] : {link_label}"\n')
    for link in all_links:
        content += link
    content += "@enduml"
    return content


def visualize(refs: Refs, outdir=None):
    """If `outdir` is present, the text representation of diagram will be saved in that folder."""
    mm_nodes = get_mm_nodes(refs)
    mm_links = get_mm_links(refs, mm_nodes, summarize_mm=False)
    mm_links_min = get_mm_links(refs, mm_nodes, summarize_mm=True)

    im_nodes = get_im_nodes(refs)
    im_links = get_im_links(refs, im_nodes)

    mm_diag_src = make_plantuml_diag(mm_nodes, mm_links)
    mm_diag_min_src = make_plantuml_diag(mm_nodes, mm_links_min)
    im_diag_src = make_plantuml_diag(im_nodes, im_links)

    mm_diag_svg, _, _, _ = render(
        mm_diag_src,
        engine="plantuml",
        format="svg",
        cacheopts={"use_cache": False},
    )
    mm_diag_min_svg, _, _, _ = render(
        mm_diag_min_src,
        engine="plantuml",
        format="svg",
        cacheopts={"use_cache": False},
    )
    im_diag_svg, _, _, _ = render(
        im_diag_src,
        engine="plantuml",
        format="svg",
        cacheopts={"use_cache": False},
    )

    if outdir:
        with open(os.path.join(outdir, "mm.txt"), "w") as f:
            f.write(str(mm_diag_src))
        with open(os.path.join(outdir, "mm.svg"), "wb") as f:
            f.write(mm_diag_svg)
        with open(os.path.join(outdir, "mm_min.svg"), "wb") as f:
            f.write(mm_diag_min_svg)
        with open(os.path.join(outdir, "im.txt"), "w") as f:
            f.write(str(im_diag_src))
        with open(os.path.join(outdir, "im.svg"), "wb") as f:
            f.write(im_diag_svg)
    return mm_diag_svg, im_diag_svg
