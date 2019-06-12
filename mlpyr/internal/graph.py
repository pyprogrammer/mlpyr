import attr
import typing


class Expr:
    pass


class Stmt:
    pass


@attr.s(auto_attribs=True)
class Sym(Expr):
    name: str
    type: typing.Optional[typing.Type] 


@attr.s(auto_attribs=True)
class BlockLabel:
    name: str


@attr.s(auto_attribs=True)
class Op(Expr):
    op: str
    args: typing.List


@attr.s(auto_attribs=True)
class Constant(Expr):
    val: typing.Any


@attr.s(auto_attribs=True)
class Call(Expr):
    func: str 
    args: typing.List[Sym]


@attr.s(auto_attribs=True)
class CallIndirect(Expr):
    func: Sym
    args: typing.List[Sym]


@attr.s(auto_attribs=True)
class Assign(Stmt):
    lhs: Sym
    rhs: Expr


@attr.s(auto_attribs=True)
class Ret(Stmt):
    val: typing.Optional[Sym]


@attr.s(auto_attribs=True)
class CondBranch:
    cond: Sym

    true: BlockLabel
    trueargs: typing.List[Sym]

    false: BlockLabel
    falseargs: typing.List[Sym]


@attr.s(auto_attribs=True)
class Branch:
    label: BlockLabel
    args: typing.List[Sym]


@attr.s(auto_attribs=True)
class Block:
    label: BlockLabel
    inputs: typing.List[Sym]
    body: typing.List[typing.Union[Stmt, Expr]]
    terminator: typing.Union[Branch, CondBranch, Ret]


@attr.s(auto_attribs=True)
class Function:
    name: str
    args: typing.List[Sym]
    ret_type: typing.Type
    entry: BlockLabel
    blocks: typing.List[Block]


@attr.s(auto_attribs=True)
class Program:
    name: str
    entry: str
    functions: typing.List[Function]
