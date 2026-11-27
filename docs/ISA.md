# Instruction Set Architecture (ISA) Reference

**Project:** Custom 8-bit Microcoded Computer\
**Document type:** Architecture and instruction-set reference\
**Status:** Draft specification based on the current hardware
description and the supplied assembler, microcode generator, and
assembly program\
**Data path:** 8-bit\
**Address width:** 16-bit

------------------------------------------------------------------------

## 1. Introduction

This document describes the Instruction Set Architecture (ISA) of a
custom-built 8-bit computer implemented using discrete 74HC-series logic
and EEPROM-based microcode.

The processor is built around an 8-bit data path and a 16-bit address
space. It uses a custom instruction set, a dedicated register file,
separate ALU operand registers, a microprogrammed control unit, and
memory-mapped video memory. Programs are written in a custom assembly
language and translated into machine code by a Python assembler.

The ISA is designed around a small set of native instructions. More
complex operations are expressed as sequences of these instructions in
software.

### 1.1 Architectural characteristics

  Feature                     Description
  --------------------------- --------------------------------------------
  Data width                  8 bits
  Address width               16 bits
  Address space               64 KiB
  General-purpose registers   8 x 8-bit (`R0`--`R7`)
  Dedicated ALU registers     `RX`, `RY` (8 bits each)
  Program Counter             16-bit
  Stack Pointer               16-bit
  Memory Address Register     16-bit, implemented as two 8-bit registers
  Instruction Register        8-bit
  Flags                       Carry (`C`), Zero (`Z`), Sign (`S`)
  Instruction encoding        Variable length: 1, 2, or 3 bytes
  Control unit                EEPROM-based microprogrammed control

------------------------------------------------------------------------

## 2. Programmer-Visible Register Architecture

### 2.1 General-purpose register file

The processor provides eight general-purpose registers:

-   `R0`
-   `R1`
-   `R2`
-   `R3`
-   `R4`
-   `R5`
-   `R6`
-   `R7`

Each register is 8 bits wide. The register file is accessed through
dedicated read-enable and write-enable control signals.

Register identifiers are represented by three bits, allowing the eight
registers to be selected.

### 2.2 Dedicated ALU registers

`RX` and `RY` are two independent 8-bit registers associated with the
ALU. They are physically separate from the general-purpose register file
and are not members of `R0`--`R7`.

Their roles are:

-   **RX:** Holds the ALU X operand and is also the principal
    destination for ALU results and several memory/pointer operations.
-   **RY:** Holds the ALU Y operand. Its value can be routed through the
    ALU using `PASS_Y`.

The ALU operates primarily on `RX` and `RY`. General-purpose registers
exchange data with these dedicated registers through `MOV` instructions.

### 2.3 Special-purpose registers

  ---------------------------------------------------------------------
  Register                                   Width Description
  -------------------- --------------------------- --------------------
  `PC`                                     16 bits Program Counter;
                                                   addresses
                                                   instruction bytes in
                                                   memory

  `SP`                                     4 bits Stack Pointer

  `MAR`                                    16 bits Memory Address
                                                   Register, split into
                                                   `MARL` and `MARH`

  `IR`                                      8 bits Instruction Register
  ---------------------------------------------------------------------

#### Program Counter (PC)

The Program Counter addresses the next byte to be fetched. PC
advancement is performed by explicit microcode steps, one byte at a
time. The processor does not increment the PC by an instruction's total
length in a single operation.

For a multi-byte instruction, the required operand bytes are fetched
through additional microcode steps. A conditional jump that is not taken
advances past its two address bytes by performing two additional
one-byte PC increments after the opcode-fetch increment.

#### Stack Pointer (SP)

The Stack Pointer is 4 bits wide. The stack grows toward higher memory
addresses during `CALL` operations.

A `CALL` stores the return address as two bytes, low byte first and high
byte second, advancing the SP as the bytes are written. `RET` decrements
the SP while retrieving the stored address, reading the high byte before
the low byte and restoring the PC.

#### Memory Address Register (MAR)

The MAR consists of two independent 8-bit registers:

-   `MARL`: low address byte
-   `MARH`: high address byte

Together they form a 16-bit memory address:

`MAR = (MARH << 8) | MARL`

#### Instruction Register (IR)

