.section .data
fmt: .string "%d\n"

.section .text
.globl main
main:
    pushq %rbp
    movq %rsp, %rbp
    subq $12, %rsp
    # # Program Start
    # Declare x as int
    movq $10, [rbp-0]
    # Declare y as int
    movq $20, [rbp-4]
    movq [rbp-4], %rax
    imulq $2, %rax
    movq [rbp-0], %rax
    addq %rax, %rax
    # Declare z as int
    movq %rax, [rbp-8]
    # # Program End

    movq $0, %rax
    movq %rbp, %rsp
    popq %rbp
    ret