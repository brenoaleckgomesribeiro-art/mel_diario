from datetime import date

from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv

from models import db, Acontecimento
from ai import analisar_relato


load_dotenv()


app = Flask(__name__)

app.config["SECRET_KEY"] = "troque-esta-chave-em-producao"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mel_diario.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db.init_app(app)


with app.app_context():
    db.create_all()


# =========================
# DASHBOARD
# =========================

@app.route("/")
def index():

    total = Acontecimento.query.count()

    positivos = Acontecimento.query.filter_by(
        categoria="positivo"
    ).count()

    negativos = Acontecimento.query.filter_by(
        categoria="negativo"
    ).count()

    ambiguos = Acontecimento.query.filter_by(
        categoria="ambíguo"
    ).count()

    recentes = (
        Acontecimento.query
        .order_by(
            Acontecimento.data.desc(),
            Acontecimento.id.desc()
        )
        .limit(8)
        .all()
    )

    return render_template(
        "index.html",
        total=total,
        positivos=positivos,
        negativos=negativos,
        ambiguos=ambiguos,
        recentes=recentes,
    )


# =========================
# ACONTECIMENTOS
# =========================

@app.route("/acontecimentos")
def acontecimentos():

    categoria = request.args.get(
        "categoria",
        ""
    ).strip()

    tema = request.args.get(
        "tema",
        ""
    ).strip()

    query = Acontecimento.query

    if categoria in {
        "positivo",
        "negativo",
        "ambíguo"
    }:

        query = query.filter_by(
            categoria=categoria
        )

    if tema:

        query = query.filter(
            Acontecimento.tema.ilike(
                f"%{tema}%"
            )
        )

    itens = (
        query
        .order_by(
            Acontecimento.data.desc(),
            Acontecimento.id.desc()
        )
        .all()
    )

    return render_template(
        "timeline.html",
        acontecimentos=itens,
        categoria=categoria,
        tema=tema,
    )


# =========================
# NOVO ACONTECIMENTO
# =========================

@app.route(
    "/acontecimentos/novo",
    methods=["GET", "POST"]
)
def novo():

    if request.method == "POST":

        titulo = (
            request.form
            .get("titulo", "")
            .strip()
        )

        descricao = (
            request.form
            .get("descricao", "")
            .strip()
        )

        data_str = (
            request.form
            .get("data", "")
            .strip()
        )


        # Validação básica

        if not titulo or not descricao:

            flash(
                "Preencha o título e a descrição.",
                "warning"
            )

            return render_template(
                "adicionar.html",
                hoje=date.today().isoformat()
            )


        # Converte a data

        try:

            data = (
                date.fromisoformat(data_str)
                if data_str
                else date.today()
            )

        except ValueError:

            flash(
                "A data informada é inválida.",
                "warning"
            )

            return render_template(
                "adicionar.html",
                hoje=date.today().isoformat()
            )


        # Analisa o relato

        analise = analisar_relato(
            descricao
        )


        # Cria o acontecimento

        acontecimento = Acontecimento(

            titulo=titulo,

            descricao=descricao,

            data=data,

            categoria=analise.get(
                "categoria",
                "ambíguo"
            ),

            tema=analise.get(
                "tema",
                "outro"
            ),

            impacto=int(
                analise.get(
                    "impacto",
                    0
                )
            ),

            sentimento=analise.get(
                "sentimento",
                "não identificado"
            ),

            analise_ia=analise.get(
                "resumo",
                ""
            ),
        )


        db.session.add(
            acontecimento
        )

        db.session.commit()


        flash(
            "Acontecimento salvo.",
            "success"
        )


        return redirect(
            url_for(
                "detalhe",
                id=acontecimento.id
            )
        )


    return render_template(
        "adicionar.html",
        hoje=date.today().isoformat()
    )


# =========================
# DETALHE
# =========================

@app.route(
    "/acontecimentos/<int:id>"
)
def detalhe(id):

    acontecimento = (
        Acontecimento.query
        .get_or_404(id)
    )

    return render_template(
        "detalhe.html",
        acontecimento=acontecimento
    )


