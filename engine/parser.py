import ply.yacc as yacc
from engine.lexer import tokens
import os

def p_program(p):
    '''program : statement_list'''
    p[0] = ('PROGRAM', p[1])

def p_statement_list_single(p):
    '''statement_list : statement'''
    p[0] = [p[1]]

def p_statement_list_multiple(p):
    '''statement_list : statement_list statement'''
    p[0] = p[1] + [p[2]]

def p_statement_dp_two_args(p):
    '''statement : DP DOT IDENTIFIER LPAREN IDENTIFIER COMMA IDENTIFIER RPAREN'''
    func_name = p[3]
    arg1 = p[5]
    arg2 = p[7]
    if func_name == 'Query':
        p[0] = ('DP_QUERY', arg1, arg2)
    elif func_name == 'Visualize':
        p[0] = ('DP_VISUALIZE', arg1, arg2)
    elif func_name == 'Train':
        p[0] = ('DP_TRAIN', arg1, arg2)
    elif func_name == 'Filter':
        p[0] = ('DP_FILTER', arg1, arg2)
    elif func_name == 'Describe':
        p[0] = ('DP_DESCRIBE', arg1, arg2)
    elif func_name == 'SQL':
        p[0] = ('DP_SQL', arg1, arg2)
    elif func_name == 'Insight':
        p[0] = ('DP_INSIGHT', arg1, arg2)
    elif func_name == 'Report':
        p[0] = ('DP_REPORT', arg1, arg2)
    elif func_name == 'Model':
        p[0] = ('DP_MODEL', arg1, arg2)
    elif func_name == 'Predict':
        p[0] = ('DP_PREDICT', arg1, arg2)
    else:
        p[0] = ('DP_UNKNOWN', arg1, arg2)

def p_statement_dp_one_arg(p):
    '''statement : DP DOT IDENTIFIER LPAREN IDENTIFIER RPAREN'''
    func_name = p[3]
    arg1 = p[5]
    if func_name == 'Query':
        p[0] = ('DP_QUERY', arg1, None)
    elif func_name == 'Visualize':
        p[0] = ('DP_VISUALIZE', arg1, None)
    elif func_name == 'Train':
        p[0] = ('DP_TRAIN', arg1, None)
    elif func_name == 'Describe':
        p[0] = ('DP_DESCRIBE', arg1, None)
    elif func_name == 'Filter':
        p[0] = ('DP_FILTER', arg1, None)
    elif func_name == 'Insight':
        p[0] = ('DP_INSIGHT', arg1, None)
    elif func_name == 'Report':
        p[0] = ('DP_REPORT', arg1, None)
    elif func_name == 'SQL':
        p[0] = ('DP_SQL', arg1, None)
    elif func_name == 'Predict':
        p[0] = ('DP_PREDICT', arg1, None)
    else:
        p[0] = ('DP_UNKNOWN', arg1, None)

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
        print(f"Syntax error at token '{p.value}'")
    else:
        print("Unexpected end of input")

parser = yacc.yacc()