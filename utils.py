import csv
import os
import pandas as pd
from telegram import InlineKeyboardButton
from datetime import datetime
from config import CSV_ORGAOS, CSV_ASSUNTOS, CSV_REGISTRO, FOTO_PATH, CAMINHO_BASE  # Importe as variáveis necessárias
import logging

logger = logging.getLogger(__name__)  # Logger para este módulo


# Funções utilitárias para o bot

def build_menu(buttons, n_cols, footer_buttons=None):
    """Constrói um menu de botões."""
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if footer_buttons:
        menu.append(footer_buttons)
    return menu


def botoes_pagina(lista, pagina, prefix="", por_pagina=5):
    """Gera botões para navegação paginada."""

    inicio = pagina * por_pagina
    fim = inicio + por_pagina
    sublista = lista[inicio:fim]

    buttons = [
        [InlineKeyboardButton(text=item, callback_data=f"{prefix}{item}")]
        for item in sublista
    ]

    # Adiciona paginação e botões extras aqui se quiser
    botoes_navegacao = []
    if pagina > 0:
        botoes_navegacao.append(InlineKeyboardButton("⬅️ Voltar", callback_data=f"{prefix}voltar"))
    if fim < len(lista):
        botoes_navegacao.append(InlineKeyboardButton("➡️ Próximo", callback_data=f"{prefix}proximo"))
    buttons.append(botoes_navegacao)

    buttons.append([
        InlineKeyboardButton("📝 Inserir manualmente", callback_data=f"{prefix}inserir_manual"),
        InlineKeyboardButton("🔄 Refazer busca", callback_data=f"{prefix}refazer_busca"),
    ])

    return buttons, pagina


# Lista de Órgãos Públicos
def ler_orgaos_csv():
    """Lê a lista de órgãos públicos do arquivo CSV."""
    try:
        df = pd.read_csv(CSV_ORGAOS)
        return df['nome'].dropna().tolist()
    except FileNotFoundError:
        logger.error(f"Arquivo não encontrado: {CSV_ORGAOS}")
        return []  # Retorna uma lista vazia em caso de erro
    except Exception as e:
        logger.error(f"Erro ao ler CSV de órgãos: {e}")
        return []


def salvar_orgao(novo_orgao: str):
    """Salva um novo órgão público no arquivo CSV."""

    try:
        # Garante que a pasta existe
        os.makedirs(os.path.dirname(CSV_ORGAOS), exist_ok=True)

        # Remove espaços extras e padroniza
        novo_orgao = novo_orgao.strip()

        # Verifica se o órgão já existe (case-insensitive)
        orgaos_existentes = set()
        if os.path.exists(CSV_ORGAOS):
            with open(CSV_ORGAOS, mode='r', encoding='utf-8', newline='', errors='ignore') as f:
                for linha in f:
                    orgaos_existentes.add(linha.strip().lower())

        # Se não existe, adiciona
        if novo_orgao and novo_orgao.lower() not in orgaos_existentes:
            with open(CSV_ORGAOS, mode='a', newline='', encoding='utf-8') as f:
                f.write(f"{novo_orgao}\n")
        return True  # Indica sucesso
    except Exception as e:
        logger.error(f"Erro ao salvar órgão: {e}")
        return False  # Indica falha


# Lista Assuntos
def ler_assuntos_csv():
    """Lê a lista de assuntos do arquivo CSV."""
    try:
        df = pd.read_csv(CSV_ASSUNTOS)
        return df['assunto'].dropna().tolist()
    except FileNotFoundError:
        logger.error(f"Arquivo não encontrado: {CSV_ASSUNTOS}")
        return []
    except Exception as e:
        logger.error(f"Erro ao ler CSV de assuntos: {e}")
        return []


def salvar_assunto(novo_assunto: str):
    """Salva um novo assunto no arquivo CSV."""
    try:
        # Garante que a pasta existe
        os.makedirs(os.path.dirname(CSV_ASSUNTOS), exist_ok=True)

        # Remove espaços extras e padroniza
        novo_assunto = novo_assunto.strip()

        # Verifica se o assunto já existe (case-insensitive)
        assuntos_existentes = set()
        if os.path.exists(CSV_ASSUNTOS):
            with open(CSV_ASSUNTOS, mode='r', encoding='utf-8', newline='', errors='ignore') as f:
                for linha in f:
                    assuntos_existentes.add(linha.strip().lower())

        # Se não existe, adiciona
        if novo_assunto and novo_assunto.lower() not in assuntos_existentes:
            with open(CSV_ASSUNTOS, mode='a', newline='', encoding='utf-8') as f:
                f.write(f"{novo_assunto}\n")
        return True
    except Exception as e:
        logger.error(f"Erro ao salvar assunto: {e}")
        return False


