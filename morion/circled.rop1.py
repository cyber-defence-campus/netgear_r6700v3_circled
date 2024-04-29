#!/usr/bin/env python3
## -*- coding: utf-8 -*-
from pprint import pprint
from triton import CPUSIZE, MemoryAccess

# Usage: `run -i circled.rop1.py`
ctx = ctx
ast = ast

# Preconditions gadget 0
g0_sp_val  = ctx.getConcreteRegisterValue(ctx.registers.sp)-9*CPUSIZE.DWORD
g0_pc_ast  = ctx.getMemoryAst(MemoryAccess(g0_sp_val+8*CPUSIZE.DWORD, CPUSIZE.DWORD))
g0_pc_val  = 0xc9b8

# Solve preconditions
model = ctx.getModel(g0_pc_ast  == g0_pc_val)
pprint(model)