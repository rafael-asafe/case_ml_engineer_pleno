import re
from pathlib import Path

# regex
# r - define como raw string para desativar a interpretação das barras invertidas
# [\s\S] - inclui qualquer conteúdo
#  - doc strings aspas duplas
#  - doc strings aspas simples

pattern = re.compile(r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'')

for f in Path(".").rglob("*.py"):
    if f.resolve() == Path(__file__).resolve():
        continue
    content = f.read_text()
    content = pattern.sub("", content)
    f.write_text(content)
