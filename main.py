"""Simulador de Sistema Operacional"""

from collections import deque
from pathlib import Path

ARQUIVO_DADOS = Path(__file__).resolve().with_name("dados_sistema.txt")

#=====Utilitarios de entrada e de texto=====
def ler(mensagem):
    try:
        return input(mensagem).strip()
    except EOFError:
        raise SystemExit("\nEntrada encerrada. Sistema finalizado.")

def ler_inteiro(mensagem, minimo=None, maximo=None):
    while True:
        bruto = ler(mensagem)
        if not bruto.isdigit():
            print("Digite apenas números inteiros.")
            continue
        valor = int(bruto)
        if minimo is not None and valor < minimo:
            print(f"O valor mínimo é {minimo}.")
            continue
        if maximo is not None and valor > maximo:
            print(f"O valor máximo é {maximo}.")
            continue
        return valor

def pausar():
    try:
        input("\nPressione Enter para continuar...")
    except EOFError:
        print()

def escapar(texto):
    return (
        str(texto)
        .replace("\\", "\\\\")   # barra invertida primeiro
        .replace("|", "\\|")
        .replace("\r", "")
        .replace("\n", "\\n")
    )


def desescapar(texto):
    resultado = []
    i = 0
    while i < len(texto):
        atual = texto[i]
        if atual == "\\" and i + 1 < len(texto):
            proximo = texto[i + 1]
            resultado.append("\n" if proximo == "n" else proximo)
            i += 2
        else:
            resultado.append(atual)
            i += 1
    return "".join(resultado)


def dividir_linha(linha):
    campos = []
    atual = []
    escapado = False

    for caractere in linha:  # nao divide o '|' que veio escapado
        if escapado:
            atual.append(caractere)
            escapado = False
        elif caractere == "\\":
            atual.append(caractere)
            escapado = True
        elif caractere == "|":
            campos.append("".join(atual))
            atual = []
        else:
            atual.append(caractere)

    campos.append("".join(atual))
    return [desescapar(campo) for campo in campos]


def montar_linha(campos):
    return "|".join(escapar(campo) for campo in campos)

#=====Estado inicial=====
def novo_diretorio():
    return {"tipo": "dir", "filhos": {}}

def novo_arquivo():
    return {"tipo": "arquivo"}

def novo_estado():
    return {
        "lista": [],
        "fila": deque(),  # popleft() no inicio em O(1)
        "pilha": [],
        "arvore": novo_diretorio(),
    }

def contar_nos(no):
    total = 0
    for filho in no["filhos"].values():
        total += 1
        if filho["tipo"] == "dir":
            total += contar_nos(filho)
    return total

#=====LISTA=====
def indice_por_pid(processos, pid):
    for indice, processo in enumerate(processos):
        if processo["pid"] == pid:
            return indice
    return -1

def exibir_processo(indice, processo):
    marcador = "->" if indice is not None else "  "
    posicao = str(indice) if indice is not None else "-"
    print(
        f" {marcador} [{posicao}] PID {processo['pid']:<8} "
        f"| {processo['nome']:<20} | {processo['recurso']:<18} | {processo['estado']}"
    )

def listar_lista(estado):
    processos = estado["lista"]
    print("\n--- Processos ativos(segundo plano) ---")
    if not processos:
        print("Nenhum processo ativo. Use a opção 1 para inserir.")
        return
    for indice, processo in enumerate(processos):
        exibir_processo(indice, processo)

def escolher_indice_lista(processos, acao):
    if not processos:
        print("A tabela está vazia.")
        return -1

    print(f"\n{acao} - como localizar o processo?")
    print("[1]Pelo PID")
    print("[2]Pelo índice da tabela")
    opcao = ler_inteiro("Opção:", 1, 2)

    if opcao == 1:
        pid = ler("PID:")
        indice = indice_por_pid(processos, pid)
        if indice == -1:
            print(f"Não existe processo com PID {pid}.")
        return indice

    indice = ler_inteiro("Índice:", 0, len(processos) - 1)
    return indice

