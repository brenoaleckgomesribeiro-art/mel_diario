# Diário de Perspectivas — Flask + SQLite + DeepSeek

Projeto pessoal para registrar acontecimentos e organizá-los por categoria, tema, impacto e sentimento.

## 1. Criar o ambiente virtual

### Windows

```powershell
python -m venv venv
venv\Scripts\activate
```

### Linux/macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

## 2. Instalar dependências

```bash
pip install -r requirements.txt
```

## 3. Configurar o DeepSeek

Copie `.env.example` para `.env` e coloque sua chave:

```text
DEEPSEEK_API_KEY=sua_chave_aqui
DEEPSEEK_MODEL=deepseek-flash
```

A aplicação funciona mesmo sem chave: nesse caso, os novos registros ficam como "ambíguo" e avisam que a IA está indisponível.

## 4. Criar dados de exemplo (opcional)

```bash
python seed.py
```

## 5. Rodar

```bash
python app.py
```

Abra:

http://127.0.0.1:5000

## Rotas

- `/` — dashboard
- `/acontecimentos` — lista e filtros
- `/acontecimentos/novo` — novo registro
- `/acontecimentos/<id>` — detalhes
- `/acontecimentos/<id>/editar` — edição
- `/api/analisar` — endpoint JSON para análise por IA

## API de análise

Exemplo de corpo:

```json
{
  "relato": "Hoje tivemos uma discussão porque eu queria jogar com meus amigos."
}
```

A resposta é um JSON estruturado com categoria, tema, impacto, sentimento e resumo.

## Segurança

Nunca coloque a chave do DeepSeek no código nem faça commit do `.env`.

Antes de publicar o projeto na internet, troque a SECRET_KEY e adicione autenticação.
