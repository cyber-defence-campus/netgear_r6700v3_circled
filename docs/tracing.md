# Tracing
```
hooks:
  lib:
    func_hook:
    - {entry: '0xd040', leave: '0xd044', mode: 'skip'}  # fclose  
    [...]
    - {entry: '0xc9c4', leave: '0xc9c8', mode: 'skip'}  # free
  libc:
    fgets:
    - {entry: '0xcfe0', leave: '0xcfe4', mode: 'model'}
    - {entry: '0xd094', leave: '0xd098', mode: 'model'}
    sscanf:
    - {entry: '0xcffc', leave: '0xd000', mode: 'model'}
```