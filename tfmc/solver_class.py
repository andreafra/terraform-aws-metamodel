from dataclasses import dataclass

import z3

Z3RefsMap = dict[str, z3.DatatypeRef]


@dataclass
class SolverSorts:
    category: z3.DatatypeSortRef
    association: z3.DatatypeSortRef
    attribute: z3.DatatypeSortRef | None
    element: z3.DatatypeSortRef
    string: z3.DatatypeSortRef | None
    value: z3.DatatypeSortRef | None


@dataclass
class SolverRefs:
    category: Z3RefsMap
    association: Z3RefsMap
    attribute: Z3RefsMap | None
    element: Z3RefsMap
    string: Z3RefsMap | None


@dataclass
class SolverFunctions:
    category: z3.FuncDeclRef
    association: z3.FuncDeclRef
    attribute: z3.FuncDeclRef | None


@dataclass
class SolverContext:
    solver: z3.Solver
    sort: SolverSorts
    ref: SolverRefs
    fn: SolverFunctions


@dataclass
class SolverResult:
    result: bool
    negate_form: bool
    error_msg: str
