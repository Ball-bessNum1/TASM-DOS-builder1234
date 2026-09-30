.8086 
.MODEL small 
.stack 100h 
.data 
    mess db "MSdosAutomatic", 0dh, 0ah, "$" 
.code 
start:
    mov dx,@stack 
    mov ss,dx 
    mov dx,@data
    mov ds,dx
    mov dx, offset mess
    mov ah,09h
    int 21h
    mov ah,01h
    int 21h
    mov ah,4Ch
    int 21h

end start