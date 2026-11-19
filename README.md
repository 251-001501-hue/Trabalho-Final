# Simulador de Sistema Operacional

## Como executar

Para rodar o projeto, é necessário ter o Python 3.8 ou uma versão mais
recente instalado no computador.

Abra o terminal na pasta em que estão os arquivos `main.py` e
`README.md` e execute:

``` bash
python main.py
```

Se estiver usando Windows, também pode iniciar com:

``` bash
py main.py
```

Caso o terminal esteja aberto na pasta anterior, entre primeiro na pasta
`simulador_so`:

``` bash
cd simulador_so
python main.py
```

O programa funciona pelo próprio terminal. A navegação é feita por menus
numéricos: basta digitar a opção desejada e apertar `Enter`. Em alguns
campos de texto, se deixar vazio e apertar `Enter`, o valor anterior é
mantido, quando isso se aplica.

Os avisos do programa utilizam acentos. Se eles aparecerem com
caracteres estranhos no CMD do Windows, execute `chcp 65001` antes de
iniciar o programa.

## Menu principal

Ao iniciar, o programa apresenta estas opções:

``` text
[1] Lista  - processos ativos em segundo plano
[2] Fila   - escalonamento da CPU
[3] Pilha  - chamadas e interrupções
[4] Árvore - sistema de arquivos
[5] Salvar dados
[6] Carregar dados
[7] Sair
```

Cada opção abre um submenu com outras operações. Nas quatro estruturas
de dados, é possível criar, consultar, atualizar e remover informações.

-   **Lista:** permite adicionar um processo em uma posição escolhida ou
    no final. Também é possível consultar pelo PID ou pelo índice, além
    de atualizar e remover registros.
-   **Fila:** os processos entram no final da fila. O programa mostra
    qual será o próximo a utilizar a CPU, permite atualizar os dados de
    um processo sem mudar sua posição e remove sempre o primeiro da
    fila.
-   **Pilha:** os novos itens são adicionados no topo. É possível
    consultar e atualizar o item do topo ou removê-lo.
-   **Árvore:** permite criar diretórios e arquivos, visualizar a
    estrutura, consultar um caminho, renomear itens e remover arquivos
    ou diretórios. Quando um diretório possui conteúdo, o programa pede
    uma confirmação antes de removê-lo.

Uma observação importante é que criar um diretório ou arquivo não salva
os dados automaticamente. Para gravar as alterações, é necessário voltar
ao menu principal e escolher a opção `[5] Salvar dados`. Fiz dessa forma
porque o salvamento é uma operação separada no enunciado.

## Arquivos do projeto

A entrega contém dois arquivos:

``` text
main.py
README.md
```

O arquivo `dados_sistema.txt` não precisa estar presente inicialmente.
Ele é criado na mesma pasta do `main.py` quando a opção de salvar os
dados é utilizada pela primeira vez. Por isso, o programa pode ser
iniciado normalmente mesmo sem esse arquivo.

## Como os dados são salvos

Para salvar as informações, utilizei um único arquivo de texto (`.txt`).
Não usei banco de dados, JSON, CSV ou `pickle`, pois a proposta era
trabalhar com o formato solicitado no enunciado.

Cada linha começa com o nome da estrutura de dados. Depois, os valores
são separados pelo caractere `|`. O formato utilizado é este:

``` text
LISTA|pid|nome|recurso|estado
FILA|pid|nome|prioridade
PILHA|id|rotulo|descricao
ARVORE|segmento1|segmento2|...|arquivo
```

Um exemplo de como essas informações podem aparecer no arquivo:

``` text
LISTA|101|Carlos Silva|Leito 04|Estavel
LISTA|102|Mariana Souza|Leito 09|Observacao
FILA|205|Roberto Alves|Prioridade Alta
FILA|206|Fernanda Lima|Prioridade Normal
PILHA|PRONT-889|Paciente 101|Consulta Cardiologia
PILHA|PRONT-890|Paciente 102|Exame Sangue
ARVORE|Clinica Geral|Cardiologia|Arritmia
ARVORE|Clinica Geral|Ortopedia|Fratura
```

Na estrutura de árvore, segui o padrão do exemplo do enunciado. O último
elemento representa o arquivo, enquanto os elementos anteriores
representam os diretórios. Assim, diretórios como `Clinica Geral` e
`Cardiologia` são identificados pelo caminho, não precisando aparecer em
linhas separadas.

Quando um diretório está vazio, ele também é registrado. Nesse caso, a
linha termina com `|`, como no exemplo:

``` text
ARVORE|Clinica Geral|Vazia|
```