The IR is 8 bits wide and normally holds the first byte---the
opcode---of the current instruction.

Pointer instructions (`PW` and `PR`) are a special case: their second
byte is also fetched into the IR and decoded as part of the same
instruction. The step counter is not reset between the two byte-level
decode stages.

------------------------------------------------------------------------

## 3. Memory Architecture

### 3.1 Address space

The processor has a 16-bit address bus, providing a 64 KiB address space
(`0x0000`--`0xFFFF`).

The current memory map is:

  -----------------------------------------------------------------------
  Address range                    Size Region          Purpose
  ----------------- ------------------- --------------- -----------------
  `0x0000-0x7FFF`                32 KiB System ROM      Program storage
                                                        and terminal
                                                        operating system

  `0x8000-0xEFFF`                28 KiB SRAM            General-purpose
                                                        read/write memory

  `0xF000-0xFFFF`                 4 KiB VRAM            Video memory used
                                                        by the VGA
                                                        subsystem
  -----------------------------------------------------------------------

The regions are selected by address-decoding logic using upper address
bits.

### 3.2 Physical memory implementation

The current physical implementation uses:

  -----------------------------------------------------------------------
  Region                  Device                  Notes
  ----------------------- ----------------------- -----------------------
  System ROM              AT28C256 EEPROM         Read-only during
                                                  processor operation

  SRAM                    UT62256CPC-70LL         Separate physical SRAM
                                                  chip

  VRAM                    UT62256CPC-70LL         Separate chip of the
                                                  same type as system
                                                  SRAM
  -----------------------------------------------------------------------

The ROM's write-enable input is tied inactive (logic high); it is not
controlled by the processor's `MEM_WE` signal. The ROM is therefore
physically write-protected in the current implementation.

The SRAM and VRAM are separate physical devices. Only the mapped
portions shown in the memory map are part of the processor's current
address-space allocation.

### 3.3 Memory access instructions

The native `LD` and `ST` instructions access memory using a 16-bit
direct address and transfer data between memory and a general-purpose
register.

-   `LD Rn, address`: reads `Memory[address]` into `Rn`.
-   `ST Rn, address`: writes the contents of `Rn` to `Memory[address]`.

The current instruction set uses the general-purpose register file for
these direct load/store operations. Earlier `LDX`, `LDY`, and `STX`
assembler definitions are not part of the current ISA described here.

### 3.4 Video memory

VRAM occupies `0xF000-0xFFFF`. There are no dedicated VGA instructions
in the ISA. Software updates video memory through ordinary memory-write
mechanisms, including `ST` and pointer-based writes (`PW`).

The VGA subsystem reads the same physical VRAM device. The detailed
electrical timing and display-access implementation are hardware-design
topics and are outside the scope of this ISA reference.

------------------------------------------------------------------------

## 4. Instruction Encoding

### 4.1 General format

Instructions are variable-length. A native instruction occupies one,
two, or three bytes, depending on its opcode and instruction family.

The opcode is contained in the first byte. Operand bytes, when present,
follow the opcode. Opcode and operand data are not packed into the same
byte.

The processor determines the instruction's execution path from the
opcode. The microcode controls whether additional bytes must be fetched
and how they are interpreted.

### 4.2 Instruction lengths

  ---------------------------------------------------------------------
                       Length General structure    Examples
  --------------------------- -------------------- --------------------
                       1 byte `OPCODE`             `HALT`, `RET`,
                                                   `MOV`, native ALU
                                                   operations

                      2 bytes `OPCODE`, `OPERAND`  `LDI`, `PW`, `PR`
                              or second opcode     
                              byte                 

                      3 bytes `OPCODE`,            `JMP`, conditional
                              `ADDRESS_LOW`,       jumps, `CALL`, `LD`,
                              `ADDRESS_HIGH`       `ST`
  ---------------------------------------------------------------------

### 4.3 8-bit immediate format

`LDI` uses a two-byte encoding:

  Byte     Meaning
  -------- ---------------------------------------------
  Byte 0   Opcode, including the destination selection
  Byte 1   8-bit immediate value

The immediate value is an unsigned 8-bit bit pattern. For example:

``` asm
LDI R3, 0x2A
```

encodes as:

``` text
13 2A
```

The destination is selected by the opcode. `LDI` supports the
general-purpose registers as well as `RX` and `RY`.