def inserir_lista(estado):
    processos = estado["lista"]
    print("\n--- Inserir processo ativo ---")

    pid = ler("PID:")
    if not pid:
        print("PID não pode ficar vazio.")
        return
    if indice_por_pid(processos, pid) != -1:
        print(f"Já existe um processo com PID {pid}.")
        return

    nome = ler("Nome da pessoa(ex.:Henrique):")
    recurso = ler("Recurso/porta/descrição(ex.:porta 22):")
    situacao = ler("Estado(ex.:Ativo, Observação):")
    bruto = ler("Índice de inserção(Enter = colocar no fim):")
    if bruto == "":
        posicao = len(processos)
    elif bruto.isdigit() and 0 <= int(bruto) <= len(processos):
        posicao = int(bruto)
    else:
        print("Índice invalido. Nada foi inserido.")
        return

    # insere na posicao escolhida e empurra os proximos
    processos.insert(posicao, {
        "pid": pid,
        "nome": nome,
        "recurso": recurso,
        "estado": situacao,
    })
    print(f"Processo {pid} inserido na posição {posicao}.")

def consultar_lista(estado):
    listar_lista(estado)
    indice = escolher_indice_lista(estado["lista"], "Consultar")
    if indice >= 0:
        print("\n Registro encontrado:")
        exibir_processo(indice, estado["lista"][indice])

def atualizar_lista(estado):
    processos = estado["lista"]
    listar_lista(estado)
    indice = escolher_indice_lista(processos, "Atualizar")
    if indice < 0:
        return

    atual = processos[indice]
    print("(Deixe em branco para manter o valor atual)")

    novo_pid = ler(f" PID [{atual['pid']}]: ") or atual["pid"]
    if novo_pid != atual["pid"] and indice_por_pid(processos, novo_pid) != -1:
        print(f" Já existe um processo com PID {novo_pid}. Atualização cancelada.")
        return

    atual["pid"] = novo_pid
    atual["nome"] = ler(f"Nome [{atual['nome']}]: ") or atual["nome"]
    atual["recurso"] = ler(f"Recurso [{atual['recurso']}]: ") or atual["recurso"]
    atual["estado"] = ler(f"Estado [{atual['estado']}]: ") or atual["estado"]
    print("Processo atualizado.")

def remover_lista(estado):
    processos = estado["lista"]
    listar_lista(estado)
    indice = escolher_indice_lista(processos, "Remover")
    if indice < 0:
        return
    removido = processos.pop(indice)
    print(f" Processo {removido['pid']} removido da tabela.")

def menu_lista(estado):
    while True:
        print("\n========== LISTA/PROCESSOS ATIVOS ==========")
        print("[1]Inserir processo(índice ou fim)")
        print("[2]Listar processos")
        print("[3]Consultar por PID ou índice")
        print("[4]Atualizar por PID ou índice")
        print("[5]Remover por PID ou índice")
        print("[6]Voltar")
        opcao = ler_inteiro("Opção:", 1, 6)

        if opcao == 1:
            inserir_lista(estado)
        elif opcao == 2:
            listar_lista(estado)
        elif opcao == 3:
            consultar_lista(estado)
        elif opcao == 4:
            atualizar_lista(estado)
        elif opcao == 5:
            remover_lista(estado)
        else:
            break
        pausar()

#=====FILA=====
def listar_fila(estado):
    fila = estado["fila"]
    print("\n--- Fila de escalonamento(cabeça -> cauda) ---")
    if not fila:
        print("Fila vazia. Use a opção 1 para enfileirar.")
        return
    for posicao, processo in enumerate(fila):
        ponto = "<== próximo da CPU" if posicao == 0 else ""
        print(
            f" [{posicao}] PID {processo['pid']:<8} | {processo['nome']:<20} "
            f"| {processo['prioridade']:<18} {ponto}"
        )

def indice_fila_por_pid(fila, pid):
    for indice, processo in enumerate(fila):
        if processo["pid"] == pid:
            return indice
    return -1

