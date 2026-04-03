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
from app.models import Base, Deputy, Municipality, Mayor, Amendment, Secretariat, BudgetItem, Program, GoalGroup, Meta

# ---------------------------------------------------------------------------
# Raw data — ALESP 35ª Legislatura (2023-2027)
# Fonte: votos/ranking = TSE/SP (02/10/2022)
#        matriculas/fotos/partidos = API ALESP legis-backend (estado em abr/2026)
# Nota: partidos refletem o estado atual (pós migrações pós-eleição)
# (name, party, votes_2022, registration, ranking, is_substitute, mandates, photo_url)
# ---------------------------------------------------------------------------
DEPUTIES_DATA = [
    ("Eduardo Suplicy", "PT", 807015, 300693, 1, False, 2, "/biografia/fotos/20230321-191506-id=987-GRD.jpg"),
    ("Carlos Giannazi", "PSOL", 276811, 300485, 2, False, 5, "/biografia/fotos/20230321-191048-id=148-GRD.jpg"),
    # fotos ALESP confirmadas via API legis-backend
    ("Paula da Bancada Feminista", "PSOL", 259771, 300678, 3, False, 1, "/biografia/fotos/20230321-110413-id=1635-GRD.jpg"),
    ("Bruno Zambelli", "PL", 235305, 300660, 4, False, 1, "/biografia/fotos/20230511-162900-id=1644-GRD.jfif"),
    ("Major Mecca", "PL", 224462, 300633, 5, False, 2, "/biografia/fotos/20230322-111405-id=521-GRD.jpeg"),
    # Tomé Abduch: migrou PP→REPUBLICANOS após eleição
    ("Tomé Abduch", "REPUBLICANOS", 221656, 300688, 6, False, 1, "/biografia/fotos/300688/dffe0759f4d72645639b028e1e5d4f636aeb1b809f61075ffd78ac589a7ac1a5.jpeg"),
    ("André do Prado", "PL", 216268, 300497, 7, False, 4, "/biografia/fotos/300497/2f42bf3f57458a3a37942214178dfc3d890395c8884ceb9979a0aea6f0a1850c.jpeg"),
    ("Tenente Coimbra", "PL", 209705, 300646, 8, False, 2, "/biografia/fotos/20230807-151348-id=506-GRD.jpg"),
    ("Delegado Olim", "PP", 201348, 300543, 9, False, 3, "/biografia/fotos/20230321-191240-id=263-GRD.jpg"),
    ("Ana Carolina Serra", "CIDADANIA", 198698, 300657, 10, False, 1, "/biografia/fotos/20230315-163915-id=1622-GRD.jpeg"),
    ("Milton Leite Filho", "UNIÃO", 198429, 300483, 11, False, 5, "/biografia/fotos/300483/2ccb4033061c8591a60f18d05a9a3d0c4a172a769cb92e198789e1f9dc05fbf4.jpeg"),
    ("Gil Diniz Bolsonaro", "PL", 196215, 300670, 12, False, 1, "/biografia/fotos/20230321-130525-id=1650-GRD.jpg"),
    ("Bruna Furlan", "PSDB", 195436, 300659, 13, False, 1, "/biografia/fotos/20230315-170525-id=1641-GRD.jpeg"),
    ("Conte Lopes", "PL", 192454, 300205, 14, False, 8, "/biografia/fotos/20230316-173502-id=180-GRD.jpg"),
    # Itamar Borges: 1º mandato (2023) — foto Nov/2019 era de outro deputado; exibe inicial
    ("Itamar Borges", "MDB", 183480, 300625, 15, False, 1, ""),
    # Marcos Damasio: matrícula corrigida (era 300638 que pertence a Paulo Fiorilo)
    ("Marcos Damasio", "PL", 183219, 300552, 16, False, 3, "/biografia/fotos/20230321-192550-id=283-GRD.jpg"),
    ("Carlos Cezar", "PL", 180690, None, 17, False, 1, ""),
    ("Carla Morando", "PSDB", 177773, 300614, 18, False, 2, "/biografia/fotos/20230315-142108-id=540-GRD.jpeg"),
    ("Jorge Wilson Xerife do Consumidor", "REPUBLICANOS", 177614, 300627, 19, False, 2, "/biografia/fotos/300627/66d82bc48da44e2c5448551d036be98f99cfd27fb168bb98f10282156ae1b532.jpeg"),
    ("Ediane Maria", "PSOL", 175617, 300667, 20, False, 1, "/biografia/fotos/20230427-144843-id=1654-GRD.jpg"),
    ("Marta Costa", "PSD", 170541, 300533, 21, False, 3, "/biografia/fotos/20191112-192923-id=284-GRD.png"),
    ("Emídio de Souza", "PT", 157834, 300395, 22, False, 5, "/biografia/fotos/20230315-145500-id=517-GRD.jpg"),
    ("Professora Bebel", "PT", 155983, 300640, 23, False, 2, "/biografia/fotos/300640/5792a9cebeacc3b58d496afab642a82010316b056eed3885ae11642bd7932177.jpeg"),
    # Guto Zacarias: foto Nov/2019 (id=530) confirmada errada pelo usuário; exibe inicial
    ("Guto Zacarias", "MISSÃO", 152481, 300624, 24, False, 2, ""),
    ("Gerson Pessoa", "PODE", 143704, None, 25, False, 1, ""),
    ("Enio Tatto", "PT", 142785, 300440, 26, False, 6, "/biografia/fotos/20191112-192019-id=175-GRD.jpg"),
    ("Luiz Fernando T. Ferreira", "PT", 141017, 300545, 27, False, 3, "/biografia/fotos/300545/b25d811e25a8378431dcab7c7b0e4fdb0e0a4989c68c339ba40d03c99abc2019.jpeg"),
    # Rogério Nogueira: migrou PSDB→PSD após eleição
    ("Rogério Nogueira", "PSD", 139756, 300407, 28, False, 6, "/biografia/fotos/20230714-155311-id=71-GRD.jpeg"),
    # Oseias de Madureira: migrou REPUBLICANOS→PL após eleição
    ("Oseias de Madureira", "PL", 137205, 300677, 29, False, 1, "/biografia/fotos/300677/d7b9c3790c2d86c4d225e4738159cf265eb2171b3a09716a53e1430af558316e.jpeg"),
    ("Valeria Bolsonaro", "PL", 131557, 300649, 30, False, 2, "/biografia/fotos/20230321-201012-id=503-GRD.png"),
    ("Lucas Bove", "PL", 130451, 300676, 31, False, 1, "/biografia/fotos/20230315-170418-id=1640-GRD.jpg"),
    ("Edmir Chedid", "PSD", 129097, None, 32, False, 1, ""),
    # Thiago Auricchio: migrou PSD→PL; matrícula corrigida (era 300508)
    ("Thiago Auricchio", "PL", 123483, 300648, 33, False, 2, "/biografia/fotos/20230329-180406-id=504-GRD.jpg"),
    ("Vinícius Camarinha", "PSB", 123316, 300655, 34, False, 2, "/biografia/fotos/20230315-171601-id=538-GRD.jpg"),
    # Maurici: migrou MDB→PT; foto hash correta (era id=529 de Itamar Borges)
    ("Maurici", "PT", 121455, 300653, 35, False, 2, "/biografia/fotos/300653/be0fae4ebcffd81468e3e343b158bf55482cc405ffaebbff06fbaf3433ffe098.jpeg"),
    # Rafael Silva: migrou REPUBLICANOS→PSD; 8 mandatos
    ("Rafael Silva", "PSD", 118182, 300344, 36, False, 8, "/biografia/fotos/300344/ac72cd78bf495cae533e7d143278c7085ea0cd64991bc9bb0117d7a60a85bcd9.jpeg"),
    # Paulo Fiorilo: matrícula corrigida (era 300471); foto atualizada
    ("Paulo Fiorilo", "PT", 110251, 300638, 37, False, 2, "/biografia/fotos/300638/8724f840684b834e46bb3550cdab9150d23eab9003b2bc6a65ba12320235895a.jpeg"),
    ("Reis", "PT", 108726, 300681, 38, False, 1, "/biografia/fotos/20230321-195741-id=1632-GRD.png"),
    ("Márcia Lia", "PT", 108587, 300534, 39, False, 3, "/biografia/fotos/20230802-131346-id=281-GRD.jpg"),
    ("Barba", "PT", 108071, 300584, 40, False, 3, "/biografia/fotos/300584/68f2d1366ca992ccd95727bfdd789c4b19fce86054251c888c7ca23342f3e448.jpeg"),
    ("Mônica do Movimento Pretas", "PSOL", 106781, 300637, 41, False, 2, "/biografia/fotos/300637/33861a85d3642f45442e3d20ccb2f7b97634d8b79ca8995492740c8ee237e5f6.jpeg"),
    ("Carlão Pignatari", "PSD", 105245, 300499, 42, False, 4, "/biografia/fotos/300499/9717fd9e32cdb65c43f9558978d7a440bc407b053773de388c2f6f345989eba6.jpeg"),
    ("Caio França", "PSB", 105173, 300540, 43, False, 3, "/biografia/fotos/20230321-190741-id=267-GRD.jpg"),
    ("Sebastião Santos", "REPUBLICANOS", 104374, 300520, 44, False, 4, "/biografia/fotos/20230321-200423-id=95-GRD.png"),
    ("Altair Moraes", "REPUBLICANOS", 98515, 300609, 45, False, 2, "/biografia/fotos/20230315-141411-id=545-GRD.jpeg"),
    # Rafael Saraiva: matrícula corrigida (era 300651); foto atualizada
    ("Rafael Saraiva", "UNIÃO", 98070, 300680, 46, False, 1, "/biografia/fotos/20230315-165421-id=1633-GRD.jpeg"),
    ("Gilmaci Santos", "REPUBLICANOS", 96361, 300671, 47, False, 1, "/biografia/fotos/20230315-170849-id=1649-GRD.jpeg"),
    ("Agente Federal Danilo Balas", "PL", 94552, 300607, 48, False, 2, "/biografia/fotos/300607/678129ff534ded49f5d96881ab26868b6170b40819639502898b48ee6030c787.jpeg"),
    ("Dirceu Dalben", "PSD", 93397, 300650, 49, False, 2, "/biografia/fotos/20230324-122116-id=561-GRD.png"),
    ("Rui Alves", "REPUBLICANOS", 91717, None, 50, False, 1, ""),
    ("Thainara Faria", "PT", 91388, 300687, 51, False, 1, "/biografia/fotos/300687/54bcd424e77bc8078e63e9e27ace179e7b56ba04fcc11fd917b82cc2d26b26bf.jpeg"),
    ("Leonardo Siqueira", "NOVO", 90688, 300675, 52, False, 1, "/biografia/fotos/20230321-192007-id=1642-GRD.png"),
    # Ricardo Madalena: matrícula corrigida (era 300703); foto atualizada
    ("Ricardo Madalena", "PL", 90630, 300539, 53, False, 3, "/biografia/fotos/20230426-174701-id=288-GRD.jfif"),
    ("Leci Brandão", "PCdoB", 90496, 300513, 54, False, 4, "/biografia/fotos/20230718-161931-id=38-GRD.jpg"),
    ("Felipe Franco", "UNIÃO", 90440, 300622, 55, False, 1, "/biografia/fotos/20200819-200938-id=532-GRD.jpeg"),
    ("Analice Fernandes", "PSD", 90135, 300431, 56, False, 6, "/biografia/fotos/300431/69142319ee3fc052a205d625527ba5a8de9faa52aa1b643a8b3c0f41f886e1a7.jpeg"),
    ("Andréa Werner", "PSB", 88820, 300658, 57, False, 1, "/biografia/fotos/300658/ec8711d9e474223bd1fdb27dbaff6fb7cab4ecb03d9f34023706fb4734e2868d.jpeg"),
    ("Donato", "PT", 88022, 300664, 58, False, 1, "/biografia/fotos/20230321-130104-id=1655-GRD.png"),
    ("Barros Munhoz", "PSD", 86372, 300188, 59, False, 7, "/biografia/fotos/300188/c5f99a2bc1c4d2dfe5d72c8a24e6b9a242b03d5b61314284be308fee932813a6.jpeg"),
    ("Paulo Mansur", "PL", 86201, 300679, 60, False, 1, "/biografia/fotos/20230321-195508-id=1634-GRD.jpg"),
    ("Marina Helou", "REDE", 85517, 300636, 61, False, 2, "/biografia/fotos/20230302-154543-id=518-GRD.jpg"),
    ("Marcio Nakashima", "PSD", 85195, 300635, 62, False, 2, "/biografia/fotos/300635/e9bff5d91c252b6c5055f1d7e8fc6742223d6af479becb1f88a008887e4df549.jpeg"),
    ("Capitão Telhada", "PP", 83438, 300661, 63, False, 1, "/biografia/fotos/20230315-173219-id=1648-GRD.png"),
    ("Edna Macedo", "REPUBLICANOS", 82932, 300318, 64, False, 4, "/biografia/fotos/20190315-152242-id=516-GRD.jpeg"),
    # Jorge Caruso: 1º mandato (2023) — foto Nov/2019 era de outro deputado; exibe inicial
    ("Jorge Caruso", "MDB", 82209, 300626, 65, False, 1, ""),
    ("Léo Oliveira", "MDB", 82145, 300264, 66, False, 5, "/biografia/fotos/300264/4480e5e51c390cae6caaa26e6692a785b08df07ff7caaed48d4a351f44e60171.jpeg"),
    ("Dr. Jorge do Carmo", "PT", 82054, 300623, 67, False, 2, "/biografia/fotos/20190315-162558-id=531-GRD.jpg"),
    # Solange Freitas: migrou PSD→UNIÃO
    ("Solange Freitas", "UNIÃO", 81870, 300686, 68, False, 1, "/biografia/fotos/20230619-135455-id=1626-GRD.png"),
    ("Daniel Soares", "UNIÃO", 81753, 300619, 69, False, 2, "/biografia/fotos/20230315-142647-id=535-GRD.jpg"),
    ("Dani Alonso", "PL", 80337, 300663, 70, False, 1, "/biografia/fotos/20230315-171350-id=1653-GRD.jpeg"),
    ("Ana Perugini", "PT", 79061, 300466, 71, False, 3, "/biografia/fotos/20230320-180813-id=81-GRD.jpg"),
    # Mauro Bragato: migrou PSDB→PSD; matrícula 300098 (parlamentar histórico, 11 mandatos)
    ("Mauro Bragato", "PSD", 78142, 300098, 72, False, 11, "/biografia/fotos/20190315-144027-id=87-GRD.jpeg"),
    ("Helinho Zanatta", "MDB", 77550, None, 73, False, 1, ""),
    # Rafa Zimbaldi: migrou CIDADANIA→UNIÃO; matrícula corrigida (era 300492)
    ("Rafa Zimbaldi", "UNIÃO", 76910, 300641, 74, False, 2, "/biografia/fotos/300641/a71cdcd1beaa217117340266ae9c98adb952dae5520a9bb94a63d01f000f4baf.jpeg"),
    ("Rogério Santos", "MDB", 76602, 300683, 75, False, 1, "/biografia/fotos/20230315-165052-id=1630-GRD.jpg"),
    ("Rodrigo Moraes", "PL", 75094, 300519, 76, False, 4, "/biografia/fotos/300519/4191e426b16ca3c439c3ee9fc27a611f644d778c805f21a9b741d657377076e9.jpeg"),
    ("Rômulo Fernandes", "PT", 75033, 300684, 77, False, 1, "/biografia/fotos/300684/12597211b0cb0c6f4ab9d7d0e068a38610b210692edda9758cd9118b8d798073.jpeg"),
    ("Alex Madureira", "PL", 74340, 300608, 78, False, 2, "/biografia/fotos/20230302-145402-id=546-GRD.jpg"),
    ("Luiz Claudio Marcolino", "PT", 70487, 300514, 79, False, 2, "/biografia/fotos/20230529-131249-id=1637-GRD.jpeg"),
    ("Delegada Graciela", "PL", 68955, 300620, 80, False, 2, "/biografia/fotos/300620/b725bb9f2b1a490e2e6b490ae913be604ec542b36f1375ded387ba72d391e184.jpeg"),
    ("Letícia Aguiar", "PL", 68556, 300631, 81, False, 2, "/biografia/fotos/20230315-150330-id=523-GRD.jpg"),
    # Maria Lucia Amary: migrou PSDB→PSD; matrícula 300415 (6 mandatos)
    ("Maria Lucia Amary", "PSD", 66956, 300415, 82, False, 6, "/biografia/fotos/300415/3f7d0ec72a40338819e60ab5285a10f7ba1940272878a742e14054cf0e420866.jpeg"),
    ("Fabiana Bolsonaro", "PL", 65497, 300668, 83, False, 1, ""),
    ("Beth Sahão", "PT", 65407, 300435, 84, False, 6, "/biografia/fotos/20230317-110718-id=31-GRD.jpeg"),
    ("Ricardo França", "PODE", 64175, 300682, 85, False, 1, "/biografia/fotos/300682/6e3a648bae583eebc11b13e0955f7105566a8ca3291620dc85be8ce114583717.jpeg"),
    ("Paulo Corrêa Jr", "REPUBLICANOS", 62239, 300536, 86, False, 3, "/biografia/fotos/300536/57790d967b293e30c5be2f49ba2949baf359017c07a783f12a05c1ea24cd21c3.jpeg"),
    ("Simão Pedro", "PT", 59785, 300511, 87, False, 4, "/biografia/fotos/20230315-165428-id=148-GRD.jpg"),
    ("Clarice Ganem", "PODE", 59342, 300662, 88, False, 1, "/biografia/fotos/300662/d9362d62e29435984b085411f9c8dd4f482f95db5b129c476778773a9d4a0cd8.jpeg"),
    ("Atila Jacomussi", "UNIÃO", 58707, 300537, 89, False, 2, "/biografia/fotos/20230315-170109-id=265-GRD.jpg"),
    # Vitão do Cachorrão: migrou REPUBLICANOS→PODE
    ("Vitão do Cachorrão", "PODE", 56729, 300689, 90, False, 1, "/biografia/fotos/300689/73aa4cf331fcbaa58dd1540efae714f861c56f5708979f153f2ad4ec32d86d7b.jpeg"),
    ("Dr. Eduardo Nóbrega", "PODE", 53607, 300665, 91, False, 1, "/biografia/fotos/20230315-171633-id=1657-GRD.jpg"),
    ("Dr. Valdomiro Lopes", "PSB", 50824, 300396, 92, False, 4, "/biografia/fotos/20230315-164216-id=1623-GRD.jpeg"),
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


# ---------------------------------------------------------------------------
# Programa de Metas — dados simulados baseados no monitoramento2023.sp.gov.br
# 260 metas | 12 objetivos | 3 eixos | prioridade A/B/C
# Status real extraído do screenshot: Em andamento=151, Em alerta=30,
#   Atrasado=28, Alcançado=10, Evento a confirmar=41
# ---------------------------------------------------------------------------

# Eixos (Pillars)
PILLAR_DIGNIDADE = "Dignidade e Comprometimento"
PILLAR_DESENVOLVIMENTO = "Desenvolvimento e Técnica"
PILLAR_DIALOGO = "Diálogo e Inovação"

# 12 Goal Groups: (number, name, pillar, n_metas, n_em_andamento, n_alerta, n_atrasado, n_alcancado, n_evento)
# Counts extraídos do screenshot
GOAL_GROUPS_DATA = [
    (1, "Educação Pública com Efetividade, Qualidade e Acesso Ampliados", PILLAR_DIGNIDADE,
     12, 12, 0, 0, 0, 0),
    (2, "Saúde Pública com Maior Acesso, Qualidade, Resolutividade e Tecnologia", PILLAR_DIGNIDADE,
     11, 9, 1, 1, 0, 0),
    (3, "Segurança Pública Fortalecida e Integrada para uma Sociedade Protegida", PILLAR_DIGNIDADE,
     31, 18, 4, 1, 2, 6),
    (4, "Menor Vulnerabilidade Social, com Redução da Pobreza e de Pessoas em Situação de Rua", PILLAR_DIGNIDADE,
     11, 9, 1, 1, 0, 0),
    (5, "Infraestrutura e Mobilidade Urbana Expandidas", PILLAR_DESENVOLVIMENTO,
     46, 12, 11, 15, 4, 4),
    (6, "Moradia Digna com Expansão da Regularização Fundiária, Revitalização e Reurbanização", PILLAR_DESENVOLVIMENTO,
     5, 1, 1, 3, 0, 0),
    (7, "Meio Ambiente e Recursos Naturais Preservados, com Garantia de Integridade e Equilíbrio", PILLAR_DESENVOLVIMENTO,
     28, 13, 3, 12, 0, 0),
    (8, "Setor Produtivo Competitivo e Empreendedorismo Fortalecido", PILLAR_DIALOGO,
     33, 27, 2, 2, 2, 0),
    (9, "Agronegócio com Produção Diversificada e Atrelado à Sustentabilidade", PILLAR_DIALOGO,
     13, 10, 3, 0, 0, 0),
    (10, "Turismo, Esporte, Cultura e Economia Criativa Aliados ao Desenvolvimento e ao Futuro", PILLAR_DIALOGO,
     29, 20, 3, 1, 5, 0),
    (11, "Governo Digital, Transparente, Ético, Técnico e Focado na Excelência dos Serviços", PILLAR_DIALOGO,
     34, 16, 2, 7, 4, 5),  # corrigido: 16+2+7+4+5=34
    (12, "Política Fiscal e Tributária com Disciplina, Equilíbrio e Eficiência", PILLAR_DIALOGO,
     7, 4, 0, 1, 1, 1),  # restante para totalizar 260
]

# Mapeamento objetivo → secretaria-index (1-based dos SECRETARIATS_DATA)
# SEDUC=1 SES=2 SSP=3 SEDS=4 SEMIL=5 SEHAB=6 SEMIL=7/5 SDE=8 SAA=9 SEC=10 SG=11/20 SEFAZ=12
OBJ_TO_SEC = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 5, 8: 8, 9: 9, 10: 10, 11: 20, 12: 4}

