# Breadboard Computer

A fully custom 8-bit computer designed and built from discrete 74HC-series logic ICs on breadboards.

## Overview

This project is an exploration of computer architecture and digital hardware design through the construction of a computer from the logic-gate level.

Rather than using a pre-existing processor or a microcontroller, the system is built from individual logic ICs. Its architecture, instruction set, control unit, and supporting software have been designed as part of the project.

The computer features a custom instruction set architecture (ISA), an EEPROM-based microcoded control unit, a general-purpose register file, and a Python-based assembler.

## Key Features

- Custom 8-bit CPU architecture
- 16-bit address bus and 64 KB address space
- Eight general-purpose 8-bit registers
- Custom ALU and instruction set
- EEPROM-based microcoded control unit
- Stack pointer and subroutine support
- Memory-mapped ROM, SRAM, and video memory
- Python-based assembler and microcode generator

## Architecture

The processor uses a custom-designed instruction set and a microcoded control unit. Each instruction is executed through a sequence of control signals stored in EEPROM.

The system includes dedicated registers for ALU operations, a program counter, a stack pointer, and memory address registers.

Detailed architectural documentation will be available in the `docs/` directory.

## Software

The project also includes software tools developed specifically for this architecture:

- Assembler written in Python
- Microcode generation tool
- Assembly-language programs
- System software

## Hardware

The computer is physically constructed using 74HC-series logic ICs mounted on breadboards.

The hardware is organized into functional units, including the CPU datapath, control unit, memory subsystem, and input/output components.

## Project Video

[Watch the project demonstration](https://youtu.be/oCEUKDI3oGM?si=A_kuf9yKiH4Wq1qx)

## Documentation

- Instruction Set Architecture (ISA): `docs/ISA.md`
- CPU Architecture: `docs/architecture.md`
- Microarchitecture: `docs/microarchitecture.md`
- Memory Map: `docs/memory-map.md`

Documentation files will be added as the project repository develops.

## Future Development

- Complete hardware documentation and circuit diagrams
- Expand the software ecosystem
- Develop an FPGA implementation using Verilog/SystemVerilog
- Improve the computer's input/output capabilities

## License

License information will be added.