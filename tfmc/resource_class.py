from dataclasses import dataclass, field
from termcolor import colored


@dataclass
class Attribute:
    id: str
    value: any
    type: any

    def __repr__(self) -> str:
        return f"{colored(self.id, 'yellow')}[{colored(self.type, 'light_green')}]={colored(self.value, 'cyan')}"


@dataclass
class Association:
    id: str
    targets: list[str]  # uuid of resource
    type: str

    def __repr__(self) -> str:
        # if len(self.target_ids) > 0 and isinstance(self.target_ids[0], object):
        #     items = list(map(lambda x: colored(x.id, "cyan"), self.target_ids))
        #     return f"{colored(self.id, 'magenta')}[{colored(self.type, 'light_green')}]={items}"
        return f"{colored(self.id, 'magenta')}[{colored(self.type, 'light_green')}]={colored(self.targets, 'cyan')}"


@dataclass
class Resource:
    id: str
    category: str
    attrs: list[Attribute]
    assocs: list[Association]
    tfmeta: dict

    # generate z3
    def encode(self):
        # TODO: Encode into a Z3 rule
        pass

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
    schema: dict[str, dict]
    im_resources: dict[str, Resource]
    im_uuids: dict[str, Resource]

    def encode(self):
        categories = list(self.schema.keys())
        associations = [res for rkey, res in self.schema.items()]
        # associations = [res.assocs for res in self.im_resources.values()]
        # attributes = [res.attrs for res in self.im_resources.values()]

        print(categories)
        print(associations)
        # print(attributes)
