"""
Seed script — CIG: Centro Integrado de Governo SP.
Dados atualizados: deputados ALESP 35ª Legislatura, eleições municipais 2024,
secretarias de Estado do Governo Tarcísio de Freitas (2023-2026).
Idempotente: verifica existência antes de inserir.
"""
import os
import sys
import random
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, SessionLocal
from app.models import Base, Deputy, Municipality, Mayor, Amendment, Secretariat, BudgetItem, Program

# ---------------------------------------------------------------------------
# Raw data — ALESP 35ª Legislatura (2023-2027)
# Fonte oficial: TSE/SP — Resultado eleições estaduais 02/10/2022
# Ordenado por votos (posição 1=mais votado, 94=menos votado)
# (name, party, votes_2022, registration, ranking, is_substitute, mandates, photo_url)
# ---------------------------------------------------------------------------
DEPUTIES_DATA = [
    ("Eduardo Suplicy", "PT", 807015, 300693, 1, False, 2, "/biografia/fotos/20230321-191506-id=987-GRD.jpg"),
    ("Carlos Giannazi", "PSOL", 276811, 300485, 2, False, 5, "/biografia/fotos/20230321-191048-id=148-GRD.jpg"),
    ("Paula da Bancada Feminista", "PSOL", 259771, None, 3, False, 1, ""),
    ("Bruno Zambelli", "PL", 235305, 300660, 4, False, 1, "/biografia/fotos/20230511-162900-id=1644-GRD.jfif"),
    ("Major Mecca", "PL", 224462, 300633, 5, False, 2, "/biografia/fotos/20230322-111405-id=521-GRD.jpeg"),
    ("Tomé Abduch", "PP", 221656, None, 6, False, 1, ""),
    ("André do Prado", "PL", 216268, 300497, 7, False, 4, "/biografia/fotos/300497/2f42bf3f57458a3a37942214178dfc3d890395c8884ceb9979a0aea6f0a1850c.jpeg"),
    ("Tenente Coimbra", "PL", 209705, None, 8, False, 1, ""),
    ("Delegado Olim", "PP", 201348, 300543, 9, False, 3, "/biografia/fotos/20230321-191240-id=263-GRD.jpg"),
    ("Ana Carolina Serra", "CIDADANIA", 198698, 300657, 10, False, 1, "/biografia/fotos/20230315-163915-id=1622-GRD.jpeg"),
    ("Milton Leite Filho", "UNIÃO", 198429, None, 11, False, 1, ""),
    ("Gil Diniz Bolsonaro", "PL", 196215, 300670, 12, False, 1, "/biografia/fotos/20230321-130525-id=1650-GRD.jpg"),
    ("Bruna Furlan", "PSDB", 195436, 300659, 13, False, 1, "/biografia/fotos/20230315-170525-id=1641-GRD.jpeg"),
    ("Conte Lopes", "PL", 192454, 300205, 14, False, 8, "/biografia/fotos/20230316-173502-id=180-GRD.jpg"),
    ("Itamar Borges", "MDB", 183480, 300625, 15, False, 1, "/biografia/fotos/20191114-174133-id=529-GRD.jpg"),
    # Nota: Itamar Borges assumiu Sec. Agricultura (Tarcísio) → suplente MDB assumiu
    ("Marcos Damasio", "PL", 183219, 300638, 16, False, 2, "/biografia/fotos/20230323-095827-id=525-GRD.jpg"),
    ("Carlos Cezar", "PL", 180690, None, 17, False, 1, ""),
    ("Carla Morando", "PSDB", 177773, 300614, 18, False, 2, "/biografia/fotos/20230315-142108-id=540-GRD.jpeg"),
    ("Jorge Wilson Xerife do Consumidor", "REPUBLICANOS", 177614, 300627, 19, False, 2, "/biografia/fotos/300627/66d82bc48da44e2c5448551d036be98f99cfd27fb168bb98f10282156ae1b532.jpeg"),
    ("Ediane Maria", "PSOL", 175617, 300667, 20, False, 1, "/biografia/fotos/20230427-144843-id=1654-GRD.jpg"),
    ("Marta Costa", "PSD", 170541, None, 21, False, 1, ""),
    ("Emídio de Souza", "PT", 157834, 300395, 22, False, 5, "/biografia/fotos/20230315-145500-id=517-GRD.jpg"),
    ("Professora Bebel", "PT", 155983, None, 23, False, 1, ""),
    ("Guto Zacarias", "MISSÃO", 152481, 300624, 24, False, 2, "/biografia/fotos/20191112-191414-id=530-GRD.jpg"),
    ("Gerson Pessoa", "PODE", 143704, None, 25, False, 1, ""),
    ("Enio Tatto", "PT", 142785, 300440, 26, False, 6, "/biografia/fotos/20191112-192019-id=175-GRD.jpg"),
    ("Luiz Fernando T. Ferreira", "PT", 141017, 300545, 27, False, 3, "/biografia/fotos/300545/b25d811e25a8378431dcab7c7b0e4fdb0e0a4989c68c339ba40d03c99abc2019.jpeg"),
    ("Rogério Nogueira", "PSDB", 139756, None, 28, False, 1, ""),
    ("Oseias de Madureira", "REPUBLICANOS", 137205, None, 29, False, 1, ""),
    ("Valeria Bolsonaro", "PL", 131557, None, 30, False, 1, ""),
    ("Lucas Bove", "PL", 130451, 300676, 31, False, 1, "/biografia/fotos/20230315-170418-id=1640-GRD.jpg"),
    ("Edmir Chedid", "PSD", 129097, None, 32, False, 1, ""),
    ("Thiago Auricchio", "PSD", 123483, 300508, 33, False, 3, "/biografia/fotos/20230315-171128-id=152-GRD.jpeg"),
    ("Vinícius Camarinha", "PSB", 123316, 300655, 34, False, 2, "/biografia/fotos/20230315-171601-id=538-GRD.jpg"),
    ("Maurici", "MDB", 121455, 300653, 35, False, 2, "/biografia/fotos/20230321-191839-id=529-GRD.jpg"),
    ("Rafael Silva", "REPUBLICANOS", 118182, None, 36, False, 1, ""),
    ("Paulo Fiorilo", "PT", 110251, 300471, 37, False, 7, "/biografia/fotos/20230315-161523-id=78-GRD.jpg"),
    ("Reis", "PT", 108726, None, 38, False, 1, ""),
    ("Márcia Lia", "PT", 108587, 300534, 39, False, 3, "/biografia/fotos/20230802-131346-id=281-GRD.jpg"),
    ("Barba", "PT", 108071, None, 40, False, 1, ""),
    ("Mônica do Movimento Pretas", "PSOL", 106781, None, 41, False, 1, ""),
    ("Carlão Pignatari", "PSD", 105245, 300499, 42, False, 4, "/biografia/fotos/300499/9717fd9e32cdb65c43f9558978d7a440bc407b053773de388c2f6f345989eba6.jpeg"),
    ("Caio França", "PSB", 105173, 300540, 43, False, 3, "/biografia/fotos/20230321-190741-id=267-GRD.jpg"),
    # Nota: Caio França assumiu Sec. Habitação (Tarcísio) → suplente PSB assumiu
    ("Sebastião Santos", "REPUBLICANOS", 104374, None, 44, False, 1, ""),
    ("Altair Moraes", "REPUBLICANOS", 98515, 300609, 45, False, 2, "/biografia/fotos/20230315-141411-id=545-GRD.jpeg"),
    ("Rafael Saraiva", "UNIÃO", 98070, 300651, 46, False, 1, "/biografia/fotos/20230315-163143-id=539-GRD.jpg"),
    ("Gilmaci Santos", "REPUBLICANOS", 96361, 300671, 47, False, 1, "/biografia/fotos/20230315-170849-id=1649-GRD.jpeg"),
    ("Agente Federal Danilo Balas", "PL", 94552, 300607, 48, False, 2, "/biografia/fotos/300607/678129ff534ded49f5d96881ab26868b6170b40819639502898b48ee6030c787.jpeg"),
    ("Dirceu Dalben", "PSD", 93397, 300650, 49, False, 2, "/biografia/fotos/20230324-122116-id=561-GRD.png"),
    ("Rui Alves", "REPUBLICANOS", 91717, None, 50, False, 1, ""),
    ("Thainara Faria", "PT", 91388, None, 51, False, 1, ""),
    ("Leonardo Siqueira", "NOVO", 90688, 300675, 52, False, 1, "/biografia/fotos/20230321-192007-id=1642-GRD.png"),
    ("Ricardo Madalena", "PL", 90630, 300703, 53, False, 2, ""),
    ("Leci Brandão", "PCdoB", 90496, 300513, 54, False, 4, "/biografia/fotos/20230718-161931-id=38-GRD.jpg"),
    ("Felipe Franco", "UNIÃO", 90440, 300622, 55, False, 1, "/biografia/fotos/20200819-200938-id=532-GRD.jpeg"),
    ("Analice Fernandes", "PSD", 90135, 300431, 56, False, 6, "/biografia/fotos/300431/69142319ee3fc052a205d625527ba5a8de9faa52aa1b643a8b3c0f41f886e1a7.jpeg"),
    ("Andréa Werner", "PSB", 88820, 300658, 57, False, 1, "/biografia/fotos/300658/ec8711d9e474223bd1fdb27dbaff6fb7cab4ecb03d9f34023706fb4734e2868d.jpeg"),
    ("Donato", "PT", 88022, 300664, 58, False, 1, "/biografia/fotos/20230321-130104-id=1655-GRD.png"),
    ("Barros Munhoz", "PSD", 86372, 300188, 59, False, 7, "/biografia/fotos/300188/c5f99a2bc1c4d2dfe5d72c8a24e6b9a242b03d5b61314284be308fee932813a6.jpeg"),
    ("Paulo Mansur", "PL", 86201, None, 60, False, 1, ""),
    ("Marina Helou", "REDE", 85517, None, 61, False, 1, ""),
    ("Marcio Nakashima", "PSD", 85195, 300635, 62, False, 2, "/biografia/fotos/300635/e9bff5d91c252b6c5055f1d7e8fc6742223d6af479becb1f88a008887e4df549.jpeg"),
    ("Capitão Telhada", "PP", 83438, 300661, 63, False, 1, "/biografia/fotos/20230315-173219-id=1648-GRD.png"),
    ("Edna Macedo", "REPUBLICANOS", 82932, 300318, 64, False, 4, "/biografia/fotos/20190315-152242-id=516-GRD.jpeg"),
    ("Jorge Caruso", "MDB", 82209, 300626, 65, False, 1, "/biografia/fotos/20191112-192211-id=528-GRD.jpg"),
    ("Léo Oliveira", "MDB", 82145, 300264, 66, False, 5, "/biografia/fotos/300264/4480e5e51c390cae6caaa26e6692a785b08df07ff7caaed48d4a351f44e60171.jpeg"),
    ("Dr. Jorge do Carmo", "PT", 82054, 300623, 67, False, 2, "/biografia/fotos/20190315-162558-id=531-GRD.jpg"),
    ("Solange Freitas", "PSD", 81870, None, 68, False, 1, ""),
    ("Daniel Soares", "UNIÃO", 81753, 300619, 69, False, 2, "/biografia/fotos/20230315-142647-id=535-GRD.jpg"),
    ("Dani Alonso", "PL", 80337, 300663, 70, False, 1, "/biografia/fotos/20230315-171350-id=1653-GRD.jpeg"),
    ("Ana Perugini", "PT", 79061, 300466, 71, False, 3, "/biografia/fotos/20230320-180813-id=81-GRD.jpg"),
    ("Mauro Bragato", "PSDB", 78142, None, 72, False, 1, ""),
    ("Helinho Zanatta", "MDB", 77550, None, 73, False, 1, ""),
    ("Rafa Zimbaldi", "CIDADANIA", 76910, 300492, 74, False, 3, "/biografia/fotos/20230315-162055-id=135-GRD.jpg"),
    ("Rogério Santos", "MDB", 76602, None, 75, False, 1, ""),
    ("Rodrigo Moraes", "PL", 75094, None, 76, False, 1, ""),
    ("Rômulo Fernandes", "PT", 75033, None, 77, False, 1, ""),
    ("Alex Madureira", "PL", 74340, 300608, 78, False, 2, "/biografia/fotos/20230302-145402-id=546-GRD.jpg"),
    ("Luiz Claudio Marcolino", "PT", 70487, 300514, 79, False, 2, "/biografia/fotos/20230529-131249-id=1637-GRD.jpeg"),
    ("Delegada Graciela", "PL", 68955, 300620, 80, False, 2, "/biografia/fotos/300620/b725bb9f2b1a490e2e6b490ae913be604ec542b36f1375ded387ba72d391e184.jpeg"),
    ("Letícia Aguiar", "PL", 68556, 300631, 81, False, 2, "/biografia/fotos/20230315-150330-id=523-GRD.jpg"),
    ("Maria Lucia Amary", "PSDB", 66956, None, 82, False, 1, ""),
    ("Fabiana Bolsonaro", "PL", 65497, 300668, 83, False, 1, ""),
    ("Beth Sahão", "PT", 65407, 300435, 84, False, 6, "/biografia/fotos/20230317-110718-id=31-GRD.jpeg"),
    ("Ricardo França", "PODE", 64175, None, 85, False, 1, ""),
    ("Paulo Corrêa Jr", "REPUBLICANOS", 62239, None, 86, False, 1, ""),
    ("Simão Pedro", "PT", 59785, 300511, 87, False, 4, "/biografia/fotos/20230315-165428-id=148-GRD.jpg"),
    ("Clarice Ganem", "PODE", 59342, 300662, 88, False, 1, "/biografia/fotos/300662/d9362d62e29435984b085411f9c8dd4f482f95db5b129c476778773a9d4a0cd8.jpeg"),
    ("Atila Jacomussi", "UNIÃO", 58707, 300537, 89, False, 2, "/biografia/fotos/20230315-170109-id=265-GRD.jpg"),
    ("Vitão do Cachorrão", "REPUBLICANOS", 56729, None, 90, False, 1, ""),
    ("Dr. Eduardo Nóbrega", "PODE", 53607, 300665, 91, False, 1, "/biografia/fotos/20230315-171633-id=1657-GRD.jpg"),
    ("Dr. Valdomiro Lopes", "PSB", 50824, None, 92, False, 1, ""),
    ("Dr. Elton", "UNIÃO", 46042, 300666, 93, False, 1, ""),
    ("Guilherme Cortez", "PSOL", 45094, 300672, 94, False, 1, "/biografia/fotos/20230321-130905-id=1646-GRD.jpg"),
]

