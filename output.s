.section .data
fmt: .string "%d\n"

.section .text
.globl main
main:
    pushq %rbp
    movq %rsp, %rbp
    subq $12, %rsp
    # # Program Start
    # Declare a as int
    movq $10, [rbp-0]
    # Declare b as int
    movq $20, [rbp-4]
    # Declare sum as int
    movq [rbp-0], %rax
    addq [rbp-4], %rax
    movq %rax, [rbp-8]
    cmpq $0, %rbx
    je L0
    movq [rbp-8], %rax
    subq $5, %rax
    movq %rax, [rbp-8]
    jmp L1
L0:
L1:
L2:
    cmpq $0, %rdx
    je L3
    movq [rbp-0], %rax
    addq $1, %rax
    movq %rax, [rbp-0]
    jmp L2
L3:
    # # Program End

    movq $0, %rax
    movq %rbp, %rsp
    popq %rbp
    ret