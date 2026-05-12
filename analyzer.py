import pdfplumber
import sys
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  #carrega o .env

PRECO_INPUT_POR_1K = 0.000150
PRECO_OUTPUT_POR_1K = 0.000600

# função para extrair texto de um PDF.
def extrair_texto_pdf(caminho_pdf):
#verifica se o arquivo existe no caminho especificado.
    if not os.path.exists(caminho_pdf):
        print(f"Erro: O arquivo '{caminho_pdf}' não foi encontrado.")
        sys.exit(1)

    texto_completo = ""

# Abre o PDF e percorre cada página para extrair o texto.
    with pdfplumber.open(caminho_pdf) as pdf:
        for pagina in pdf.pages:
            texto = pagina.extract_text()
            if texto:  # ignora páginas que só são imagens
                texto_completo += texto + "\n"

# Se não foi possível extrair texto, encerra com um erro.
    if not texto_completo.strip():
        print(f"Erro: Não foi possível extrair texto do arquivo '{caminho_pdf}'.")
        sys.exit(1)

    return texto_completo

# função para para instruir o modelo a enviar apenas a resposta JSON.
def chamar_openai(texto_pdf, pergunta, nome_documento):
    client = OpenAI() # pega a chave da API do .env

    # Instrução para o modelo, pedindo para responder apenas com JSON.
    system_prompt = """Você é um analisador de documentos de negócio.
Responda SOMENTE com um objeto JSON válido, sem nenhum texto fora dele, sem markdwn fences (sem ```).
O JSON deve ter exatamente essa estrutura:
{
  "type": "text",
  "text": "<resposta em Markdown com títulos, listas e destaques>",
  "source": "<nome do documento>",
  "suggestions": ["<pergunta 1>", "<pergunta 2>", "<pergunta 3>"]
}"""


    #Mensagem com o conteúdo do PDF e a pergunta do usuário.
    user_prompt = f"""Documento: {nome_documento}

Conteúdo do documento:
{texto_pdf}

Pergunta: {pergunta}"""
    
    response = client.chat.completions.create(
        model="gpt-4o-mini", # melhor custo-benefício para análise de documentos
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3 # valor baixo para respostas mais precisas e consistentes

    )

    return response 


# função pra pegar a resposta da API e fazer o parse do JSON. E calcula o custo estimado da chamada.
def processar_resposta(response, nome_documento):
    conteudo = response.choices[0].message.content.strip()

    # Bloco para remover ```json ``` mesmo sendo instruído a não usar, para evitar erros de parse.
    if conteudo.startswith("```"):
        conteudo = conteudo.split("```")[1]  # pega o conteúdo entre os fences
        if conteudo.startswith("json"):
            conteudo = conteudo[4:]
    

    # Tenta converter o texto em JSON
    try:
        resultado = json.loads(conteudo)
    except json.JSONDecodeError:
        print("Erro: A resposta da API não é um JSON válido.")
        print("Resposta recebida:", conteudo)
        sys.exit(1)


    # Garante que o source está preenchido com o nome do arquivo
    if not resultado.get("source") or resultado["source"] == "N/A":
        resultado["source"] = nome_documento


    # Calcula o custo estimado com base no número de tokens usados 
    tokens_input = response.usage.prompt_tokens
    tokens_output = response.usage.completion_tokens
    custo = (tokens_input / 1000 * PRECO_INPUT_POR_1K) + \
            (tokens_output / 1000 * PRECO_OUTPUT_POR_1K)
    

    print(f"\n--- Uso de tokens ---")
    print(f"Input: {tokens_input} tokens")
    print(f"Output: {tokens_output} tokens")
    print(f"Custo estimado: ${custo:.6f}")
    print("-------------------\n")

    return resultado

# Função para orquestrar tudo, ler argumentos, chamar as funções e exibir a resposta final.
def main():
    # Verifica se o usuário passou o caminho do PDF e a pergunta no terminal
    if len(sys.argv) < 3:
        print("Uso: python analyzer.py <caminho_para_pdf> \"<pergunta>\"")
        sys.exit(1)

    caminho_pdf = sys.argv[1] # primeiro argumento é o caminho do PDF
    pergunta = sys.argv[2] # segundo argumento é a pergunta do usuário
    nome_documento = os.path.basename(caminho_pdf) # extrai só o nome do arquivo do caminho
    
    print(f"Lendo PDF: {nome_documento}...")
    texto_pdf = extrair_texto_pdf(caminho_pdf) # extrai o texto do PDF

    print("Enviando para OpenAI...")
    response = chamar_openai(texto_pdf, pergunta, nome_documento) # chama a API do OpenAI

    resultado = processar_resposta(response, nome_documento) # processa a resposta e calcula o custo

    # Imprime o JSON final formatado
    print(json.dumps(resultado, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()