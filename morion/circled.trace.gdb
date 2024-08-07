# Setup
set pagination off
set disassembly-flavor intel
set architecture armv7
set arm fallback-mode arm

# Target
target remote localhost:3000

# Addresses
set $main                     = 0xe3f0
set $before_daemon            = 0xe5fc
set $after_daemon             = 0xe600
set $before_fork              = 0xe7d4
set $after_fork               = 0xe7d8
set $before_updating_database = 0xf1a0
set $after_updating_database  = 0xf1a4
set $before_vulnerability     = 0xcfc0
set $after_vulnerability      = 0xcf24

# Ingore the cancellation of threads
handle SIG32 nostop
handle SIG33 nostop

# Let GDB follow either the parent or the child, but not both
set detach-on-fork on

# Let GDB follow the parent process
set follow-fork-mode parent

# Break before function daemon
break *$before_daemon
continue

# Let GDB follow the child process
set follow-fork-mode child

# Break after function daemon
break *$after_daemon
continue

# Let GDB follow the parent process
set follow-fork-mode parent

# Break before function fork
break *$before_fork
continue

# Let GDB follow the child process
set follow-fork-mode child

# Break after function fork
break *$after_fork
continue

# Let GDB follow the parent process
set follow-fork-mode parent

# Determine callee-save registers before function updating_database (use original circleinfo.txt)
break *$before_updating_database
continue
echo \n
echo Callee-save registers before updating_database: \n
info registers r4 r5 r6 r7 r8 r9 r10 r11

# Break before vulnerabilty
break *$before_vulnerability
continue

# Trace till return of function updating_database (address 0xf1a4)
morion_trace debug circled.yaml 0xf1a4

# Determine callee-save registers after invocation of updating_database (use original circleinfo.txt)
echo \n
echo Callee-save registers after updating_database: \n
info registers r4 r5 r6 r7 r8 r9 r10 r11