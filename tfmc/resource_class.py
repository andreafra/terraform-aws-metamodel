from dataclasses import dataclass, field
from termcolor import colored


@dataclass
class Attribute:
    id: str
    value: any
    type: any

    def encode(self):
        pass

    def __repr__(self) -> str:
        return f"{colored(self.id, 'yellow')}[{colored(self.type, 'light_green')}]={colored(self.value, 'cyan')}"


@dataclass
class Association:
    id: str
    target_ids: list["Resource"]
    type: str

    def encode(self):
        pass

    def __repr__(self) -> str:
        # if len(self.target_ids) > 0 and isinstance(self.target_ids[0], object):
        #     items = list(map(lambda x: colored(x.id, "cyan"), self.target_ids))
        #     return f"{colored(self.id, 'magenta')}[{colored(self.type, 'light_green')}]={items}"
        return f"{colored(self.id, 'magenta')}[{colored(self.type, 'light_green')}]={colored(self.target_ids, 'cyan')}"


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
