import re

# Padrão dos tokens
token_specification = [
    ('NUMBER',   r'\d+'),
    ('ID',       r'[a-zA-Z_][a-zA-Z_0-9]*'),
    ('OP',       r'[+\-*/=()]'),
    ('SEMI',     r';'),
    ('SKIP',     r'[ \t]+'),
    ('MISMATCH', r'.')
]
token_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)

def scanner(code):
    tokens = []
    for mo in re.finditer(token_regex, code):
        kind = mo.lastgroup
        value = mo.group()
        if kind == 'SKIP':
            continue
        elif kind == 'MISMATCH':
            raise RuntimeError(f'Token inválido: {value}')
        tokens.append((kind, value))
    return tokens

def to_infix(expr_tokens):
    res = ''
    for tok in expr_tokens:
        if tok[0] in ['NUMBER', 'ID']:
            res += tok[1]
        elif tok[0] == 'OP':
            if tok[1] in ['(', ')']:
                res += tok[1]
            else:
                res += ' ' + tok[1] + ' '
    return res

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[self.pos] if self.tokens else None
        self.infix_output = []
        self.symbols = set()

    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None

    def consume(self, expected_type, expected_value=None):
        if self.current_token is None:
            raise SyntaxError(f'Esperado {expected_type}, mas fim do código.')
        kind, value = self.current_token
        if kind != expected_type:
            raise SyntaxError(f'Esperado {expected_type}, encontrado {kind} ({value})')
        if expected_value and value != expected_value:
            raise SyntaxError(f'Esperado "{expected_value}", encontrado "{value}"')
        self.advance()
        return value

    def parse(self):
        stmts = []
        while self.current_token is not None:
            stmts.append(self.statement())
        return stmts

    def statement(self):
        if self.current_token and self.current_token[0] == 'ID':
            if self.current_token[1] == 'print':
                return self.print_stmt()
            # Atribuição
            var = self.consume('ID')
            self.consume('OP', '=')
            expr_tokens = self.expression()
            self.consume('SEMI')
            self.symbols.add(var)
            expr_str = to_infix(expr_tokens)
            self.infix_output.append(f'{var} = {expr_str.strip()};')
            return (var, expr_tokens)
        else:
            raise SyntaxError(f'Statement inválido: {self.current_token}')

    def print_stmt(self):
        self.consume('ID') # 'print'
        self.consume('OP', '(')
        expr_tokens = self.expression()
        self.consume('OP', ')')
        self.consume('SEMI')
        expr_str = to_infix(expr_tokens)
        self.infix_output.append(f'print({expr_str.strip()});')
        return ('print', expr_tokens)

    def expression(self):
        tokens = self.term()
        while self.current_token and self.current_token[0] == 'OP' and self.current_token[1] in ('+', '-'):
            op = self.consume('OP')
            tokens.append(('OP', op))
            tokens += self.term()
        return tokens

    def term(self):
        tokens = self.factor()
        while self.current_token and self.current_token[0] == 'OP' and self.current_token[1] in ('*', '/'):
            op = self.consume('OP')
            tokens.append(('OP', op))
            tokens += self.factor()
        return tokens

    def factor(self):
        tokens = []
        if self.current_token[0] == 'NUMBER':
            val = self.consume('NUMBER')
            tokens.append(('NUMBER', val))
        elif self.current_token[0] == 'ID':
            name = self.consume('ID')
            tokens.append(('ID', name))
        elif self.current_token[0] == 'OP' and self.current_token[1] == '(':
            tokens.append(('OP', '('))
            self.consume('OP', '(')
            tokens += self.expression()
            self.consume('OP', ')')
            tokens.append(('OP', ')'))
        else:
            raise SyntaxError(f'Fator inválido: {self.current_token}')
        return tokens

class SemanticAnalyzer:
    def __init__(self, symbol_table):
        self.symbol_table = symbol_table
    def check_expr(self, expr_tokens):
        for token in expr_tokens:
            if token[0] == 'ID' and token[1] not in self.symbol_table:
                raise RuntimeError(f'Variável "{token[1]}" NÃO declarada')

# Código-fonte de exemplo
teste = """
a = 10;
b = 2 * a + 3;
c = b / (a - 5);
print(c);
"""

tokens = scanner(teste)
parser = Parser(tokens)
statements = parser.parse()

# Monta tabela de símbolos
symbol_table = set([stmt[0] for stmt in statements if stmt[0] != 'print'])
s_analyzer = SemanticAnalyzer(symbol_table)
for stmt in statements:
    if stmt[0] != 'print':
        s_analyzer.check_expr(stmt[1])
    else:
        s_analyzer.check_expr(stmt[1])

# Gera e salva código infixo
with open('saida.rpn', 'w') as f:
    for line in parser.infix_output:
        f.write(line + '\n')
print('Código gerado em "saida.rpn".')
