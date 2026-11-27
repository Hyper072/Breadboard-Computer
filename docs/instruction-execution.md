
# Instruction Execution Walkthrough: PW

This document demonstrates how the custom processor executes the `PW` (Pointer Write) instruction, from assembly code generation to the final memory write operation.

The example follows the actual instruction encoding and microcode definitions implemented in the assembler and EEPROM microcode generator.

## 1. Example Program

Consider the following assembly program:

```asm
LDI X 0x5A
LDI R6 0x00
LDI R7 0x80

PW R6, R7
```

The program initializes the processor's internal registers and then writes the value stored in `RX` to a memory address constructed from `R6` and `R7`.

Initial values before executing `PW`:

| Register | Value |
|---|---:|
| RX | `0x5A` |
| R6 | `0x00` |
| R7 | `0x80` |

## 2. Assembly to Machine Code

The assembler encodes `PW` using two instruction bytes.

The encoding rule is:

- First byte: `0x20 | register_number`
- Second byte: `0x28 | register_number`

For `PW R6, R7`:

| Byte | Calculation | Result |
|---|---|---|
| First | `0x20 | 0x06` | `0x26` |
| Second | `0x28 | 0x07` | `0x2F` |

The resulting machine code is:

```text
26 2F
```

The first byte selects the low address register, while the second byte selects the high address register.

## 3. Address Generation

The processor constructs a 16-bit memory address using two 8-bit general-purpose registers.

The address is formed as:

```text
Address = (R7 << 8) | R6
```

With the example register values:

```text
R7 = 0x80
R6 = 0x00

Address = 0x8000
```

The address is transferred into the Memory Address Register (MAR):

- `MARL` receives the contents of `R6`.
- `MARH` receives the contents of `R7`.

Therefore:

```text
MAR = 0x8000
```

## 4. Microcoded Instruction Execution

The control unit uses four EEPROMs to generate the processor's control signals.

The microprogram address is organized using the current microstep, opcode, and processor flags.

Instruction execution begins with the common instruction-fetch sequence.

### 4.1 Common Fetch Sequence

| Microstep | Control Signals | Operation |
|---|---|---|
| 0 | `PC_OE`, `MEM_RE`, `IR_LD` | Read the first instruction byte into IR |
| 1 | `PC_EN` | Increment PC |

After this sequence, the first byte (`0x26`) is decoded.

### 4.2 First Byte: `0x26`

The opcode is matched against the `0x20` instruction group using the mask `0xF8`.

The register selection identifies `R6`.

| Microstep | Control Signals | Operation |
|---|---|---|
| 2 | `RF_RE`, `MARL` | Transfer R6 to MARL |
| 3 | `PC_OE`, `MEM_RE`, `IR_LD` | Read the second instruction byte into IR |

The second byte (`0x2F`) is now available in the instruction register.

### 4.3 Second Byte: `0x2F`

The second byte is matched against the `0x28` instruction group, also using the mask `0xF8`.

The register selection identifies `R7`.

| Microstep | Control Signals | Operation |
|---|---|---|
| 4–6 | `NULLY` | Reserved/unused control-word entries |
| 7 | `RF_RE`, `MARH` | Transfer R7 to MARH |
| 8 | `MAR_OE`, `RX_OE`, `MEM_WE` | Write RX to the memory address held in MAR |
| 9 | `PC_EN` | Increment PC |
| 10 | `SC_RST` | Reset the microstep counter |

At microstep 8, the memory write operation takes place:

```text
Memory[MAR] = RX
Memory[0x8000] = 0x5A
```

The instruction execution is then completed, and the control unit returns to the instruction-fetch sequence.

## 5. Final Processor State

After executing `PW R6, R7`, the relevant processor state is:

| Component | Final Value |
|---|---:|
| RX | `0x5A` |
| R6 | `0x00` |
| R7 | `0x80` |
| MARL | `0x00` |
| MARH | `0x80` |
| MAR | `0x8000` |
| Memory[`0x8000`] | `0x5A` |

The address `0x8000` belongs to the SRAM region of the computer's memory map.

## 6. Execution Summary

The `PW` instruction demonstrates how the processor combines its register file, internal address registers, instruction register, memory interface, and microcoded control unit to perform a 16-bit addressed memory write.

Although the processor has an 8-bit data bus, it can address a 16-bit memory space by constructing addresses from two 8-bit registers.

This instruction is a practical example of how the custom instruction set and EEPROM-based microarchitecture work together to implement memory operations.