### 4.4 16-bit address format

Direct memory and control-flow instructions use a three-byte encoding:

  Byte     Meaning
  -------- -------------------
  Byte 0   Opcode
  Byte 1   Address low byte
  Byte 2   Address high byte

The address is encoded little-endian: the low byte is stored first.

For example, address `0x1234` is encoded as:

``` text
34 12
```

A complete jump instruction is therefore:

``` asm
JMP 0x1234
```

``` text
08 34 12
```

### 4.5 Register selection within opcodes

The ISA uses opcode bits to encode general-purpose register selection. A
three-bit register identifier selects one of `R0`--`R7`.

This reduces the need for separate register-operand bytes in native
instructions. The exact bit placement depends on the instruction family;
the tables in the instruction reference specify each family's encoding.

### 4.6 Pointer instruction encoding

`PW` and `PR` are native two-byte instructions. Both bytes participate
in decoding:

-   The first byte selects the low-address register.
-   The second byte selects the high-address register.

For `PW Rn, Rm`, the encoding is:

``` text
Byte 0: 0x20 | n
Byte 1: 0x28 | m
```

For `PR Rn, Rm`, the encoding is:

``` text
Byte 0: 0x30 | n
Byte 1: 0x38 | m
```

The resulting address is:

`Address = (Rm << 8) | Rn`

The second byte is fetched into the IR without resetting the step
counter. The microprogram then decodes that byte to select the
high-address register and complete the memory operation.

### 4.7 Flag-update bit on ALU opcodes

For native ALU instructions, bit 0 of the opcode selects whether the
operation updates the flags:

-   Base opcode: flags are preserved.
-   Base opcode with bit 0 set: all three flags (`C`, `Z`, and `S`) are
    updated.

In assembly syntax, this option is written using the `F` suffix, for
example `ADD F`.

------------------------------------------------------------------------

## 5. Instruction Set Reference

This section lists the native instructions supported by the current
hardware description. Opcode values are shown in hexadecimal.

### 5.1 Processor control

  ---------------------------------------------------------------------
  Mnemonic                    Opcode              Length Operation
  -------------- ------------------- ------------------- --------------
  `HALT`                      `0x01`              1 byte Asserts the
                                                         processor halt
                                                         control signal

  `LDK`                       `0x02`              1 byte Reads keyboard
                                                         input into
                                                         `RX` and
                                                         clears the
                                                         keyboard input
                                                         state
  ---------------------------------------------------------------------

`LDK` does not wait for keyboard input. Software can repeatedly poll the
keyboard as part of a loop.

### 5.2 Immediate loads

  Assembly form           Opcode    Length Operation
  ---------------- ------------- --------- -------------
  `LDI Rn, imm8`     `0x10 \| n`   2 bytes `Rn <- imm8`
  `LDI X, imm8`           `0x18`   2 bytes `RX <- imm8`
  `LDI Y, imm8`           `0x1C`   2 bytes `RY <- imm8`

Here, `n` is the three-bit register number from 0 to 7.

Examples:

``` asm
LDI R3, 42
LDI X, 0x80
LDI Y, 0x01
```

### 5.3 Register transfers (`MOV`)

The native `MOV` family transfers data between the general-purpose
register file and the dedicated ALU registers.

  Assembly form          Opcode Actual data transfer
  --------------- ------------- ----------------------
  `MOV Rn, RX`      `0x40 \| n` `Rn <- RX`
  `MOV RX, Rn`      `0x50 \| n` `RX <- Rn`
  `MOV Rn, RY`      `0x58 \| n` `RY <- Rn`

**Important syntax note:** The `MOV Rn, RY` form is intentionally
unusual. Despite the apparent source/destination order suggested by the
text, the hardware operation selected by this encoding transfers the
contents of `Rn` into `RY`. The actual data-transfer direction is shown
in the table above.

Each `MOV` instruction is one byte long.

### 5.4 Direct memory access

  Assembly form             Opcode    Length Operation
  ------------------ ------------- --------- ------------------------
  `LD Rn, address`     `0x60 \| n`   3 bytes `Rn <- Memory[address]`
  `ST Rn, address`     `0x70 \| n`   3 bytes `Memory[address] <- Rn`

The address is encoded as low byte followed by high byte.

Examples:

