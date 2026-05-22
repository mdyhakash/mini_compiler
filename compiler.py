def translate_instruction(self, instruction: str):
        """Translate single IR instruction to assembly"""
        instruction = instruction.strip()
        
        if instruction.startswith("#") or not instruction:
            self.assembly.append(f"    # {instruction}")
            return
        
        if instruction.startswith("DECLARE"):
            # Variable declaration - space already allocated
            parts = instruction.split()
            self.assembly.append(f"    # Declare {parts[1]} as {parts[2]}")
            return
        
        if ":" in instruction and not "=" in instruction:
            # Label
            self.assembly.append(f"{instruction}")
            return
        
        if instruction.startswith("GOTO"):
            label = instruction.split()[1]
            self.assembly.append(f"    jmp {label}")
            return
        
        if instruction.startswith("IF_FALSE"):
            parts = instruction.split()
            cond = parts[1]
            label = parts[3]
            symbol = self.symbol_table.lookup(cond)
            if symbol:
                self.assembly.append(f"    cmpq $0, -{symbol.offset}(%rbp)")
            else:
                reg = self.get_register(cond)
                if reg.startswith('-'):
                    self.assembly.append(f"    cmpq $0, {reg}")
                else:
                    self.assembly.append(f"    cmpq $0, %{reg}")
            self.assembly.append(f"    je {label}")
            return
        
        if instruction.startswith("PRINT"):
            var = instruction.split()[1]
            symbol = self.symbol_table.lookup(var)
            if symbol:
                self.assembly.append(f"    movq -{symbol.offset}(%rbp), %rsi")
            else:
                reg = self.get_register(var)
                if reg.startswith('-'):
                    self.assembly.append(f"    movq {reg}, %rsi")
                else:
                    self.assembly.append(f"    movq %{reg}, %rsi")
            self.assembly.append(f"    leaq fmt(%rip), %rdi")
            self.assembly.append(f"    xorq %rax, %rax")
            self.assembly.append(f"    call printf@PLT")
            return
        
        if instruction.startswith("RETURN"):
            var = instruction.split()[1]
            symbol = self.symbol_table.lookup(var)
            if symbol:
                self.assembly.append(f"    movq -{symbol.offset}(%rbp), %rax")
            else:
                reg = self.get_register(var)
                if reg.startswith('-'):
                    self.assembly.append(f"    movq {reg}, %rax")
                else:
                    self.assembly.append(f"    movq %{reg}, %rax")
            return
        
        if "=" in instruction:
            parts = instruction.split("=")
            lhs = parts[0].strip()
            rhs = parts[1].strip()
            
            # Handle binary operations
            if any(op in rhs for op in ['+', '-', '*', '/']):
                for op in ['+', '-', '*', '/']:
                    if op in rhs:
                        operands = rhs.split(op)
                        if len(operands) == 2:
                            left = operands[0].strip()
                            right = operands[1].strip()
                            
                            # Load left operand into %rax
                            if left.replace('.', '').replace('-', '').isdigit():
                                self.assembly.append(f"    movq ${left}, %rax")
                            else:
                                left_symbol = self.symbol_table.lookup(left)
                                if left_symbol:
                                    self.assembly.append(f"    movq -{left_symbol.offset}(%rbp), %rax")
                                else:
                                    left_reg = self.get_register(left)
                                    if left_reg.startswith('-'):
                                        self.assembly.append(f"    movq {left_reg}, %rax")
                                    else:
                                        self.assembly.append(f"    movq %{left_reg}, %rax")
                            
                            # Perform operation with right operand
                            if right.replace('.', '').replace('-', '').isdigit():
                                if op == '+':
                                    self.assembly.append(f"    addq ${right}, %rax")
                                elif op == '-':
                                    self.assembly.append(f"    subq ${right}, %rax")
                                elif op == '*':
                                    self.assembly.append(f"    imulq ${right}, %rax")
                                elif op == '/':
                                    self.assembly.append(f"    movq ${right}, %rbx")
                                    self.assembly.append(f"    cqo")
                                    self.assembly.append(f"    idivq %rbx")
                            else:
                                right_symbol = self.symbol_table.lookup(right)
                                if right_symbol:
                                    if op == '+':
                                        self.assembly.append(f"    addq -{right_symbol.offset}(%rbp), %rax")
                                    elif op == '-':
                                        self.assembly.append(f"    subq -{right_symbol.offset}(%rbp), %rax")
                                    elif op == '*':
                                        self.assembly.append(f"    imulq -{right_symbol.offset}(%rbp), %rax")
                                    elif op == '/':
                                        self.assembly.append(f"    movq -{right_symbol.offset}(%rbp), %rbx")
                                        self.assembly.append(f"    cqo")
                                        self.assembly.append(f"    idivq %rbx")
                                else:
                                    right_reg = self.get_register(right)
                                    if right_reg.startswith('-'):
                                        if op == '+':
                                            self.assembly.append(f"    addq {right_reg}, %rax")
                                        elif op == '-':
                                            self.assembly.append(f"    subq {right_reg}, %rax")
                                        elif op == '*':
                                            self.assembly.append(f"    imulq {right_reg}, %rax")
                                        elif op == '/':
                                            self.assembly.append(f"    movq {right_reg}, %rbx")
                                            self.assembly.append(f"    cqo")
                                            self.assembly.append(f"    idivq %rbx")
                                    else:
                                        if op == '+':
                                            self.assembly.append(f"    addq %{right_reg}, %rax")
                                        elif op == '-':
                                            self.assembly.append(f"    subq %{right_reg}, %rax")
                                        elif op == '*':
                                            self.assembly.append(f"    imulq %{right_reg}, %rax")
                                        elif op == '/':
                                            self.assembly.append(f"    movq %{right_reg}, %rbx")
                                            self.assembly.append(f"    cqo")
                                            self.assembly.append(f"    idivq %rbx")
                            
                            # Store result
                            lhs_symbol = self.symbol_table.lookup(lhs)
                            if lhs_symbol:
                                self.assembly.append(f"    movq %rax, -{lhs_symbol.offset}(%rbp)")
                            else:
                                lhs_reg = self.get_register(lhs)
                                self.register_map[lhs] = 'rax'
                        break
            else:
                # Simple assignment
                lhs_symbol = self.symbol_table.lookup(lhs)
                if rhs.replace('.', '').replace('-', '').isdigit():
                    # Constant assignment
                    if lhs_symbol:
                        self.assembly.append(f"    movq ${rhs}, %rax")
                        self.assembly.append(f"    movq %rax, -{lhs_symbol.offset}(%rbp)")
                    else:
                        lhs_reg = self.get_register(lhs)
                        self.assembly.append(f"    movq ${rhs}, %{lhs_reg}")
                else:
                    # Variable assignment
                    rhs_symbol = self.symbol_table.lookup(rhs)
                    if rhs_symbol and lhs_symbol:
                        self.assembly.append(f"    movq -{rhs_symbol.offset}(%rbp), %rax")
                        self.assembly.append(f"    movq %rax, -{lhs_symbol.offset}(%rbp)")
                    elif rhs_symbol:
                        self.assembly.append(f"    movq -{rhs_symbol.offset}(%rbp), %rax")
                        lhs_reg = self.get_register(lhs)
                        self.register_map[lhs] = 'rax'
                    else:
                        rhs_reg = self.get_register(rhs)
                        if lhs_symbol:
                            if rhs_reg.startswith('-'):
                                self.assembly.append(f"    movq {rhs_reg}, %rax")
                                self.assembly.append(f"    movq %rax, -{lhs_symbol.offset}(%rbp)")
                            else:
                                self.assembly.append(f"    movq %{rhs_reg}, %rax")
                                self.assembly.append(f"    movq %rax, -{lhs_symbol.offset}(%rbp)")
                        else:
                            lhs_reg = self.get_register(lhs)
                            if rhs_reg.startswith('-'):
                                self.assembly.append(f"    movq {rhs_reg}, %{lhs_reg}")
                            else:
                                self.assembly.append(f"    movq %{rhs_reg}, %{lhs_reg}")
                #!/usr/bin/env python3
