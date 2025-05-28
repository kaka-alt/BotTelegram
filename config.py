import os
from dotenv import load_dotenv

load_dotenv()  # Carrega variáveis de ambiente do arquivo .env

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Caminhos dos arquivos - agora relativos ao diretório do script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Diretório base do projeto
CSV_ORGAOS = os.path.join(BASE_DIR, "listas", "orgaos.csv")
CSV_PATH = os.path.join(BASE_DIR, "data")
FOTO_PATH = os.path.join(BASE_DIR, "fotos")
CSV_ASSUNTOS = os.path.join(BASE_DIR, "listas", "assuntos.csv")
CSV_REGISTRO = os.path.join(BASE_DIR, "data", "registros.csv")

PAGINACAO_TAMANHO = 5
COLABORADORES = ["Orlando", "Derielle", "Ricardo", "Vania", "Danillo"]