# Templates de meta por objetivo (descrições realistas)
META_TEMPLATES = {
    1: [  # Educação
        ("Ampliar o número de matrículas na educação integral", "unidades", 500000, 487000, "2026-12", "A"),
        ("Construir e reformar escolas estaduais", "unidades", 400, 312, "2026-06", "A"),
        ("Implementar sistema de avaliação de aprendizagem", "%", 100, 95, "2025-12", "B"),
        ("Reduzir o abandono escolar no ensino médio", "%", 10, 8.5, "2026-12", "A"),
        ("Capacitar professores em metodologias ativas", "profissionais", 80000, 71000, "2026-06", "B"),
        ("Expandir acesso a tecnologia nas escolas públicas", "unidades", 1200, 980, "2026-12", "A"),
        ("Aumentar índice IDESP no ensino fundamental", "índice", 4.5, 4.2, "2026-12", "B"),
        ("Implantar centros de formação profissional", "unidades", 30, 22, "2025-12", "B"),
        ("Garantir material didático a todos os alunos", "%", 100, 98, "2025-03", "A"),
        ("Expandir programa de alimentação escolar saudável", "escolas", 5000, 4800, "2025-12", "C"),
        ("Criar salas de recursos multifuncionais inclusivas", "unidades", 500, 430, "2026-06", "B"),
        ("Implementar jornada integral nas CEIs municipais", "CEIs", 200, 195, "2026-12", "B"),
    ],
    2: [  # Saúde
        ("Ampliar cobertura de atenção básica à saúde", "%", 95, 89, "2026-12", "A"),
        ("Reduzir filas de espera em procedimentos eletivos", "%", 30, 22, "2026-06", "A"),
        ("Construir e modernizar UPAs no estado", "unidades", 45, 38, "2026-12", "A"),
        ("Expandir vacinação infantil acima de 95%", "%", 95, 93, "2025-12", "A"),
        ("Implementar prontuário eletrônico unificado", "%", 100, 87, "2026-06", "B"),
        ("Ampliar serviços de saúde mental", "CAPS", 50, 41, "2026-12", "B"),
        ("Reduzir mortalidade materna no estado", "coeficiente", 35, 38, "2026-12", "A"),
        ("Aumentar transplantes de órgãos", "unidades", 5000, 4680, "2026-12", "B"),
        ("Ampliar cobertura de saúde bucal", "equipes", 2000, 1850, "2026-06", "B"),
        ("Fortalecer vigilância epidemiológica", "%", 100, 91, "2025-12", "B"),
        ("Expandir diagnóstico precoce de câncer", "exames", 200000, 185000, "2026-12", "A"),
    ],
    3: [  # Segurança
        ("Reduzir índice de homicídios no estado", "%", 20, 14, "2026-12", "A"),
        ("Integrar dados de inteligência das forças de segurança", "%", 100, 78, "2025-12", "A"),
        ("Ampliar monitoramento eletrônico de presos", "unidades", 20000, 17400, "2026-06", "A"),
        ("Construir novas unidades prisionais", "vagas", 8000, 5200, "2026-12", "B"),
        ("Implantar câmeras de vigilância inteligente", "câmeras", 10000, 7800, "2026-06", "B"),
        ("Reduzir crimes patrimoniais na capital", "%", 15, 9, "2026-12", "A"),
        ("Expandir policiamento comunitário", "batalhões", 30, 24, "2025-12", "B"),
        ("Modernizar armamento e viaturas da PM", "%", 100, 82, "2026-06", "A"),
        ("Implementar videomonitoramento integrado SINESP", "%", 100, 72, "2026-12", "B"),
        ("Reduzir letalidade policial", "%", 30, 18, "2026-12", "A"),
        ("Ampliar serviços de mediação de conflitos", "centros", 20, 14, "2025-12", "C"),
        ("Fortalecer combate ao crime organizado", "operações", 500, 412, "2026-12", "A"),
        ("Implantar sistema biométrico nas penitenciárias", "%", 100, 68, "2026-06", "B"),
        ("Ampliar ressocialização com educação em presídios", "%", 40, 28, "2026-12", "B"),
        ("Reduzir reincidência criminal", "%", 10, 6, "2026-12", "B"),
        ("Criar delegacias especializadas em crimes digitais", "unidades", 15, 9, "2025-12", "B"),
        ("Ampliar investigação de crimes ambientais", "delegacias", 10, 7, "2026-12", "C"),
        ("Implementar central de monitoramento 24h", "centrais", 5, 4, "2025-06", "A"),
        ("Expandir guarda civil metropolitana", "agentes", 5000, 3800, "2026-12", "B"),
        ("Integrar banco de dados de mandados de prisão", "%", 100, 84, "2025-12", "A"),
        ("Fortalecer policiamento nas fronteiras estaduais", "postos", 20, 15, "2026-06", "B"),
        ("Ampliar combate ao trabalho escravo", "fiscalizações", 200, 162, "2026-12", "B"),
        ("Instalar sistemas antidrone em presídios", "unidades", 50, 29, "2026-06", "A"),
        ("Reduzir suicídio entre servidores PM/PC", "%", 20, 9, "2026-12", "C"),
        ("Criar centro de inteligência policial SP", "centros", 1, 1, "2024-06", "A"),
        ("Modernizar IML e perícias oficiais", "unidades", 20, 14, "2026-12", "B"),
        ("Implantar boletim de ocorrência online 24h", "%", 100, 92, "2024-12", "A"),
        ("Ampliar proteção às mulheres vítimas de violência", "casas-abrigo", 30, 22, "2026-12", "A"),
        ("Fortalecer Conselho de Segurança públicos locais", "conselhos", 200, 145, "2025-12", "C"),
        ("Expandir rede de proteção à criança e adolescente", "centros", 25, 17, "2026-06", "B"),
        ("Instalar câmeras em uniformes (body cam) PM", "unidades", 20000, 12000, "2026-12", "A"),
    ],
    4: [  # Vulnerabilidade Social
        ("Ampliar transferência de renda a famílias vulneráveis", "famílias", 300000, 278000, "2026-12", "A"),
        ("Erradicar situação de rua na capital", "%", 50, 28, "2026-12", "A"),
        ("Construir centros de acolhimento para moradores de rua", "vagas", 5000, 3800, "2026-12", "A"),
        ("Ampliar cobertura do SUAS no estado", "%", 95, 89, "2025-12", "B"),
        ("Fortalecer rede de proteção a idosos", "centros", 100, 82, "2026-06", "B"),
        ("Ampliar serviços de apoio a crianças vulneráveis", "CRAS", 50, 42, "2025-12", "A"),
        ("Reduzir trabalho infantil no estado", "%", 30, 21, "2026-12", "B"),
        ("Implementar sistema de busca ativa de beneficiários", "%", 100, 87, "2025-12", "A"),
        ("Expandir acesso à assistência social em municípios", "municípios", 600, 548, "2025-12", "B"),
        ("Fortalecer proteção à pessoa com deficiência", "beneficiários", 50000, 44000, "2026-12", "B"),
        ("Ampliar banco de alimentos e combate ao desperdício", "toneladas", 5000, 4200, "2026-12", "C"),
    ],
    5: [  # Infraestrutura
        ("Duplicar rodovias estaduais prioritárias", "km", 500, 198, "2026-12", "A"),
        ("Conservar malha rodoviária estadual", "km", 15000, 12800, "2025-12", "A"),
        ("Ampliar capacidade dos aeroportos regionais", "passageiros/ano", 5000000, 3200000, "2026-12", "B"),
        ("Expandir metro na RMSP — Linha 2 Verde", "km", 14, 6, "2027-06", "A"),
        ("Expandir metro na RMSP — Linha 6 Laranja", "km", 15, 8, "2027-12", "A"),
        ("Entregar obras do VLT — Linha 18 Bronze", "km", 13, 2, "2028-12", "A"),
        ("Ampliar Trem Intercidades SP-Campinas", "km", 180, 0, "2028-12", "A"),
        ("Recuperar pontes e viadutos em risco", "unidades", 200, 142, "2026-06", "A"),
        ("Ampliar acesso à internet banda larga no interior", "municípios", 400, 280, "2026-12", "B"),
        ("Expandir rede de ciclovias integradas ao metro", "km", 200, 128, "2025-12", "B"),
        ("Implantar corredor de BRT prioritário", "km", 80, 31, "2026-12", "A"),
        ("Ampliar saneamento básico em municípios", "municípios", 200, 148, "2026-12", "A"),
        ("Universalizar tratamento de esgoto no estado", "%", 100, 82, "2026-12", "A"),
        ("Ampliar abastecimento d'água em baixada santista", "%", 100, 89, "2025-12", "A"),
        ("Construir novas barragens de contenção de cheias", "unidades", 10, 3, "2028-12", "B"),
        ("Readequar terminais rodoviários intermunicipais", "terminais", 50, 32, "2026-06", "B"),
        ("Concluir rodoanel trecho norte", "km", 45, 8, "2028-12", "A"),
        ("Ampliar capacidade portuária em Santos", "%", 30, 12, "2028-12", "A"),
        ("Instalar iluminação LED nas rodovias estaduais", "km", 3000, 1920, "2025-12", "B"),
        ("Implantar pesagem virtual de caminhões", "postos", 40, 28, "2025-06", "B"),
        ("Recuperar estradas vicinais no interior", "km", 5000, 3400, "2026-06", "B"),
        ("Ampliar parque tecnológico em São José dos Campos", "%", 100, 48, "2026-12", "B"),
        ("Completar obras do Contorno de Ribeirão Preto", "km", 25, 7, "2027-06", "A"),
        ("Implantar sistema de pedágio por km rodado", "praças", 50, 12, "2027-12", "B"),
        ("Ampliar capacidade de energia renovável no estado", "GW", 2, 0.8, "2026-12", "B"),
        ("Digitalizar plantas de infraestrutura hídrica", "%", 100, 62, "2025-12", "C"),
        ("Instalar semáforos inteligentes na capital", "cruzamentos", 1000, 580, "2025-12", "B"),
        ("Ampliar faixas expressas dinâmicas na Marginal", "km", 20, 8, "2025-06", "B"),
        ("Recuperar patrimônio histórico de infraestrutura", "bens", 30, 18, "2026-12", "C"),
        ("Ampliar conectividade 5G em municípios do interior", "municípios", 100, 42, "2026-12", "B"),
        ("Implantar centro de controle operacional ferroviário", "unidades", 1, 0, "2027-12", "A"),
        ("Expandir rede de carregamento de veículos elétricos", "pontos", 500, 180, "2026-12", "B"),
        ("Modernizar gestão hídrica com IoT", "%", 100, 38, "2026-12", "B"),
        ("Ampliar estações de tratamento de resíduos sólidos", "unidades", 20, 8, "2027-06", "B"),
        ("Concluir construção do Arco Metropolitano de SP", "km", 100, 14, "2028-12", "A"),
        ("Implantar sistema de travessias seguras em rodovias", "travessias", 300, 198, "2025-12", "B"),
        ("Digitalizar processos de licenciamento de obras", "%", 100, 74, "2025-06", "C"),
        ("Ampliar dragagem de rios e córregos na RMSP", "km", 200, 98, "2026-06", "A"),
        ("Implementar gestão de ativos rodoviários", "km", 20000, 8400, "2026-12", "B"),
        ("Ampliar programa de manutenção preventiva de pontes", "pontes", 500, 320, "2025-12", "B"),
        ("Expandir rede de terminais intermodais", "terminais", 15, 4, "2027-12", "B"),
        ("Concluir duplicação SP-055 (Rodovia dos Imigrantes)", "km", 30, 8, "2027-06", "A"),
        ("Implantar sistema de gestão de frotas oficiais", "%", 100, 68, "2025-12", "C"),
        ("Ampliar acesso à mobilidade em cidades médias", "cidades", 30, 18, "2026-12", "B"),
        ("Modernizar centros de controle de tráfego", "CCOs", 10, 6, "2025-12", "B"),
        ("Ampliar programa de conservação de pontes rurais", "pontes", 200, 124, "2025-06", "C"),
    ],
    6: [  # Moradia
        ("Construir unidades habitacionais de interesse social", "unidades", 30000, 8400, "2026-12", "A"),
        ("Regularizar assentamentos precários", "famílias", 50000, 19000, "2026-12", "A"),
        ("Urbanizar favelas em áreas de risco", "m²", 500000, 145000, "2026-12", "A"),
        ("Ampliar crédito habitacional popular", "contratos", 10000, 3800, "2026-06", "B"),
        ("Implementar programa de locação social", "unidades", 5000, 1200, "2026-12", "A"),
    ],
    7: [  # Meio Ambiente
        ("Reduzir desmatamento ilegal no estado", "%", 30, 12, "2026-12", "A"),
        ("Ampliar unidade de conservação ambiental", "ha", 50000, 18000, "2026-12", "B"),
        ("Recuperar áreas degradadas e matas ciliares", "ha", 10000, 3800, "2026-12", "B"),
        ("Expandir coleta seletiva de resíduos", "municípios", 500, 328, "2025-12", "B"),
        ("Reduzir emissão de GEE no setor de transporte", "%", 15, 6, "2026-12", "A"),
        ("Ampliar parques estaduais abertos à visitação", "parques", 20, 12, "2025-12", "B"),
        ("Implementar política estadual de carbono neutro", "%", 100, 42, "2026-12", "A"),
        ("Recuperar praias e rios com qualidade de banho", "%", 80, 58, "2026-12", "B"),
        ("Ampliar programas de educação ambiental", "municípios", 400, 248, "2025-12", "C"),
        ("Criar corredores ecológicos na Mata Atlântica", "km²", 200, 68, "2026-12", "A"),
        ("Reduzir queimadas no cerrado paulista", "%", 40, 15, "2026-12", "A"),
        ("Digitalizar licenciamento ambiental", "%", 100, 78, "2025-06", "B"),
        ("Ampliar reator de biogás em aterros", "unidades", 10, 3, "2027-06", "B"),
        ("Implementar sistema de monitoramento hídrico online", "%", 100, 48, "2026-06", "B"),
        ("Expandir áreas verdes em municípios do interior", "ha", 5000, 1980, "2026-12", "C"),
        ("Cadastrar nascentes no estado", "nascentes", 5000, 2100, "2025-12", "B"),
        ("Ampliar controle de poluição atmosférica na RMSP", "%", 20, 8, "2026-12", "A"),
        ("Desenvolver plano diretor de recursos hídricos", "%", 100, 62, "2025-12", "B"),
        ("Fortalecer fiscalização ambiental com drones", "equipes", 30, 14, "2025-12", "B"),
        ("Implantar ecopontos nos municípios do interior", "unidades", 200, 85, "2026-06", "C"),
        ("Ampliar gestão sustentável de resíduos industriais", "%", 80, 34, "2026-12", "B"),
        ("Recuperar rios degradados na bacia do Paraíba", "km", 100, 38, "2026-12", "A"),
        ("Reduzir poluição sonora nos centros urbanos", "%", 15, 5, "2026-12", "C"),
        ("Criar banco de sementes de espécies nativas", "espécies", 500, 210, "2026-12", "B"),
        ("Ampliar transição energética em secretarias", "%", 30, 9, "2026-12", "C"),
        ("Fortalecer consórcios intermunicipais de resíduos", "consórcios", 30, 12, "2026-06", "B"),
        ("Implementar sistema de qualidade da água em tempo real", "estações", 100, 48, "2025-12", "B"),
        ("Ampliar reflorestamento com espécies nativas", "mudas", 10000000, 4200000, "2026-12", "A"),
    ],
    8: [  # Setor Produtivo
        ("Atrair novos investimentos produtivos para o estado", "R$ bi", 50, 38, "2026-12", "A"),
        ("Reduzir burocracia para abertura de empresas", "dias", 1, 1, "2023-12", "A"),
        ("Ampliar acesso a crédito para MPMEs", "empresas", 100000, 87000, "2026-12", "A"),
        ("Expandir hubs de inovação no estado", "hubs", 20, 14, "2025-12", "B"),
        ("Aumentar exportações do agronegócio paulista", "%", 15, 10, "2026-12", "A"),
        ("Qualificar mão de obra para setores estratégicos", "pessoas", 300000, 248000, "2026-06", "A"),
        ("Implantar zonas de processamento export no interior", "ZPE", 3, 1, "2027-12", "B"),
        ("Ampliar parques industriais sustentáveis", "unidades", 10, 7, "2026-12", "B"),
        ("Fortalecer cadeias produtivas locais", "cadeias", 20, 16, "2025-12", "B"),
        ("Digitalizar processos de fiscalização tributária", "%", 100, 82, "2025-12", "B"),
        ("Atrair empresas de tecnologia para SP", "empresas", 200, 148, "2026-12", "A"),
        ("Implementar programa de internacionalização de empresas", "empresas", 500, 380, "2026-12", "B"),
        ("Ampliar programa Investe SP de simplificação", "%", 100, 78, "2025-12", "B"),
        ("Reduzir ICMS para setores estratégicos", "setores", 5, 4, "2024-12", "A"),
        ("Expandir economia circular no setor industrial", "%", 20, 14, "2026-12", "B"),
        ("Fortalecer cooperativismo e associativismo", "cooperativas", 200, 148, "2025-12", "C"),
        ("Ampliar microcrédito a empreendedores individuais", "MEIs", 50000, 41000, "2025-12", "B"),
        ("Criar programa estadual de startups", "startups", 100, 74, "2025-12", "B"),
        ("Expandir feiras de negócios internacionais", "eventos", 10, 8, "2026-12", "C"),
        ("Digitalizar câmaras de comércio no estado", "%", 100, 84, "2025-06", "C"),
        ("Ampliar infraestrutura de inovação nas universidades", "laboratórios", 30, 22, "2026-12", "B"),
        ("Estabelecer centro de arbitragem empresarial", "centros", 5, 4, "2024-12", "B"),
        ("Criar fundo de investimento em inovação SP", "R$ mi", 500, 420, "2026-12", "A"),
        ("Fortalecer arranjos produtivos locais", "APLs", 30, 24, "2025-12", "B"),
        ("Ampliar e-commerce para pequenos negócios", "empresas", 20000, 16000, "2025-12", "C"),
        ("Implementar certificação para economia verde", "empresas", 500, 320, "2026-12", "B"),
        ("Expandir energia para distritos industriais", "MWh", 500, 380, "2025-12", "A"),
        ("Criar central de inteligência de mercados", "unidades", 1, 1, "2024-06", "B"),
        ("Ampliar inclusão produtiva de jovens vulneráveis", "jovens", 50000, 38000, "2026-12", "A"),
        ("Fortalecer programa de qualificação industrial", "trabalhadores", 100000, 78000, "2025-12", "A"),
        ("Modernizar sistema de registros empresariais", "%", 100, 88, "2024-12", "B"),
        ("Criar selos de qualidade para produtos paulistas", "produtos", 50, 38, "2025-12", "C"),
        ("Ampliar acesso ao comércio nas periferias", "centros", 20, 14, "2026-12", "C"),
    ],
    9: [  # Agronegócio
        ("Ampliar irrigação em lavouras do interior", "ha", 100000, 78000, "2026-12", "A"),
        ("Certificar produtores rurais em boas práticas", "produtores", 50000, 41000, "2025-12", "B"),
        ("Expandir programa de crédito rural", "contratos", 30000, 25000, "2026-12", "A"),
        ("Ampliar pesquisa agropecuária no IAC e APTA", "%", 30, 22, "2026-12", "B"),
        ("Reduzir perdas pós-colheita no estado", "%", 20, 14, "2026-12", "B"),
        ("Digitalizar cadastro de propriedades rurais", "%", 100, 78, "2025-12", "B"),
        ("Ampliar rastreabilidade da carne bovina paulista", "%", 80, 62, "2026-06", "A"),
        ("Fortalecer sistemas de defesa agropecuária", "laboratórios", 10, 7, "2025-12", "B"),
        ("Expandir agricultura familiar certificada", "famílias", 20000, 16000, "2026-12", "A"),
        ("Ampliar acesso à água para o agro no semiárido paulista", "cisternas", 5000, 3800, "2025-12", "B"),
        ("Criar centro de excelência em agrotech", "centros", 3, 2, "2026-06", "A"),
        ("Fortalecer mercados orgânicos certificados", "produtores", 10000, 7800, "2026-12", "B"),
        ("Implementar monitoramento por satélite de lavouras", "%", 100, 68, "2026-12", "B"),
    ],
    10: [  # Turismo, Esporte, Cultura
        ("Aumentar turistas internacionais no estado", "milhões", 5, 3.8, "2026-12", "A"),
        ("Ampliar roteiros turísticos regionais certificados", "roteiros", 100, 72, "2025-12", "B"),
        ("Construir e reformar equipamentos esportivos", "unidades", 200, 148, "2026-12", "B"),
        ("Ampliar projetos culturais em municípios", "projetos", 500, 380, "2025-12", "B"),
        ("Restaurar patrimônio histórico tombado", "bens", 50, 38, "2026-12", "B"),
        ("Expandir Lei Paulo Gustavo — fomento cultural", "projetos", 1000, 920, "2024-12", "A"),
        ("Ampliar programas esportivos para jovens", "participantes", 500000, 420000, "2025-12", "A"),
        ("Criar centro de excelência esportiva", "centros", 5, 4, "2026-12", "B"),
        ("Fortalecer economia criativa no estado", "empresas", 2000, 1620, "2026-12", "B"),
        ("Ampliar festivais e eventos culturais", "eventos", 100, 82, "2025-12", "C"),
        ("Digitalizar acervos museológicos", "%", 100, 74, "2025-12", "B"),
        ("Expandir programas de leitura nas escolas", "alunos", 1000000, 820000, "2025-12", "A"),
        ("Fortalecer cinema e audiovisual paulista", "produções", 100, 78, "2026-12", "B"),
        ("Ampliar turismo de negócios em SP capital", "%", 20, 16, "2026-12", "B"),
        ("Criar museus interativos de ciência", "unidades", 5, 4, "2026-12", "B"),
        ("Expandir acesso à banda larga em pontos turísticos", "pontos", 200, 148, "2025-12", "C"),
        ("Ampliar programa de microcrédito para artistas", "artistas", 5000, 3800, "2025-12", "C"),
        ("Implantar tour virtual de patrimônios estaduais", "patrimônios", 50, 38, "2025-12", "C"),
        ("Fortalecer escolas públicas de artes e esportes", "escolas", 30, 24, "2026-12", "B"),
        ("Ampliar espaços de prática de esportes nas periferias", "espaços", 100, 80, "2026-06", "A"),
        ("Criar programa de artistas residentes", "artistas", 200, 148, "2025-12", "C"),
        ("Expandir museus regionais no interior", "museus", 10, 8, "2026-12", "B"),
        ("Ampliar financiamento do patrimônio cultural", "projetos", 200, 148, "2026-12", "B"),
        ("Fortalecer turismo comunitário e indígena", "comunidades", 30, 20, "2025-12", "C"),
        ("Realizar candidatura de SP para eventos olímpicos", "candidaturas", 1, 1, "2024-12", "A"),
        ("Ampliar publicidade do turismo paulista no exterior", "%", 50, 38, "2026-12", "B"),
        ("Criar fundo estadual de apoio ao cinema", "R$ mi", 50, 42, "2025-12", "B"),
        ("Fortalecer museus comunitários", "museus", 20, 14, "2026-12", "C"),
        ("Ampliar programa de sarau e cultura nas escolas", "escolas", 500, 380, "2025-12", "C"),
    ],
    11: [  # Governo Digital
        ("Digitalizar 100% de serviços ao cidadão", "%", 100, 74, "2026-12", "A"),
        ("Implantar identidade digital estadual", "usuários", 20000000, 14800000, "2025-12", "A"),
        ("Ampliar conectividade nos prédios públicos", "%", 100, 82, "2025-06", "B"),
        ("Implementar plataforma integrada de dados gov", "%", 100, 52, "2026-12", "A"),
        ("Criar lei estadual de proteção de dados LGPD", "%", 100, 100, "2023-06", "A"),
        ("Ampliar transparência nos contratos públicos", "%", 100, 88, "2024-12", "A"),
        ("Modernizar sistemas legados das secretarias", "%", 60, 28, "2026-12", "B"),
        ("Implementar IA em atendimento ao cidadão", "%", 100, 48, "2026-12", "B"),
        ("Criar centro de dados gov. soberano", "centros", 1, 0, "2027-06", "A"),
        ("Digitalizar processos de licitação", "%", 100, 84, "2025-06", "A"),
        ("Ampliar uso de open data no governo SP", "datasets", 1000, 620, "2026-12", "B"),
        ("Implantar assinatura digital em todos os atos", "%", 100, 92, "2024-12", "A"),
        ("Expandir rede de wi-fi gratuito em pontos públicos", "pontos", 1000, 580, "2026-06", "B"),
        ("Criar programa de formação em tecnologia para servidores", "servidores", 30000, 21000, "2025-12", "B"),
        ("Ampliar avaliação de desempenho de servidores", "%", 100, 72, "2025-12", "B"),
        ("Implementar ouvidoria digital integrada", "%", 100, 84, "2024-12", "A"),
        ("Reduzir tempo médio de atendimento gov", "dias", 5, 7, "2025-12", "A"),
        ("Criar programa anti-corrupção digital", "%", 100, 68, "2025-12", "A"),
        ("Ampliar auditoria digital de gastos públicos", "%", 100, 78, "2026-06", "B"),
        ("Digitalizar acervos históricos do estado", "%", 100, 48, "2026-12", "C"),
        ("Implementar GovTech incubadora no estado", "startups", 50, 34, "2025-12", "B"),
        ("Criar portal unificado de licitações SP", "%", 100, 92, "2024-06", "A"),
        ("Implantar sistema de gestão de talentos no governo", "%", 100, 58, "2026-12", "B"),
        ("Ampliar blockchain em registros públicos", "%", 30, 12, "2026-12", "B"),
        ("Desenvolver app único de serviços SP ao cidadão", "downloads", 5000000, 3800000, "2025-12", "A"),
        ("Fortalecer cibersegurança em infraestrutura crítica", "%", 100, 62, "2026-12", "A"),
        ("Ampliar uso de análise de dados para políticas públicas", "%", 70, 38, "2026-12", "B"),
        ("Criar programa de inclusão digital para idosos", "idosos", 500000, 320000, "2026-12", "B"),
        ("Implantar sistema de gestão de contratos Gov", "%", 100, 74, "2025-12", "B"),
        ("Expandir acesso a documentos cidadão via app", "%", 100, 88, "2024-12", "A"),
        ("Fortalecer ética e integridade no servidor público", "capacitados", 50000, 36000, "2025-12", "B"),
        ("Ampliar dados abertos na saúde e segurança", "datasets", 200, 148, "2025-12", "B"),
        ("Criar plataforma de participação cidadã online", "usuários", 500000, 280000, "2025-12", "B"),
        ("Implementar gestão por resultados no governo SP", "%", 100, 58, "2026-12", "A"),
    ],
    12: [  # Política Fiscal
        ("Reduzir dívida consolidada do estado SP", "%", 10, 6, "2026-12", "A"),
        ("Ampliar eficiência do sistema de arrecadação", "%", 15, 10, "2025-12", "A"),
        ("Modernizar o sistema tributário paulista", "%", 100, 68, "2026-12", "A"),
        ("Equilibrar resultado primário das contas públicas", "R$ bi superavit", 5, 3.8, "2026-12", "A"),
        ("Ampliar transparência fiscal municipal", "%", 100, 78, "2025-12", "B"),
        ("Reduzir contencioso tributário em 20%", "%", 20, 12, "2026-12", "B"),
        ("Implementar reforma da previdência estadual", "%", 100, 84, "2024-12", "A"),
    ],
}

