include wasmenv.mk
include ../../py/mkenv.mk

CROSS = 0

QSTR_DEFS = qstrdefsport.h

FROZEN_MANIFEST ?= manifest.py

include $(TOP)/py/py.mk
include $(TOP)/extmod/extmod.mk

CC = $(EMCC)
LD = $(EMCC)

INC += -I.
INC += -I$(TOP)
INC += -I$(BUILD)

CFLAGS += -std=c99 -Wall -Werror -Wdouble-promotion -Wfloat-conversion
CFLAGS += -Os
CFLAGS += $(INC)
CFLAGS += -sSUPPORT_LONGJMP=wasm -fwasm-exceptions

SRC_SHARED = $(addprefix shared/,\
	runtime/gchelper_generic.c \
	runtime/interrupt_char.c \
	runtime/stdout_helpers.c \
	runtime/pyexec.c \
	readline/readline.c \
	)

SRC_C = \
	main.c \
	mphalport.c \

SRC_QSTR += $(SRC_C) $(SRC_SHARED)

OBJ += $(PY_O)
OBJ += $(addprefix $(BUILD)/, $(SRC_SHARED:.c=.o))
OBJ += $(addprefix $(BUILD)/, $(SRC_C:.c=.o))

LDFLAGS += --no-entry
LDFLAGS += -sSUPPORT_LONGJMP=wasm -fwasm-exceptions -sFILESYSTEM=0

all: $(BUILD)/micropython.wasm

$(BUILD)/micropython.wasm: $(OBJ)
	$(MKDIR) -p $(BUILD)/wasm
	$(Q)$(EMCC) $(LDFLAGS) -o $(BUILD)/wasm/micropython.wasm $(OBJ)

include $(TOP)/py/mkrules.mk
include Makefile.wasm2c