# ---------------------------------------------------------------------------
# Secretarias de Estado — Governo Tarcísio de Freitas (2023-2026)
# (name, acronym, emoji, secretary_name, party, executives)
# executives format: "Nome|Partido;Nome|Partido"
# ---------------------------------------------------------------------------
SECRETARIATS_DATA = [
    (
        "Educação", "SEDUC", "📚",
        "Renato Feder", "sem partido",
        "João Marcelo Borges|sem partido;Célia Tokoro|sem partido",
    ),
    (
        "Saúde", "SES", "🏥",
        "Eleuses Vieira de Paiva", "PL",
        "Carlos Eduardo Fratezi|sem partido;Ana Cristina|sem partido",
    ),
    (
        "Segurança Pública", "SSP", "🚔",
        "Guilherme Derrite", "PL",
        "José Carlos Rocha|sem partido;Benedito Mariano|sem partido",
    ),
    (
        "Fazenda e Planejamento", "SEFAZ", "💰",
        "Samuel Kinoshita", "PSDB",
        "Felipe Salto|sem partido;André Carvalho|sem partido",
    ),
    (
        "Meio Ambiente, Infraestrutura e Logística", "SEMIL", "🌿",
        "Natália Resende", "PL",
        "Marcus Vinicius|sem partido;Patricia Ellen|sem partido",
    ),
    (
        "Habitação", "SEHAB", "🏠",
        "Marcello Lima", "PODE",
        "Marcos Pellegrini|sem partido;Sandra Momesso|sem partido",
    ),
    (
        "Agricultura e Abastecimento", "SAA", "🌾",
        "Guilherme Piai", "AVANTE",
        "Fábio Meirelles|sem partido;Ana Paula Rodrigues|sem partido",
    ),
    (
        "Desenvolvimento Econômico", "SDE", "💼",
        "Jorge Lima Lima", "PL",
        "Rodrigo Garcia|sem partido;Camila Moretti|sem partido",
    ),
    (
        "Cultura e Economia Criativa", "SEC", "🎭",
        "Marilia Marton", "sem partido",
        "Luiz Marcelo|sem partido;Renata Fukushima|sem partido",
    ),
    (
        "Turismo e Viagens", "SETUR", "✈️",
        "Roberto de Lucena", "REPUBLICANOS",
        "Thiago Martins|sem partido;Fernanda Lima|sem partido",
    ),
    (
        "Cidades e Desenvolvimento Regional", "SCDR", "🏙️",
        "Marco Vinholi", "PSDB",
        "Eduardo Mazzei|sem partido;Sonia Racy|sem partido",
    ),
    (
        "Transportes Metropolitanos", "STM", "🚇",
        "Diego Basei", "sem partido",
        "Paulo Galli|sem partido;Carla Figueiredo|sem partido",
    ),
    (
        "Desenvolvimento Social e Família", "SEDS", "🤝",
        "Gilmara Lima", "sem partido",
        "Vania Borges|sem partido;Claudia Motta|sem partido",
    ),
    (
        "Esportes", "SE", "⚽",
        "Laercio Benko", "sem partido",
        "Carlos Augusto|sem partido;Marcos Aurélio|sem partido",
    ),
    (
        "Casa Civil", "CC", "🏛️",
        "Arthur Lima", "sem partido",
        "Mauricio Trentin|sem partido;Adriana Lima|sem partido",
    ),
    (
        "Parcerias em Investimentos", "SPI", "🤝",
        "Rafael Benini", "sem partido",
        "Bruno Giannini|sem partido;Lucas Oliveira|sem partido",
    ),
    (
        "Relações Internacionais", "SRI", "🌍",
        "Julio Saqui", "sem partido",
        "Monica Nogueira|sem partido;Rodrigo Alves|sem partido",
    ),
    (
        "Administração Penitenciária", "SAP", "🔒",
        "Marcello Streifinger", "sem partido",
        "Paulo Lacerda|sem partido;Renato Campos|sem partido",
    ),
    (
        "Comunicação", "SECOM", "📢",
        "Tanara Cossa", "sem partido",
        "Alexandre Tavares|sem partido;Bianca Fernandes|sem partido",
    ),
    (
        "Governo", "SG", "⭐",
        "Gilberto Kassab", "PSD",
        "Marcos Penido|PSDB;Renato Arnaldo|PSD",
    ),
]