def enfileirar(estado):
    fila = estado["fila"]
    print("\n--- Enfileirar processo ---")

    pid = ler("PID:")
    if not pid:
        print("PID não pode ficar vazio.")
        return
    if indice_fila_por_pid(fila, pid) != -1:
        print(f"O PID {pid} já está na fila.")
        return

    nome = ler("Nome da pessoa:")
    prioridade = ler("Prioridade(ex.: Alta, Normal, Baixa):")

    # append() sempre adiciona no fim da fila
    fila.append({"pid": pid, "nome": nome, "prioridade": prioridade})
    print(f"Processo {pid} enfileirado na posição {len(fila) - 1}.")

def consultar_fila(estado):
    fila = estado["fila"]
    if not fila:
        print("\n Fila vazia. Não ha próximo processo.")
        return
    proximo = fila[0]
    print("\n Próximo a receber a CPU:")
    print(
        f" PID {proximo['pid']} | {proximo['nome']} "
        f"| Prioridade: {proximo['prioridade']}"
    )

def atualizar_fila(estado):
    fila = estado["fila"]
    listar_fila(estado)
    if not fila:
        return

    print("\n Atualizar - como localizar?")
    print("[1]Pelo PID")
    print("[2]Pela posição na fila")
    opcao = ler_inteiro("Opção:", 1, 2)

    if opcao == 1:
        pid = ler("PID:")
        indice = indice_fila_por_pid(fila, pid)
        if indice == -1:
            print("PID não encontrado na fila.")
            return
    else:
        indice = ler_inteiro("Posição:", 0, len(fila) - 1)

    atual = fila[indice]
    print("(Deixe em branco para manter o valor atual)")
    novo_pid = ler(f" PID [{atual['pid']}]: ") or atual["pid"]

    if novo_pid != atual["pid"] and indice_fila_por_pid(fila, novo_pid) != -1:
        print(f"O PID {novo_pid} já está na fila. Atualização cancelada.")
        return

    atual["pid"] = novo_pid
    atual["nome"] = ler(f"Nome [{atual['nome']}]: ") or atual["nome"]
    atual["prioridade"] = ler(
        f"Prioridade [{atual['prioridade']}]: "
    ) or atual["prioridade"]
    print("Processo atualizado sem alterar sua posição na fila.")

def desenfileirar(estado):
    fila = estado["fila"]
    if not fila:
        print("\n Fila vazia. Nada para desenfileirar.")
        return
    removido = fila.popleft()  # tira quem chegou primeiro
    print(f"Processo {removido['pid']} ({removido['nome']}) saiu da fila.")

def menu_fila(estado):
    while True:
        print("\n========== FILA/ESCALONAMENTO ==========")
        print("[1]Enfileirar(inserir no fim)")
        print("[2]Listar fila")
        print("[3]Consultar próximo da CPU")
        print("[4]Atualizar processo(mantém a posição)")
        print("[5]Desenfileirar(remover do início)")
        print("[6]Voltar")
        opcao = ler_inteiro("Opção:", 1, 6)

        if opcao == 1:
            enfileirar(estado)
        elif opcao == 2:
            listar_fila(estado)
        elif opcao == 3:
            consultar_fila(estado)
        elif opcao == 4:
            atualizar_fila(estado)
        elif opcao == 5:
            desenfileirar(estado)
        else:
            break
        pausar()

#=====PILHA=====
def listar_pilha(estado):
    pilha = estado["pilha"]
    print("\n--- Pilha de chamadas (base -> topo) ---")
    if not pilha:
        print("Pilha vazia. Use a opção 1 para empilhar.")
        return
    for indice, chamada in enumerate(pilha):
        ponto = "<== topo" if indice == len(pilha) - 1 else ""
        print(
            f" [{indice}] {chamada['id']:<12} | {chamada['rotulo']:<18} "
            f"| {chamada['descricao']} {ponto}"
        )

def indice_pilha_por_id(pilha, identificador):
    for indice, chamada in enumerate(pilha):
        if chamada["id"] == identificador:
            return indice
    return -1