# flags realistas por objetivo
FLAGS_BY_OBJ = {
    1: {"100d": True, "est": True, "folha": True, "int": False, "cap": True, "infra": False},
    2: {"100d": True, "est": True, "folha": False, "int": True, "cap": True, "infra": False},
    3: {"100d": True, "est": True, "folha": True, "int": True, "cap": True, "infra": False},
    4: {"100d": False, "est": False, "folha": True, "int": True, "cap": True, "infra": False},
    5: {"100d": False, "est": True, "folha": True, "int": True, "cap": False, "infra": True},
    6: {"100d": False, "est": True, "folha": False, "int": False, "cap": True, "infra": True},
    7: {"100d": False, "est": False, "folha": True, "int": True, "cap": False, "infra": False},
    8: {"100d": False, "est": True, "folha": False, "int": True, "cap": False, "infra": False},
    9: {"100d": False, "est": False, "folha": False, "int": True, "cap": False, "infra": False},
    10: {"100d": False, "est": False, "folha": False, "int": True, "cap": True, "infra": False},
    11: {"100d": True, "est": True, "folha": False, "int": False, "cap": True, "infra": False},
    12: {"100d": False, "est": True, "folha": True, "int": False, "cap": True, "infra": False},
}

STATUS_LIST = [
    "Em andamento", "Em andamento", "Em andamento", "Em andamento",
    "Em alerta", "Atrasado", "Alcançado", "Evento a confirmar",
]