# budget base values in billions (used to generate realistic orçamento data)
BUDGET_BASES = {
    "SEDUC": 70.0, "SES": 50.0, "SSP": 22.0, "SEMIL": 15.0, "SCDR": 12.0,
    "SEFAZ": 10.0, "SEC": 3.5, "SEHAB": 8.0, "SAA": 4.0, "STM": 18.0,
    "SDE": 6.0, "SEDS": 9.0, "SETUR": 2.5, "SE": 2.0, "CC": 3.0,
    "SPI": 1.5, "SRI": 0.8, "SAP": 7.0, "SECOM": 1.2, "SG": 2.0,
}

# ---------------------------------------------------------------------------
# Municípios — maiores cidades SP com coordenadas geográficas
# (name, region, population, lat, lng)
# ---------------------------------------------------------------------------
MUNICIPALITIES_DATA = [
    ("São Paulo", "Grande SP", 12325232, -23.5505, -46.6333),
    ("Guarulhos", "Grande SP", 1392121, -23.4628, -46.5333),
    ("Campinas", "Interior", 1223237, -22.9099, -47.0626),
    ("São Bernardo do Campo", "Grande SP", 844483, -23.6939, -46.5650),
    ("São José dos Campos", "Vale do Paraíba", 750183, -23.1794, -45.8869),
    ("Santo André", "Grande SP", 720294, -23.6639, -46.5383),
    ("Osasco", "Grande SP", 700682, -23.5324, -46.7920),
    ("Sorocaba", "Interior", 724670, -23.5015, -47.4526),
    ("Ribeirão Preto", "Interior", 720294, -21.1775, -47.8103),
    ("Mauá", "Grande SP", 478564, -23.6678, -46.4611),
    ("Mogi das Cruzes", "Grande SP", 464886, -23.5224, -46.1883),
    ("São José do Rio Preto", "Interior", 466981, -20.8080, -49.3816),
    ("Diadema", "Grande SP", 424058, -23.6861, -46.6231),
    ("Jundiaí", "Interior", 432242, -23.1857, -46.8989),
    ("Piracicaba", "Interior", 415458, -22.7253, -47.6497),
    ("Carapicuíba", "Grande SP", 396973, -23.5226, -46.8350),
    ("Bauru", "Interior", 380442, -22.3147, -49.0600),
    ("Santos", "Litoral", 433311, -23.9618, -46.3322),
    ("Mogi Guaçu", "Interior", 151201, -22.3724, -46.9410),
    ("Praia Grande", "Litoral", 338045, -24.0059, -46.4022),
    ("Taubaté", "Vale do Paraíba", 318069, -23.0246, -45.5556),
    ("Franca", "Interior", 360022, -20.5386, -47.4008),
    ("Limeira", "Interior", 317048, -22.5639, -47.4017),
    ("São Carlos", "Interior", 259805, -22.0087, -47.8909),
    ("Americana", "Interior", 242282, -22.7384, -47.3315),
    ("Araraquara", "Interior", 242755, -21.7942, -48.1758),
    ("Jacareí", "Vale do Paraíba", 252035, -23.2979, -45.9652),
    ("Presidente Prudente", "Interior", 234003, -22.1208, -51.3882),
    ("Marília", "Interior", 240032, -22.2192, -49.9434),
    ("São Vicente", "Litoral", 371188, -23.9607, -46.3882),
]

