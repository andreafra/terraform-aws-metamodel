from dataclasses import dataclass, field
import itertools
from termcolor import colored

from tfmc.schema_gen import Schema


@dataclass
class Attribute:
    id: str
    value: int | str | bool
    type: str
    schema_type: str

    def __repr__(self) -> str:
        return f"{colored(self.id, 'yellow')}[{colored(self.type, 'light_green')}]={colored(str(self.value), 'cyan')}"


@dataclass
class Association:
    id: str
    targets: list[str]  # uuid of resource
    target_refs: list["Resource"]
    target_type: str
    schema_type: str

    def __repr__(self) -> str:
        # if len(self.target_ids) > 0 and isinstance(self.target_ids[0], object):
        #     items = list(map(lambda x: colored(x.id, "cyan"), self.target_ids))
        #     return f"{colored(self.id, 'magenta')}[{colored(self.type, 'light_green')}]={items}"
        return f"{colored(self.id, 'magenta')}[{colored(self.target_type, 'light_green')}]={colored(str(self.targets), 'cyan')}"


@dataclass
class Resource:
    id: str
    category: str
    attrs: list[Attribute]
    assocs: list[Association]
    tfmeta: dict

    def gen_association_refs(self, refs: "Refs"):
        for assoc in self.assocs:
            for uuid in assoc.targets:
                if tgt_ref := refs.im_uuids.get(uuid):
                    assoc.target_refs.append(tgt_ref)
                else:
                    print(f"Association: target ref {uuid} not found!")

    def __repr__(self) -> str:
        return f"{colored(self.id, 'light_cyan')}:\n" + (
            "\tattrs:\n\t"
            + "\n\t".join([repr(x) for x in self.attrs] if self.attrs else "")
            + "\n\tassocs:\n\t"
            + "\n\t".join([repr(x) for x in self.assocs])
            if self.assocs
            else "\t<empty>"
        )


@dataclass
class Refs:
    schema: Schema
    im_resources: dict[str, Resource]
    im_uuids: dict[str, Resource]

    def gen_association_refs(self):
        for res in self.im_resources.values():
            res.gen_association_refs(self)

    def get_mm_categories(self):
        return self.schema.categories

    def get_mm_associations(self):
        return list(self.schema.associations.keys())

    def get_mm_attributes(self):
        return list(self.schema.attributes.keys())

    def get_im_elements(self):
        return list(self.im_resources.keys())

    def get_im_associations(self):
        assocs = [res.assocs for res in self.im_resources.values()]
        return list(itertools.chain(*assocs))

    def get_im_attributes(self):
        attrs = [res.attrs for res in self.im_resources.values()]
        return list(itertools.chain(*attrs))
