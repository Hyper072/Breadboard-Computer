# Computer Architecture

**Project:** Breadboard Computer  
**Architecture:** Custom 8-bit processor  
**Implementation:** Discrete 74HC-series logic ICs  
**Control Unit:** EEPROM-based microcoded controller  
**Status:** Physical hardware implementation

---

## 1. System Overview

The Breadboard Computer is a custom-designed 8-bit computer physically implemented using discrete 74HC-series logic integrated circuits mounted on breadboards.

The system was designed from the ground up, including its processor datapath, register architecture, arithmetic logic unit, instruction set, microcoded control unit, memory subsystem, and supporting software.

The processor uses an 8-bit data bus and a 16-bit address bus, providing a 64 KB address space. Its control unit is implemented using EEPROMs that store the microinstructions required to execute each native instruction.

The computer also includes memory-mapped video memory and a PS/2 keyboard interface, allowing it to execute software and interact with external input and output devices.

### 1.1 Main Specifications

| Component | Specification |
|---|---|
| Data bus | 8 bits |
| Address bus | 16 bits |
| Address space | 64 KB |
| General-purpose registers | 8 x 8-bit |
| ALU operand registers | RX and RY, 8 bits each |
| Program Counter (PC) | 16 bits |
| Stack Pointer (SP) | 4 bits |
| Memory Address Register (MAR) | 16 bits |
| Instruction Register (IR) | 8 bits |
| Flags | Carry, Zero, Sign |
| Control unit | EEPROM-based microcoded |
| Main logic family | 74HC series |

---

## 2. System Architecture

The computer consists of several interconnected functional units. Each unit is implemented using discrete logic ICs and communicates with the others through the processor's internal buses and control signals.

The main functional units are:

- CPU datapath
- Register file
- Arithmetic Logic Unit (ALU)
- Microcoded control unit
- Memory subsystem
- Video memory and VGA interface
- PS/2 keyboard interface

### 2.1 High-Level Block Diagram

The following diagram illustrates the main functional organization of the system.

```
                   +----------------------+
                   |    Control Unit      |
                   |   EEPROM Microcode   |
                   +----------+-----------+
                              |
                       Control Signals
                              |
                              v
+------------------------------------------------------+
|                        CPU                           |
|                                                      |
|  +----------------+       +----------------------+  |
|  | Register File  |       |    ALU Registers     |  |
|  |                |       |                      |  |
|  | R0 - R7        |       | RX          RY       |  |
|  +-------+--------+       +----------+-----------+  |
|          |                           |              |
|          |                           v              |
|          |                  +----------------+      |
|          +----------------->|      ALU       |      |
|                             +----------------+      |
|                                                      |
|  +----------+  +----------+  +-------------------+   |
|  |   PC     |  |   SP     |  |       MAR         |   |
|  |  16-bit  |  |  4-bit  |  |      16-bit       |   |
|  +----------+  +----------+  +-------------------+   |
|                                                      |
|                   +-------------+                    |
|                   |     IR      |                    |
|                   |   8-bit     |                    |
|                   +-------------+                    |
+--------------------------+---------------------------+
                           |
                    8-bit Data Bus
                           |
                           v
                 +-------------------+
                 |  Memory Subsystem |
                 +---------+---------+
                           |
             +-------------+-------------+
             |             |             |
             v             v             v
         System ROM      SRAM          VRAM
                                      |
                                      v
                                 VGA Output
                           
                 PS/2 Keyboard Interface
                           |
                           v
                      CPU Input
```

This is a functional overview rather than a complete electrical schematic. Individual signal connections and logic-level implementations can be documented separately.

---

## 3. CPU Datapath

The processor datapath is responsible for transferring, storing, and processing 8-bit data values.

It contains a general-purpose register file, dedicated ALU operand registers, an arithmetic logic unit, and several special-purpose registers.

The main data path is built around an 8-bit internal data bus.

### 3.1 Internal Data Bus

The internal data bus is 8 bits wide and is used to transfer data between the processor's functional units.

It provides communication between:

- General-purpose registers
- ALU operand registers
- Memory interface
- Instruction register
- Special-purpose registers

The control unit determines which component can drive the bus and which component receives data during each microinstruction.

### 3.2 Register File

The processor contains eight general-purpose 8-bit registers:

`R0`, `R1`, `R2`, `R3`, `R4`, `R5`, `R6`, and `R7`.

These registers are used to store intermediate values, operands, and program data.