# =========================
# EDITAR ACONTECIMENTO
# =========================

@app.route(
    "/acontecimentos/<int:id>/editar",
    methods=["GET", "POST"]
)
def editar(id):

    acontecimento = (
        Acontecimento.query
        .get_or_404(id)
    )


    if request.method == "POST":

        # =========================
        # TÍTULO
        # =========================

        acontecimento.titulo = (
            request.form
            .get("titulo", "")
            .strip()
        )


        # =========================
        # DESCRIÇÃO
        # =========================

        acontecimento.descricao = (
            request.form
            .get("descricao", "")
            .strip()
        )


        # =========================
        # CLASSIFICAÇÃO
        # =========================

        categoria = (
            request.form
            .get("categoria", "")
            .strip()
        )

        if categoria in {
            "positivo",
            "negativo",
            "ambíguo"
        }:

            acontecimento.categoria = categoria


        # =========================
        # TEMA
        # =========================

        tema = (
            request.form
            .get("tema", "")
            .strip()
        )

        if tema:

            acontecimento.tema = tema


        # =========================
        # SENTIMENTO
        # =========================

        sentimento = (
            request.form
            .get("sentimento", "")
            .strip()
        )

        if sentimento:

            acontecimento.sentimento = sentimento


        # =========================
        # IMPACTO
        # =========================

        impacto_str = (
            request.form
            .get("impacto", "")
            .strip()
        )

        try:

            impacto = int(
                impacto_str
            )

            if -5 <= impacto <= 5:

                acontecimento.impacto = impacto

        except (ValueError, TypeError):

            pass


        # =========================
        # DATA
        # =========================

        data_str = (
            request.form
            .get("data", "")
            .strip()
        )


        if data_str:

            try:

                acontecimento.data = (
                    date.fromisoformat(
                        data_str
                    )
                )

            except ValueError:

                flash(
                    "A data informada é inválida.",
                    "warning"
                )

                return render_template(
                    "editar.html",
                    acontecimento=acontecimento
                )


        # =========================
        # REANÁLISE DA IA
        # =========================

        if request.form.get(
            "reanalisar"
        ) == "1":

            analise = analisar_relato(
                acontecimento.descricao
            )


            acontecimento.categoria = (
                analise.get(
                    "categoria",
                    "ambíguo"
                )
            )


            acontecimento.tema = (
                analise.get(
                    "tema",
                    "outro"
                )
            )


            acontecimento.impacto = int(
                analise.get(
                    "impacto",
                    0
                )
            )


            acontecimento.sentimento = (
                analise.get(
                    "sentimento",
                    "não identificado"
                )
            )


            acontecimento.analise_ia = (
                analise.get(
                    "resumo",
                    ""
                )
            )


        # =========================
        # SALVAR
        # =========================

        db.session.commit()


        flash(
            "Acontecimento atualizado.",
            "success"
        )


        return redirect(
            url_for(
                "detalhe",
                id=id
            )
        )


    return render_template(
        "editar.html",
        acontecimento=acontecimento
    )


# =========================
# EXCLUIR
# =========================

@app.post(
    "/acontecimentos/<int:id>/excluir"
)
def excluir(id):

    acontecimento = (
        Acontecimento.query
        .get_or_404(id)
    )


    db.session.delete(
        acontecimento
    )

    db.session.commit()


    flash(
        "Acontecimento excluído.",
        "success"
    )


    return redirect(
        url_for("acontecimentos")
    )


# =========================
# API DE ANÁLISE
# =========================

@app.route(
    "/api/analisar",
    methods=["POST"]
)
def api_analisar():

    dados = (
        request
        .get_json(silent=True)
        or {}
    )


    relato = str(
        dados.get(
            "relato",
            ""
        )
    ).strip()


    if not relato:

        return {
            "erro": "Envie um relato."
        }, 400


    return analisar_relato(
        relato
    )


# =========================
# EXECUÇÃO
# =========================

if __name__ == "__main__":

    app.run(
        debug=True
    )