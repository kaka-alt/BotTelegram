from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackQueryHandler
import logging
import config
from handlers import *
import handlers

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def cancelar(update, context):
    await update.message.reply_text("Operação cancelada pelo usuário.")
    context.user_data.clear()
    return ConversationHandler.END

async def start(update, context):
    await update.message.reply_text("Olá! Use /iniciar para começar o registro de uma ocorrência.")

app = ApplicationBuilder().token(config.TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('iniciar', handlers.iniciar_colaborador)],
    states={
        "COLABORADOR": [CallbackQueryHandler(handlers.colaborador_button, pattern="^colaborador_")],
        "COLABORADOR_MANUAL": [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.colaborador_manual)],
        "ORGAO_PUBLICO_KEYWORD": [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.buscar_orgao)],
        "ORGAO_PUBLICO_PAGINACAO": [CallbackQueryHandler(handlers.orgao_paginacao, pattern="^orgao_")],
        "ORGAO_PUBLICO_MANUAL": [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.orgao_manual)],
        "CARGO": [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.cargo)],
        "FIGURA_PUBLICA": [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.figura_publica_input)],
        "ASSUNTO_PALAVRA_CHAVE": [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.buscar_assunto)],
        "ASSUNTO_PAGINACAO": [CallbackQueryHandler(handlers.assunto_paginacao, pattern="^assunto_")],
        "ASSUNTO_MANUAL": [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.assunto_manual)],
        "MUNICIPIO": [MessageHandler(filters.TEXT & ~filters.COMMAND, municipio)],
        "DATA": [
            CallbackQueryHandler(handlers.data, pattern="^data_"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.data),
        ],
        "DATA_MANUAL": [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.data)],
        "FOTO": [MessageHandler(filters.PHOTO, handlers.foto)],
        "DEMANDA_ESCOLHA": [CallbackQueryHandler(handlers.demanda, pattern="^(add_demanda|pular_demanda|fim_demandas)$")],
        "DEMANDA_DIGITAR": [MessageHandler(filters.TEXT & ~filters.COMMAND, demanda_digitar)],
        "OV": [MessageHandler(filters.TEXT & ~filters.COMMAND, ov)],
        "PRO": [MessageHandler(filters.TEXT & ~filters.COMMAND, pro)],
        "OBSERVACAO_ESCOLHA": [CallbackQueryHandler(observacao_escolha, pattern="^(add_obs|skip_obs)$")],
        "OBSERVACAO_DIGITAR": [MessageHandler(filters.TEXT & ~filters.COMMAND, observacao_digitar)],
        "MAIS_DEMANDAS": [CallbackQueryHandler(mais_demandas, pattern="^(mais_demanda)$")],
        "RESUMO": [CallbackQueryHandler(handlers.resumo)],
        "CONFIRMACAO": [CallbackQueryHandler(handlers.confirmacao, pattern="^(confirmar|cancelar)$")],
        "CONFIRMACAO_FINAL": [CallbackQueryHandler(confirmacao, pattern="^(confirmar_salvar|cancelar_resumo)$")],
    },
    fallbacks=[CommandHandler('cancelar', cancelar)],
)

app.add_handler(CommandHandler('oi', start))
app.add_handler(conv_handler)

if __name__ == '__main__':
    print("Bot rodando...")
    app.run_polling()
