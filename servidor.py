import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os

API_KEY = os.environ.get('GEMINI_API_KEY')

app = Flask(__name__)
CORS(app)

try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    print("Modelo de IA inicializado com sucesso.")
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

        # --- PROMPT OTIMIZADO AQUI ---
        prompt = f"Você é um assistente para ordens de serviço. Seu objetivo é criar um 'assunto' curto e direto para um técnico. Leia a ordem de serviço abaixo e resuma o problema principal em no máximo 5 palavras, adicionando detalhes técnicos cruciais como 'LOS piscando' se estiverem presentes. Exemplo de saída: 'Sem conexão / LOS piscando'. Ordem de serviço: '{texto_para_resumir}'"

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