# Mayors — eleições municipais outubro 2024, mandato 2025-2028
# (name, party, term_start, term_end)
MAYORS_DATA = [
    ("Ricardo Nunes", "MDB", 2025, 2028),            # São Paulo — reeleito
    ("Gustavo Henric Costa", "PP", 2025, 2028),      # Guarulhos
    ("Dário Saadi", "REPUBLICANOS", 2025, 2028),     # Campinas — reeleito
    ("Marcelo Lima", "PODE", 2025, 2028),            # São Bernardo do Campo
    ("Anderson Farias", "PP", 2025, 2028),           # São José dos Campos
    ("Gilvan Junior", "SD", 2025, 2028),             # Santo André
    ("Rogério Lins", "PODE", 2025, 2028),            # Osasco — reeleito
    ("Rodrigo Manga", "REPUBLICANOS", 2025, 2028),   # Sorocaba — reeleito
    ("Eduardo Lacera", "PSD", 2025, 2028),           # Ribeirão Preto
    ("Marcelo Oliveira", "PT", 2025, 2028),          # Mauá — reeleito
    ("Caio Cunha", "PODE", 2025, 2028),              # Mogi das Cruzes — reeleito
    ("Edinho Araújo", "MDB", 2025, 2028),            # São José do Rio Preto — reeleito
    ("José de Filippi", "PT", 2025, 2028),           # Diadema — reeleito
    ("Gustavo Martinelli", "MDB", 2025, 2028),       # Jundiaí — reeleito
    ("Luciano Almeida", "MDB", 2025, 2028),          # Piracicaba — reeleito
    ("Marcos Neves", "MDB", 2025, 2028),             # Carapicuíba
    ("Suéllen Rosim", "REPUBLICANOS", 2025, 2028),   # Bauru — reeleita
    ("Lucas Mangas Bigi", "PL", 2025, 2028),         # Santos
    ("Walter Caveanha", "REPUBLICANOS", 2025, 2028), # Mogi Guaçu
    ("Carlos Persuhn", "PP", 2025, 2028),            # Praia Grande
    ("Ortiz Junior", "PSD", 2025, 2028),             # Taubaté
    ("Alexandre Ferreira", "MDB", 2025, 2028),       # Franca
    ("Denis Andia", "PL", 2025, 2028),               # Limeira
    ("Netto Donato", "PSDB", 2025, 2028),            # São Carlos
    ("Chico Sardelli", "PL", 2025, 2028),            # Americana — reeleito
    ("Edson Antonio Martins", "MDB", 2025, 2028),    # Araraquara
    ("Lucas Storino", "PSDB", 2025, 2028),           # Jacareí
    ("Eduardo Albertassi", "MDB", 2025, 2028),       # Presidente Prudente
    ("Daniel Alonso", "PODE", 2025, 2028),           # Marília
    ("Robson Rodrigues da Fonseca", "PSD", 2025, 2028), # São Vicente
]