def empilhar(estado):
    pilha = estado["pilha"]
    print("\n--- Empilhar chamada / interrupção ---")

    identificador = ler("ID(ex.:INT-01, CALL-07):")
    if not identificador:
        print("ID não pode ficar vazio.")
        return
    if indice_pilha_por_id(pilha, identificador) != -1:
        print(f"O ID {identificador} já está na pilha.")
        return

    rotulo = ler("Rótulo(ex.:Paciente 000):")
    descricao = ler("Descrição(ex.:Raio-X):")

    pilha.append({
        "id": identificador,
        "rotulo": rotulo,
        "descricao": descricao,
    })
    print(f"Chamada {identificador} empilhada no topo.")

def consultar_topo(estado):
    pilha = estado["pilha"]
    if not pilha:
        print("\n Pilha vazia. Não há topo.")
        return
    topo = pilha[-1]
    print("\n Topo da pilha(próximo a retornar):")
    print(f"ID {topo['id']} | {topo['rotulo']} | {topo['descricao']}")

def atualizar_pilha(estado):
    pilha = estado["pilha"]
    if not pilha:
        print("\n Pilha vazia. Nada para atualizar.")
        return

    consultar_topo(estado)
    topo = pilha[-1]
    print("(Deixe em branco para manter o valor atual)")

    novo_id = ler(f"ID [{topo['id']}]: ") or topo["id"]
    if novo_id != topo["id"] and indice_pilha_por_id(pilha, novo_id) != -1:
        print(f"O ID {novo_id} já está na pilha. Atualização cancelada.")
        return

    topo["id"] = novo_id
    topo["rotulo"] = ler(f" Rótulo [{topo['rotulo']}]: ") or topo["rotulo"]
    topo["descricao"] = ler(
        f" Descrição [{topo['descricao']}]: "
    ) or topo["descricao"]
    print("Topo atualizado.")

def desempilhar(estado):
    pilha = estado["pilha"]
    if not pilha:
        print("\n Pilha vazia. Nada para desempilhar.")
        return
    removida = pilha.pop()  # tira o topo
    print(f"Chamada {removida['id']} ({removida['rotulo']}) retornou.")

def menu_pilha(estado):
    while True:
        print("\n========== PILHA / CHAMADAS E INTERRUPÇÕES ==========")
        print("[1]Empilhar(inserir no topo)")
        print("[2]Listar pilha")
        print("[3]Consultar topo")
        print("[4]Atualizar topo")
        print("[5]Desempilhar(remover do topo)")
        print("[6]Voltar")
        opcao = ler_inteiro("Opção:", 1, 6)

        if opcao == 1:
            empilhar(estado)
        elif opcao == 2:
            listar_pilha(estado)
        elif opcao == 3:
            consultar_topo(estado)
        elif opcao == 4:
            atualizar_pilha(estado)
        elif opcao == 5:
            desempilhar(estado)
        else:
            break
        pausar()

#=====ARVORE=====
def partes_caminho(texto):
    return [
        parte for parte in texto.replace("\\", "/").split("/")
        if parte not in ("", ".")
    ]

def caminho_amigavel(partes):
    return "/" + "/".join(partes) if partes else "/(raiz)"

def navegar(raiz, partes, criar=False):
    atual = raiz
    for parte in partes:
        if atual["tipo"] != "dir":
            return None, f" '{parte}' está dentro de um arquivo, não de um diretório."
        if parte not in atual["filhos"]:
            # cria os diretorios intermediarios quando pedido
            if not criar:
                return None, f" Caminho inexistente: {caminho_amigavel(partes)}"
            atual["filhos"][parte] = novo_diretorio()
        atual = atual["filhos"][parte]
    return atual, None

def criar_diretorio(estado):
    partes = partes_caminho(ler("Caminho do diretório(ex.:Clinica Geral/Cardiologia):"))
    if not partes:
        print("A raiz já existe. Informe um caminho abaixo dela.")
        return

    pai, erro = navegar(estado["arvore"], partes[:-1], criar=True)
    if erro:
        print(f" Erro:{erro}")
        return

    nome = partes[-1]
    if nome in pai["filhos"]:
        print(f"Já existe um item chamado '{nome}' nesse diretório.")
        return

    pai["filhos"][nome] = novo_diretorio()
    print(f"Diretório {caminho_amigavel(partes)} criado.")

