# CPU Microarchitecture

**Project:** Breadboard Computer  
**Processor:** Custom 8-bit CPU  
**Control Architecture:** EEPROM-based microprogrammed control  
**Microinstruction Width:** 32 bits  
**Active Control Signals:** 27  
**Microcode Address Width:** 15 bits

---

## 1. Overview

The processor uses a microprogrammed control architecture. Its control unit is implemented using four EEPROM devices that store the microinstructions required to execute the processor's native instruction set.

Rather than generating control signals through a large hardwired control circuit, the processor retrieves predefined control words from EEPROM. Each control word determines which hardware operations are performed during a particular microstep.

The microcode generator is implemented in Python. It converts the instruction definitions, execution sequences, and conditional flag logic into four binary EEPROM images.

The control unit coordinates the processor datapath, register file, ALU, memory interface, Program Counter, Stack Pointer, and input interface.

---

## 2. Microcode Address Organization

The microcode address is composed of three fields:

| Field | Width | Description |
|---|---:|---|
| Microstep | 4 bits | Current execution step |
| Opcode | 8 bits | Instruction opcode |
| Flags | 3 bits | Current processor flag states |
| Total | 15 bits | EEPROM address |

The address fields are arranged as follows:

```text
+----------------+----------------+----------------+
|   Microstep    |     Opcode     |     Flags      |
|     4 bits     |     8 bits     |     3 bits     |
+----------------+----------------+----------------+
   Bits 14-11       Bits 10-3        Bits 2-0
```

The microcode generator extracts these fields using the following operations:

```python
step = (address >> 11) & 0x0F
opcode = (address >> 3) & 0xFF
flags = address & 0x07
```

This organization allows the control unit to select microinstructions based on the current instruction, its execution step, and the processor's flag state.

### 2.1 Microstep Counter

The microstep counter tracks the current stage of instruction execution.

It provides the microstep field used in the EEPROM address.

The counter is reset using the `SC_RST` control signal when an instruction finishes. The next instruction then begins from the common fetch sequence.

The microstep field is 4 bits wide, allowing up to 16 distinct microsteps per instruction.

---

## 3. EEPROM-Based Control Unit

The control unit uses four EEPROM devices to store the generated microcode.

Each EEPROM stores one byte of the 32-bit control word.

| EEPROM | Control Word Bits |
|---|---|
| EEPROM 0 | Bits 0-7 |
| EEPROM 1 | Bits 8-15 |
| EEPROM 2 | Bits 16-23 |
| EEPROM 3 | Bits 24-31 |

Each EEPROM contains 32,768 addressable entries, corresponding to the 15-bit microcode address space.

The Python generator creates four binary files:

```text
eeprom_0.bin
eeprom_1.bin
eeprom_2.bin
eeprom_3.bin
```

These files contain the individual control-word bytes for programming the EEPROM devices.

Although the control word provides 32 bit positions, 27 active control signals are defined in the current implementation.

---

## 4. Control Signal Architecture

The microcode controls the processor through a set of dedicated control signals.

The signals are grouped according to the hardware units they operate.

### 4.1 ALU and Register Control

| Signal | Function |
|---|---|
| RX_MUX | Selects the RX input source |
| RX_LD | Loads RX |
| RY_LD | Loads RY |
| RX_OE | Enables RX output |
| CARRY | Controls the ALU carry input |
| FLAG_WE | Enables flag register updates |
| RF_RE | Enables register file read |
| RF_WE | Enables register file write |

### 4.2 Program Counter Control

| Signal | Function |
|---|---|
| PC_EN | Enables Program Counter increment |
| PC_OE | Enables Program Counter output |
| PC_LD | Loads the Program Counter |
| PC_BL | Selects the low-byte path for PC operations |
| PC_BH | Selects the high-byte path for PC operations |
| PC_JE | Enables loading the PC from the jump-address path |

### 4.3 Memory and Address Register Control

| Signal | Function |
|---|---|
| MEM_RE | Enables memory read |
| MEM_WE | Enables memory write |
| MARL | Loads the low byte of MAR |
| MARH | Loads the high byte of MAR |
| MAR_OE | Enables MAR output |

