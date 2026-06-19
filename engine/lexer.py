import ply.lex as lex

tokens = (
    'LOAD', 'FILTER', 'PLOT', 'WHERE', 'AS',
    'IDENTIFIER', 'STRING', 'NUMBER',
    'GREATER', 'LESS', 'EQUALS',
    'DP', 'DOT', 'LPAREN', 'RPAREN', 'COMMA'
)

t_GREATER = r'>'
t_LESS    = r'<'
t_EQUALS  = r'=='
t_DOT     = r'\.'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_COMMA   = r','
t_ignore  = ' \t\r'

def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    keywords = {
        'load': 'LOAD',
        'filter': 'FILTER',
        'plot': 'PLOT',
        'where': 'WHERE',
        'as': 'AS',
        'dp': 'DP'
    }
    t.type = keywords.get(t.value.lower(), 'IDENTIFIER')
    return t

def t_STRING(t):
    r'\"[^\"]*\"'
    t.value = t.value[1:-1]
    return t

def t_COMMENT(t):
    r'\#.*'
    pass

def t_NUMBER(t):
    r'\d+(\.\d+)?'
    t.value = float(t.value) if '.' in str(t.value) else int(t.value)
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    t.lexer.skip(1)

lexer = lex.lex()