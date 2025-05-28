import csv
import os
import pandas as pd
from telegram import InlineKeyboardButton
from datetime import datetime
from config import * 
from globals import user_data
import logging

logger = logging.getLogger(__name__)  



def salvar_csv(data: dict):
    logger.info(f"Salvar informaçoes em data: {data}")

    ano, semana, _ = datetime.now().isocalendar()

    # Caminhos dos diretorios
    pasta_data = os.path.join(CAMINHO_BASE, "data")
    pasta_backup = os.path.join(pasta_data, "backup")
    pasta_semanal = os.path.join(pasta_data, f"{ano}-semana-{semana}-registros.csv")
    caminho_principal = CSV_REGISTRO
    caminho_backup = os.path.join(pasta_backup, f"{datetime.now().strftime('%Y-%m-%d')}-backup.csv")

    logger.info(f"pasta_data: {pasta_data}")
    logger.info(f"pasta_backup: {pasta_backup}")
    logger.info(f"pasta_semanal: {pasta_semanal}")
    logger.info(f"caminho_principal: {caminho_principal}")
    logger.info(f"caminho_backup: {caminho_backup}")

    # cria diretorios caso não exista
    try:
        os.makedirs(pasta_semanal, exist_ok=True)
        logger.info(f"Directory created: {pasta_semanal}")
    except FileExistsError:
        logger.info(f"Directory already exists: {pasta_semanal}")
    except Exception as e:
        logger.error(f"Error creating directory {pasta_semanal}: {e}")

    try:
        os.makedirs(pasta_data, exist_ok=True)
        logger.info(f"Directory created: {pasta_data}")
    except FileExistsError:
        logger.info(f"Directory already exists: {pasta_data}")
    except Exception as e:
        logger.error(f"Error creating directory {pasta_data}: {e}")

    try:
        os.makedirs(pasta_backup, exist_ok=True)
        logger.info(f"Directory created: {pasta_backup}")
    except FileExistsError:
        logger.info(f"Directory already exists: {pasta_backup}")
    except Exception as e:
        logger.error(f"Error creating directory {pasta_backup}: {e}")

    cabecalho = [
        'colaborador', 'orgao_publico', 'figura_publica', 'cargo',
        'assunto', 'municipio', 'data', 'foto',
        'demanda', 'ov', 'pro', 'observacao'
    ]

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
                logger.info(f"Successfully wrote to {caminho_arquivo}")
        except Exception as e:
            logger.error(f"Error writing to {caminho_arquivo}: {e}")

    escrever_linhas_csv(caminho_principal)
    escrever_linhas_csv(caminho_backup)
    escrever_linhas_csv(pasta_semanal)