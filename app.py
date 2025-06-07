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
    print("Modelo de IA (versão aprimorada) inicializado com sucesso.")
except Exception as e:
    print(f"Erro Crítico: Não foi possível configurar a API do Google. Verifique a chave. Erro: {e}")
    model = None

@app.route('/resumir', methods=['POST'])
def resumir_texto():
    if not model:
        return jsonify({'erro': 'O modelo de IA não foi inicializado corretamente.'}), 500

    try:
        data = request.get_json()
        if not data or 'texto' not in data:
            return jsonify({'erro': 'Requisição inválida.'}), 400

        texto_para_resumir = data['texto']
        
        # --- PROMPT OTIMIZADO PARA PRECISÃO E CONCISÃO ---
        prompt = f"""
        Você é um especialista em analisar ordens de serviço. Sua tarefa é criar um 'assunto' extremamente conciso (3-5 palavras) para um técnico.
        1. Identifique o PROBLEMA PRINCIPAL ou a AÇÃO PRINCIPAL a ser executada.
        2. Se houver um diagnóstico técnico CLARAMENTE MARCADO com (x) (ex: 'ESTÁ EM LOS? SIM (x)'), inclua-o de forma curta (ex: '/ LOS ATIVO'). Se estiver marcado 'NÃO (x)', NÃO inclua essa informação no resumo.
        3. Ignore detalhes secundários como agendamento, preços, orçamentos ou conversas. Foque apenas no trabalho técnico.
        Texto da Ordem de Serviço: '{texto_para_resumir}'
        """
        
        response = model.generate_content(prompt)
        resumo_limpo = response.text.strip().replace('\n', ' ').replace('"', '').replace("'", "")

        print(f"Resumo gerado: {resumo_limpo}") 
        return jsonify({'resumo': resumo_limpo})

    except Exception as e:
        print(f"Erro durante o resumo: {e}")
        return jsonify({'erro': str(e)}), 500

if __name__ == '__main__':
    print("Servidor iniciado. Aguardando requisições em http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
