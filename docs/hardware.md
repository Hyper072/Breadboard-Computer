# Hardware Implementation

## 1. Overview

The computer is built entirely from discrete 74HC-series logic integrated circuits mounted on solderless breadboards.

Unlike conventional systems that rely on a dedicated processor chip or microcontroller, this project implements the CPU's datapath, control unit, registers, and supporting logic using individual logic ICs.

The physical implementation consists of approximately 70-80 integrated circuits distributed across multiple breadboards.

The design aims to make the internal operation of a computer physically observable, from individual logic operations to instruction execution.

## 2. Logic Components and Datapath

The CPU is primarily constructed using 74HC-series logic ICs. Its major functional units are implemented by combining individual logic components rather than relying on dedicated processor subsystems.

### Arithmetic Logic Unit (ALU)

The ALU is a custom-built logic circuit, not a dedicated ALU integrated circuit.

It is constructed from:

- Adder circuits for arithmetic operations
- Logic gates for bitwise operations
- Multiplexers (MUXes) for selecting the appropriate operation result

This modular implementation allows the ALU's arithmetic and logical operations to be physically realized and inspected at the logic level.

### Other Datapath Components

Additional logic circuits implement:

- General-purpose and special-purpose registers
- Data bus routing and selection
- Program counter and address registers
- Flags register
- Microcode step counter
- Control signal distribution
- Address decoding and memory control

The datapath is assembled from individual logic ICs, making the processor's internal data flow directly observable.

## 3. Memory Components

The system uses dedicated memory ICs for program storage, general-purpose memory, video memory, and microcode storage.

| Component | Model | Purpose |
|---|---|---|
| System ROM | AT28C256 | Stores the system program |
| Main SRAM | UT62256CPC-70LL | General-purpose memory |
| Video RAM (VRAM) | UT62256CPC-70LL | Stores video data |
| Microcode EEPROMs | AT28C256 | Stores microprogram control words |

The memory architecture and address allocation are documented separately in [Memory Map](memory-map.md).

## 4. Microcoded Control Unit

The control unit is implemented using EEPROM-based microcode.

Four AT28C256 EEPROMs are used to provide a 32-bit-wide control word. Of these, 27 control signals are actively used to coordinate the datapath and execute instructions.

The microcode is generated using a custom Python program, which converts microinstruction definitions into EEPROM-compatible data.

Each instruction is executed through a sequence of microinstructions controlled by the microcode step counter.

For more details, see [Microarchitecture](microarchitecture.md).

## 5. Clock System

The processor uses an external clock source.

The system has been tested at several clock frequencies:

- 1 Hz
- 1 kHz
- 1 MHz

The computer has been successfully operated at 1 MHz.

## 6. Video and Input Hardware

The computer includes hardware interfaces for video output and keyboard input.

### VGA Output

A dedicated region of the address space is allocated to video memory (VRAM).

The VGA circuitry reads this memory to generate the video output. The CPU can modify video memory through its normal memory write operations; no dedicated VGA instruction is required.

### PS/2 Keyboard

A PS/2 keyboard interface provides input to the computer. Keyboard input is made available to software through the processor's I/O mechanism.

## 7. Physical Construction

The processor is assembled across multiple solderless breadboards.

The physical implementation makes it possible to inspect individual registers, buses, control signals, and logic circuits. This also allows individual subsystems to be tested during development.

The project prioritizes transparency and modularity: the processor is built from discrete logic components rather than being hidden inside a single programmable device.

## 8. Future Hardware Development

The current breadboard implementation serves as a physical realization of the processor architecture.

Planned development includes:

- Completing and refining the VGA and keyboard interfaces
- Improving the physical layout and wiring
- Reimplementing the architecture in Verilog/SystemVerilog
- Porting the design to an FPGA platform