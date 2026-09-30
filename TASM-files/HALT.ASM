; HALT.ASM
; TASM 4.1 / 8086
; QEMU ISA debug-exit helper.
;
; QEMU must be started with:
;   -device isa-debug-exit,iobase=0xf4,iosize=0x04
;
; Writing 0 to port 0F4h makes QEMU terminate.

.MODEL TINY
.CODE
ORG 100h

start:
    xor ax, ax
    mov dx, 0F4h
    out dx, al
    ret

END start
