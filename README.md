# Simulador de Sistema Operacional

## Como executar
Precisa ter Python 3.8 ou mais novo. Abra a pasta onde estão `main.py` e `README.md` e rode:
```bash
python main.py
```

No Windows também dá para usar:
```bash
py main.py
```

Se você estiver na pasta pai, antes entra em `simulador_so`:
```bash
cd simulador_so
python main.py
```

A interação é só pelo terminal, com menu numérico:digita o número e dá `Enter`. Em campo de texto, deixar em branco e dar `Enter` mantém o valor anterior quando faz sentido.
**Os avisos do programa têm acento. Se aparecerem caracteres estranhos no `cmd` do Windows, roda `chcp 65001` antes de iniciar.**

## Menu
No menu principal tem:
```text
[1] Lista  - processos ativos em segundo plano
[2] Fila   - escalonamento da CPU
[3] Pilha  - chamadas e interrupções
[4] Árvore - sistema de arquivos
[5] Salvar dados
[6] Carregar dados
[7] Sair
```
Cada opção abre um submenu também numérico. Nas quatro estruturas tem criar, consultar/listar, atualizar e remover:
- **Lista**: insiro em um índice escolhido ou no fim; consulto por PID ou índice; atualizo e removo da mesma forma.
- **Fila**: enfileiro no fim, vejo quem está próximo da CPU, atualizo o processo sem mudar a posição dele e desenfileiro o primeiro.
- **Pilha**: empilho no topo, vejo o topo, atualizo só o topo e desempilho.
- **Árvore**: crio diretório ou arquivo, listo a árvore, consulto um caminho, renomeio e removo (com confirmação se o diretório tiver coisas dentro).

Um detalhe que eu achei importante:criar diretório ou arquivo não salva sozinho. O salvamento é sempre pela opção `[5]`, como o enunciado pediu.

## Arquivos da entrega
O repositório tem só:
```text
main.py
README.md
```

O `dados_sistema.txt` não vai junto. Ele aparece na mesma pasta do `main.py` na primeira vez que eu escolho "Salvar dados", até lá, o programa roda vazio.

## Como os dados são salvos
Usei um único arquivo `.txt`, sem banco, sem JSON, sem CSV e sem `pickle`. Cada linha começa com o identificador da estrutura e os campos vão separados por `|`:
```text
LISTA|pid|nome|recurso|estado
FILA|pid|nome|prioridade
PILHA|id|rotulo|descricao
ARVORE|segmento1|segmento2|...|arquivo
```

Exemplo parecido com o que pediu o enunciado:
```text
LISTA|101|Carlos Silva|Leito 04|Estavel
LISTA|102|Mariana Souza|Leito 09|Observacao
FILA|205|Roberto Alves|Prioridade Alta
FILA|206|Fernanda Lima|Prioridade Normal
PILHA|PRONT-889|Paciente 101|Consulta Cardiologia
PILHA|PRONT-890|Paciente 102|Exame Sangue
ARVORE|Clinica Geral|Cardiologia|Arritmia
ARVORE|Clinica Geral|Ortopedia|Fratura
```

Na árvore eu segui exatamente o formato do exemplo. O último pedaço é o arquivo; os anteriores são os diretórios. Por isso `Clinica Geral` e `Cardiologia` não aparecem em linhas próprias, elas são inferidas pelo prefixo.
Se um diretório ficar vazio, ele é gravado com um `|` no final, por exemplo:
```text
ARVORE|Clinica Geral|Vazia|
```

Para conseguir a linha `ARVORE|Clinica Geral|Cardiologia|Arritmia`, o caminho tem que ser digitado completo no menu:
```text
[4] Árvore
  [1] Criar diretório → /Clinica Geral
  [1] Criar diretório → /Clinica Geral/Cardiologia
  [2] Criar arquivo   → /Clinica Geral/Cardiologia/Arritmia
```

