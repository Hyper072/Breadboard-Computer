eeprom_byte0 = bytearray(32768) # Signals 0 - 7
eeprom_byte1 = bytearray(32768) # Signals 8 - 15
eeprom_byte2 = bytearray(32768) # Signals 16 - 23
eeprom_byte3 = bytearray(32768) # Signals 24 - 26

#FLAG BITS
FLAG_C = 1 << 0
FLAG_Z = 1 << 1  
FLAG_S = 1 << 2

#ALU pins
RX_MUX = 1 << 0x00
RX_LD = 1 << 0x01
RY_LD = 1 << 0x02
RX_OE = 1 << 0x03
CARRY = 1 << 0x04
FLAG_WE = 1 << 0x05

#Register File pins
RF_RE = 1 << 0x06
RF_WE = 1 << 0x07

#PC pins
PC_EN = 1 << 0x08
PC_OE = 1 << 0x09
PC_LD = 1 << 0x0A
PC_BL = 1 << 0x0B
PC_BH = 1 << 0x0C
PC_JE = 1 << 0x0D

#Memory pins
MEM_RE = 1 << 0x0E
MEM_WE = 1 << 0x0F

#MAR pins
MARL = 1 << 0x10
MARH = 1 << 0x11
MAR_OE = 1 << 0x12

#Stack Pointer pins
SP_DEC = 1 << 0x13
SP_EN = 1 << 0x14
SP_OE = 1 << 0x15

#Step Counter pins
SC_RST = 1 << 0x16

#Instruction Register pins
IR_LD = 1 << 0x17

#Keyboard pins
KB_OE = 1 << 0x18
KB_CLR = 1 << 0x19

#Clock pins
HLT = 1 << 0x1A

#NULL pin
NULLY = 1 << 0x1F


INSTRUCTIONS = [
    #NOPE
    (0x00, 0xFF, [
        NULLY,
        SC_RST
    ]),
    #HALT
    (0x01, 0xFF, [
        HLT   
    ]),
    #LOAD_KEYBOARD
    (0x02, 0xFE, [
        KB_OE | RX_LD,
        KB_CLR,
        SC_RST
    ]),
    #CALL
    (0x04, 0xFE, [
        PC_OE | MEM_RE | MARL,
        PC_EN,
        PC_OE | MEM_RE | MARH,
        PC_EN,
        PC_OE | PC_LD,
        PC_BL | SP_OE | MEM_WE,
        SP_EN,
        PC_BH | SP_OE | MEM_WE,
        MAR_OE | PC_JE | SP_EN,
        SC_RST
    ]),
    #RET
    (0x06, 0xFE, [
        SP_EN | SP_DEC,
        SP_OE | MEM_RE | MARH,
        SP_EN | SP_DEC,
        SP_OE| MEM_RE | MARL,
        MAR_OE | PC_JE,
        SC_RST
    ]),
    #JUMP
    (0x08, 0xFF, [
        PC_OE | MEM_RE | MARL,
        PC_EN,
        PC_OE | MEM_RE | MARH,
        MAR_OE | PC_JE,
        SC_RST
    ]),
    
    #JZ 
    (0x09, 0xFF, {
            'target_flag': FLAG_Z,
            'invert': False,
            'if_true':  [  PC_OE | MEM_RE | MARL, PC_EN, PC_OE | MEM_RE | MARH, MAR_OE | PC_JE, SC_RST  ],
            'if_false': [ PC_EN, PC_EN, SC_RST ]
            }),
    
    #JNZ
    (0x0A, 0xFF, {
        'target_flag': FLAG_Z,
        'invert': True,
        'if_true':  [  PC_OE | MEM_RE | MARL, PC_EN, PC_OE | MEM_RE | MARH, MAR_OE | PC_JE, SC_RST  ],
        'if_false': [ PC_EN, PC_EN, SC_RST ]
        }),
        
    #JC
    (0x0B, 0xFF, {
        'target_flag': FLAG_C,
        'invert': False,
        'if_true':  [  PC_OE | MEM_RE | MARL, PC_EN, PC_OE | MEM_RE | MARH, MAR_OE | PC_JE, SC_RST  ],
        'if_false': [ PC_EN, PC_EN, SC_RST ]
        }),
      
    #JNC
    (0x0C, 0xFF, {
        'target_flag': FLAG_C,
        'invert': True,
        'if_true':  [  PC_OE | MEM_RE | MARL, PC_EN, PC_OE | MEM_RE | MARH, MAR_OE | PC_JE, SC_RST  ],
        'if_false': [ PC_EN, PC_EN, SC_RST ]
        }),
    
    #JS
    (0x0D, 0xFF, {
        'target_flag': FLAG_S,
        'invert': False,
        'if_true':  [  PC_OE | MEM_RE | MARL, PC_EN, PC_OE | MEM_RE | MARH, MAR_OE | PC_JE, SC_RST  ],
        'if_false': [ PC_EN, PC_EN, SC_RST ]
        }),
    
    #JNS
    (0x0E, 0xFF, {
        'target_flag': FLAG_S,
        'invert': True,
        'if_true':  [  PC_OE | MEM_RE | MARL, PC_EN, PC_OE | MEM_RE | MARH, MAR_OE | PC_JE, SC_RST  ],
        'if_false': [ PC_EN, PC_EN, SC_RST ]
        }),
    
    #IM_LD(to_RF)
    (0x10, 0xF8, [
        PC_OE | MEM_RE | RF_WE,
        PC_EN,
        SC_RST
        ]),
    
    #IM_LD(to_RX)
    (0x18, 0xFC, [
        PC_OE | MEM_RE | RX_LD,
        PC_EN,
        SC_RST
        ]),
    
    #IM_LD(to_RY)
    (0x1C, 0xFC, [
        PC_OE | MEM_RE | RY_LD,
        PC_EN,
        SC_RST
        ]),
        
    #POINTER(RX TO MEM)
    (0x20, 0xF8, [
        RF_RE | MARL,
        PC_OE | MEM_RE | IR_LD
        ]),
        
    (0x28, 0xF8, [
        NULLY,
        NULLY,
        NULLY,
        NULLY,
        NULLY,
        RF_RE | MARH,
        MAR_OE | RX_OE | MEM_WE,
        PC_EN,
        SC_RST
        ]),
     
    #POINTER(MEM TO RX)
    (0x30, 0xF8, [
        RF_RE | MARL,
        PC_OE | MEM_RE | IR_LD
        ]),
        
    (0x38, 0xF8, [
        NULLY,
        NULLY,
        NULLY,
        NULLY,
        NULLY,
        RF_RE | MARH,
        MAR_OE | MEM_RE | RX_LD,
        PC_EN,
        SC_RST
        ]),
        
    #MEMORY(MOV REG_X TO RF)
    (0x40, 0xF0, [
        RX_OE | RF_WE,
        SC_RST
        ]),
    
    #MEMORY(MOV RF TO REG_X)
    (0x50, 0xF8, [
        RF_RE | RX_LD,
        SC_RST
        ]),
    #MEMORY(MOV RF TO REG_Y)
    (0x58, 0xF8, [
        RF_RE | RY_LD,
        SC_RST
        ]),
        
    #MEMORY(LOAD RF TO ADDRESS)
    (0x60, 0xF0, [
        PC_OE | MEM_RE | MARL,
        PC_EN,
        PC_OE | MEM_RE | MARH,
        MAR_OE | MEM_RE | RF_WE | PC_EN,
        SC_RST
        ]),
        
    #MEMORY(STORE ADDRESS TO RF)
    (0x70, 0xF0,  [
        PC_OE | MEM_RE | MARL,
        PC_EN,
        PC_OE | MEM_RE | MARH,
        MAR_OE | MEM_WE | RF_RE | PC_EN,
        SC_RST
        ])
]

