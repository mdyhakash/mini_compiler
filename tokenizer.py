#!/usr/bin/env python3
"""
Standalone Tokenizer - Performs lexical analysis and outputs tokens
"""

import re
import sys

class Token:
    def __init__(self, token_type, lexeme, line_num):
        self.type = token_type
        self.lexeme = lexeme
        self.line = line_num
    
    def __repr__(self):
        return f"{self.type:20} {self.lexeme:20} {self.line}"

class Tokenizer:
    def __init__(self):
        self.tokens = []
        self.line_num = 1
        
        # Token patterns (order matters!)
        self.token_patterns = [
            ('COMMENT', r'//.*'),
            ('FLOAT_LITERAL', r'\d+\.\d+'),
            ('INT_LITERAL', r'\d+'),
            ('KEYWORD', r'\b(int|float|if|else|while|return|print)\b'),
            ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),
            ('OPERATOR', r'==|!=|<=|>=|[+\-*/=<>]'),
            ('DELIMITER', r'[(){};,]'),
            ('WHITESPACE', r'[ \t]+'),
            ('NEWLINE', r'\n'),
        ]
        
        # Compile patterns
        self.compiled_patterns = [(name, re.compile(pattern)) 
                                  for name, pattern in self.token_patterns]
    
    def tokenize(self, source_code):
        """Tokenize the source code"""
        position = 0
        
        while position < len(source_code):
            match_found = False
            
            for token_type, pattern in self.compiled_patterns:
                match = pattern.match(source_code, position)
                
                if match:
                    lexeme = match.group(0)
                    
                    if token_type == 'NEWLINE':
                        self.line_num += 1
                    elif token_type != 'WHITESPACE':  # Skip whitespace tokens
                        self.tokens.append(Token(token_type, lexeme, self.line_num))
                    
                    position = match.end()
                    match_found = True
                    break
            
            if not match_found:
                # Unknown character
                char = source_code[position]
                self.tokens.append(Token('UNKNOWN', char, self.line_num))
                print(f"Warning: Unknown character '{char}' at line {self.line_num}", 
                      file=sys.stderr)
                position += 1
        
        return self.tokens
    
    def display_tokens(self):
        """Display tokens in a formatted table"""
        print("="*70)
        print("TASK 1: LEXICAL ANALYSIS (TOKENIZATION)")
        print("="*70)
        print(f"{'TOKEN TYPE':<20} {'LEXEME':<20} {'LINE'}")
        print("-"*70)
        
        for token in self.tokens:
            print(token)
        
        print("="*70)
        print(f"Total Tokens: {len(self.tokens)}")
        print("="*70)
    
    def save_tokens(self, filename="tokens.txt"):
        """Save tokens to a file"""
        with open(filename, 'w') as f:
            f.write("="*70 + "\n")
            f.write("LEXICAL ANALYSIS - TOKEN LIST\n")
            f.write("="*70 + "\n")
            f.write(f"{'TOKEN TYPE':<20} {'LEXEME':<20} {'LINE'}\n")
            f.write("-"*70 + "\n")
            
            for token in self.tokens:
                f.write(f"{token}\n")
            
            f.write("="*70 + "\n")
            f.write(f"Total Tokens: {len(self.tokens)}\n")
            f.write("="*70 + "\n")
        
        print(f"✓ Tokens saved to {filename}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 tokenizer.py <source_file>")
        sys.exit(1)
    
    source_file = sys.argv[1]
    
    try:
        with open(source_file, 'r') as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"Error: File '{source_file}' not found")
        sys.exit(1)
    
    # Tokenize
    tokenizer = Tokenizer()
    tokenizer.tokenize(source_code)
    
    # Display results
    tokenizer.display_tokens()
    
    # Save to file
    tokenizer.save_tokens("tokens.txt")
    
    # Statistics
    print("\n--- Token Statistics ---")
    token_counts = {}
    for token in tokenizer.tokens:
        token_counts[token.type] = token_counts.get(token.type, 0) + 1
    
    for token_type, count in sorted(token_counts.items()):
        print(f"  {token_type:<20}: {count}")

if __name__ == "__main__":
    main()