Para gerar uma linha como `ARVORE|Clinica Geral|Cardiologia|Arritmia`, é
necessário criar os diretórios seguindo o caminho completo pelo menu:

``` text
[4] Árvore
  [1] Criar diretório → /Clinica Geral
  [1] Criar diretório → /Clinica Geral/Cardiologia
  [2] Criar arquivo   → /Clinica Geral/Cardiologia/Arritmia
```

Depois disso, basta voltar ao menu principal e selecionar
`[5] Salvar dados`. Se o diretório `Cardiologia` fosse criado
diretamente na raiz, o registro seria diferente, ficando assim:
`ARVORE|Cardiologia|Arritmia`.

Também tratei alguns caracteres que poderiam atrapalhar a gravação do
arquivo. Se o usuário digitar `|`, `\` ou uma quebra de linha em um
nome, esses caracteres são convertidos antes de salvar (`\|`, `\\` e
`\n`). Na hora de carregar os dados, o programa faz o processo inverso.
Dessa forma, um nome como `a|b.txt` é recuperado corretamente.

## Por que utilizei cada estrutura de dados

### Lista --- processos ativos em segundo plano

Para representar os processos ativos em segundo plano, utilizei a
estrutura `list` do próprio Python. Escolhi essa estrutura porque esses
processos podem ser consultados, alterados ou removidos a qualquer
momento, sem precisar seguir uma ordem fixa de entrada e saída.

A lista também facilita o acesso aos elementos por índice. Nesse caso, o
acesso é `O(1)`. Para inserir ou remover um item em uma posição
específica, utilizei operações como `insert()` e `pop()`.

Outro ponto é que a lista mantém a ordem dos processos, o que facilita
mostrar as informações no terminal. Cada processo possui um PID, que
funciona como identificador. Antes de cadastrar ou alterar um processo,
o programa verifica se esse PID já está sendo utilizado, evitando
duplicidade.

### Fila --- escalonamento da CPU

Para a fila de processos, utilizei `collections.deque`. Essa escolha tem
relação com o funcionamento do escalonamento FIFO (*First In, First
Out*), em que o primeiro processo que entra é também o primeiro a sair.

Com o `deque`, consigo adicionar um processo no final usando `append()`
e remover o primeiro usando `popleft()`. Essas duas operações têm custo
`O(1)`.

Se tivesse utilizado uma lista comum, a remoção do primeiro elemento com
`pop(0)` exigiria deslocar os outros elementos, tendo custo `O(n)`. Como
essa operação faz parte do funcionamento principal da fila, o `deque`
acaba sendo mais adequado.

Também tomei cuidado para que a atualização de um processo não altere
sua posição. Assim, mesmo quando os dados são modificados, a ordem de
atendimento da fila continua a mesma.

### Pilha --- chamadas e interrupções

Na pilha, também utilizei uma `list` do Python. Nesse caso, trabalho
apenas com o topo da estrutura, utilizando `append()` para adicionar um
item e `pop()` para removê-lo. As duas operações possuem custo `O(1)`.

A pilha segue a lógica LIFO (*Last In, First Out*), ou seja, o último
elemento que entra é o primeiro a sair. Isso representa bem situações
como chamadas de funções e interrupções, nas quais o contexto mais
recente precisa ser tratado primeiro.

Por esse motivo, a atualização também foi limitada ao elemento que está
no topo. Alterar um item que está no meio ou no final da pilha não
seguiria a lógica dessa estrutura.

### Árvore --- sistema de arquivos

Para representar o sistema de arquivos, utilizei dicionários aninhados,
já que o Python não possui uma estrutura `Tree` pronta para esse caso.
Com essa organização, cada diretório pode guardar outros diretórios ou
arquivos.

A representação básica ficou assim:

``` python
# Diretório
{"tipo": "dir", "filhos": {"home": ..., "etc": ...}}

# Arquivo
{"tipo": "arquivo"}
```

Escolhi uma árvore porque ela representa bem a relação entre diretórios
e arquivos. Um caminho como `/home/aluno/notas.txt`, por exemplo, é
percorrido parte por parte até chegar ao arquivo desejado. O nome de
cada item funciona como chave no dicionário, então não é possível
cadastrar dois itens com o mesmo nome dentro do mesmo diretório.

Para mostrar toda a estrutura e salvar os dados no arquivo TXT, utilizei
recursão. Assim, o programa consegue percorrer os diretórios e seus
conteúdos até chegar aos arquivos. As operações de criação, renomeação e
remoção atuam somente no trecho da árvore correspondente ao caminho
informado.
