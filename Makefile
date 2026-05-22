# Makefile for Mini Compiler Project
# Integrates Lex, Bison, and Python

CC = gcc
LEX = flex
YACC = bison
PYTHON = python3

# Compiler flags
CFLAGS = -Wall -g
YFLAGS = -d -v

# Target executable
TARGET = parser
PYTHON_SCRIPT = compiler.py

# Source files
LEX_SRC = lexer.l
YACC_SRC = parser.y
LEX_OUT = lex.yy.c
YACC_OUT = parser.tab.c
YACC_HEADER = parser.tab.h

# Generated files
AST_FILE = ast.json
ASSEMBLY_FILE = output.s
EXECUTABLE = program

.PHONY: all clean compile run test help

all: $(TARGET)

# Build the parser from Lex and Bison
$(TARGET): $(LEX_SRC) $(YACC_SRC)
	@echo "=== Building Lexer and Parser ==="
	$(YACC) $(YFLAGS) $(YACC_SRC)
	$(LEX) $(LEX_SRC)
	$(CC) $(CFLAGS) $(YACC_OUT) $(LEX_OUT) -o $(TARGET) -lfl
	@echo "✓ Parser built successfully!"

# Compile a source file through all phases
compile: $(TARGET)
	@echo ""
	@echo "=== Running Complete Compilation Pipeline ==="
	@if [ ! -f "$(INPUT)" ]; then \
		echo "Error: Please specify INPUT=<filename>"; \
		echo "Example: make compile INPUT=example.txt"; \
		exit 1; \
	fi
	@echo "Input file: $(INPUT)"
	@echo ""
	@echo "[1/3] Lexical & Syntax Analysis (Lex + Bison)..."
	./$(TARGET) $(INPUT)
	@echo ""
	@echo "[2/3] Semantic Analysis & Code Generation (Python)..."
	$(PYTHON) $(PYTHON_SCRIPT) $(AST_FILE)
	@echo ""
	@echo "✓ Compilation pipeline completed!"
	@echo ""
	@echo "Generated files:"
	@echo "  - $(AST_FILE) (Abstract Syntax Tree)"
	@echo "  - $(ASSEMBLY_FILE) (Assembly code)"

# Compile and assemble to executable
build: compile
	@echo ""
	@echo "=== Assembling to Executable ==="
	$(CC) $(ASSEMBLY_FILE) -o $(EXECUTABLE) -no-pie
	@echo "✓ Executable created: $(EXECUTABLE)"

# Run the compiled program
run: build
	@echo ""
	@echo "=== Running Program ==="
	./$(EXECUTABLE)
	@echo ""

# Test with example program
test: $(TARGET)
	@echo "=== Testing with example.txt ==="
	@make compile INPUT=example.txt
	@echo ""
	@echo "=== Contents of example.txt ==="
	@cat example.txt
	@echo ""

# Clean generated files
clean:
	@echo "Cleaning generated files..."
	rm -f $(TARGET) $(LEX_OUT) $(YACC_OUT) $(YACC_HEADER)
	rm -f $(AST_FILE) $(ASSEMBLY_FILE) $(EXECUTABLE)
	rm -f parser.output
	@echo "✓ Clean complete!"

# Help message
help:
	@echo "Mini Compiler - Makefile Commands"
	@echo "=================================="
	@echo ""
	@echo "Available targets:"
	@echo "  make all          - Build the parser (Lex + Bison)"
	@echo "  make compile      - Run full compilation pipeline"
	@echo "                      Usage: make compile INPUT=yourfile.txt"
	@echo "  make build        - Compile and assemble to executable"
	@echo "                      Usage: make build INPUT=yourfile.txt"
	@echo "  make run          - Build and run the program"
	@echo "                      Usage: make run INPUT=yourfile.txt"
	@echo "  make test         - Test with example.txt"
	@echo "  make clean        - Remove all generated files"
	@echo "  make help         - Show this help message"
	@echo ""
	@echo "Example workflow:"
	@echo "  1. make test                    # Test with example"
	@echo "  2. make compile INPUT=prog.txt  # Compile your program"
	@echo "  3. make run INPUT=prog.txt      # Build and run"
	@echo ""