``` asm
LD R3, 0x1234
ST R3, 0x1234
```

### 5.5 Pointer-based memory access

`PW` and `PR` use two general-purpose registers to construct a 16-bit
address. The low-address byte comes from the first register operand, and
the high-address byte comes from the second register operand.

  ------------------------------------------------------------------------------------
  Mnemonic         First-byte   Second-byte    Length Operation
                       opcode        opcode           
  ------------- ------------- ------------- --------- --------------------------------
  `PW Rn, Rm`     `0x20 \| n`   `0x28 \| m`   2 bytes `Memory[(Rm << 8) \| Rn] <- RX`

  `PR Rn, Rm`     `0x30 \| n`   `0x38 \| m`   2 bytes `RX <- Memory[(Rm << 8) \| Rn]`
  ------------------------------------------------------------------------------------

These instructions use `RX` as their data register. `PW` writes the
value in `RX` to the addressed memory location; `PR` reads the addressed
memory location into `RX`.

### 5.6 Unconditional control flow

  -----------------------------------------------------------------------
  Mnemonic                      Opcode              Length Operation
  ---------------- ------------------- ------------------- --------------
  `CALL address`                `0x04`             3 bytes Saves the
                                                           return address
                                                           on the stack
                                                           and transfers
                                                           control to
                                                           `address`

  `RET`                         `0x06`              1 byte Restores the
                                                           return address
                                                           from the stack

  `JMP address`                 `0x08`             3 bytes Loads the
                                                           target address
                                                           into the PC
  -----------------------------------------------------------------------

`CALL` stores the return address so that execution resumes at the
instruction following the three-byte `CALL` instruction when `RET` is
executed.

The stack grows toward higher addresses during a call. The
return-address low byte is written first, followed by the high byte.
`RET` retrieves the high byte and then the low byte while decrementing
the SP.

### 5.7 Conditional jumps

All conditional jumps are three bytes long and use a 16-bit
little-endian target address.

  Mnemonic          Opcode Condition
  --------------- -------- -----------
  `JZ address`      `0x09` `Z = 1`
  `JNZ address`     `0x0A` `Z = 0`
  `JC address`      `0x0B` `C = 1`
  `JNC address`     `0x0C` `C = 0`
  `JS address`      `0x0D` `S = 1`
  `JNS address`     `0x0E` `S = 0`

If the condition is true, the target address is loaded into the PC. If
the condition is false, the processor advances past the two address
bytes and continues with the next instruction.

Control-flow instructions do not modify the `C`, `Z`, or `S` flags.

### 5.8 Native ALU operations