# ALU Base Opcodes (With mask 0xFE, bit 0 the F flag is ignored.)[cite: 7]
ALU_BASE_OPCODES = {
    0x84, 0xA6, 0x8E, 0xBE, 0xEE, 0x9C, 0xE4, 0x80, 
    0xAA, 0x9E, 0xE6, 0x9A, 0xE2, 0x98, 0xE0, 0xD4, 
    0xFE, 0xF4
}

# ALU instructions that require a CARRY (Cin=1) signal due to arithmetic rules
ALU_OPCODES_CARRY = {0xA6, 0x8E, 0xBE, 0xEE, 0x9E, 0xE6}


for adress in range(32768):

    control_word = 0
    
    step = (adress >> 11) & 0x0F    # 4 bit (0 - 15)[cite: 5]
    opcode = (adress >> 3) & 0xFF   # 8 bit (256 different opcodes)[cite: 5]
    flags = adress & 0x07           # 3 bit (8 different flag combinations)[cite: 5]

    if step == 0:
        control_word = PC_OE | MEM_RE | IR_LD
        
    elif step == 1:
        control_word = PC_EN
        
    else:
        exec_index = step - 2
        
        # ALU Instruction Control (captured via Base Opcode & 0xFE check, including F-variations)
        base_op_check = opcode & 0xFE
        if base_op_check in ALU_BASE_OPCODES:
            if exec_index == 0:
                control_word = RX_MUX | RX_LD
                # If F (flag update) has been requested, bit 0 is active.
                if opcode & 0x01:
                    control_word |= FLAG_WE
                # Activate the CARRY pin if the operation requires CARRY
                if base_op_check in ALU_OPCODES_CARRY:
                    control_word |= CARRY
            elif exec_index == 1:
                control_word = SC_RST
        else:
            for base_opcode, mask, command_list in INSTRUCTIONS:
                if (opcode & mask) == base_opcode:

                    if isinstance(command_list, list):
                        if exec_index < len(command_list):
                            control_word = command_list[exec_index]
                    
                    elif isinstance(command_list, dict):
                        current_flag = command_list['target_flag']
                        is_inverted = command_list['invert']
                        is_flag_active = bool(flags & current_flag)
                        
                        condition_result = not is_flag_active if is_inverted else is_flag_active
                        
                        activated_list = command_list['if_true'] if condition_result else command_list['if_false']
                        
                        if exec_index < len(activated_list):
                            control_word = activated_list[exec_index]
                    break
              
    eeprom_byte0[adress] = (control_word >> 0)  & 0xFF
    eeprom_byte1[adress] = (control_word >> 8)  & 0xFF
    eeprom_byte2[adress] = (control_word >> 16) & 0xFF
    eeprom_byte3[adress] = (control_word >> 24) & 0xFF

with open("eeprom_0.bin", "wb") as f0, \
     open("eeprom_1.bin", "wb") as f1, \
     open("eeprom_2.bin", "wb") as f2, \
     open("eeprom_3.bin", "wb") as f3:
    f0.write(eeprom_byte0)
    f1.write(eeprom_byte1)
    f2.write(eeprom_byte2)
    f3.write(eeprom_byte3)

print("All EEPROM files are ready!")