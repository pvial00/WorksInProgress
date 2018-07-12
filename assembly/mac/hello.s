.section __DATA,__data
str:
  .asciz "Testing 123\n"

  .section __TEXT,__text
  .global _main
  _main:
    movl $0x2000004, %eax
    movl $1, %edi
    movq str@GOTPCREL(%rip), %rsi
    movq $100, %rdx
    syscall

    movl $0, %ebx
    movl $0x2000001, %eax
    syscall
