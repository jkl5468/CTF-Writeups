BITS 32
global _check

section .text

_check:
push eax
add eax,ebx
shl eax,1
inc ebx
pop eax
dec ebx
db 0xCC, 0x23
push ebp
mov ebp,esp
db 0xCC, 0xb7, 0xaa, 0x40, 0x00, 0x55,0xC3
push ebx
lea ebx, [ebp+8]
mov ebx, dword [ebx]
mov eax, dword[ebx]
xor eax, 0xCC9B402A
rol eax,1
db 0xCC, 0x9b, 0xbb, 0x9a, 0x3e, 0xf0, 0xb4, 0x49
sub eax, 0xffbdd1f7     ;0x4502e516
mov ecx,eax
mov eax, dword [ebx+4]
db 0xcc, 0xf2, 0x78, 0xfa, 0xd, 0xe3
mov edx,eax
add edx,eax
add edx,eax
db 0xcc, 0x69, 0x9d, 0xe1
add edx, 0x6363e154
xor eax,eax
or edx, ecx
jne end
db 0xcc, 0xc1
mov dx,word[ebx+8]
cmp dx,105
jne end
inc eax
end:pop ebx
    pop ebp
    ret
db 0x9D, 0x9a, 0xf5, 0x7c, 0xd, 0x54, 0x6f, 0x93

