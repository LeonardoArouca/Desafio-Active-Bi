# Analisador de Documentos com IA

Script Python que analisa PDFs e responde perguntas em linguagem natural usando a API da OpenAI.

## Instalação

```bash
pip install -r requirements.txt
```

Crie um arquivo `.env` na raiz do projeto:
```
OPENAI_API_KEY=sk-sua-chave-aqui
```

## Uso

```bash
python analyzer.py <caminho_do_pdf> "<sua pergunta>"
```

**Exemplo:**
```bash
python analyzer.py relatorio.pdf "Quais são os principais KPIs do relatório?"
```

## Modelo utilizado

Foi escolhido o modelo `gpt-4o-mini` pelos seguintes motivos:
- Suporte a contextos longos, ideal para PDFs extensos
- Alta capacidade de seguir instruções de formato JSON
- Melhor custo-benefício comparado ao `gpt-4o`
- Velocidade de resposta superior

## Estimativa de custo

O script exibe automaticamente após cada execução:
- Tokens de input consumidos
- Tokens de output consumidos
- Custo estimado em dólares