def criar_arquivo(estado):
    partes = partes_caminho(ler("Caminho do arquivo(ex.:Clinica Geral/Cardiologia/Arritmia):"))
    if not partes:
        print("Informe um nome de arquivo válido.")
        return

    pai, erro = navegar(estado["arvore"], partes[:-1], criar=False)
    if erro:
        print(f"Erro:{erro} Crie o diretório antes.")
        return

    nome = partes[-1]
    if nome in pai["filhos"]:
        print(f"Já existe um item chamado '{nome}' nesse diretório.")
        return

    pai["filhos"][nome] = novo_arquivo()
    print(f"Arquivo {caminho_amigavel(partes)} criado.")

def listar_no(no, prefixo=""):
    for nome, filho in sorted(no["filhos"].items()):
        if filho["tipo"] == "dir":
            print(f"{prefixo}{nome}/")
            listar_no(filho, prefixo + "    ")
        else:
            print(f"{prefixo}{nome}  [arquivo]")

def listar_arvore(estado):
    print("\n--- Sistema de arquivos ---")
    print("/")
    if not estado["arvore"]["filhos"]:
        print("(vazio)")
    else:
        listar_no(estado["arvore"], "    ")

def consultar_caminho(estado):
    partes = partes_caminho(ler("Caminho a consultar: "))
    no, erro = navegar(estado["arvore"], partes, criar=False)
    if erro:
        print(f"Erro:{erro}")
        return

    print(f"\n Caminho: {caminho_amigavel(partes)}")
    if no["tipo"] == "dir":
        print("Tipo: diretório")
        print(f"Itens dentro: {len(no['filhos'])}")
    else:
        print("Tipo: arquivo")

def renomear_no(estado):
    partes = partes_caminho(ler("Caminho do item a renomear: "))
    if not partes:
        print("A raiz não pode ser renomeada.")
        return

    pai, erro = navegar(estado["arvore"], partes[:-1], criar=False)
    if erro:
        print(f"Erro:{erro}")
        return

    nome_atual = partes[-1]
    if nome_atual not in pai["filhos"]:
        print(f"Item '{nome_atual}' não existe nesse diretório.")
        return

    novo_nome = ler("Novo nome:")
    if not novo_nome or "/" in novo_nome or "\\" in novo_nome:
        print("Nome invalido (não use barras e não deixe vazio).")
        return
    if novo_nome != nome_atual and novo_nome in pai["filhos"]:
        print("Já existe outro item com esse nome no mesmo diretório.")
        return

    pai["filhos"][novo_nome] = pai["filhos"].pop(nome_atual)
    print(f"Renomeado para '{novo_nome}'.")

def remover_no(estado):
    partes = partes_caminho(ler("Caminho do item a remover: "))
    if not partes:
        print("A raiz não pode ser removida.")
        return

    pai, erro = navegar(estado["arvore"], partes[:-1], criar=False)
    if erro:
        print(f"Erro:{erro}")
        return

    nome = partes[-1]
    alvo = pai["filhos"].get(nome)
    if alvo is None:
        print(f"Item '{nome}' não existe nesse diretório.")
        return

    if alvo["tipo"] == "dir" and alvo["filhos"]:
        print(f"O diretório '{nome}' contém {contar_nos(alvo)} item(ns).")
        print("[1]Remover mesmo assim(recursivo)")
        print("[2]Cancelar")
        if ler_inteiro("Opção:", 1, 2) != 1:
            print("Remoção cancelada.")
            return

    del pai["filhos"][nome]
    print(f"Item '{nome}' removido.")