### 4.4 Stack Pointer Control

| Signal | Function |
|---|---|
| SP_DEC | Controls SP decrement |
| SP_EN | Enables SP update |
| SP_OE | Enables SP output |

### 4.5 Other Control Signals

| Signal | Function |
|---|---|
| SC_RST | Resets the microstep counter |
| IR_LD | Loads the Instruction Register |
| KB_OE | Enables keyboard data output |
| KB_CLR | Clears keyboard input state |
| HLT | Activates processor halt control |

---

## 5. Instruction Fetch and Execution

The processor uses a common instruction fetch sequence before executing the instruction-specific microprogram.

### 5.1 Fetch Cycle

The first two microsteps are shared by the instruction set.

**Microstep 0 - Instruction Fetch**

```text
PC_OE | MEM_RE | IR_LD
```

The Program Counter provides the address of the current instruction byte. Memory read is enabled, and the fetched opcode is loaded into the Instruction Register.

**Microstep 1 - Program Counter Increment**

```text
PC_EN
```

The Program Counter advances to the next instruction byte.

### 5.2 Instruction Execution

Instruction-specific execution begins at microstep 2.

The generator calculates the execution index as:

```python
exec_index = step - 2
```

The opcode selects the corresponding microprogram. The execution index selects the control word within that microprogram.

When the instruction completes, the microprogram activates `SC_RST`, returning the microstep counter to the beginning of the next fetch sequence.

### 5.3 Fetch and Execute Flow

```text
             +----------------------+
             |   Microstep 0        |
             |   Fetch Opcode       |
             +----------+-----------+
                        |
                        v
             +----------------------+
             |   Microstep 1        |
             |   Increment PC       |
             +----------+-----------+
                        |
                        v
             +----------------------+
             |   Microstep 2+       |
             |   Instruction        |
             |   Execution          |
             +----------+-----------+
                        |
                        v
             +----------------------+
             |      SC_RST          |
             |   Reset Step Counter |
             +----------+-----------+
                        |
                        v
                  Next Fetch
```

The number of execution microsteps depends on the instruction.

---

## 6. ALU Microcode Execution

ALU instructions follow a dedicated microcode path.

The generator identifies ALU instructions using a predefined set of base opcodes.

Bit 0 of the opcode is reserved for the optional flag-update variation. Therefore, the generator masks this bit when identifying the base ALU operation:

```python
base_op_check = opcode & 0xFE
```

### 6.1 ALU Execution Sequence

ALU operations use two execution microsteps after the common fetch sequence.

**Execution Index 0 - ALU Operation**

The control unit activates:

```text
RX_MUX | RX_LD
```

The RX input multiplexer selects the ALU result, and RX is loaded with that result.

Additional control signals depend on the instruction:

- `FLAG_WE` is activated when opcode bit 0 is set.
- `CARRY` is activated for the ALU operations defined in the microcode generator's carry-control set.

**Execution Index 1 - Microstep Reset**

```text
SC_RST
```

The microstep counter is reset, and the processor returns to the instruction fetch sequence.

### 6.2 Flag Update Selection

The lowest opcode bit controls whether the ALU instruction updates the processor flags.

| Opcode Bit 0 | Behavior |
|---|---|
| 0 | Preserve existing flags |
| 1 | Enable flag register updates |

When flag updates are enabled, the processor can update its Carry, Zero, and Sign flags according to the ALU result.

The exact flag definitions and arithmetic conventions are documented in `ISA.md`.

---

## 7. Conditional Branch Microcode

Conditional branch instructions use the current processor flags as part of the microcode address.

The microcode generator evaluates the relevant flag and selects one of two execution sequences.

The supported conditions are:

| Instruction | Condition |
|---|---|
| JZ | Zero flag is set |
| JNZ | Zero flag is clear |
| JC | Carry flag is set |
| JNC | Carry flag is clear |
| JS | Sign flag is set |
| JNS | Sign flag is clear |

### 7.1 Conditional Sequence

When the branch condition is satisfied, the processor fetches the two target-address bytes and loads the target address into the Program Counter.

