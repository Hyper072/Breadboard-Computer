# Memory Map and Memory Subsystem

**Project:** Breadboard Computer  
**Address Bus:** 16 bits  
**Data Bus:** 8 bits  
**Total Address Space:** 64 KB  
**Memory Organization:** Memory-mapped ROM, SRAM, and VRAM

---

## 1. Overview

The Breadboard Computer uses a 16-bit address bus, providing a total addressable memory space of 64 KB.

The memory subsystem is divided into three regions:

- System ROM
- General-purpose SRAM
- Video RAM (VRAM)

Each region is selected through address decoding logic. All memory devices share a common 8-bit data bus.

The Control Unit provides the memory read and write control signals, while the address decoding logic selects the appropriate memory device.

---

## 2. Memory Map

The complete 64 KB address space is organized as follows:

| Address Range | Size | Memory Device | Purpose |
|---|---:|---|---|
| `0x0000 - 0x7FFF` | 32 KB | AT28C256 | System ROM |
| `0x8000 - 0xEFFF` | 28 KB | UT62256CPC-70LL | General-purpose SRAM |
| `0xF000 - 0xFFFF` | 4 KB | UT62256CPC-70LL | Video RAM |

### 2.1 Address Space Diagram

```text
+-----------------------------+ 0xFFFF
|                             |
|          Video RAM          |
|            4 KB             |
|                             |
+-----------------------------+ 0xF000
|                             |
|                             |
|       General-Purpose       |
|             SRAM            |
|            28 KB            |
|                             |
|                             |
+-----------------------------+ 0x8000
|                             |
|                             |
|          System ROM         |
|            32 KB            |
|                             |
|                             |
+-----------------------------+ 0x0000
```

The three regions cover the entire 16-bit address space without overlapping.

---

## 3. System ROM

The lower 32 KB of the address space is assigned to the System ROM.

| Property | Value |
|---|---|
| Address range | `0x0000 - 0x7FFF` |
| Capacity | 32 KB |
| Device | AT28C256 |
| Access type | Read-only during normal operation |

The System ROM stores the program code executed by the processor, including the terminal operating system.

The ROM is accessed through the common data bus and selected by the memory address decoding logic.

### 3.1 Write Protection

The ROM write-enable input is tied directly to VCC.

Consequently, the normal `MEM_WE` control signal does not control ROM writes. The ROM remains write-disabled during normal processor operation.

---

## 4. General-Purpose SRAM

The SRAM region occupies addresses `0x8000` through `0xEFFF`.

| Property | Value |
|---|---|
| Address range | `0x8000 - 0xEFFF` |
| Mapped size | 28 KB |
| Device | UT62256CPC-70LL |
| Access type | Read and write |

This region provides writable memory for program data and runtime operations.

The SRAM is accessed using the processor's normal memory read and write operations.

The memory address is supplied through the processor's Memory Address Register (MAR).

Although the physical UT62256CPC-70LL device has a capacity of 32 KB, only the 28 KB address range assigned to this region is mapped into the processor's address space.

---

## 5. Video RAM (VRAM)

The upper 4 KB of the address space is reserved for video memory.

| Property | Value |
|---|---|
| Address range | `0xF000 - 0xFFFF` |
| Mapped size | 4 KB |
| Device | UT62256CPC-70LL |
| Access type | Read and write |

VRAM is implemented using a separate UT62256CPC-70LL SRAM chip.

It is mapped into the processor's address space, allowing software to access video memory through normal memory operations.

### 5.1 CPU Access

The CPU accesses VRAM using the same memory interface used for general-purpose memory.

Software can write data to VRAM using the processor's memory store instructions.

There are no dedicated VGA instructions in the current ISA.

### 5.2 VGA Access

The VGA subsystem reads data from the same physical VRAM chip to generate the video output.

This allows the contents of video memory to be used by both the processor and the VGA subsystem.

The physical VRAM device has a capacity of 32 KB, but only the final 4 KB of the CPU address space is assigned to the video memory region.

---

## 6. Memory Interface

All memory devices share a common 8-bit data bus.

The processor uses its Memory Address Register to provide the address for memory operations.

The Control Unit generates two main memory control signals:

| Signal | Function |
|---|---|
| `MEM_RE` | Enables memory read operations |
| `MEM_WE` | Enables memory write operations |

The address decoding logic selects the appropriate memory device based on the address placed on the address bus.

This separates memory selection from the instruction-specific control logic.

### 6.1 Memory Read Operation

During a memory read operation:

1. The processor places the requested address into the Memory Address Register.
2. The address decoding logic selects the corresponding memory device.
3. The Control Unit activates `MEM_RE`.
4. The selected memory device provides its data on the common 8-bit data bus.
5. The destination register or processor component captures the data.

### 6.2 Memory Write Operation

During a memory write operation:

1. The processor places the target address into the Memory Address Register.
2. The address decoding logic selects the corresponding memory device.
3. The processor places the data to be stored on the data bus.
4. The Control Unit activates `MEM_WE`.
5. The selected writable memory device stores the data.

The System ROM remains write-disabled because its write-enable input is tied to VCC.

---

## 7. Address Decoding

The memory subsystem uses address decoding logic to determine which memory device corresponds to the current 16-bit address.

The address decoder examines the upper address bits to distinguish between the three memory regions.

The resulting selection signals activate the appropriate memory device.

The address decoder and memory control signals work together:

- Address decoding determines which memory device is selected.
- `MEM_RE` controls CPU memory read operations.
- `MEM_WE` controls CPU memory write operations.

The exact gate-level implementation of the address decoder can be documented separately in the hardware schematics.

---

## 8. Memory Subsystem Summary

| Region | Start Address | End Address | Mapped Size | Device |
|---|---|---|---:|---|
| System ROM | `0x0000` | `0x7FFF` | 32 KB | AT28C256 |
| SRAM | `0x8000` | `0xEFFF` | 28 KB | UT62256CPC-70LL |
| VRAM | `0xF000` | `0xFFFF` | 4 KB | UT62256CPC-70LL |
| **Total** | `0x0000` | `0xFFFF` | **64 KB** | |

The memory subsystem provides the storage required for system software, runtime data, and video output.

Its organization combines EEPROM-based program storage, writable SRAM, and memory-mapped video memory within a single 16-bit address space.

---

## 9. Related Documentation

- [Computer Architecture](architecture.md)
- [CPU Microarchitecture](microarchitecture.md)
- [Instruction Set Architecture](ISA.md)

Detailed circuit schematics and address-decoding logic diagrams can be added as separate hardware documentation.