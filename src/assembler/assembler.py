class Assembler:
    def __init__(self):
        self.symbol_table = {}  
        self.pc = 0             
        self.machine_code = []  

    def pass_one(self, lines):
        print("--- PASS 1 Labels are scanning ---")
        self.pc = 0x0000
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
                
            if line.endswith(":"):
                label = line[:-1].strip()
                if label in self.symbol_table:
                    raise ValueError(f"Error: [Line {line_num}]: '{label}' has already taken")
                self.symbol_table[label] = self.pc
                print(f"Label found -> {label} : 0x{self.pc:04X}")
                continue
                
            byte_size = self.get_instruction_size(line)
            self.pc += byte_size
            
        print(f"--- PASS 1 completed. Total memory size: {self.pc} bayt ---\n")

    def pass_two(self, lines):
        print("--- PASS 2 ---")
        self.pc = 0x0000
        self.machine_code = []
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith("#") or line.endswith(":"):
                continue
                
            bytes_generated = self.assemble_instruction(line, self.pc)
            self.machine_code.extend(bytes_generated)
            self.pc += len(bytes_generated)
            
        print("--- PASS 2 Completed ---")

    def get_instruction_size(self, line):
        parts = line.split()
        if not parts:
            return 0
            
        mnemonic = parts[0].upper()
        args = [p.replace(",", "") for p in parts[1:]]
        real_args = [arg for arg in args if arg.upper() != "F"]
        
        alu_commands = [
            "ADD", "SUB", "SUB_REV", "INC_X", "INC_Y", "DEC_X", "DEC_Y", 
            "AND", "OR", "NEG_X", "NEG_Y", "NOT_X", "NOT_Y", 
            "PASS_X", "PASS_Y", "ZERO", "ONE", "NEG_ONE"
        ]
        
        # ALU Commands length list
        if mnemonic in alu_commands:
            if len(real_args) == 0:
                return 1  # Yalın ALU (Örn: ADD, DEC_X)
            elif len(real_args) == 2:
                return 3  # 2 Register'lı ALU (Örn: ADD R3, R2) -> 1 bayt opcode + 2 bayt reg
            elif len(real_args) == 3:
                return 4  # 3 Register'lı ALU (Örn: ADD R3, R2, R1) -> 1 bayt opcode + 3 bayt reg

        three_byte_instructions = [
            "JMP", "JZ", "JNZ", "JC", "JNC", "JS", "JNS", "CALL", 
            "LDX", "LDY", "LD", "STX", "ST"
        ]
        if mnemonic in three_byte_instructions:
            return 3

        two_byte_instructions = ["LDI", "PW", "PR"]
        if mnemonic in two_byte_instructions:
            return 2

        return 1

    def parse_reg(self, reg_str):
        reg_str = reg_str.upper().strip()
        if reg_str.startswith("R") and reg_str[1:].isdigit():
            val = int(reg_str[1:])
            if 0 <= val <= 7:
                return val
        raise ValueError(f"Invalid Register Format: {reg_str}")

    def assemble_instruction(self, line, current_pc):
        parts = line.split()
        if not parts:
            return []
            
        mnemonic = parts[0].upper()
        raw_args = [p.replace(",", "") for p in parts[1:]]
        
        # Extract 'F' (flag update) variation
        update_flags = False
        if "F" in [arg.upper() for arg in raw_args]:
            update_flags = True
            args = [arg for arg in raw_args if arg.upper() != "F"]
        else:
            args = raw_args

        # 1. HALT, LDK, RET (1 Byte)
        if mnemonic == "HALT" and len(args) == 0:
            return [0x01]
        if mnemonic == "LDK" and len(args) == 0:
            return [0x02]
        if mnemonic == "RET" and len(args) == 0:
            return [0x06]

        # 2. JUMP and CALL (3 Byte)
        jump_ops = {
            "CALL": 0x04, "JMP": 0x08, "JZ": 0x09, "JNZ": 0x0A,
            "JC": 0x0B, "JNC": 0x0C, "JS": 0x0D, "JNS": 0x0E
        }
        if mnemonic in jump_ops and len(args) == 1:
            target = args[0]
            addr = self.symbol_table[target] if target in self.symbol_table else int(target, 0)
            return [jump_ops[mnemonic], addr & 0xFF, (addr >> 8) & 0xFF]

        # 3. IMMEDIATE Loads - LDI (2 Byte)
        if mnemonic == "LDI" and len(args) == 2:
            dest = args[0].upper()
            val_str = args[1]
            imm_val = (self.symbol_table[val_str] if val_str in self.symbol_table else int(val_str, 0)) & 0xFF
            
            if dest == "X":
                return [0x18, imm_val]
            elif dest == "Y":
                return [0x1C, imm_val]
            elif dest.startswith("R"):
                return [0x10 | self.parse_reg(dest), imm_val]
            else:
                raise ValueError(f"Invalid LDI target: {dest}")

        # 4. POINTER Operations - PW, PR (2 Byte)
        if mnemonic in ["PW", "PR"] and len(args) == 2:
            r1, r2 = self.parse_reg(args[0]), self.parse_reg(args[1])
            return [0x20 | r1, 0x28 | r2] if mnemonic == "PW" else [0x30 | r1, 0x38 | r2]

        # 5. REGISTERS - MOV (1 Byte)
        if mnemonic == "MOV" and len(args) == 2:
            dest, src = args[0].upper(), args[1].upper()
            if dest == "RX" and src.startswith("R"):
                return [0x50 | self.parse_reg(src)]
            elif dest.startswith("R" ) and src == "RX":
                return [0x40 | self.parse_reg(dest)]
            elif dest.startswith("R") and src == "RY":
                return [0x58 | self.parse_reg(dest)]
            else:
                raise ValueError(f"Invalid MOV combination: {line}")

        # 6. MEMORY ADDRESSING - LDX, LDY, STX, LD R?, ST R? (3 Byte)
        if mnemonic in ["LDX", "LDY", "STX"] and len(args) == 1:
            addr = int(args[0], 0)
            opcodes = {"LDX": 0x60, "LDY": 0x61, "STX": 0x70}
            return [opcodes[mnemonic], addr & 0xFF, (addr >> 8) & 0xFF]

        if mnemonic in ["LD", "ST"] and len(args) == 2:
            reg_num = self.parse_reg(args[0])
            addr = int(args[1], 0)
            base_op = 0x60 if mnemonic == "LD" else 0x70
            return [base_op | reg_num, addr & 0xFF, (addr >> 8) & 0xFF]

        # 7. ALU Operations (Custom HEX opcode table and 4-step RTL bus packetization)
        alu_opcodes = {
            "ADD": 0x84, "SUB": 0xA6, "SUB_REV": 0x8E, "INC_X": 0xBE, 
            "INC_Y": 0xEE, "DEC_X": 0x9C, "DEC_Y": 0xE4, "AND": 0x80, 
            "OR": 0xAA, "NEG_X": 0x9E, "NEG_Y": 0xE6, "NOT_X": 0x9A, 
            "NOT_Y": 0xE2, "PASS_X": 0x98, "PASS_Y": 0xE0, "ZERO": 0xD4, 
            "ONE": 0xFE, "NEG_ONE": 0xF4
        }
        
        if mnemonic in alu_opcodes:
            base_op = alu_opcodes[mnemonic]
            # Flag update (F) if desired, bit-0 activated (ex: 0x84 -> 0x85)
            opcode = (base_op | 0x01) if update_flags else base_op
            
            if len(args) == 0:
                return [opcode]
            elif len(args) == 2:  # ex: ADD R3, R2 (3 Byte: Opcode + Source1 + Source2)
                r1, r2 = self.parse_reg(args[0]), self.parse_reg(args[1])
                return [opcode, r1, r2]
            elif len(args) == 3:  # ex: ADD R3, R2, R1 (4 Byte: Opcode + Source1 + Source2 + Target)
                r1, r2, r3 = self.parse_reg(args[0]), self.parse_reg(args[1]), self.parse_reg(args[2])
                return [opcode, r1, r2, r3]

        raise ValueError(f"Invalid command or argument type: {line}")

    def save_to_bin(self, filename="program.bin"):
        with open(filename, "wb") as f:
            f.write(bytearray(self.machine_code))
        print(f"'{filename}' file was succesfully created!")


if __name__ == "__main__":
    file_name = "assembly_codes.asm"
    try:
        with open(file_name, "r", encoding="utf-8") as file:
            code_lines = file.readlines()
            
        asm = Assembler()
        asm.pass_one(code_lines)
        asm.pass_two(code_lines)
        
        print("Generated Symbol Table:", asm.symbol_table)
        asm.save_to_bin("program.bin")
        
    except FileNotFoundError:
        print(f"Error: There is no file that named by '{file_name}'")