The register file is physically separate from the dedicated ALU operand registers.

Register selection is encoded in instruction opcode bits for several instruction groups, reducing the need for additional operand bytes.

### 3.3 ALU Operand Registers

The ALU uses two dedicated 8-bit registers:

- RX: First ALU operand and result register.
- RY: Second ALU operand register.

These registers are separate from the general-purpose register file.

The ALU receives its operands from RX and RY. Depending on the selected operation, the result is written back into RX.

This arrangement allows multiple native ALU instructions to operate on previously loaded values without requiring all operands to be fetched from memory.

The RX input multiplexer selects between the internal data bus and the ALU result.

RY is loaded from the internal data bus.

### 3.4 Arithmetic Logic Unit

The ALU performs arithmetic and logical operations on 8-bit values.

Its instruction set includes operations such as:

- Addition
- Subtraction
- Bitwise AND
- Bitwise OR
- Bitwise NOT
- Increment
- Decrement
- Negation
- Operand pass-through
- Constant generation

The ALU result is written into RX.

The ALU also generates status information used by the processor's flag register.

### 3.5 Flag Register

The processor maintains three status flags:

| Flag | Description |
|---|---|
| C | Carry flag |
| Z | Zero flag |
| S | Sign flag |

These flags provide information about the result of ALU operations and are used by conditional branch instructions.

Flag updates are controlled by the instruction encoding. Instructions that do not request flag updates preserve the existing flag values.

Detailed flag behavior is documented in `ISA.md`.

---

## 4. Special-Purpose Registers

In addition to the general-purpose register file, the processor contains several dedicated registers that support instruction execution and memory operations.

### 4.1 Program Counter (PC)

The Program Counter is a 16-bit register that stores the address of the next instruction byte to be fetched.

It is connected to the memory interface and can place its value onto the internal data bus through its high-byte and low-byte output paths.

The PC is incremented through explicit control-unit operations during instruction fetching and execution.

It also supports loading a new address for jump and subroutine instructions.

### 4.2 Instruction Register (IR)

The Instruction Register is an 8-bit register that stores the instruction opcode used by the control unit.

The opcode determines which microprogram is executed.

Most instructions use the first instruction byte as their opcode. Certain multi-byte instructions also use the IR to decode an additional instruction byte during their execution sequence.

### 4.3 Memory Address Register (MAR)

The Memory Address Register stores the 16-bit address used for memory access.

It is implemented using two 8-bit registers:

- MARL: Low address byte
- MARH: High address byte

Together, they form the complete memory address:

```text
MAR = (MARH << 8) | MARL
```

The MAR provides the address to the memory subsystem during read and write operations.

### 4.4 Stack Pointer (SP)

The Stack Pointer is a 4-bit register used to manage the processor's stack.

It supports subroutine calls and returns through the `CALL` and `RET` instructions.

The stack grows toward higher memory addresses.

During a `CALL`, the return address is pushed onto the stack. During a `RET`, the saved return address is restored to the Program Counter.

---

## 5. Microcoded Control Unit

The processor uses a microprogrammed control unit implemented with EEPROMs.

Instead of generating all control signals through a large network of hardwired combinational logic, the control unit retrieves microinstructions from EEPROM and activates the corresponding control signals.

Each native instruction is associated with a microprogram consisting of multiple execution steps.

### 5.1 Microcode Organization

The microcode address is determined by three fields:

- Microstep counter
- Instruction opcode
- Processor flag states

The control unit uses these values to select the appropriate microinstruction.

The microcode is stored across four EEPROM devices, providing 32 available control-signal positions. The implementation uses 27 active control signals.

### 5.2 Control Signals

The control unit manages operations throughout the processor, including:

- Register reads and writes
- ALU operand loading
- ALU result selection
- Program Counter operations
- Memory read and write operations
- Memory Address Register loading
- Stack operations
- Instruction Register loading
- Keyboard input handling
- Microstep counter reset
- Processor halt control

### 5.3 Instruction Execution

Instruction execution is divided into microsteps.

The common instruction fetch sequence begins with:

**Microstep 0: Instruction Fetch**

The Program Counter places the current address on the bus, memory read is enabled, and the instruction opcode is loaded into the Instruction Register.

**Microstep 1: Program Counter Update**

The Program Counter is incremented to point to the next instruction byte.

**Microstep 2 and Later: Instruction Execution**

