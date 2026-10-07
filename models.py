from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Acontecimento(db.Model):
    __tablename__ = "acontecimentos"

    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False)
    titulo = db.Column(db.String(160), nullable=False)
    descricao = db.Column(db.Text, nullable=False)

    categoria = db.Column(db.String(20), nullable=False, default="ambíguo")
    tema = db.Column(db.String(80), nullable=False, default="outro")
    impacto = db.Column(db.Integer, nullable=False, default=0)
    sentimento = db.Column(db.String(80), nullable=False, default="não identificado")

    analise_ia = db.Column(db.Text, nullable=True)
    criado_em = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<Acontecimento {self.id}: {self.titulo}>"
