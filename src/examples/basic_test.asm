LDI X 1
LDI Y 1
LDI R6 0x00
LDI R7 0x80
JMP Simple_ALU_OP

Simple_ALU_OP:
    ADD F
    JC Stack_pointer_addition
    MOV R1, RX
    PASS_Y
    MOV R1, RY
    JMP Simple_ALU_OP

Stack_pointer_addition:
    ADD
    ADD
    ADD
    ADD
    CALL Stack_pointer_subtraction
    JMP pointer_test_initializer

Stack_pointer_subtraction:
    SUB
    SUB
    SUB
    CALL Stack_pointer_addition2
    RET

Stack_pointer_addition2:
    LDI Y 32
    ADD
    ADD
    RET

pointer_test_initializer:
    LDI X 10
    LDI Y 1
    JMP pointer_test

pointer_test:
    CALL XY_Store
    CALL Pointer_Inc
    CALL XY_Load
    PW R6, R7
    SUB F
    JC initializer
    JMP pointer_test

XY_Store:
    MOV R1, RX
    PASS_Y
    MOV R2, RX
    RET

XY_Load:
    MOV RX, R1
    MOV R2, RY
    RET

initializer:
    LDI Y 10
    INC_X
    JMP pointer_test2


pointer_test2:
    CALL XY_Store
    CALL Pointer_Dec
    CALL XY_Load
    PR R6, R7
    SUB F
    JZ NUMON
    JMP pointer_test2


NUMON:
    ZERO
    JMP NUMON


#############################################################################
Pointer_Inc:
    # Increase the pointer with 1
    MOV RX, R6
    INC_X F
    MOV R6, RX
    JC Pointer_Inc_Carry
    RET

Pointer_Dec:
    # Decrease the pointer with 1
    MOV RX, R6
    DEC_X F
    MOV R6, RX
    # potential error part 
    JNC Pointer_Dec_Carry
    RET

Pointer_Inc_with_var:
    # First, increase lower byte of pointer. If carry bit gets HIGH, Jump to carry conditions subroutine
    MOV R6, RX
    ADD F
    MOV RX, R6
    JC Pointer_Inc_Carry
    RET


Pointer_Inc_Carry:
    MOV RX, R7
    INC_X
    MOV R7, RX
    RET

Pointer_Dec_with_var:
    # First, decrease the lower byte of pointer. If carry bit gets HIGH, Jump to carry conditions subroutine
    MOV RX, R6
    SUB F
    MOV R6, RX
    # potential error part
    JNC Pointer_Dec_Carry
    RET


Pointer_Dec_Carry:
    MOV RX, R7
    DEC_X
    MOV R7, RX
    RET

############################################


