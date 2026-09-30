# Cross-platform GNU Make + Python + QEMU + DOS/TASM/Turbo C
# Requirements on both Linux and Windows:
#   - GNU make
#   - Python 3 in PATH
#   - qemu-system-i386 in PATH
PYTHON ?= python3
QEMU ?= qemu-system-i386

# Project and tool directories. Override them from the command line if needed:
#   make PROJECT_DIR=/path/to/project TOOLS_DIR=/path/to/TASM-files build
PROJECT_DIR ?= $(CURDIR)
TOOLS_DIR ?= $(CURDIR)/../TASM-files

TARGET ?= main
FILELANG ?= asm
SRC := $(PROJECT_DIR)/$(TARGET).$(FILELANG)

IMG := $(TOOLS_DIR)/msdos.img
EXCHANGE := $(TOOLS_DIR)/exchange.img
FAT_TOOL := $(TOOLS_DIR)/make_fat.py
BUILD_BAT := $(TOOLS_DIR)/BUILD.BAT
BUILD_COM_BAT := $(TOOLS_DIR)/BUILDCOM.BAT
RUN_BAT := $(TOOLS_DIR)/RUN.BAT
RUN_COM_BAT := $(TOOLS_DIR)/RUN_COM.BAT
GUI_BAT := $(TOOLS_DIR)/GUI.BAT

# QEMU options common to the three scenarios.
QEMU_COMMON := -drive file="$(IMG)",format=raw -fda "$(EXCHANGE)" -boot c -m 32
QEMU_EXIT := -device isa-debug-exit,iobase=0xf4,iosize=0x04
QEMU_NOGRAPHIC := -nographic -serial mon:stdio

.PHONY: prepare build run gui cli clean check

check:
	@$(PYTHON) "$(FAT_TOOL)" --check "$(SRC)" "$(BUILD_BAT)" "$(RUN_BAT)" "$(GUI_BAT)"

# Prepare only the source file on A:.
prepare:
	@echo === Creating NEW FAT12 floppy image ===
	@$(PYTHON) "$(FAT_TOOL)" "$(EXCHANGE)" "$(SRC)"
	@echo [OK] $(TARGET).$(FILELANG) copied to A: as DOS text when applicable.

# Build: source + BUILD.BAT are placed on a fresh A: image in one operation.
build:
	@echo === Creating NEW FAT12 floppy image ===
	@$(PYTHON) "$(FAT_TOOL)" "$(EXCHANGE)" "$(SRC)" "$(BUILD_BAT)"
	@echo [OK] Source and BUILD.BAT copied to A:
	@echo === Starting DOS BUILD mode ===
	@$(QEMU) $(QEMU_COMMON) $(QEMU_NOGRAPHIC) $(QEMU_EXIT)

build-com:
	@echo === Creating NEW FAT12 floppy image ===
	@$(PYTHON) "$(FAT_TOOL)" "$(EXCHANGE)" "$(SRC)" "$(BUILD_COM_BAT)"
	@echo [OK] Source and BUILD.BAT copied to A:
	@echo === Starting DOS BUILD mode ===
	@$(QEMU) $(QEMU_COMMON) $(QEMU_NOGRAPHIC) $(QEMU_EXIT)


# Run: source + RUN.BAT are placed on a fresh A: image.
run:
	@echo === Creating NEW FAT12 floppy image ===
	@$(PYTHON) "$(FAT_TOOL)" "$(EXCHANGE)" "$(SRC)" "$(RUN_BAT)"
	@echo [OK] Source and RUN.BAT copied to A:
	@echo === Starting DOS RUN mode ===
	@$(QEMU) $(QEMU_COMMON) $(QEMU_NOGRAPHIC) $(QEMU_EXIT)

run-com:
	@echo === Creating NEW FAT12 floppy image ===
	@$(PYTHON) "$(FAT_TOOL)" "$(EXCHANGE)" "$(SRC)" "$(RUN_COM_BAT)"
	@echo [OK] Source and RUN.BAT copied to A:
	@echo === Starting DOS RUN mode ===
	@$(QEMU) $(QEMU_COMMON) $(QEMU_NOGRAPHIC) $(QEMU_EXIT)


# GUI: source + GUI.BAT are placed on a fresh A: image.
gui:
	@echo === Creating NEW FAT12 floppy image ===
	@$(PYTHON) "$(FAT_TOOL)" "$(EXCHANGE)" "$(SRC)" "$(GUI_BAT)"
	@echo [OK] Source and GUI.BAT copied to A:
	@echo === Starting DOS GUI mode ===
	@$(QEMU) $(QEMU_COMMON) $(QEMU_EXIT)

# GUI from a terminal without the graphical QEMU window.
cli:
	@echo === Creating NEW FAT12 floppy image ===
	@$(PYTHON) "$(FAT_TOOL)" "$(EXCHANGE)" "$(SRC)" "$(GUI_BAT)"
	@echo [OK] Source and GUI.BAT copied to A:
	@echo === Starting DOS GUI CLI mode ===
	@$(QEMU) $(QEMU_COMMON) $(QEMU_NOGRAPHIC) $(QEMU_EXIT)

clean:
	@$(PYTHON) "$(FAT_TOOL)" --clean "$(PROJECT_DIR)" "$(TARGET)"
