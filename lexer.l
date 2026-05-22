%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "parser.tab.h"

int line_num = 1;
%}

%option noyywrap

%%

[ \t]+              { /* skip whitespace */ }
\n                  { line_num++; }
"//".*              { /* skip comments */ }

"int"               { return INT; }
"float"             { return FLOAT; }
"if"                { return IF; }
"else"              { return ELSE; }
"while"             { return WHILE; }
"return"            { return RETURN; }
"print"             { return PRINT; }

[a-zA-Z_][a-zA-Z0-9_]*  { 
                        yylval.string = strdup(yytext); 
                        return IDENTIFIER; 
                    }

[0-9]+              { 
                        yylval.int_val = atoi(yytext); 
                        return INT_LITERAL; 
                    }

[0-9]+\.[0-9]+      { 
                        yylval.float_val = atof(yytext); 
                        return FLOAT_LITERAL; 
                    }

"+"                 { return PLUS; }
"-"                 { return MINUS; }
"*"                 { return MULT; }
"/"                 { return DIV; }
"="                 { return ASSIGN; }
"=="                { return EQ; }
"!="                { return NEQ; }
"<"                 { return LT; }
">"                 { return GT; }
"<="                { return LE; }
">="                { return GE; }
"("                 { return LPAREN; }
")"                 { return RPAREN; }
"{"                 { return LBRACE; }
"}"                 { return RBRACE; }
";"                 { return SEMICOLON; }
","                 { return COMMA; }

.                   { 
                        fprintf(stderr, "Unknown character: %s at line %d\n", yytext, line_num); 
                    }

%%