"""
Mini Compiler Backend - Python
Handles: Symbol Table, Semantic Analysis, Intermediate Code Generation, 
         Optimization, and Assembly Code Generation
"""

import json
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Any

# ============================================================================
# TASK 2: SYMBOL TABLE
# ============================================================================

@dataclass
class Symbol:
    name: str
    type: str
    scope: int
    offset: int
    initialized: bool = False

class SymbolTable:
    def __init__(self):
        self.symbols: Dict[str, Symbol] = {}
        self.current_scope = 0
        self.offset_counter = 0
    
    def insert(self, name: str, sym_type: str) -> bool:
        if name in self.symbols:
            return False
        self.symbols[name] = Symbol(name, sym_type, self.current_scope, 
                                     self.offset_counter, False)
        self.offset_counter += 4  # 4 bytes per variable
        return True
    
    def lookup(self, name: str) -> Optional[Symbol]:
        return self.symbols.get(name)
    
    def update_initialized(self, name: str):
        if name in self.symbols:
            self.symbols[name].initialized = True
    
    def display(self):
        print("\n=== Symbol Table ===")
        print(f"{'Name':<15} {'Type':<10} {'Scope':<8} {'Offset':<8} {'Init':<8}")
        print("-" * 60)
        for sym in self.symbols.values():
            print(f"{sym.name:<15} {sym.type:<10} {sym.scope:<8} "
                  f"{sym.offset:<8} {sym.initialized}")