def menu_arvore(estado):
    while True:
        print("\n========== ÁRVORE/SISTEMA DE ARQUIVOS ==========")
        print("[1]Criar diretório")
        print("[2]Criar arquivo")
        print("[3]Listar árvore")
        print("[4]Consultar caminho")
        print("[5]Renomear diretório/arquivo(atualizar)")
        print("[6]Remover diretório/arquivo")
        print("[7]Voltar")
        opcao = ler_inteiro("Opção:", 1, 7)

        if opcao == 1:
            criar_diretorio(estado)
        elif opcao == 2:
            criar_arquivo(estado)
        elif opcao == 3:
            listar_arvore(estado)
        elif opcao == 4:
            consultar_caminho(estado)
        elif opcao == 5:
            renomear_no(estado)
        elif opcao == 6:
            remover_no(estado)
        else:
            break
        pausar()

#=====PERSISTENCIA=====
def serializar_arvore(no, partes, linhas):
    for nome, filho in sorted(no["filhos"].items()):
        caminho = partes + [nome]
        if filho["tipo"] == "dir":
            if filho["filhos"]:
                serializar_arvore(filho, caminho, linhas)
            else:
                # O campo vazio no final sinaliza "diretorio sem arquivos".
                linhas.append(montar_linha(["ARVORE"] + caminho + [""]))
        else:
            linhas.append(montar_linha(["ARVORE"] + caminho))

def salvar_dados(estado):
    linhas = []

    for processo in estado["lista"]:
        linhas.append(montar_linha([
            "LISTA",
            processo["pid"],
            processo["nome"],
            processo["recurso"],
            processo["estado"],
        ]))

    for processo in estado["fila"]:
        linhas.append(montar_linha([
            "FILA",
            processo["pid"],
            processo["nome"],
            processo["prioridade"],
        ]))

    for chamada in estado["pilha"]:
        linhas.append(montar_linha([
            "PILHA",
            chamada["id"],
            chamada["rotulo"],
            chamada["descricao"],
        ]))

    serializar_arvore(estado["arvore"], [], linhas)

    try:
        ARQUIVO_DADOS.write_text(
            "\n".join(linhas) + ("\n" if linhas else ""),
            encoding="utf-8",
        )
    except OSError as erro:
        print(f"\n Não foi possivel salvar: {erro}")
        return

    print(f"\n Dados salvos em {ARQUIVO_DADOS} ({len(linhas)} registro(s)).")