Depois volto ao menu principal e escolho `[5] Salvar dados`. Se eu tivesse criado `Cardiologia` direto na raiz, a linha sairia separada, só com `ARVORE|Cardiologia|Arritmia`.
Também tratei o caso de alguém digitar `|`, `\` ou quebra de linha dentro de um nome. Antes de gravar eu escapo esses caracteres (`\|`, `\\`, `\n`) e na leitura desfaz o escape. Assim um arquivo chamado `a|b.txt` volta certinho.

"Se sobrar um TXT antigo com `ARVORE|ARQ|...` ou `ARVORE|DIR|...`, o carregador ainda reconhece. Na próxima gravação ele já sai no formato limpo."

## Por que eu escolhi cada estrutura
### Lista — processos ativos em segundo plano
Usei a `list` nativa. Um processo que fica rodando em segundo plano, tipo `sshd` ou `cron`, não tem uma regra rígida de entrada e saída: ele pode ser consultado, alterado ou encerrado a qualquer momento, inclusive pela posição que ocupa na tabela.

A `list` serve bem porque:
- acesso por índice é direto, `O(1)`;
- `insert(posicao, item)` e `pop(indice)` resolvem a manipulação por índice;
- a ordem da tabela fica estável para mostrar no terminal;
- o PID funciona como chave e eu confiro se ele já existe antes de inserir ou renomear.

### Fila — escalonamento da CPU
Aqui escolhi `collections.deque` em vez de `list`. A regra da fila de prontos é FIFO: quem chegou primeiro recebe a CPU primeiro. As duas operações que eu mais uso são `append()` no fim e `popleft()` no início, e as duas são `O(1)` no `deque`.
Se eu usasse `list`, todo `pop(0)` teria que deslocar os outros elementos, custando `O(n)`. Em um simulador de escalonamento isso acontece o tempo todo, então seria um gargalo besta. Quando atualizo um processo, altero os campos no mesmo índice para não "furar a fila".

### Pilha — chamadas e interrupções
A pilha também é uma `list`, mas eu só uso `append()` e `pop()`, sempre no topo. Isso é `O(1)` e reproduz o que a CPU faz: quando uma rotina chama outra, ou quando chega uma interrupção, o contexto novo vai por cima; na volta, o sistema retorna primeiro para o topo.
Por isso mesmo a atualização eu limitei ao topo. Mexer em um elemento lá de baixo quebraria a lógica LIFO. Se fosse fila, o retorno sairia na ordem errada.

### Árvore — sistema de arquivos
O Python não tem um tipo `Tree` pronto, então montei a hierarquia com dicionários aninhados, sem criar classe de nó nem ponteiro na mão:
```python
# diretório
{"tipo": "dir", "filhos": {"home": ..., "etc": ...}}

# arquivo
{"tipo": "arquivo"}
```

A árvore faz sentido aqui porque diretório e arquivo são naturalmente pai e filho. Um caminho como `/home/aluno/notas.txt` é percorrido pedaço por pedaço, e o nome do filho serve de chave do dicionário — então não dá para ter dois itens com o mesmo nome dentro do mesmo diretório.
A listagem completa e a gravação no TXT são feitas por recursão, que é o jeito mais direto de percorrer uma hierarquia. Criar, renomear ou apagar um nó mexe só no ramo correspondente.

## Cuidados que eu tive
- O sistema começa vazio; nada é lido do disco automaticamente.
- Salvar e carregar são opções separadas no menu.
- Fila só sai pelo início e pilha só sai pelo topo.
- Lista aceita tanto índice quanto PID.
- PID e ID duplicados são barrados.
- Linha inválida no TXT é ignorada com aviso, em vez de quebrar o programa.
- Todo o código ficou em `main.py`, separado em funções e com comentários curtos nos pontos mais importantes.

## Testes que rodei
Antes de fechar eu conferi:
- `python -m py_compile main.py`;
- salvar, fechar e carregar de novo;
- linhas da árvore saindo exatamente como no exemplo do enunciado;
- FIFO na fila e LIFO na pilha;
- nome com `|` sendo gravado e restaurado certo;
- diretório vazio sobrevivendo ao save/load;
- arquivo antigo com `ARQ`/`DIR` ainda carregando.
