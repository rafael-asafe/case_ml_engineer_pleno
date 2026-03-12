Devido ao tempo restrito tive que fazer escolhas difíceis sobre o que priorizar, vou explorar o tema nas linhas abaixo.

[] Revisão de Documentação gerada por ia 

- Ajuste de exemplos 
- Limpeza de materiais repetidos 
- Adicionar templates e macros:
    - Isso é crucial para  aumentar a manutenibilidade do código, código envelhece como leite, o ideal é que uma doc acompanhe esse dinamismo. 

[] Revisão de testes gerados por ia 

- Garantir que o coverage do teste realmente reflita cobertura de segurança do código 

- A assistente de código reproduz a má pratica de criar mocks excessivos para qualquer coisa que fuja do padrão, isso tende a criar cenários distantes do contexto do código. 


[] Adicionar usuário não root aos dockerfiles 

- Boa pratica de segurança 

