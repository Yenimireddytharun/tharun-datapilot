import ply.yacc as yacc
from engine.lexer import tokens 
import sys
import os 
from engine.executor import DataPilotExecutor

def p_program(p):
    '''program : statement_list'''
    p[0] = ('PROGRAM', p[1])

def p_statement_list(p):
    '''statement_list : statement
                  | statement_list statement'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]



def p_statement_dp_logic(p):
    '''statement : DP DOT IDENTIFIER LPAREN  IDENTIFIER RPAREN
           | DP DOT IDENTIFIER LPAREN IDENTIFIER COMMA IDENTIFIER RPAREN'''
    
    
    if len(p) == 9:
        func_name = p[3]
        if func_name == 'Query':
            p[0] = ('DP_QUERY', p[5], p[7])
        elif func_name == 'Visualize':
            p[0] = ('DP_VISUALIZE', p[5], p[7])
        elif func_name == 'Model':
            p[0] = ('DP_MODEL', p[5], p[7])
            
    
    elif len(p) == 7:
        if p[3] == 'Transform':
            p[0] = ('DP_TRANSFORM', p[5])

def p_statement_load(p):
    '''statement : LOAD STRING AS IDENTIFIER'''
    p[0] = ('LOAD_STMT', p[2], p[4])


def p_statement_filter(p):
    '''statement : FILTER IDENTIFIER WHERE IDENTIFIER comparison NUMBER AS IDENTIFIER'''
    p[0] = ('FILTER_STMT', p[2], p[4], p[5], p[6], p[8])

def p_statement_plot(p):
    '''statement : PLOT IDENTIFIER AS IDENTIFIER'''
    p[0] = ('PLOT_STMT', p[2], p[4])


def p_comparison(p):
    '''comparison : GREATER
               | LESS
               | EQUALS'''
    p[0] = p[1]

    
   
def p_error(p):
    if p:
        # Use a raw string to avoid SyntaxWarnings with backslashes
        print(r"\n[!] VALIDATION ERROR DETECTED")
        print("-" * 50)
        # ... your existing error printing logic ...
        print(f"MESSAGE: Syntax error at token '{p.value}'. Check grammar rules.")
    else:
        print("MESSAGE: Unexpected end of input.")
    os._exit(0)

parser = yacc.yacc()