The control unit executes the microprogram associated with the opcode. Depending on the instruction, additional memory accesses, register transfers, ALU operations, or control-flow operations may occur.

After the instruction completes, the microstep counter is reset and the processor begins fetching the next instruction.

The exact sequence of control signals depends on the instruction's microprogram.

---

## 6. Memory Architecture

The processor uses a 16-bit address bus, providing a total address space of 64 KB.

The memory subsystem is divided into three regions:

| Address Range | Size | Device | Purpose |
|---|---:|---|---|
| `0x0000 - 0x7FFF` | 32 KB | AT28C256 | System ROM |
| `0x8000 - 0xEFFF` | 28 KB | UT62256CPC-70LL | SRAM |
| `0xF000 - 0xFFFF` | 4 KB | UT62256CPC-70LL | Video RAM |

### 6.1 System ROM

The first 32 KB of the address space is assigned to the system ROM.

It uses an AT28C256 EEPROM and stores the system program, including the terminal operating system.

The ROM is read-only during normal processor operation. Its write-enable input is tied inactive.

### 6.2 SRAM

The SRAM region occupies addresses `0x8000` through `0xEFFF`.

It is implemented using a UT62256CPC-70LL static RAM chip.

This region provides general-purpose read and write memory for programs and runtime data.

### 6.3 Video RAM

The final 4 KB of the address space is reserved for video memory.

It is implemented using a separate UT62256CPC-70LL SRAM chip.

The VGA interface reads data from this memory region to generate the video output.

Video memory is memory-mapped. Software accesses it through normal memory operations rather than dedicated VGA instructions.

### 6.4 Address Decoding

The memory subsystem uses address decoding logic to select the appropriate memory device based on the address placed on the address bus.

The control unit provides the memory read and write control signals.

The address decoder determines which memory region is active during an access.

---

## 7. Input and Output Architecture

The computer includes two main input/output interfaces: a VGA video output and a PS/2 keyboard input.

### 7.1 VGA Interface

The VGA output is driven by the video subsystem using the dedicated video memory region.

The video memory is accessible to the CPU through the memory-mapped address space.

Software can update the displayed content by writing data to video memory using normal memory instructions.

There are no dedicated VGA instructions in the current ISA.

### 7.2 PS/2 Keyboard Interface

The computer includes a PS/2 keyboard interface for user input.

Keyboard data is made available to the processor through a keyboard input buffer.

The `LDK` instruction reads the available keyboard data directly into RX and clears the keyboard input state.

The instruction does not block or wait for a key press when the buffer is empty. Software can poll the keyboard input in a loop when it needs to wait for user input.

---

## 8. Instruction Execution and Control Flow

The processor supports several instruction categories:

- Data transfer instructions
- Immediate load instructions
- Arithmetic and logical instructions
- Memory access instructions
- Conditional and unconditional jumps
- Subroutine calls and returns
- Input operations
- Halt operation

Instructions have variable lengths of one, two, or three bytes.

The Program Counter advances through instruction bytes using explicit microcoded operations.

Conditional branch instructions evaluate the current processor flags to determine whether the branch should be taken.

Subroutine calls and returns use the dedicated stack mechanism implemented through the Stack Pointer.

For the complete opcode definitions, instruction encodings, and assembly syntax, refer to `ISA.md`.

---

## 9. Physical Implementation

The computer is physically constructed using 74HC-series logic ICs mounted on breadboards.

The design is divided into functional hardware sections, allowing the datapath, control unit, memory subsystem, and input/output components to be developed and tested independently.

The microcode is programmed into EEPROM devices using a custom Python-based microcode generation tool.

The processor has been tested at clock frequencies of 1 Hz, 1 kHz, and 1 MHz, with stable operation demonstrated at 1 MHz.

The physical implementation is an important part of the project: the computer is not merely a processor simulation or an FPGA design, but a functioning system assembled from discrete logic components.

---

## 10. Related Documentation

- [Instruction Set Architecture](ISA.md)
- [Microarchitecture](microarchitecture.md)
- [Memory Map](memory-map.md)

Additional hardware diagrams, circuit documentation, and implementation details will be added as the project documentation develops.

---

## 11. Future Development

Planned development includes:

- More detailed hardware schematics and circuit diagrams
- Expanded documentation of individual functional units
- Further software development for the custom architecture
- A Verilog/SystemVerilog implementation
- An FPGA-based version of the processor

The FPGA implementation will provide an opportunity to explore the same architecture using RTL design and programmable logic.