def obter_proxima_linha_csv(caminho_csv: str) -> int:
    """Obtém o número da próxima linha em um arquivo CSV."""
    try:
        with open(caminho_csv, 'r', newline='', encoding='utf-8') as arquivo_csv:
            leitor_csv = csv.reader(arquivo_csv)
            numero_linhas = sum(1 for linha in leitor_csv)
        return numero_linhas + 1
    except FileNotFoundError:
        return 1  # Se o arquivo não existe, a próxima linha é a primeira
    except Exception as e:
        logger.error(f"Erro ao obter próxima linha do CSV: {e}")
        return 1  # Retorna 1 como padrão em caso de erro


def salvar_csv(data: dict):
    """Salva os dados coletados em arquivos CSV."""

    logger.info(f"Dados a serem salvos: {data}")  # Log dos dados

    ano, semana, _ = datetime.now().isocalendar()
    # Garante pastas
    pasta_data = os.path.join(CAMINHO_BASE, "data")
    pasta_backup = os.path.join(pasta_data, "backup")
    pasta_semanal = os.path.join(pasta_data, "semanal")
    os.makedirs(pasta_semanal, exist_ok=True)
    os.makedirs(pasta_data, exist_ok=True)
    os.makedirs(pasta_backup, exist_ok=True)

    # Arquivo principal (fixo)
    caminho_principal = CSV_REGISTRO

    caminho_semanal = os.path.join(pasta_semanal, f"{ano}-semana-{semana}-registros.csv")

    # Arquivo de backup diário
    data_hoje = datetime.now().strftime('%Y-%m-%d')
    caminho_backup = os.path.join(pasta_backup, f"{data_hoje}-backup.csv")

    # Cabeçalhos
    cabecalho = [
        'colaborador', 'orgao_publico', 'figura_publica', 'cargo',
        'assunto', 'municipio', 'data', 'foto',
        'demanda', 'ov', 'pro', 'observacao'
    ]

    # Função para escrever nos arquivos
    def escrever_linhas_csv(caminho_arquivo):
        arquivo_existe = os.path.isfile(caminho_arquivo)
        try:
            with open(caminho_arquivo, mode='a', newline='', encoding='utf-8') as arquivo:
                writer = csv.DictWriter(arquivo, fieldnames=cabecalho)
                if not arquivo_existe:
                    writer.writeheader()
                demandas = data.get('demandas')
                if demandas:
                    for demanda in demandas:
                        linha = {
                            'colaborador': data.get('colaborador'),
                            'orgao_publico': data.get('orgao_publico'),
                            'figura_publica': data.get('figura_publica'),
                            'cargo': data.get('cargo'),
                            'assunto': data.get('assunto'),
                            'municipio': data.get('municipio'),
                            'data': data.get('data'),
                            'foto': data.get('foto'),
                            'demanda': demanda.get('texto'),
                            'ov': demanda.get('ov'),
                            'pro': demanda.get('pro'),
                            'observacao': demanda.get('observacao', '')
                        }
                        writer.writerow(linha)
                else:
                    # Escreve uma linha mesmo sem demandas
                    linha = {
                        'colaborador': data.get('colaborador'),
                        'orgao_publico': data.get('orgao_publico'),
                        'figura_publica': data.get('figura_publica'),
                        'cargo': data.get('cargo'),
                        'assunto': data.get('assunto'),
                        'municipio': data.get('municipio'),
                        'data': data.get('data'),
                        'foto': data.get('foto'),
                        'demanda': '',
                        'ov': '',
                        'pro': '',
                        'observacao': ''
                    }
                    writer.writerow(linha)
        except Exception as e:
            logger.error(f"Erro ao escrever no arquivo CSV {caminho_arquivo}: {e}")

    # Salva no CSV principal (fixo)
    escrever_linhas_csv(caminho_principal)

    # Salva no backup diário
    escrever_linhas_csv(caminho_backup)

    # Salva no CSV semanal
    escrever_linhas_csv(caminho_semanal)