# ============================================================================
# TASK 3 & 4: AST REPRESENTATION
# ============================================================================

class ASTNode:
    def __init__(self, node_id: int, node_type: str, value: Any):
        self.id = node_id
        self.type = node_type
        self.value = value
        self.children: List[ASTNode] = []
    
    def add_child(self, child):
        self.children.append(child)
    
    def __repr__(self):
        return f"Node({self.type}, {self.value})"

# ============================================================================
# TASK 5: INTERMEDIATE CODE GENERATION (Three-Address Code)
# ============================================================================

class IntermediateCodeGenerator:
    def __init__(self, symbol_table: SymbolTable):
        self.symbol_table = symbol_table
        self.code: List[str] = []
        self.temp_counter = 0
        self.label_counter = 0
    
    def new_temp(self) -> str:
        temp = f"t{self.temp_counter}"
        self.temp_counter += 1
        return temp
    
    def new_label(self) -> str:
        label = f"L{self.label_counter}"
        self.label_counter += 1
        return label
    
    def emit(self, instruction: str):
        self.code.append(instruction)
    
    def generate(self, node: ASTNode) -> Optional[str]:
        """Generate intermediate code from AST node"""
        
        if node.type == "program":
            self.emit("# Program Start")
            for child in node.children:
                self.generate(child)
            self.emit("# Program End")
            return None
        
        elif node.type == "statement_list":
            for child in node.children:
                self.generate(child)
            return None
        
        elif node.type == "declaration":
            type_node = node.children[0]
            id_node = node.children[1]
            var_type = type_node.value
            var_name = id_node.value
            
            if not self.symbol_table.insert(var_name, var_type):
                print(f"Error: Variable '{var_name}' already declared")
            self.emit(f"DECLARE {var_name} {var_type}")
            return None
        
        elif node.type == "declaration_init":
            type_node = node.children[0]
            id_node = node.children[1]
            expr_node = node.children[2]
            
            var_type = type_node.value
            var_name = id_node.value
            
            if not self.symbol_table.insert(var_name, var_type):
                print(f"Error: Variable '{var_name}' already declared")
            
            expr_result = self.generate(expr_node)
            self.emit(f"DECLARE {var_name} {var_type}")
            self.emit(f"{var_name} = {expr_result}")
            self.symbol_table.update_initialized(var_name)
            return None
        
        elif node.type == "assignment":
            id_node = node.children[0]
            expr_node = node.children[1]
            
            var_name = id_node.value
            symbol = self.symbol_table.lookup(var_name)
            if not symbol:
                print(f"Error: Variable '{var_name}' not declared")
            
            expr_result = self.generate(expr_node)
            self.emit(f"{var_name} = {expr_result}")
            self.symbol_table.update_initialized(var_name)
            return None
        
        elif node.type == "binary_op":
            left = self.generate(node.children[0])
            right = self.generate(node.children[1])
            temp = self.new_temp()
            op = node.value
            self.emit(f"{temp} = {left} {op} {right}")
            return temp
        
        elif node.type == "int_literal":
            return str(int(node.value))
        
        elif node.type == "float_literal":
            return str(node.value)
        
        elif node.type == "identifier":
            var_name = node.value
            symbol = self.symbol_table.lookup(var_name)
            if not symbol:
                print(f"Warning: Variable '{var_name}' used before declaration")
            return var_name
        
        elif node.type == "if":
            cond = self.generate(node.children[0])
            label_false = self.new_label()
            label_end = self.new_label()
            
            self.emit(f"IF_FALSE {cond} GOTO {label_false}")
            self.generate(node.children[1])
            self.emit(f"GOTO {label_end}")
            self.emit(f"{label_false}:")
            self.emit(f"{label_end}:")
            return None
        
        elif node.type == "if_else":
            cond = self.generate(node.children[0])
            label_else = self.new_label()
            label_end = self.new_label()
            
            self.emit(f"IF_FALSE {cond} GOTO {label_else}")
            self.generate(node.children[1])
            self.emit(f"GOTO {label_end}")
            self.emit(f"{label_else}:")
            self.generate(node.children[2])
            self.emit(f"{label_end}:")
            return None
        
        elif node.type == "while":
            label_start = self.new_label()
            label_end = self.new_label()
            
            self.emit(f"{label_start}:")
            cond = self.generate(node.children[0])
            self.emit(f"IF_FALSE {cond} GOTO {label_end}")
            self.generate(node.children[1])
            self.emit(f"GOTO {label_start}")
            self.emit(f"{label_end}:")
            return None
        
        elif node.type == "print":
            expr = self.generate(node.children[0])
            self.emit(f"PRINT {expr}")
            return None
        
        elif node.type == "return":
            expr = self.generate(node.children[0])
            self.emit(f"RETURN {expr}")
            return None
        
        return None
    
    def display(self):
        print("\n=== Intermediate Code (Three-Address Code) ===")
        for i, instruction in enumerate(self.code):
            print(f"{i:3d}: {instruction}")