def carregar_dados():
    if not ARQUIVO_DADOS.exists():
        print(f"\n Arquivo {ARQUIVO_DADOS} não encontrado. Salve antes de carregar.")
        return None

    try:
        conteudo = ARQUIVO_DADOS.read_text(encoding="utf-8")
    except OSError as erro:
        print(f"\n Não foi possivel ler o arquivo: {erro}")
        return None

    estado = novo_estado()
    ignoradas = 0

    for numero, linha in enumerate(conteudo.splitlines(), start=1):
        if not linha.strip() or linha.lstrip().startswith("#"):
            continue

        campos = dividir_linha(linha)
        identificador = campos[0]

        try:
            if identificador == "LISTA":
                if len(campos) != 5:
                    raise ValueError("formato esperado:LISTA|pid|nome|recurso|estado")
                pid, nome, recurso, situacao = campos[1:]
                if indice_por_pid(estado["lista"], pid) != -1:
                    raise ValueError(f"PID duplicado: {pid}")
                estado["lista"].append({
                    "pid":pid,
                    "nome":nome,
                    "recurso":recurso,
                    "estado":situacao,
                })

            elif identificador == "FILA":
                if len(campos) != 4:
                    raise ValueError("formato esperado: FILA|pid|nome|prioridade")
                pid, nome, prioridade = campos[1:]
                if indice_fila_por_pid(estado["fila"], pid) != -1:
                    raise ValueError(f"PID duplicado na fila: {pid}")
                # A ordem das linhas eh a ordem de chegada na CPU.
                estado["fila"].append({
                    "pid":pid,
                    "nome":nome,
                    "prioridade":prioridade,
                })

            elif identificador == "PILHA":
                if len(campos) != 4:
                    raise ValueError("formato esperado:PILHA|id|rótulo|descrição")
                identificador_chamada, rotulo, descricao = campos[1:]
                if indice_pilha_por_id(estado["pilha"], identificador_chamada) != -1:
                    raise ValueError(f"ID duplicado: {identificador_chamada}")
                # A ultima linha vira o topo da pilha.
                estado["pilha"].append({
                    "id":identificador_chamada,
                    "rotulo":rotulo,
                    "descricao":descricao,
                })

            elif identificador == "ARVORE":
                if len(campos) < 2:
                    raise ValueError("formato esperado: ARVORE|pasta|...|arquivo")
                legado = len(campos) >= 3 and campos[1] in ("ARQ", "DIR")

                if legado:
                    caminho = campos[2:]
                    if campos[1] == "DIR":
                        diretorio_vazio = True
                    else:
                        # No formato antigo, um '|' final era o conteudo vazio.
                        diretorio_vazio = False
                        if caminho and caminho[-1] == "":
                            caminho = caminho[:-1]
                else:
                    caminho = campos[1:]

                    if caminho in ([], ["/"], [""]):
                        continue

                    diretorio_vazio = len(caminho) >= 2 and caminho[-1] == ""
                    if diretorio_vazio:
                        caminho = caminho[:-1]

                if not caminho:
                    raise ValueError("caminho vazio")
                if any(not parte for parte in caminho):
                    raise ValueError("segmento de caminho vazio")

                pai, erro = navegar(estado["arvore"], caminho[:-1], criar=True)
                if erro:
                    raise ValueError(erro.strip())

                nome = caminho[-1]
                existente = pai["filhos"].get(nome)

                if diretorio_vazio:
                    if existente is not None and existente["tipo"] != "dir":
                        raise ValueError(f"conflito: '{nome}' já é arquivo")
                    if existente is None:
                        pai["filhos"][nome] = novo_diretorio()
                else:
                    if existente is not None and existente["tipo"] != "arquivo":
                        raise ValueError(f"conflito: '{nome}' já é diretório")
                    pai["filhos"][nome] = novo_arquivo()

            else:
                raise ValueError(f"identificador desconhecido: {identificador}")

        except ValueError as erro:
            ignoradas += 1
            print(f"Linha {numero} ignorada: {erro}")

    print(
        "\n Carregamento concluído:"
        f"{len(estado['lista'])} lista,"
        f"{len(estado['fila'])} fila,"
        f"{len(estado['pilha'])} pilha,"
        f"{contar_nos(estado['arvore'])} no(s) na árvore."
    )
    if ignoradas:
        print(f"{ignoradas} linha(s) ignorada(s) por inconsistência.")
    return estado

#=====MENU PRINCIPAL=====
def exibir_menu(estado):
    print("\n" + "=" * 58)
    print("      SIMULADOR DE SISTEMA OPERACIONAL")
    print("=" * 58)
    print(
        f"Em memória: lista={len(estado['lista'])} | "
        f"fila={len(estado['fila'])} | "
        f"pilha={len(estado['pilha'])} | "
        f"árvore={contar_nos(estado['arvore'])}"
    )
    print("-" * 58)
    print("[1]Lista  - processos ativos em segundo plano")
    print("[2]Fila   - escalonamento da CPU")
    print("[3]Pilha  - chamadas e interrupções")
    print("[4]Árvore - sistema de arquivos")
    print("[5]Salvar dados(dados_sistema.txt)")
    print("[6]Carregar dados(dados_sistema.txt)")
    print("[7]Sair")
    print("-" * 58)
    return ler_inteiro("Opção:", 1, 7)

def main():
    estado = novo_estado()
    print("Sistema iniciado vazio. Use [6] para trazer dados salvos, se houver.")

    while True:
        opcao = exibir_menu(estado)

        if opcao == 1:
            menu_lista(estado)
        elif opcao == 2:
            menu_fila(estado)
        elif opcao == 3:
            menu_pilha(estado)
        elif opcao == 4:
            menu_arvore(estado)
        elif opcao == 5:
            salvar_dados(estado)
            pausar()
        elif opcao == 6:
            carregado = carregar_dados()
            if carregado is not None:
                estado = carregado
            pausar()
        else:
            print("\n Sistema encerrado. Até mais!")
            break

if __name__ == "__main__":
    main()