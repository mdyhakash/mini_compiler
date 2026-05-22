%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

extern int yylex();
extern int line_num;
extern FILE *yyin;
void yyerror(const char *s);

FILE *ast_file;
int node_count = 0;

void emit_node(const char *type, const char *value) {
    fprintf(ast_file, "{\"id\": %d, \"type\": \"%s\", \"value\": \"%s\"},\n", 
            node_count++, type, value);
}

void emit_node_int(const char *type, int value) {
    fprintf(ast_file, "{\"id\": %d, \"type\": \"%s\", \"value\": %d},\n", 
            node_count++, type, value);
}

void emit_node_float(const char *type, float value) {
    fprintf(ast_file, "{\"id\": %d, \"type\": \"%s\", \"value\": %f},\n", 
            node_count++, type, value);
}

void emit_parent_child(int parent, int child) {
    fprintf(ast_file, "{\"parent\": %d, \"child\": %d},\n", parent, child);
}
%}

%union {
    int int_val;
    float float_val;
    char *string;
    int node_id;
}

%token <string> IDENTIFIER
%token <int_val> INT_LITERAL
%token <float_val> FLOAT_LITERAL
%token INT FLOAT IF ELSE WHILE RETURN PRINT
%token PLUS MINUS MULT DIV ASSIGN
%token EQ NEQ LT GT LE GE
%token LPAREN RPAREN LBRACE RBRACE SEMICOLON COMMA

%type <node_id> program statement_list statement declaration assignment
%type <node_id> expression term factor if_statement while_statement
%type <node_id> print_statement return_statement type

%left PLUS MINUS
%left MULT DIV
%nonassoc EQ NEQ LT GT LE GE

%%

program:
    statement_list { 
        $$ = node_count;
        emit_node("program", "main");
        fprintf(ast_file, "{\"parent\": %d, \"child\": %d},\n", $$, $1);
    }
    ;

statement_list:
    statement { $$ = $1; }
    | statement_list statement {
        $$ = node_count;
        emit_node("statement_list", "");
        fprintf(ast_file, "{\"parent\": %d, \"child\": %d},\n", $$, $1);
        fprintf(ast_file, "{\"parent\": %d, \"child\": %d},\n", $$, $2);
    }
    ;

statement:
    declaration { $$ = $1; }
    | assignment { $$ = $1; }
    | if_statement { $$ = $1; }
    | while_statement { $$ = $1; }
    | print_statement { $$ = $1; }
    | return_statement { $$ = $1; }
    ;

type:
    INT { 
        $$ = node_count;
        emit_node("type", "int");
    }
    | FLOAT {
        $$ = node_count;
        emit_node("type", "float");
    }
    ;

declaration:
    type IDENTIFIER SEMICOLON {
        $$ = node_count;
        emit_node("declaration", "");
        fprintf(ast_file, "{\"parent\": %d, \"child\": %d},\n", $$, $1);
        int id_node = node_count;
        emit_node("identifier", $2);
        fprintf(ast_file, "{\"parent\": %d, \"child\": %d},\n", $$, id_node);
        free($2);
    }
    | type IDENTIFIER ASSIGN expression SEMICOLON {
        $$ = node_count;
        emit_node("declaration_init", "");
        fprintf(ast_file, "{\"parent\": %d, \"child\": %d},\n", $$, $1);
        int id_node = node_count;
        emit_node("identifier", $2);
        fprintf(ast_file, "{\"parent\": %d, \"child\": %d},\n", $$, id_node);
        fprintf(ast_file, "{\"parent\": %d, \"child\": %d},\n", $$, $4);
        free($2);
    }
    ;

assignment:
    IDENTIFIER ASSIGN expression SEMICOLON {
        $$ = node_count;
        emit_node("assignment", "");
        int id_node = node_count;
        emit_node("identifier", $1);
        fprintf(ast_file, "{\"parent\": %d, \"child\": %d},\n", $$, id_node);
        fprintf(ast_file, "{\"parent\": %d, \"child\": %d},\n", $$, $3);
        free($1);
    }
    ;

if_statement:
    IF LPAREN expression RPAREN LBRACE statement_list RBRACE {
        $$ = node_count;
        emit_node("if", "");
        fprintf(ast_file, "{\"parent\": %d, \"child\": %d},\n", $$, $3);
        fprintf(ast_file, "{\"parent\": %d, \"child\": %d},\n", $$, $6);
    }
    | IF LPAREN expression RPAREN LBRACE statement_list RBRACE ELSE LBRACE statement_list RBRACE {
        $$ = node_count;
        emit_node("if_else", "");
        fprintf(ast_file, "{\"parent\": %d, \"child\": %d},\n", $$, $3);
        fprintf(ast_file, "{\"parent\": %d, \"child\": %d},\n", $$, $6);
        fprintf(ast_file, "{\"parent\": %d, \"child\": %d},\n", $$, $10);
    }
    ;