When the condition is not satisfied, the microcode increments the Program Counter twice to skip the two-byte target address.

This allows both execution paths to continue at the next instruction without executing the branch target.

The branch selection is performed by the microcode generator using the current flag field and the condition associated with the opcode.

### 7.2 Flag-Dependent Microcode Selection

The conditional microprogram definitions contain:

- Target flag
- Inversion setting
- Execution sequence when the condition is true
- Execution sequence when the condition is false

For instructions such as `JNZ`, `JNC`, and `JNS`, the corresponding flag condition is inverted.

---

## 8. Multi-Byte Instruction Handling

The processor supports instructions with different lengths. The microcode controls the fetching and interpretation of their additional bytes.

### 8.1 Immediate Instructions

Immediate load instructions retrieve the next instruction byte from memory and load it into the selected destination.

The destination may be a general-purpose register, RX, or RY.

The Program Counter is incremented after the immediate byte is fetched.

### 8.2 Direct Memory Instructions

Direct memory instructions retrieve a 16-bit address from the instruction stream.

The low address byte is loaded into MARL, followed by the high address byte into MARH.

The completed address is then used for the memory read or write operation.

### 8.3 Pointer Instructions

The `PW` and `PR` instructions use two instruction bytes to select the low and high address registers.

Their execution is handled through a special microcode sequence.

The first instruction byte selects the register used to load MARL. The second byte is fetched into the Instruction Register without resetting the microstep counter.

The second byte selects the register used to load MARH.

After both address bytes are assembled:

- `PW` writes the value of RX to the selected memory address.
- `PR` reads the selected memory address into RX.

This mechanism allows software to perform indirect memory access using register-selected addresses.

---

## 9. Stack and Subroutine Control

The microcoded control unit manages subroutine calls and returns through the Stack Pointer.

### 9.1 CALL

The `CALL` instruction retrieves the target address from the instruction stream and saves the return address on the stack.

The return address is stored as two bytes:

1. Low byte
2. High byte

The stack grows toward higher memory addresses.

After the return address has been saved, the target address is loaded into the Program Counter.

### 9.2 RET

The `RET` instruction restores the saved return address from the stack.

The high byte is retrieved first, followed by the low byte.

The restored address is transferred to the Program Counter, allowing execution to continue after the original `CALL` instruction.

---

## 10. Microcode Generation

The microcode is generated using a custom Python program.

The generator defines:

- Processor flag bit positions
- Control signal bit positions
- Native instruction opcodes
- Instruction-specific microprograms
- Conditional execution sequences
- ALU operation handling

It iterates through the complete 15-bit microcode address space and generates a 32-bit control word for each address.

The resulting control word is divided into four bytes and written to separate binary files.

### 10.1 Generation Process

```text
+---------------------------+
|  Instruction Definitions  |
+-------------+-------------+
              |
              v
+---------------------------+
|    Opcode and Flag Logic  |
+-------------+-------------+
              |
              v
+---------------------------+
|   Microstep Generation    |
+-------------+-------------+
              |
              v
+---------------------------+
|   32-bit Control Words    |
+-------------+-------------+
              |
              v
+---------------------------+
|   Split into 4 Bytes      |
+-------------+-------------+
              |
              v
+---------------------------+
|   Four EEPROM Binary Files|
+---------------------------+
```

The generated binary files are used to program the EEPROM devices that implement the processor's control unit.

---

## 11. Hardware Implementation Notes

The microcoded control unit is physically implemented using EEPROM devices rather than being simulated in software.

The Python generator is a development tool used to create the control memory contents. During processor operation, the EEPROMs provide the control words required by the hardware.

The control unit coordinates the processor's physical components through dedicated control signals.

This design makes the instruction execution process explicit and allows the processor's behavior to be modified by changing the microcode.

---

## 12. Related Documentation

- [Computer Architecture](architecture.md)
- [Instruction Set Architecture](ISA.md)
- [Memory Map](memory-map.md)

Additional timing diagrams, detailed control-signal sequences, and hardware schematics can be added as the documentation develops.