PROGRAMS_DATA = [
    ("Escola em Tempo Integral", "Ampliação da jornada escolar em período integral nas escolas estaduais de São Paulo.", 1, 2022, None, 4_800_000_000.0, "ativo"),
    ("Bolsa do Povo", "Programa de transferência de renda para famílias em situação de vulnerabilidade social.", 13, 2021, None, 2_100_000_000.0, "ativo"),
    ("Educação SP Digital", "Transformação digital das escolas estaduais com tablets, conectividade e formação docente.", 1, 2023, None, 1_200_000_000.0, "ativo"),
    ("Habita SP", "Programa habitacional para famílias de baixa renda com subsídios e parcerias com municípios.", 6, 2022, None, 3_400_000_000.0, "ativo"),
    ("Infra SP", "Modernização de rodovias, pontes e estrutura viária do estado de São Paulo.", 5, 2021, 2025, 6_700_000_000.0, "ativo"),
    ("Verde Perto", "Recuperação de áreas degradadas, reflorestamento e pagamento por serviços ambientais.", 5, 2022, 2024, 850_000_000.0, "concluido"),
    ("Agro SP", "Fomento ao agronegócio familiar e modernização do setor rural paulista.", 7, 2023, None, 620_000_000.0, "ativo"),
    ("Metrô SP Expansão", "Expansão das linhas de metrô e trem metropolitano na RMSP.", 12, 2021, None, 12_500_000_000.0, "ativo"),
    ("SP nos Trilhos", "Modernização e expansão da malha ferroviária estadual.", 12, 2022, None, 5_200_000_000.0, "ativo"),
    ("São Paulo pela Paz", "Programa integrado de segurança pública com tecnologia e inteligência.", 3, 2023, None, 980_000_000.0, "ativo"),
    ("Construa SP", "Programa habitacional de mutirão e regularização fundiária.", 6, 2023, None, 1_800_000_000.0, "ativo"),
    ("Investe SP Turismo", "Fomento ao turismo regional com infraestrutura e marketing.", 10, 2023, None, 450_000_000.0, "ativo"),
]