while_statement:
    WHILE LPAREN expression RPAREN LBRACE statement_list RBRACE {
        $$ = node_count;
        emit_node("while", "");
        fprintf(ast_file, "{\"parent\": %d, \"child\": %d},\n", $$, $3);
        fprintf(ast_file, "{\"parent\": %d, \"child\": %d},\n", $$, $6);
    }
    ;

print_statement:
    PRINT LPAREN expression RPAREN SEMICOLON {
        $$ = node_count;
        emit_node("print", "");
        fprintf(ast_file, "{\"parent\": %d, \"child\": %d},\n", $$, $3);
    }
    ;

return_statement:
    RETURN expression SEMICOLON {
        $$ = node_count;
        emit_node("return", "");
        fprintf(ast_file, "{\"parent\": %d, \"child\": %d},\n", $$, $2);
    }
    ;

expression:
    term { $$ = $1; }
    | expression PLUS term {
        $$ = node_count;
        emit_node("binary_op", "+");
        fprintf(ast_file, "{\"parent\": %d, \"child\": %d},\n", $$, $1);
        fprintf(ast_file, "{\"parent\": %d, \"child\": %d},\n", $$, $3);
    }
    | expression MINUS term {
        $$ = node_count;
        emit_node("binary_op", "-");
        fprintf(ast_file, "{\"parent\": %d, \"child\": %d},\n", $$, $1);
        fprintf(ast_file, "{\"parent\": %d, \"child\": %d},\n", $$, $3);
    }
    | expression EQ term {
        $$ = node_count;
        emit_node("binary_op", "==");
        fprintf(ast_file, "{\"parent\": %d, \"child\": %d},\n", $$, $1);
        fprintf(ast_file, "{\"parent\": %d, \"child\": %d},\n", $$, $3);
    }
    | expression LT term {
        $$ = node_count;
        emit_node("binary_op", "<");
        fprintf(ast_file, "{\"parent\": %d, \"child\": %d},\n", $$, $1);
        fprintf(ast_file, "{\"parent\": %d, \"child\": %d},\n", $$, $3);
    }
    | expression GT term {
        $$ = node_count;
        emit_node("binary_op", ">");
        fprintf(ast_file, "{\"parent\": %d, \"child\": %d},\n", $$, $1);
        fprintf(ast_file, "{\"parent\": %d, \"child\": %d},\n", $$, $3);
    }
    ;

term:
    factor { $$ = $1; }
    | term MULT factor {
        $$ = node_count;
        emit_node("binary_op", "*");
        fprintf(ast_file, "{\"parent\": %d, \"child\": %d},\n", $$, $1);
        fprintf(ast_file, "{\"parent\": %d, \"child\": %d},\n", $$, $3);
    }
    | term DIV factor {
        $$ = node_count;
        emit_node("binary_op", "/");
        fprintf(ast_file, "{\"parent\": %d, \"child\": %d},\n", $$, $1);
        fprintf(ast_file, "{\"parent\": %d, \"child\": %d},\n", $$, $3);
    }
    ;

factor:
    INT_LITERAL {
        $$ = node_count;
        emit_node_int("int_literal", $1);
    }
    | FLOAT_LITERAL {
        $$ = node_count;
        emit_node_float("float_literal", $1);
    }
    | IDENTIFIER {
        $$ = node_count;
        emit_node("identifier", $1);
        free($1);
    }
    | LPAREN expression RPAREN {
        $$ = $2;
    }
    ;

%%

void yyerror(const char *s) {
    fprintf(stderr, "Error at line %d: %s\n", line_num, s);
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <input_file>\n", argv[0]);
        return 1;
    }

    yyin = fopen(argv[1], "r");
    if (!yyin) {
        perror("Error opening input file");
        return 1;
    }

    ast_file = fopen("ast.json", "w");
    if (!ast_file) {
        perror("Error creating AST file");
        return 1;
    }

    fprintf(ast_file, "[\n");
    int result = yyparse();
    
    // Remove the trailing comma if it exists
    fseek(ast_file, -2, SEEK_CUR);  // Go back 2 chars (,\n)
    fprintf(ast_file, "\n]\n");

    fclose(ast_file);
    fclose(yyin);

    if (result == 0) {
        printf("Parsing successful! AST written to ast.json\n");
    }

    return result;
}