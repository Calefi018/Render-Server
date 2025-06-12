import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

API_KEY = 'AIzaSyCbV4idbSFVq_gkt5Q1EMyC8Im7VVKtXDU' 

app = Flask(__name__)
CORS(app)

try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    print("Modelo de IA inicializado com sucesso.")
except Exception as e:
    print(f"Erro Crítico: Não foi possível configurar a API do Google. Verifique a chave. Erro: {e}")
    model = None

# ROTA 1: Para os chamados do Suporte Externo (já existia)
@app.route('/resumir', methods=['POST'])
def resumir_texto():
    if not model:
        return jsonify({'erro': 'O modelo de IA não foi inicializado corretamente.'}), 500
    try:
        data = request.get_json()
        texto_para_resumir = data.get('texto', '')
        prompt = f"""Você é um especialista em analisar ordens de serviço. Sua tarefa é criar um 'assunto' extremamente conciso (3-5 palavras) para um técnico.
        1. Identifique o PROBLEMA PRINCIPAL ou a AÇÃO PRINCIPAL a ser executada.
        2. Se houver um diagnóstico técnico CLARAMENTE MARCADO com (x) (ex: 'ESTÁ EM LOS? SIM (x)'), inclua-o de forma curta (ex: '/ LOS ATIVO'). Se estiver marcado 'NÃO (x)', NÃO inclua essa informação no resumo.
        3. Ignore detalhes secundários como agendamento, preços, orçamentos ou conversas. Foque apenas no trabalho técnico.
        Texto da Ordem de Serviço: '{texto_para_resumir}'"""
        response = model.generate_content(prompt)
        resumo_limpo = response.text.strip().replace('\n', ' ').replace('"', '').replace("'", "")
        print(f"(Rota /resumir) Resumo gerado: {resumo_limpo}") 
        return jsonify({'resumo': resumo_limpo})
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

# ROTA 2: Nova rota para as Retiradas de Cancelamento
@app.route('/extrair-retirada', methods=['POST'])
def extrair_info_retirada():
    if not model:
        return jsonify({'erro': 'O modelo de IA não foi inicializado corretamente.'}), 500
    try:
        data = request.get_json()
        texto_para_analisar = data.get('texto', '')
        prompt = f"""Analise o texto de ordem de serviço a seguir. Encontre a seção que começa com 'Mensagem importante para o técnico fazer a retirada:'. 
        Extraia e retorne APENAS o texto exato que vem depois de 'R:'. Não adicione palavras. 
        Se essa seção não existir ou estiver vazia, retorne o texto 'Verificar detalhes na O.S.'.
        Texto: '{texto_para_analisar}'"""
        response = model.generate_content(prompt)
        extracao_limpa = response.text.strip().replace('\n', ' ').replace('"', '').replace("'", "")
        print(f"(Rota /extrair-retirada) Informação extraída: {extracao_limpa}")
        return jsonify({'periodo_contato': extracao_limpa})
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

if __name__ == '__main__':
    print("Servidor iniciado com 2 rotas. Aguardando requisições em http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