AMENDMENT_DESCRIPTIONS = [
    "Pavimentação de vias urbanas",
    "Construção de unidade básica de saúde",
    "Aquisição de equipamentos hospitalares",
    "Reforma de escola estadual",
    "Implantação de sistema de drenagem",
    "Construção de centro esportivo",
    "Aquisição de ônibus para transporte escolar",
    "Iluminação pública em LED",
    "Revitalização de praça pública",
    "Construção de creche municipal",
    "Ampliação de rede de água e esgoto",
    "Reforma de centro comunitário",
    "Aquisição de viaturas policiais",
    "Implantação de câmeras de segurança",
    "Construção de ponte sobre córrego",
    "Recuperação de estradas vicinais",
    "Compra de ambulâncias",
    "Implantação de ciclovia",
    "Construção de quadra poliesportiva coberta",
    "Aquisição de computadores para escolas",
]


def seed_all():
    # Create tables
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()

    try:
        # Check idempotency
        if db.query(Deputy).count() > 0:
            print("Database already seeded, skipping.")
            return

        print("Seeding deputies...")
        deputies = []
        for row in DEPUTIES_DATA:
            name, party, votes, reg, ranking, is_sub, mandates, photo = row
            d = Deputy(
                name=name,
                party=party,
                votes_2022=votes,
                registration=reg,
                ranking=ranking,
                is_substitute=is_sub,
                mandates=mandates,
                photo_url=photo if photo else None,
            )
            db.add(d)
            deputies.append(d)
        db.flush()

        print("Seeding mayors and municipalities...")
        mayors = []
        for m_data in MAYORS_DATA:
            name, party, ts, te = m_data
            mayor = Mayor(name=name, party=party, term_start=ts, term_end=te)
            db.add(mayor)
            mayors.append(mayor)
        db.flush()

        municipalities = []
        for i, (mname, region, pop, lat, lng) in enumerate(MUNICIPALITIES_DATA):
            mun = Municipality(
                name=mname,
                region=region,
                population=pop,
                lat=lat,
                lng=lng,
                mayor_id=mayors[i].id,
            )
            db.add(mun)
            municipalities.append(mun)
        db.flush()

        print("Seeding secretariats...")
        secretariats = []
        for name, acronym, emoji, sec_name, party, executives in SECRETARIATS_DATA:
            s = Secretariat(
                name=name,
                acronym=acronym,
                emoji=emoji,
                secretary_name=sec_name,
                party=party,
                executives=executives,
            )
            db.add(s)
            secretariats.append(s)
        db.flush()

        print("Seeding programs...")
        programs = []
        for (pname, pdesc, sec_idx, yr_start, yr_end, budget, status) in PROGRAMS_DATA:
            sec = secretariats[sec_idx - 1] if sec_idx else None
            p = Program(
                name=pname,
                description=pdesc,
                secretariat_id=sec.id if sec else None,
                year_start=yr_start,
                year_end=yr_end,
                total_budget=budget,
                status=status,
            )
            db.add(p)
            programs.append(p)
        db.flush()

        print("Seeding budget items...")
        random.seed(42)
        categories = ["dotacao", "empenhado", "liquidado", "pago"]
        ratios = {"dotacao": 1.0, "empenhado": 0.88, "liquidado": 0.82, "pago": 0.75}

        for sec in secretariats:
            base = BUDGET_BASES.get(sec.acronym, 5.0) * 1_000_000_000
            for year in range(2022, 2026):
                year_factor = 1 + (year - 2022) * 0.05
                for cat in categories:
                    value = base * year_factor * ratios[cat] * (1 + random.uniform(-0.03, 0.03))
                    item = BudgetItem(
                        secretariat_id=sec.id,
                        year=year,
                        category=cat,
                        value=round(value, 2),
                        description=f"Execução orçamentária {year} - {cat}",
                    )
                    db.add(item)

        # Budget items per mayor/municipality
        for i, mayor in enumerate(mayors):
            for year in range(2023, 2026):
                for cat in categories:
                    base_val = random.uniform(5_000_000, 80_000_000)
                    value = base_val * ratios[cat]
                    item = BudgetItem(
                        mayor_id=mayor.id,
                        year=year,
                        category=cat,
                        value=round(value, 2),
                        description=f"Repasse municipal {year} - {cat}",
                    )
                    db.add(item)

        print("Seeding amendments...")
        statuses = ["aprovada", "pendente", "executada"]
        status_weights = [0.3, 0.25, 0.45]

        random.seed(99)
        amendment_combinations = set()
        count = 0
        while count < 80:
            dep = random.choice(deputies)
            mun = random.choice(municipalities)
            year = random.randint(2023, 2025)
            key = (dep.id, mun.id, year)
            if key in amendment_combinations:
                continue
            amendment_combinations.add(key)
            status = random.choices(statuses, weights=status_weights)[0]
            value = round(random.uniform(500_000, 5_000_000), 2)
            desc = random.choice(AMENDMENT_DESCRIPTIONS)
            am = Amendment(
                deputy_id=dep.id,
                municipality_id=mun.id,
                year=year,
                value=value,
                description=desc,
                status=status,
            )
            db.add(am)
            count += 1

        db.commit()
        print("Seeding complete!")

    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_all()
