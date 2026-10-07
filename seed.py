from datetime import date
from app import app
from models import db, Acontecimento

exemplos = [
    {
        "data": date(2026, 9, 28),
        "titulo": "Ela percebeu que eu não estava bem",
        "descricao": "Mel percebeu que eu estava diferente e perguntou o que tinha acontecido, tentando entender o que eu estava sentindo.",
        "categoria": "positivo",
        "tema": "apoio",
        "impacto": 4,
        "sentimento": "acolhimento",
        "analise_ia": "Ela demonstrou atenção ao estado emocional dele e tentou abrir espaço para conversa.",
    },
    {
        "data": date(2026, 10, 2),
        "titulo": "Discussão depois de um jogo",
        "descricao": "Depois de uma situação durante uma partida, a conversa acabou se tornando uma discussão maior sobre a relação e sobre a forma como os dois estavam se tratando.",
        "categoria": "negativo",
        "tema": "conflitos",
        "impacto": -4,
        "sentimento": "frustração",
        "analise_ia": "Um problema pontual durante o jogo acabou se conectando a questões maiores da relação.",
    },
]


with app.app_context():
    db.create_all()

    if Acontecimento.query.count() == 0:
        for item in exemplos:
            db.session.add(Acontecimento(**item))
        db.session.commit()
        print("Dados de exemplo inseridos.")
    else:
        print("O banco já possui dados; nada foi alterado.")
