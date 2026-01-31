import ply.lex as lex

# 1. Define Token Names
tokens = (
    'LOAD', 'FILTER', 'PLOT', 'WHERE', 'AS',
    'IDENTIFIER', 'STRING', 'NUMBER',
    'GREATER', 'LESS', 'EQUALS','DP','DOT','LPAREN','RPAREN','COMMA'
  
)

# 2. Simple regex rules for operators
t_GREATER = r'>'
t_LESS    = r'<'
t_EQUALS  = r'=='
t_DOT    = r'\.'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_COMMA  = r','

def find_column(input, token):
    line_start = input.rfind('\n', 0, token.lexpos) + 1
    return (token.lexpos - line_start) + 1
# 3. Rules for Keywords (Case-insensitive)
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

# 4. Rules for Literals
def t_STRING(t):
    r'\"[^\"]*\"'
    t.value = t.value[1:-1] # Remove quotes
    return t

def t_COMMENT(t):
    r'\#.*'
     

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Ignore spaces and tabs
t_ignore  = ' \t\r'

def t_error(t):
    col = find_column(t.lexer.lexdata, t)
    print(f"[!] LEXICAL ERROR: Illegal character '{t.value[0]}' at Line {t.lineno}, Column {col}")
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()