# X-compile with `CC=arm-linux-gcc make`
CC      ?= gcc
CFLAGS  = -Wall -fPIC -D_GNU_SOURCE
LDFLAGS = -shared -ldl

SOURCES = circled.c
TARGET  = libcircled.so
OBJECTS = $(SOURCES:.c=.o)

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(OBJECTS)
	$(CC) $(LDFLAGS) $(OBJECTS) -o $@

clean:
	rm -r $(OBJECTS) $(TARGET)