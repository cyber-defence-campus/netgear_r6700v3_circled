#include <stdio.h>
#include <string.h>
#include <dlfcn.h>

int (*orig_system)(const char*);

int system(const char *command) {
    // Initialize pointer to original system function
    if(!orig_system) {
        orig_system = dlsym(RTLD_NEXT, "system");
    }

    // Download circleinfo.txt
    if(strstr(command, "curl -s -m 180 -k -o /tmp/circleinfo.txt") != NULL) {
        const char *new_command = "curl -s -m 180 -k -o /tmp/circleinfo.txt http://127.0.0.1:5000/circleinfo.txt";
        printf("[+] Hook function 'system':\n");
        printf("    - old command: '%s'\n", command);
        printf("    - new command: '%s'\n", new_command);
        return orig_system(new_command);
    }

    // Download database.bin
    if(strstr(command, "curl -s -m 180 -k -o /tmp/database.bin") != NULL) {
        const char *new_command = "curl -s -m 180 -k -o /tmp/database.bin http://127.0.0.1:5000/database.bin";
        printf("[+] Hook function 'system':\n");
        printf("    - old command: '%s'\n", command);
        printf("    - new command: '%s'\n", new_command);
        return orig_system(new_command);
    }

    // Call original system function
    return orig_system(command);
}