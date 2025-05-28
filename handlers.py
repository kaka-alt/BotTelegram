from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler
from datetime import datetime
import os
from config import *
import utils
from telegram.constants import ParseMode
import csv
import logging

# Logger para registrar erros e informações
logger = logging.getLogger(__name__)


# --- Início: Colaborador ---
async def iniciar_colaborador(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia a conversa para selecionar o colaborador."""

    buttons = [InlineKeyboardButton(name, callback_data=f"colaborador_{name}") for name in COLABORADORES]
    buttons.append(InlineKeyboardButton("Outro", callback_data="colaborador_outro"))
    keyboard = InlineKeyboardMarkup(utils.build_menu(buttons, n_cols=2))
    await update.message.reply_text(
        "👨‍💼 Selecione o colaborador ou clique em Outro para digitar manualmente:", reply_markup=keyboard
    )
    return "COLABORADOR"


async def colaborador_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lida com a seleção de colaborador via botão."""

    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "colaborador_outro":
        await query.message.reply_text("👨‍💼 Digite o nome do colaborador:")
        return "COLABORADOR_MANUAL"
    else:
        colaborador = data.replace("colaborador_", "")
        context.user_data['colaborador'] = colaborador
        await query.message.reply_text(f"Colaborador selecionado: {colaborador}")
        await query.message.reply_text("🏠 Agora, digite uma palavra-chave para buscar o órgão público:")
        return "ORGAO_PUBLICO_KEYWORD"


async def colaborador_manual(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lida com a entrada manual do nome do colaborador."""

    nome = update.message.text.strip()
    context.user_data['colaborador'] = nome
    await update.message.reply_text(f"Nome do colaborador registrado: {nome}")
    await update.message.reply_text("🏠 Agora, digite uma palavra-chave para buscar o órgão público:")
    return "ORGAO_PUBLICO_KEYWORD"


# --- Órgão público ---
async def buscar_orgao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Busca órgãos públicos com base em uma palavra-chave."""

    keyword = update.message.text.lower()
    orgaos = utils.ler_orgaos_csv()
    resultados = [o for o in orgaos if keyword in o.lower()]
    context.user_data['orgaos_busca'] = resultados
    context.user_data['orgao_pagina'] = 0

    if not resultados:
        await update.message.reply_text("❗ Nenhum órgão encontrado. Digite manualmente o nome do órgão público:")
        return "ORGAO_PUBLICO_MANUAL"

    buttons, pagina_atual = utils.botoes_pagina(resultados, 0, prefix="orgao_")
    keyboard = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(f"Resultados encontrados : {len(resultados)}", reply_markup=keyboard)
    return "ORGAO_PUBLICO_PAGINACAO"


async def orgao_paginacao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Controla a paginação dos resultados da busca de órgãos públicos."""

    query = update.callback_query
    await query.answer()
    data = query.data

    pagina_atual = context.user_data.get("orgao_pagina", 0)
    resultados = context.user_data.get("orgaos_busca", [])

    if data == "orgao_proximo":
        pagina_atual += 1
    elif data == "orgao_voltar":
        pagina_atual = max(0, pagina_atual - 1)
    elif data == "orgao_inserir_manual":
        await query.message.reply_text("✍️ Digite manualmente o nome do órgão público:")
        return "ORGAO_PUBLICO_MANUAL"
    elif data == "orgao_refazer_busca":
        await query.message.reply_text("🔎 Digite uma nova palavra-chave para buscar o órgão:")
        return "ORGAO_PUBLICO_KEYWORD"  # Corrigido para ORGAO_PUBLICO_KEYWORD
    else:
        orgao_selecionado = data.replace("orgao_", "")
        context.user_data["orgao_publico"] = orgao_selecionado
        await query.message.reply_text(f"🏢 Órgão selecionado: {orgao_selecionado}")
        await query.message.reply_text("🧥 Digite o nome da figura pública:")
        return "FIGURA_PUBLICA"

    # Atualiza a página e a interface
    context.user_data["orgao_pagina"] = pagina_atual
    botoes, _ = utils.botoes_pagina(resultados, pagina_atual, prefix="orgao_")
    await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(botoes))
    return "ORGAO_PUBLICO_PAGINACAO"


async def orgao_manual(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lida com a entrada manual do nome do órgão público."""

    nome = update.message.text.strip()
    context.user_data['orgao_publico'] = nome
    try:
        utils.salvar_orgao(nome)
        await update.message.reply_text(f"✔️ Órgão público registrado manualmente: {nome}")
    except Exception as e:
        logger.error(f"Erro ao salvar órgão: {e}")
        await update.message.reply_text(
            "❗ Erro ao registrar o órgão. Por favor, tente novamente."
        )  # Mensagem amigável para o usuário
    await update.message.reply_text("🧥 Digite o nome da figura pública:")
    return "FIGURA_PUBLICA"


# --- Figura pública ---
async def figura_publica_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lida com a entrada do nome da figura pública."""

    figura_publica = update.message.text.strip()
    context.user_data['figura_publica'] = figura_publica
    await update.message.reply_text(f"✔️ Figura pública registrada: {figura_publica}.")
    await update.message.reply_text("🧥 Digite o Cargo:")
    return "CARGO"


# --- Cargo ---
async def cargo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lida com a entrada do cargo."""
    cargo = update.message.text.strip()
    context.user_data['cargo'] = cargo
    await update.message.reply_text(f"✔️ Cargo registrado: {cargo}")
    await update.message.reply_text("✉️ Digite o Assunto:")
    return "ASSUNTO_PALAVRA_CHAVE"


# --- Assunto ---
async def buscar_assunto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Busca assuntos com base em uma palavra-chave."""

    palavra_chave = update.message.text.lower()
    assuntos = utils.ler_assuntos_csv()
    resultados = [a for a in assuntos if palavra_chave in a.lower()]
    context.user_data['assuntos_busca'] = resultados
    context.user_data['assunto_pagina'] = 0

    if not resultados:
        await update.message.reply_text("❗ Nenhum assunto encontrado. Digite manualmente o assunto:")
        return "ASSUNTO_MANUAL"

    buttons, pagina_atual = utils.botoes_pagina(resultados, 0, prefix="assunto_")
    keyboard = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(f"Resultados encontrados (página {pagina_atual + 1}):", reply_markup=keyboard)
    return "ASSUNTO_PAGINACAO"


async def assunto_paginacao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Controla a paginação dos resultados da busca de assuntos."""

    query = update.callback_query
    await query.answer()
    data = query.data

    pagina_atual = context.user_data.get("assunto_pagina", 0)
    resultados = context.user_data.get("assuntos_busca", [])

    if data == "assunto_proximo":
        pagina_atual += 1
    elif data == "assunto_voltar":
        pagina_atual = max(0, pagina_atual - 1)
    elif data == "assunto_inserir_manual":
        await query.message.reply_text("✍️ Digite manualmente o nome do assunto:")
        return "ASSUNTO_MANUAL"
    elif data == "assunto_refazer_busca":
        await query.message.reply_text("🔎 Digite uma nova palavra-chave para buscar o assunto:")
        return "ASSUNTO_PALAVRA_CHAVE"  # Corrigido para ASSUNTO_PALAVRA_CHAVE
    else:
        assunto_selecionado = data.replace("assunto_", "")
        context.user_data["assunto"] = assunto_selecionado
        await query.message.reply_text(f"📌 Assunto selecionado: {assunto_selecionado}")
        await query.message.reply_text("🏙️ Digite o município:")
        return "MUNICIPIO"

    # Atualiza a página e a interface
    context.user_data["assunto_pagina"] = pagina_atual
    botoes, _ = utils.botoes_pagina(resultados, pagina_atual, prefix="assunto_")
    await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(botoes))
    return "ASSUNTO_PAGINACAO"


async def assunto_manual(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lida com a entrada manual do assunto."""

    assunto = update.message.text.strip()
    context.user_data['assunto'] = assunto
    try:
        utils.salvar_assunto(assunto)
        await update.message.reply_text(f"✔️ Assunto registrado: {assunto}")
    except Exception as e:
        logger.error(f"Erro ao salvar assunto: {e}")
        await update.message.reply_text("❗ Erro ao registrar o assunto. Por favor, tente novamente.")
    await update.message.reply_text("🏙️ Digite o município:")
    return "MUNICIPIO"


# --- Município ---
async def municipio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lida com a entrada do município."""

    context.user_data['municipio'] = update.message.text.strip()
    return await solicitar_data(update, context)


# --- Data ---
async def solicitar_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Solicita a data da ocorrência."""

    buttons = [
        InlineKeyboardButton("📅 Usar data/hora atual", callback_data="data_hoje"),
        InlineKeyboardButton("✏️ Digitar data manualmente", callback_data="data_manual"),
    ]
    keyboard = InlineKeyboardMarkup.from_row(buttons)

    await update.message.reply_text("Selecione uma opção para a data:", reply_markup=keyboard)
    return "DATA"


async def data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lida com a seleção ou entrada da data."""

    query = update.callback_query
    if query:
        await query.answer()

        if query.data == "data_hoje":
            dt = datetime.now()
            context.user_data['data'] = dt.strftime("%d-%m-%Y")
            await query.message.edit_text(f"✔️ Data registrada: {dt.strftime('%d/%m/%Y')}")
            await query.message.reply_text("📷 Por favor, envie a foto:")
            return "FOTO"

        elif query.data == "data_manual":
            await query.message.edit_text("Digite a data no formato DD/MM/AAAA:")
            return "DATA_MANUAL"

    else:
        texto = update.message.text.strip()
        try:
            dt = datetime.strptime(texto, "%d/%m/%Y")
            context.user_data['data'] = dt.strftime("%d-%m-%Y")
            await update.message.reply_text("✔️ Data registrada com sucesso.")
            await update.message.reply_text("📷 Por favor, envie a foto:")
            return "FOTO"
        except ValueError:
            await update.message.reply_text("❗ Formato inválido. Digite a data no formato DD/MM/AAAA:")
            return "DATA_MANUAL"


# --- Foto ---
async def foto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lida com o recebimento da foto."""

    if not update.message.photo:
        await update.message.reply_text("❗ Por favor, envie uma foto válida.")
        return "FOTO"

    try:
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)

        # Usar caminhos definidos em config.py
        pasta_fotos = FOTO_PATH
        os.makedirs(pasta_fotos, exist_ok=True)

        # Obter o número da próxima linha do CSV (movido para utils)
        proxima_linha = utils.obter_proxima_linha_csv(CSV_REGISTRO)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"foto_{timestamp}_linha-{proxima_linha}.jpg"
        file_path = os.path.join(pasta_fotos, filename)

        await file.download_to_drive(file_path)

        context.user_data["foto"] = file_path
        context.user_data["demandas"] = []  # Inicializa a lista de demandas

        buttons = [
            [InlineKeyboardButton("➕ Adicionar demanda", callback_data="add_demanda")],
            [InlineKeyboardButton("❌ Não adicionar demanda", callback_data="fim_demandas")],
        ]
        reply_markup = InlineKeyboardMarkup(buttons)

        await update.message.reply_text("✔️ Foto recebida. Quer adicionar uma demanda?", reply_markup=reply_markup)
        return "DEMANDA_ESCOLHA"

    except Exception as e:
        logger.error(f"Erro ao processar foto: {e}")
        await update.message.reply_text("❗ Erro ao processar a foto. Por favor, tente novamente.")
        return ConversationHandler.END


# --- Demanda ---
async def demanda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lida com a escolha de adicionar ou não demandas."""

    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "add_demanda":
            await query.edit_message_text("Por favor, digite a demanda:")
            return "DEMANDA_DIGITAR"
    elif data == "fim_demandas":
            await query.edit_message_text("Finalizando demandas. Vamos para o resumo...")
            return await resumo(update, context)

async def demanda_digitar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lida com a entrada do texto da demanda."""

    context.user_data["nova_demanda"] = {"texto": update.message.text}
    await update.message.reply_text("Informe o número do OV:")
    return "OV"


async def ov(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lida com a entrada do número do OV."""

    context.user_data["nova_demanda"]["ov"] = update.message.text
    await update.message.reply_text("Informe o número do PRO:")
    return "PRO"


async def pro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lida com a entrada do número do PRO."""

    context.user_data["nova_demanda"]["pro"] = update.message.text

    keyboard = [
        [InlineKeyboardButton("Adicionar observação", callback_data="add_obs")],
        [InlineKeyboardButton("Pular", callback_data="skip_obs")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Deseja adicionar uma observação?", reply_markup=reply_markup)
    return "OBSERVACAO_ESCOLHA"


async def observacao_escolha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lida com a escolha de adicionar observação à demanda."""

    query = update.callback_query
    await query.answer()

    if query.data == "add_obs":
        await query.message.reply_text("Digite a observação:")
        return "OBSERVACAO_DIGITAR"
    elif query.data == "skip_obs":  # Alterado para elif
        context.user_data["nova_demanda"]["observacao"] = ""
        return await salvar_demanda(update, context)


async def observacao_digitar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lida com a entrada do texto da observação."""

    context.user_data["nova_demanda"]["observacao"] = update.message.text
    return await salvar_demanda(update, context)


async def salvar_demanda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Salva a demanda atual na lista de demandas do contexto."""

    demanda = context.user_data.pop("nova_demanda", None)
    if demanda:
        context.user_data.setdefault("demandas", []).append(demanda)

    buttons = [
        [InlineKeyboardButton("➕ Adicionar outra demanda", callback_data="add_demanda")],
        [InlineKeyboardButton("✅ Finalizar", callback_data="fim_demandas")],
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    if update.callback_query:
        await update.callback_query.message.edit_text(  # Use edit_text para atualizar a mensagem
            "✅ Demanda adicionada. Deseja adicionar outra?", reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            "✅ Demanda adicionada. Deseja adicionar outra?", reply_markup=reply_markup
        )
    return "DEMANDA_ESCOLHA"


# --- Resumo ---
async def resumo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gera e exibe o resumo dos dados coletados."""

    query = update.callback_query
    if query:
        await query.answer()

    dados = context.user_data

    resumo_texto = (
        "<b>Resumo dos dados coletados:</b>\n"
        f"👤 <b>Colaborador:</b> {dados.get('colaborador', 'N/A')}\n"
        f"🏢 <b>Órgão Público:</b> {dados.get('orgao_publico', 'N/A')}\n"
        f"🧑‍💼 <b>Figura Pública:</b> {dados.get('figura_publica', 'N/A')}\n"
        f"💼 <b>Cargo:</b> {dados.get('cargo', 'N/A')}\n"
        f"📌 <b>Assunto:</b> {dados.get('assunto', 'N/A')}\n"
        f"🏙️ <b>Município:</b> {dados.get('municipio', 'N/A')}\n"
        f"📅 <b>Data:</b> {dados.get('data', 'N/A')}\n"
        f"📷 <b>Foto:</b> {os.path.basename(dados.get('foto', 'N/A'))}\n\n"
        "<b>Demandas:</b>\n"
    )

    demandas = dados.get("demandas", [])
    if demandas:
        for i, d in enumerate(demandas, 1):
            resumo_texto += (
                f"{i}. {d.get('texto', '')}\n"
                f"   OV: {d.get('ov', '')} | PRO: {d.get('pro', '')}\n"
                f"   Obs: {d.get('observacao', '')}\n"
            )
    else:
        resumo_texto += "Nenhuma demanda registrada.\n"

    buttons = [
        [InlineKeyboardButton("✅ Confirmar", callback_data="confirmar_salvar")],
        [InlineKeyboardButton("❌ Cancelar", callback_data="cancelar_resumo")],
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    try:
        if query:
            await query.edit_message_text(
                resumo_texto, reply_markup=reply_markup, parse_mode=ParseMode.HTML
            )
        else:
            await update.message.reply_text(
                resumo_texto, reply_markup=reply_markup, parse_mode=ParseMode.HTML
            )
    except Exception as e:
        logger.error(f"Erro ao exibir resumo: {e}")
        await update.message.reply_text(
            "❗ Erro ao exibir resumo. Por favor, tente novamente."
        )
        return ConversationHandler.END

    return "CONFIRMACAO_FINAL"


# --- Confirmação Final ---
async def confirmacao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lida com a confirmação final do usuário para salvar os dados."""

    query = update.callback_query
    if query:
        await query.answer()

    data = query.data

    if data == "confirmar_salvar":
        try:
            utils.salvar_csv(context.user_data)
            await query.edit_message_text("✅ Dados salvos com sucesso! Obrigado pelo registro.")
        except Exception as e:
            logger.error(f"Erro ao salvar dados no CSV: {e}")
            await query.message.reply_text(
                "❗ Erro ao salvar dados. Por favor, tente novamente."
            )
        finally:
            context.user_data.clear()
            return ConversationHandler.END

    elif data == "cancelar_resumo":
        await query.edit_message_text("❌ Operação cancelada. Os dados não foram salvos.")
        context.user_data.clear()
        return ConversationHandler.END


# --- Cancelar ---
async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancela a conversa e limpa os dados do usuário."""

    await update.message.reply_text("Operação cancelada. Use /iniciar para reiniciar.")
    context.user_data.clear()
    return ConversationHandler.END