#include <stdio.h>
#include <string.h>
#include <sys/types.h>
#include <dlfcn.h>

char* (*orig_getenv)(const char*);
int (*orig_system)(const char*);

char* getenv(const char* name) {
    // Initialize pointer to original getenv function
    if(!orig_getenv) {
        orig_getenv = dlsym(RTLD_NEXT, "getenv");
    }

    // Call original getenv function for everything else than LD_PRELOAD
    if(strcmp(name, "LD_PRELOAD") != 0) {
        return orig_getenv(name);
    }

    printf("[+] Hooking getenv('%s')\n", name);
    return NULL;
}

int system(const char *command) {
    // Initialize pointer to original system function
    if(!orig_system) {
        orig_system = dlsym(RTLD_NEXT, "system");
    }

    // Download circleinfo.txt
    if(strstr(command, "curl -s -m 180 -k -o /tmp/circleinfo.txt") != NULL) {
        printf("[+] Hooink system('%s')\n", command);
        return orig_system("cp /circleinfo.txt /tmp/circleinfo.txt");
    }

    // Download database.bin
    if(strstr(command, "curl -s -m 180 -k -o /tmp/database.bin") != NULL) {
        printf("[+] Hooink system('%s')\n", command);
        return orig_system("cp /database.bin /tmp/database.bin");
    }

    // Call original system function
    return orig_system(command);
}