# ============================================================================
# TASK 6: CODE OPTIMIZATION
# ============================================================================

class Optimizer:
    def __init__(self, code: List[str]):
        self.code = code
    
    def constant_folding(self) -> List[str]:
        """Optimize constant expressions"""
        optimized = []
        for instruction in self.code:
            if '=' in instruction and any(op in instruction for op in ['+', '-', '*', '/']):
                parts = instruction.split('=')
                if len(parts) == 2:
                    lhs = parts[0].strip()
                    rhs = parts[1].strip()
                    
                    # Try to evaluate constant expressions
                    try:
                        # Simple constant folding for two numbers
                        for op in ['+', '-', '*', '/']:
                            if op in rhs:
                                operands = rhs.split(op)
                                if len(operands) == 2:
                                    left = operands[0].strip()
                                    right = operands[1].strip()
                                    if left.replace('.', '').isdigit() and right.replace('.', '').isdigit():
                                        result = eval(f"{left} {op} {right}")
                                        optimized.append(f"{lhs} = {result}")
                                        continue
                    except:
                        pass
            
            optimized.append(instruction)
        return optimized
    
    def dead_code_elimination(self) -> List[str]:
        """Remove unused temporary variables (simple version)"""
        used_vars = set()
        
        # Find all used variables
        for instruction in self.code:
            if '=' in instruction:
                parts = instruction.split('=')
                if len(parts) == 2:
                    rhs = parts[1].strip()
                    # Extract variables from RHS
                    tokens = rhs.replace('+', ' ').replace('-', ' ').replace('*', ' ').replace('/', ' ').split()
                    for token in tokens:
                        if token and not token.replace('.', '').isdigit():
                            used_vars.add(token)
        
        # Keep only instructions that define used variables or are control flow
        optimized = []
        for instruction in self.code:
            if any(keyword in instruction for keyword in ['IF_FALSE', 'GOTO', 'PRINT', 'RETURN', 'DECLARE', '#', ':']):
                optimized.append(instruction)
            elif '=' in instruction:
                lhs = instruction.split('=')[0].strip()
                if lhs in used_vars or not lhs.startswith('t'):
                    optimized.append(instruction)
        
        return optimized
    
    def optimize(self) -> List[str]:
        """Apply all optimizations"""
        code = self.constant_folding()
        code = self.dead_code_elimination()
        return code
    
    def display_comparison(self, original: List[str], optimized: List[str]):
        print("\n=== Code Optimization ===")
        print(f"Original: {len(original)} instructions")
        print(f"Optimized: {len(optimized)} instructions")
        print(f"Reduction: {len(original) - len(optimized)} instructions")

