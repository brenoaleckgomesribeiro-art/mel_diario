import json
import os
from openai import OpenAI

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-flash")

if DEEPSEEK_API_KEY:
    client = OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com",
    )
else:
    client = None


def analise_fallback():
    return {
        "categoria": "ambíguo",
        "tema": "outro",
        "impacto": 0,
        "sentimento": "não identificado",
        "resumo": "A análise por IA não está disponível. Revise e classifique manualmente.",
    }


def analisar_relato(relato: str) -> dict:
    if not client:
        return analise_fallback()

    system_prompt = """
Você é um classificador neutro de acontecimentos de um diário pessoal de relacionamento.

Sua função NÃO é dizer quem está certo, quem está errado, se alguém é uma pessoa boa ou ruim,
nem recomendar término ou continuidade.

Analise apenas o relato fornecido.

Responda obrigatoriamente em JSON válido, sem Markdown, com exatamente estas chaves:
{
  "categoria": "positivo | negativo | ambíguo",
  "tema": "carinho | comunicação | confiança | ciúmes | amizades | tempo_juntos | conflitos | apoio | diversão | liberdade | outro",
  "impacto": -5,
  "sentimento": "texto curto",
  "resumo": "resumo objetivo em uma ou duas frases"
}

Regras:
- positivo: o relato descreve predominantemente algo que aproximou, ajudou ou fez bem.
- negativo: o relato descreve predominantemente algo que causou desgaste, mágoa ou afastamento.
- ambíguo: existem elementos positivos e negativos ou faltam informações para classificar.
- impacto deve ser inteiro entre -5 e 5.
- Não invente fatos que não estejam no relato.
- Não diagnostique ninguém.
- Não transforme uma situação isolada em padrão.
- O resumo deve separar fatos do relato de interpretações.
- A resposta precisa conter JSON.
"""

    try:
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": (
                        "Analise o seguinte relato e produza o JSON solicitado.\n\n"
                        + relato
                    ),
                },
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
            max_tokens=500,
        )

        content = response.choices[0].message.content
        dados = json.loads(content)

        categoria = dados.get("categoria", "ambíguo")
        if categoria not in {"positivo", "negativo", "ambíguo"}:
            categoria = "ambíguo"

        try:
            impacto = int(dados.get("impacto", 0))
        except (TypeError, ValueError):
            impacto = 0

        impacto = max(-5, min(5, impacto))

        return {
            "categoria": categoria,
            "tema": str(dados.get("tema", "outro"))[:80],
            "impacto": impacto,
            "sentimento": str(
                dados.get("sentimento", "não identificado")
            )[:80],
            "resumo": str(dados.get("resumo", "")),
        }

    except Exception as exc:
        print(f"[DeepSeek] erro: {exc}")
        return analise_fallback()