All native ALU operations are one-byte instructions. They operate on the
dedicated `RX` and `RY` registers unless their name explicitly
identifies one of those registers.

  Mnemonic      Base opcode Operation
  ----------- ------------- ----------------------------------------
  `AND`              `0x80` `RX <- RX AND RY`
  `ADD`              `0x84` `RX <- RX + RY`
  `PASS_X`           `0x98` `RX <- RX` (pass `RX` through the ALU)
  `NOT_X`            `0x9A` `RX <- NOT RX`
  `DEC_X`            `0x9C` `RX <- RX - 1`
  `NEG_X`            `0x9E` `RX <- -RX` (two's-complement negation)
  `SUB`              `0xA6` `RX <- RX - RY`
  `OR`               `0xAA` `RX <- RX OR RY`
  `SUB_REV`          `0x8E` `RX <- RY - RX`
  `INC_X`            `0xBE` `RX <- RX + 1`
  `PASS_Y`           `0xE0` `RX <- RY` (pass `RY` through the ALU)
  `NOT_Y`            `0xE2` `RX <- NOT RY`
  `DEC_Y`            `0xE4` `RX <- RY - 1`
  `NEG_Y`            `0xE6` `RX <- -RY` (two's-complement negation)
  `INC_Y`            `0xEE` `RX <- RY + 1`
  `NEG_ONE`          `0xF4` `RX <- 0xFF`
  `ONE`              `0xFE` `RX <- 0x01`
  `ZERO`             `0xD4` `RX <- 0x00`

For operations whose result is defined as an ALU output, the processor's
ALU datapath determines how that result is transferred to the
destination register or bus. The dedicated register-transfer
instructions are documented separately above.

#### ALU flag-update form

Appending `F` to an ALU mnemonic sets bit 0 of its opcode and enables
flag writes:

``` asm
ADD       # Preserve existing flags
ADD F     # Update C, Z, and S

SUB       # Preserve existing flags
SUB F     # Update C, Z, and S
```

The `F` form updates all three flags together. Without `F`, the previous
flag values are preserved.

------------------------------------------------------------------------

## 6. Flag Architecture

The processor exposes three status flags:

  Flag   Name    Set condition
  ------ ------- -------------------------------------------
  `C`    Carry   Set when an addition produces a carry-out
  `Z`    Zero    Set when the ALU result is `0x00`
  `S`    Sign    Set when bit 7 of the ALU result is `1`

### 6.1 Carry behavior during subtraction

Subtraction is implemented using two's-complement arithmetic. The
processor's documented Carry behavior for subtraction is:

-   Carry is set when a larger value is reduced by a smaller value.
-   Carry is not set when a smaller value has a larger value subtracted
    from it.

This is the processor's own Carry convention and should not be assumed
to be identical to a borrow flag convention used by other architectures.

### 6.2 Flag preservation

ALU instructions preserve the previous flag values unless the `F` option
is specified. When `F` is specified, `C`, `Z`, and `S` are updated
together.

Control-flow instructions do not modify these flags.

------------------------------------------------------------------------

## 7. Microarchitecture and Instruction Execution

This section describes the implementation-level mechanisms relevant to
understanding the ISA. It is not a gate-level schematic.

### 7.1 Microprogrammed control unit

The control unit is implemented using EEPROMs containing microcode. The
microcode address is composed of:

-   A 4-bit microstep index
-   An 8-bit opcode
-   Three status-flag bits

The address layout used by the microcode generator is:

``` text
[ microstep: 4 bits ][ opcode: 8 bits ][ flags: 3 bits ]
```

This produces a 15-bit microcode address space.

The microcode generator distributes the control word across four EEPROM
output bytes. The implementation defines 27 active control signals.

### 7.2 Common fetch sequence

The common initial microsteps are:

1.  The opcode byte is read from memory and loaded into the IR.
2.  The PC is incremented by one byte.
3.  The instruction-specific microprogram begins.

Instruction-specific microcode performs any remaining operand fetches,
register transfers, memory operations, and control-flow changes. The
step counter is reset when the instruction completes.

### 7.3 Pointer instruction sequencing

`PW` and `PR` use a special multi-stage sequence:

1.  The first opcode byte selects the register used for the low address
    byte.
2.  That register's value is loaded into `MARL`.
3.  The next instruction byte is fetched into the IR without resetting
    the step counter.
4.  The second byte selects the register used for the high address byte.
5.  That register's value is loaded into `MARH`.
6.  The memory operation is performed using the assembled 16-bit MAR
    address.
7.  The PC is advanced past the second byte and the instruction sequence
    completes.

This allows a two-byte pointer instruction to use both bytes as
separately decoded control information within the existing
microprogrammed sequencing mechanism.

### 7.4 Conditional branch sequencing

The microcode evaluates the relevant flag for each conditional jump. If
the condition is satisfied, the two target-address bytes are fetched and
used to load the PC. If the condition is not satisfied, the PC is
incremented twice to skip those two bytes.

### 7.5 Control-signal groups

The microcode generator defines control signals for the following
functional groups:

-   ALU register input, output, and operation control
-   General-purpose register-file read and write
-   Program Counter control
-   Memory read and write
-   Memory Address Register loading and output
-   Stack Pointer control
-   Microstep-counter reset
-   Instruction Register loading
-   Keyboard input and clear
-   Processor halt

The exact electrical behavior and timing of these signals belong in the
hardware implementation documentation.

------------------------------------------------------------------------

## 8. Assembly Language

### 8.1 General syntax

Assembly instructions consist of a mnemonic followed by zero or more
operands. Commas may be used to separate operands.

Examples:

``` asm
HALT
LDI R0, 10
LDI X, 0x2A
MOV RX, R1
LD R3, 0x8000
JMP main_loop
```

Register names are written as `R0` through `R7`, with `RX` and `RY` used
for the dedicated ALU registers.

### 8.2 Numeric literals

The supplied assembler accepts integer literals using Python-style base
detection:

``` asm
LDI R0, 25       # Decimal
LDI R1, 0x19     # Hexadecimal
```

Immediate values are encoded as 8-bit values. Direct memory and jump
addresses are encoded as 16-bit values.

### 8.3 Labels

A label is written on its own line and ends with a colon:

``` asm
main_loop:
    LDI X, 1
    JMP main_loop
```

The assembler uses a two-pass process. The first pass records label
addresses; the second pass emits machine-code bytes and resolves label
references.

### 8.4 Comments

The supplied assembly examples use `#` for comments:

``` asm
# Initialize the pointer
LDI R6, 0x00
LDI R7, 0x80
```

### 8.5 Assembler behavior and scope

The supplied assembler implementation uses a two-pass label-resolution
process and emits a binary machine-code file.

The supplied source does not define directives such as `.org`, `.byte`,
or `.word`. It also does not implement a general macro-expansion
facility. Such features should not be assumed to be part of the current
assembly language unless added to the assembler.

------------------------------------------------------------------------

## 9. Programming Patterns

The following examples illustrate how software can combine native
instructions to perform higher-level tasks.

### 9.1 Polling the keyboard

`LDK` reads the keyboard input state into `RX` and clears the keyboard
input state. It does not block while waiting for a key. A program can
poll repeatedly:

``` asm
keyboard_loop:
    LDK
    # Examine or process RX here
    JMP keyboard_loop
```

### 9.2 Constructing a 16-bit pointer in general-purpose registers

A common software convention is to use two 8-bit general-purpose
registers as a 16-bit pointer:

-   Low byte: `R6`
-   High byte: `R7`

The pointer value is:

`Pointer = (R7 << 8) | R6`

The `PW` and `PR` instructions can then use this pair:

``` asm
PW R6, R7
PR R6, R7
```

### 9.3 Incrementing a 16-bit pointer in software

Because the ALU is 8 bits wide, a 16-bit pointer increment can be
implemented by incrementing the low byte and propagating a carry into
the high byte:

``` asm
Pointer_Inc:
    MOV RX, R6
    INC_X F
    MOV R6, RX
    JC Pointer_Inc_Carry
    RET

Pointer_Inc_Carry:
    MOV RX, R7
    INC_X
    MOV R7, RX
    RET
```

This illustrates how software can build wider arithmetic operations from
the native 8-bit ALU and conditional branches.

### 9.4 Subroutines

Subroutines use `CALL` and `RET`:

``` asm
    CALL routine
    JMP continue

routine:
    # Subroutine body
    RET

continue:
    HALT
```

`CALL` saves the return address on the stack; `RET` restores it.

------------------------------------------------------------------------

## 10. ISA Summary

The architecture combines:

-   An 8-bit datapath and 16-bit address space
-   Eight general-purpose registers
-   Two dedicated ALU registers (`RX` and `RY`)
-   A 16-bit Program Counter, Stack Pointer, and Memory Address Register
-   Three status flags (`C`, `Z`, and `S`)
-   Variable-length 1-, 2-, and 3-byte native instructions
-   Opcode-based register selection
-   Little-endian 16-bit address operands
-   A microprogrammed control unit
-   Direct and pointer-based memory access
-   Memory-mapped VRAM and polled keyboard input

The instruction set is intentionally small at the hardware level. More
elaborate behavior---including 16-bit pointer arithmetic and multi-step
arithmetic expressions---is built by composing native instructions in
software.

------------------------------------------------------------------------

## 11. Implementation Notes and Verification Status

This document describes the current architecture as clarified by the
project author, using the supplied source files as implementation
evidence where they agree with that description.

The supplied assembler snapshot contains legacy or inconsistent
definitions for `LDX`, `LDY`, and `STX`; these are excluded from the
current instruction set in accordance with the author's clarification
that direct `LD` and `ST` operate through the general-purpose register
file.

The supplied assembler snapshot also contains operand-bearing ALU
assembly forms that should not be interpreted as additional native ALU
instructions. Native ALU operations are one-byte instructions operating
on `RX` and `RY`; multi-step computations are expressed as sequences of
native instructions.

Before treating this document and the source code as a synchronized
release, the assembler should be updated or checked so that its opcode
definitions, instruction-size calculation, and emitted machine code
match the current hardware implementation.