# ============================================================================
# TASK 7: ASSEMBLY CODE GENERATION (x86-64 style)
# ============================================================================

class AssemblyGenerator:
    def __init__(self, symbol_table: SymbolTable, ir_code: List[str]):
        self.symbol_table = symbol_table
        self.ir_code = ir_code
        self.assembly: List[str] = []
        self.register_map: Dict[str, str] = {}
        self.available_registers = ['rax', 'rbx', 'rcx', 'rdx', 'rsi', 'rdi']
        self.reg_index = 0
    
    def get_register(self, var: str) -> str:
        """Allocate register for variable"""
        if var not in self.register_map:
            if self.reg_index < len(self.available_registers):
                self.register_map[var] = self.available_registers[self.reg_index]
                self.reg_index += 1
            else:
                # Use stack if out of registers
                symbol = self.symbol_table.lookup(var)
                if symbol:
                    return f"-{symbol.offset}(%rbp)"
                return "-0(%rbp)"
        return self.register_map[var]
    
    def generate(self):
        """Generate assembly code from intermediate code"""
        self.assembly.append(".section .data")
        self.assembly.append("fmt: .string \"%d\\n\"")
        self.assembly.append("")
        self.assembly.append(".section .text")
        self.assembly.append(".globl main")
        self.assembly.append("main:")
        self.assembly.append("    pushq %rbp")
        self.assembly.append("    movq %rsp, %rbp")
        
        # Allocate stack space for variables
        total_size = self.symbol_table.offset_counter
        if total_size > 0:
            self.assembly.append(f"    subq ${total_size}, %rsp")
        
        for instruction in self.ir_code:
            self.translate_instruction(instruction)
        
        self.assembly.append("")
        self.assembly.append("    movq $0, %rax")
        self.assembly.append("    movq %rbp, %rsp")
        self.assembly.append("    popq %rbp")
        self.assembly.append("    ret")
    
    def translate_instruction(self, instruction: str):
        """Translate single IR instruction to assembly"""
        instruction = instruction.strip()
        
        if instruction.startswith("#") or not instruction:
            self.assembly.append(f"    # {instruction}")
            return
        
        if instruction.startswith("DECLARE"):
            # Variable declaration - space already allocated
            parts = instruction.split()
            self.assembly.append(f"    # Declare {parts[1]} as {parts[2]}")
            return
        
        if ":" in instruction and not "=" in instruction:
            # Label
            self.assembly.append(f"{instruction}")
            return
        
        if instruction.startswith("GOTO"):
            label = instruction.split()[1]
            self.assembly.append(f"    jmp {label}")
            return
        
        if instruction.startswith("IF_FALSE"):
            parts = instruction.split()
            cond = parts[1]
            label = parts[3]
            reg = self.get_register(cond)
            self.assembly.append(f"    cmpq $0, %{reg}")
            self.assembly.append(f"    je {label}")
            return
        
        if instruction.startswith("PRINT"):
            var = instruction.split()[1]
            symbol = self.symbol_table.lookup(var)
            if symbol:
                self.assembly.append(f"    movq [rbp-{symbol.offset}], %rsi")
            else:
                reg = self.get_register(var)
                self.assembly.append(f"    movq %{reg}, %rsi")
            self.assembly.append(f"    leaq fmt(%rip), %rdi")
            self.assembly.append(f"    xorq %rax, %rax")
            self.assembly.append(f"    call printf")
            return
        
        if instruction.startswith("RETURN"):
            var = instruction.split()[1]
            reg = self.get_register(var)
            self.assembly.append(f"    movq %{reg}, %rax")
            return
        
        if "=" in instruction:
            parts = instruction.split("=")
            lhs = parts[0].strip()
            rhs = parts[1].strip()
            
            # Handle binary operations
            if any(op in rhs for op in ['+', '-', '*', '/']):
                for op in ['+', '-', '*', '/']:
                    if op in rhs:
                        operands = rhs.split(op)
                        if len(operands) == 2:
                            left = operands[0].strip()
                            right = operands[1].strip()
                            
                            # Load left operand
                            if left.replace('.', '').isdigit():
                                self.assembly.append(f"    movq ${left}, %rax")
                            else:
                                left_symbol = self.symbol_table.lookup(left)
                                if left_symbol:
                                    self.assembly.append(f"    movq [rbp-{left_symbol.offset}], %rax")
                                else:
                                    left_reg = self.get_register(left)
                                    self.assembly.append(f"    movq %{left_reg}, %rax")
                            
                            # Perform operation with right operand
                            if right.replace('.', '').isdigit():
                                if op == '+':
                                    self.assembly.append(f"    addq ${right}, %rax")
                                elif op == '-':
                                    self.assembly.append(f"    subq ${right}, %rax")
                                elif op == '*':
                                    self.assembly.append(f"    imulq ${right}, %rax")
                                elif op == '/':
                                    self.assembly.append(f"    movq ${right}, %rbx")
                                    self.assembly.append(f"    cqo")
                                    self.assembly.append(f"    idivq %rbx")
                            else:
                                right_symbol = self.symbol_table.lookup(right)
                                if right_symbol:
                                    if op == '+':
                                        self.assembly.append(f"    addq [rbp-{right_symbol.offset}], %rax")
                                    elif op == '-':
                                        self.assembly.append(f"    subq [rbp-{right_symbol.offset}], %rax")
                                    elif op == '*':
                                        self.assembly.append(f"    imulq [rbp-{right_symbol.offset}], %rax")
                                    elif op == '/':
                                        self.assembly.append(f"    movq [rbp-{right_symbol.offset}], %rbx")
                                        self.assembly.append(f"    cqo")
                                        self.assembly.append(f"    idivq %rbx")
                                else:
                                    right_reg = self.get_register(right)
                                    if op == '+':
                                        self.assembly.append(f"    addq %{right_reg}, %rax")
                                    elif op == '-':
                                        self.assembly.append(f"    subq %{right_reg}, %rax")
                                    elif op == '*':
                                        self.assembly.append(f"    imulq %{right_reg}, %rax")
                                    elif op == '/':
                                        self.assembly.append(f"    movq %{right_reg}, %rbx")
                                        self.assembly.append(f"    cqo")
                                        self.assembly.append(f"    idivq %rbx")
                            
                            # Store result
                            lhs_symbol = self.symbol_table.lookup(lhs)
                            if lhs_symbol:
                                self.assembly.append(f"    movq %rax, [rbp-{lhs_symbol.offset}]")
                            else:
                                lhs_reg = self.get_register(lhs)
                                self.register_map[lhs] = 'rax'
                        break
            else:
                # Simple assignment
                lhs_symbol = self.symbol_table.lookup(lhs)
                if rhs.replace('.', '').replace('-', '').isdigit():
                    # Constant assignment
                    if lhs_symbol:
                        self.assembly.append(f"    movq ${rhs}, [rbp-{lhs_symbol.offset}]")
                    else:
                        lhs_reg = self.get_register(lhs)
                        self.assembly.append(f"    movq ${rhs}, %{lhs_reg}")
                else:
                    # Variable assignment
                    rhs_symbol = self.symbol_table.lookup(rhs)
                    if rhs_symbol and lhs_symbol:
                        self.assembly.append(f"    movq [rbp-{rhs_symbol.offset}], %rax")
                        self.assembly.append(f"    movq %rax, [rbp-{lhs_symbol.offset}]")
                    elif rhs_symbol:
                        self.assembly.append(f"    movq [rbp-{rhs_symbol.offset}], %rax")
                        lhs_reg = self.get_register(lhs)
                        self.register_map[lhs] = 'rax'
                    else:
                        rhs_reg = self.get_register(rhs)
                        if lhs_symbol:
                            self.assembly.append(f"    movq %{rhs_reg}, [rbp-{lhs_symbol.offset}]")
                        else:
                            lhs_reg = self.get_register(lhs)
                            self.assembly.append(f"    movq %{rhs_reg}, %{lhs_reg}")
    
    def display(self):
        print("\n=== Assembly Code (x86-64) ===")
        for line in self.assembly:
            print(line)
    
    def save(self, filename: str):
        try:
            with open(filename, 'w') as f:
                f.write('\n'.join(self.assembly))
            print(f"\n✓ Assembly code saved to {filename}")
        except Exception as e:
            print(f"\n✗ Error saving assembly code: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

# ============================================================================
# AST CONSTRUCTION FROM JSON
# ============================================================================

def build_ast_from_json(json_data: List[Dict]) -> Optional[ASTNode]:
    """Build AST from JSON representation"""
    nodes: Dict[int, ASTNode] = {}
    relationships = []
    root = None
    
    for item in json_data:
        if 'end' in item:
            break
        
        if 'id' in item:
            node = ASTNode(item['id'], item['type'], item.get('value', ''))
            nodes[item['id']] = node
            if item['type'] == 'program':
                root = node
        
        if 'parent' in item and 'child' in item:
            relationships.append((item['parent'], item['child']))
    
    # Build tree structure
    for parent_id, child_id in relationships:
        if parent_id in nodes and child_id in nodes:
            nodes[parent_id].add_child(nodes[child_id])
    
    return root

def print_ast(node: ASTNode, prefix: str = "", is_last: bool = True):
    """Pretty print AST with tree branches"""
    # Determine the connector
    connector = "└── " if is_last else "├── "
    
    # Print current node with color coding for different node types
    value_str = f": {node.value}" if node.value else ""
    node_display = f"{node.type}{value_str}"
    
    # Add visual indicators for different node types
    if node.type in ['program', 'statement_list']:
        node_display = f"[{node.type}]"
    elif node.type in ['int_literal', 'float_literal']:
        node_display = f"{node.type} = {node.value}"
    elif node.type == 'identifier':
        node_display = f"ID({node.value})"
    elif node.type == 'binary_op':
        node_display = f"OP({node.value})"
    elif node.type in ['declaration', 'declaration_init', 'assignment']:
        node_display = f"<{node.type}>"
    
    print(f"{prefix}{connector}{node_display}")
    
    # Prepare prefix for children
    extension = "    " if is_last else "│   "
    new_prefix = prefix + extension
    
    # Print children
    for i, child in enumerate(node.children):
        is_last_child = (i == len(node.children) - 1)
        print_ast(child, new_prefix, is_last_child)


def print_ast_simple(node: ASTNode, level: int = 0):
    """Simple indented AST print"""
    indent = "  " * level
    value_str = f": {node.value}" if node.value else ""
    print(f"{indent}{node.type}{value_str}")
    for child in node.children:
        print_ast_simple(child, level + 1)

# ============================================================================
# MAIN COMPILER DRIVER
# ============================================================================

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 compiler.py <ast.json>")
        sys.exit(1)
    
    ast_file = sys.argv[1]
    
    # Load AST from JSON
    print("="*70)
    print("MINI COMPILER - Python Backend")
    print("="*70)
    
    try:
        with open(ast_file, 'r') as f:
            content = f.read()
            # Fix trailing comma before the end marker
            # Remove the "end" marker and any trailing commas
            content = content.replace(',\n{"end": true}\n]', '\n]')
            content = content.replace('{"end": true}\n]', ']')
            # Also handle case with no end marker but trailing comma
            lines = content.split('\n')
            # Find last line with actual content before ]
            for i in range(len(lines) - 1, -1, -1):
                if lines[i].strip() and lines[i].strip() != ']':
                    # Remove trailing comma from last data line
                    lines[i] = lines[i].rstrip(',')
                    break
            content = '\n'.join(lines)
            json_data = json.loads(content)
    except FileNotFoundError:
        print(f"Error: Could not find {ast_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {ast_file}")
        print(f"Details: {e}")
        print(f"\nTrying to fix JSON formatting...")
        # Try to manually fix the JSON
        try:
            with open(ast_file, 'r') as f:
                content = f.read()
            # More aggressive fix - remove everything after the last }
            last_brace = content.rfind('},')
            if last_brace > 0:
                content = content[:last_brace+1] + '\n]'
            json_data = json.loads(content)
            print("✓ JSON fixed and loaded successfully!")
        except:
            print("✗ Could not fix JSON. Please check ast.json format.")
            sys.exit(1)
    
    # Build AST
    print("\n[Phase 1] Building Abstract Syntax Tree...")
    try:
        root = build_ast_from_json(json_data)
    except Exception as e:
        print(f"Error building AST: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    if not root:
        print("Error: Failed to build AST - no root node found")
        print(f"JSON data has {len(json_data)} items")
        sys.exit(1)
    
    print("AST constructed successfully!")
    print("\n" + "="*70)
    print("ABSTRACT SYNTAX TREE")
    print("="*70)
    print_ast(root)
    
    # Create Symbol Table
    print("\n[Phase 2] Creating Symbol Table...")
    symbol_table = SymbolTable()
    
    # Generate Intermediate Code
    print("\n[Phase 3] Generating Intermediate Code...")
    try:
        ic_gen = IntermediateCodeGenerator(symbol_table)
        ic_gen.generate(root)
    except Exception as e:
        print(f"Error generating intermediate code: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Display results
    symbol_table.display()
    ic_gen.display()
    
    # Optimize Code
    print("\n[Phase 4] Optimizing Code...")
    try:
        optimizer = Optimizer(ic_gen.code)
        optimized_code = optimizer.optimize()
        optimizer.display_comparison(ic_gen.code, optimized_code)
    except Exception as e:
        print(f"Error during optimization: {e}")
        import traceback
        traceback.print_exc()
        optimized_code = ic_gen.code  # Use unoptimized code
    
    print("\n--- Optimized Intermediate Code ---")
    for i, instruction in enumerate(optimized_code):
        print(f"{i:3d}: {instruction}")
    
    # Generate Assembly
    print("\n[Phase 5] Generating Assembly Code...")
    try:
        asm_gen = AssemblyGenerator(symbol_table, optimized_code)
        asm_gen.generate()
        asm_gen.display()
        asm_gen.save("output.s")
    except Exception as e:
        print(f"Error generating assembly: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("\n" + "="*70)
    print("COMPILATION COMPLETE!")
    print("="*70)
    print("\nOutput files generated:")
    print("  - output.s (Assembly code)")
    print("\nTo assemble and run (on Linux/Mac):")
    print("  gcc output.s -o program")
    print("  ./program")

if __name__ == "__main__":
    main()