def _seed_metas(db: Session, secretariats: list):
    """Popula goal_groups e metas com dados simulados realistas."""
    groups = []
    for (num, name, pillar, n_meta, n_and, n_ale, n_atra, n_alc, n_eve) in GOAL_GROUPS_DATA:
        g = GoalGroup(number=num, name=name, pillar=pillar)
        db.add(g)
        groups.append((g, num, n_and, n_ale, n_atra, n_alc, n_eve))
    db.flush()

    random.seed(123)
    for (group_obj, obj_num, n_and, n_ale, n_atra, n_alc, n_eve) in groups:
        templates = META_TEMPLATES.get(obj_num, [])
        flags = FLAGS_BY_OBJ.get(obj_num, {})
        sec_idx = OBJ_TO_SEC.get(obj_num)
        sec = secretariats[sec_idx - 1] if sec_idx and sec_idx <= len(secretariats) else None

        # Build status queue matching counts from screenshot
        statuses = (["Em andamento"] * n_and + ["Em alerta"] * n_ale +
                    ["Atrasado"] * n_atra + ["Alcançado"] * n_alc +
                    ["Evento a confirmar"] * n_eve)
        random.shuffle(statuses)

        for i, template in enumerate(templates):
            desc, unit, planned, actual, planned_date, priority = template
            status = statuses[i] if i < len(statuses) else "Em andamento"
            progress = round((actual / planned * 100) if planned > 0 else 0, 1)

            m = Meta(
                code=f"{obj_num}.{i + 1}",
                description=desc,
                goal_group_id=group_obj.id,
                secretariat_id=sec.id if sec else None,
                priority=priority,
                status=status,
                flag_100_dias=flags.get("100d", False),
                flag_estadao=flags.get("est", False),
                flag_folha=flags.get("folha", False),
                flag_interior=flags.get("int", False),
                flag_capital=flags.get("cap", False),
                flag_infraestrutura=flags.get("infra", False),
                planned_value=planned,
                actual_value=actual,
                unit=unit,
                planned_date=planned_date,
                progress_pct=progress,
            )
            db.add(m)
    db.flush()


def seed_all():
    # Create tables
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()

    try:
        # Check idempotency for main data
        if db.query(Deputy).count() > 0:
            # Check if metas need seeding separately
            if db.query(GoalGroup).count() == 0:
                print("Main data already seeded. Seeding metas...")
                secretariats = db.query(Secretariat).all()
                _seed_metas(db, secretariats)
                db.commit()
                print("Metas seeded successfully.")
            else:
                print("Database already seeded, skipping.")
            return
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

        print("Seeding metas (Programa de Metas)...")
        _seed_metas(db, secretariats)

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
