# Setup
set pagination off
set disassembly-flavor intel
set architecture armv7
set arm fallback-mode arm

# Target
target remote localhost:3000

# Addresses
set $main = 0xe3f0
set $daemon = 0xe5fc
set $system_mount_circle = 0xe6a4
set $fork = 0xe7d4
set $system_cp_firmware = 0xf7d8
set $sscnaf = 0xcffc

# Ingore the cancellation of threads
handle SIG32 nostop
handle SIG33 nostop

# Let GDB follow the parent process only
set detach-on-fork on
set follow-fork-mode parent

# Break before invocation of function daemon
break *$daemon
continue

# Let GDB follow the child process
set follow-fork-mode child

# Break before invocation of function system
break *$system_mount_circle
continue

# Let GDB follow the parent process
set follow-fork-mode parent

# Break before invocation of function fork
break *$fork
continue

# Let GDB follow the child process
set follow-fork-mode child

# Break before invocation of function system
break *$system_cp_firmware
continue

# Let GDB follow the parent process
set follow-fork-mode parent

# Break before invocation of function fgets
break *0xcfc0
continue

# Trace till return of function updating_database
# morion_trace debug circled.yaml 0xf768 0xc9b8