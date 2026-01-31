from datapilot.engine.lexer import lexer
from datapilot.engine.parser import parser

data = '''
load "monthly_sales.csv" as sales
filter sales where revenue > 5000 as high_value_sales
plot high_value_sales as bar_chart
'''

print("--- TOKEN STREAM (LEXER) ---")
lexer.input(data)
for tok in lexer:
    print(tok)

print("\n--- ABSTRACT SYNTAX TREE (PARSER) ---")
result = parser.parse(data)
print(result)