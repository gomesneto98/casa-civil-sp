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
from sqlalchemy import text

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
    ("Éducação", "SEDUC", "📚", "Samuel Kinoshita", "sem partido", "João Marcelo Borges|sem partido;Célia Tokoro|sem partido"),
    ("Saúde", "SES", "🏥", "Eleuses Vieira de Paiva", "PL", "Carlos Eduardo Fratezi|sem partido;Ana Cristina|sem partido"),
    ("Segurança Pública", "SSP", "🚔", "Guilherme Derrite", "PL", "José Carlos Rocha|sem partido;Benedito Mariano|sem partido"),
    ("Fazenda e Planejamento", "SEFAZ", "💰", "Samuel Kinoshita", "sem partido", "Felipe Salto|sem partido;André Carvalho|sem partido"),
    ("Meio Ambiente, Infraestrutura e Logística", "SEMIL", "🌿", "Natália Resende", "PL", "Marcus Vinicius|sem partido;Patricia Ellen|sem partido"),
    ("Habitação", "SEHAB", "🏠", "Marcello Lima", "PODE", "Marcos Pellegrini|sem partido;Sandra Momesso|sem partido"),
    ("Agricultura e Abastecimento", "SAA", "🌾", "Guilherme Piai", "AVANTE", "Fábio Meirelles|sem partido;Ana Paula Rodrigues|sem partido"),
    ("Desenvolvimento Econômico", "SDE", "💼", "Jorge Lima", "PL", "Rodrigo Garcia|sem partido;Camila Moretti|sem partido"),
    ("Cultura e Economia Criativa", "SEC", "🎭", "Marilia Marton", "sem partido", "Luiz Marcelo|sem partido;Renata Fukushima|sem partido"),
    ("Turismo e Viagens", "SETUR", "✈️", "Roberto de Lucena", "REPUBLICANOS", "Thiago Martins|sem partido;Fernanda Lima|sem partido"),
    ("Cidades e Desenvolvimento Regional", "SCDR", "🏙️", "Marco Vinholi", "PSDB", "Eduardo Mazzei|sem partido;Sonia Racy|sem partido"),
    ("Transportes Metropolitanos", "STM", "🚇", "Diego Basei", "sem partido", "Paulo Galli|sem partido;Carla Figueiredo|sem partido"),
    ("Desenvolvimento Social e Família", "SEDS", "🤝", "Gilmara Lima", "sem partido", "Vania Borges|sem partido;Claudia Motta|sem partido"),
    ("Esportes", "SE", "⚽", "Laercio Benko", "sem partido", "Carlos Augusto|sem partido;Marcos Aurélio|sem partido"),
    ("Casa Civil", "CC", "🏛️", "Arthur Lima", "sem partido", "Mauricio Trentin|sem partido;Adriana Lima|sem partido"),
    ("Parcerias em Investimentos", "SPI", "🤝", "Rafael Benini", "sem partido", "Bruno Giannini|sem partido;Lucas Oliveira|sem partido"),
    ("Relações Internacionais", "SRI", "🌍", "Julio Saqui", "sem partido", "Monica Nogueira|sem partido;Rodrigo Alves|sem partido"),
    ("Administração Penitenciária", "SAP", "🔒", "Marcello Streifinger", "sem partido", "Paulo Lacerda|sem partido;Renato Campos|sem partido"),
    ("Comunicação", "SECOM", "📢", "Tanara Cossa", "sem partido", "Alexandre Tavares|sem partido;Bianca Fernandes|sem partido"),
    ("Governo", "SG", "⭐", "Gilberto Kassab", "PSD", "Marcos Penido|PSDB;Renato Arnaldo|PSD"),
    ("Ciência, Tecnologia e Inovação", "SCTEI", "🔬", "Vahan Agopyan", "sem partido", "Carlos Henrique|sem partido;Maria Clara|sem partido"),
    ("Justiça e Cidadania", "SJC", "⚖️", "Fábio Prieto de Souza", "PL", "André Rodrigues|sem partido;Luciana Ferreira|sem partido"),
    ("Mulher", "SM", "👩", "Valéria Monteiro", "sem partido", "Adriana Accorsi|sem partido;Carolina Matos|sem partido"),
    ("Direitos da Pessoa com Deficiência", "SEDPcD", "♿", "Célia Leão", "sem partido", "Roberta Cardoso|sem partido;Paulo Henrique|sem partido"),
]

# budget base values in billions (used to generate realistic orçamento data)
BUDGET_BASES = {
    "SEDUC": 70.0, "SES": 50.0, "SSP": 22.0, "SEMIL": 15.0, "SCDR": 12.0,
    "SEFAZ": 10.0, "SEC": 3.5, "SEHAB": 8.0, "SAA": 4.0, "STM": 18.0,
    "SDE": 6.0, "SEDS": 9.0, "SETUR": 2.5, "SE": 2.0, "CC": 3.0,
    "SPI": 1.5, "SRI": 0.8, "SAP": 7.0, "SECOM": 1.2, "SG": 2.0,
    "SCTEI": 2.8, "SJC": 3.2, "SM": 1.0, "SEDPcD": 0.9,
}

# ---------------------------------------------------------------------------
# Municípios — maiores cidades SP com coordenadas geográficas
# (name, region, population, lat, lng)
# ---------------------------------------------------------------------------
MUNICIPALITIES_DATA = [
    ("Adamantina", "Interior", 34687, None, None),
    ("Adolfo", "Interior", 4351, None, None),
    ("Aguaí", "Interior", 32072, None, None),
    ("Agudos", "Interior", 37680, None, None),
    ("Alambari", "Interior", 6141, None, None),
    ("Alfredo Marcondes", "Interior", 4445, None, None),
    ("Altair", "Interior", 3451, None, None),
    ("Altinópolis", "Interior", 16818, None, None),
    ("Alto Alegre", "Interior", 3841, None, None),
    ("Alumínio", "Interior", 17301, None, None),
    ("Alvinlândia", "Interior", 2885, None, None),
    ("Americana", "Interior", 237240, None, None),
    ("Amparo", "Interior", 68008, None, None),
    ("Américo Brasiliense", "Interior", 33019, None, None),
    ("Américo de Campos", "Interior", 5870, None, None),
    ("Analândia", "Interior", 4589, None, None),
    ("Andradina", "Interior", 59783, None, None),
    ("Angatuba", "Interior", 24022, None, None),
    ("Anhembi", "Interior", 5674, None, None),
    ("Anhumas", "Interior", 4023, None, None),
    ("Aparecida", "Vale do Paraíba", 32569, None, None),
    ("Aparecida d\'Oeste", "Interior", 4086, None, None),
    ("Apiaí", "Interior", 24585, None, None),
    ("Aramina", "Interior", 5420, None, None),
    ("Arandu", "Interior", 6885, None, None),
    ("Arapeí", "Vale do Paraíba", 2330, None, None),
    ("Araraquara", "Interior", 242228, None, None),
    ("Araras", "Interior", 130866, None, None),
    ("Araçariguama", "Interior", 21522, None, None),
    ("Araçatuba", "Interior", 200124, None, None),
    ("Araçoiaba da Serra", "Interior", 32443, None, None),
    ("Arco-Íris", "Interior", 2044, None, None),
    ("Arealva", "Interior", 8130, None, None),
    ("Areias", "Vale do Paraíba", 3577, None, None),
    ("Areiópolis", "Interior", 10130, None, None),
    ("Ariranha", "Interior", 7602, None, None),
    ("Artur Nogueira", "Interior", 51456, None, None),
    ("Arujá", "Grande SP", 86678, None, None),
    ("Aspásia", "Interior", 1842, None, None),
    ("Assis", "Interior", 101409, None, None),
    ("Atibaia", "Interior", 158647, None, None),
    ("Auriflama", "Interior", 13692, None, None),
    ("Avanhandava", "Interior", 11263, None, None),
    ("Avaré", "Interior", 92805, None, None),
    ("Avaí", "Interior", 4483, None, None),
    ("Bady Bassitt", "Interior", 27260, None, None),
    ("Balbinos", "Interior", 3887, None, None),
    ("Bananal", "Vale do Paraíba", 9969, None, None),
    ("Barbosa", "Interior", 5640, None, None),
    ("Bariri", "Interior", 31595, None, None),
    ("Barra Bonita", "Interior", 34346, None, None),
    ("Barra do Chapéu", "Interior", 5179, None, None),
    ("Barra do Turvo", "Litoral", 6876, None, None),
    ("Barretos", "Interior", 122485, None, None),
    ("Barrinha", "Interior", 32092, None, None),
    ("Barueri", "Grande SP", 316473, None, None),
    ("Barão de Antonina", "Interior", 3531, None, None),
    ("Bastos", "Interior", 21503, None, None),
    ("Batatais", "Interior", 58402, None, None),
    ("Bauru", "Interior", 379146, None, None),
    ("Bebedouro", "Interior", 76373, None, None),
    ("Bento de Abreu", "Interior", 2606, None, None),
    ("Bernardino de Campos", "Interior", 11607, None, None),
    ("Bertioga", "Grande SP", 64188, None, None),
    ("Bilac", "Interior", 7319, None, None),
    ("Birigui", "Interior", 118979, None, None),
    ("Biritiba Mirim", "Grande SP", 29683, None, None),
    ("Boa Esperança do Sul", "Interior", 12978, None, None),
    ("Bocaina", "Interior", 11259, None, None),
    ("Bofete", "Interior", 10460, None, None),
    ("Boituva", "Interior", 61081, None, None),
    ("Bom Jesus dos Perdões", "Interior", 22006, None, None),
    ("Bom Sucesso de Itararé", "Interior", 3555, None, None),
    ("Boracéia", "Interior", 4715, None, None),
    ("Borborema", "Interior", 14226, None, None),
    ("Borebi", "Interior", 2713, None, None),
    ("Borá", "Interior", 907, None, None),
    ("Botucatu", "Interior", 145155, None, None),
    ("Bragança Paulista", "Interior", 176811, None, None),
    ("Braúna", "Interior", 5356, None, None),
    ("Brejo Alegre", "Interior", 2565, None, None),
    ("Brodowski", "Interior", 25201, None, None),
    ("Brotas", "Interior", 23898, None, None),
    ("Buri", "Interior", 20250, None, None),
    ("Buritama", "Interior", 17210, None, None),
    ("Buritizal", "Interior", 4356, None, None),
    ("Bálsamo", "Interior", 9596, None, None),
    ("Cabreúva", "Interior", 47011, None, None),
    ("Cabrália Paulista", "Interior", 4299, None, None),
    ("Cachoeira Paulista", "Vale do Paraíba", 31564, None, None),
    ("Caconde", "Interior", 17101, None, None),
    ("Cafelândia", "Interior", 16654, None, None),
    ("Caiabu", "Interior", 3712, None, None),
    ("Caieiras", "Grande SP", 95032, None, None),
    ("Caiuá", "Interior", 5466, None, None),
    ("Cajamar", "Grande SP", 92689, None, None),
    ("Cajati", "Litoral", 28515, None, None),
    ("Cajobi", "Interior", 9133, None, None),
    ("Cajuru", "Interior", 23830, None, None),
    ("Campina do Monte Alegre", "Interior", 5954, None, None),
    ("Campinas", "Interior", 1139047, None, None),
    ("Campo Limpo Paulista", "Interior", 77632, None, None),
    ("Campos Novos Paulista", "Interior", 4888, None, None),
    ("Campos do Jordão", "Vale do Paraíba", 46974, None, None),
    ("Cananéia", "Litoral", 12289, None, None),
    ("Canas", "Vale do Paraíba", 4931, None, None),
    ("Canitar", "Interior", 6283, None, None),
    ("Capela do Alto", "Interior", 22866, None, None),
    ("Capivari", "Interior", 50068, None, None),
    ("Capão Bonito", "Interior", 46337, None, None),
    ("Caraguatatuba", "Vale do Paraíba", 134873, None, None),
    ("Carapicuíba", "Grande SP", 386984, None, None),
    ("Cardoso", "Interior", 11345, None, None),
    ("Casa Branca", "Interior", 28083, None, None),
    ("Castilho", "Interior", 19977, None, None),
    ("Catanduva", "Interior", 115791, None, None),
    ("Catiguá", "Interior", 7003, None, None),
    ("Caçapava", "Vale do Paraíba", 96202, None, None),
    ("Cedral", "Interior", 12618, None, None),
    ("Cerqueira César", "Interior", 21469, None, None),
    ("Cerquilho", "Interior", 44695, None, None),
    ("Cesário Lange", "Interior", 19048, None, None),
    ("Charqueada", "Interior", 15535, None, None),
    ("Chavantes", "Interior", 12211, None, None),
    ("Clementina", "Interior", 6982, None, None),
    ("Colina", "Interior", 18486, None, None),
    ("Colômbia", "Interior", 6629, None, None),
    ("Conchal", "Interior", 28101, None, None),
    ("Conchas", "Interior", 15232, None, None),
    ("Cordeirópolis", "Interior", 24514, None, None),
    ("Coroados", "Interior", 5400, None, None),
    ("Coronel Macedo", "Interior", 4280, None, None),
    ("Corumbataí", "Interior", 4195, None, None),
    ("Cosmorama", "Interior", 8719, None, None),
    ("Cosmópolis", "Interior", 59773, None, None),
    ("Cotia", "Grande SP", 274413, None, None),
    ("Cravinhos", "Interior", 33281, None, None),
    ("Cristais Paulista", "Interior", 9272, None, None),
    ("Cruzeiro", "Vale do Paraíba", 74961, None, None),
    ("Cruzália", "Interior", 2108, None, None),
    ("Cubatão", "Grande SP", 112476, None, None),
    ("Cunha", "Vale do Paraíba", 22110, None, None),
    ("Cássia dos Coqueiros", "Interior", 2799, None, None),
    ("Cândido Mota", "Interior", 29449, None, None),
    ("Cândido Rodrigues", "Interior", 2889, None, None),
    ("Descalvado", "Interior", 31756, None, None),
    ("Diadema", "Grande SP", 393237, None, None),
    ("Dirce Reis", "Interior", 1620, None, None),
    ("Divinolândia", "Interior", 11158, None, None),
    ("Dobrada", "Interior", 8759, None, None),
    ("Dois Córregos", "Interior", 24510, None, None),
    ("Dolcinópolis", "Interior", 2207, None, None),
    ("Dourado", "Interior", 8096, None, None),
    ("Dracena", "Interior", 45474, None, None),
    ("Duartina", "Interior", 12328, None, None),
    ("Dumont", "Interior", 9471, None, None),
    ("Echaporã", "Interior", 6205, None, None),
    ("Eldorado", "Litoral", 13069, None, None),
    ("Elias Fausto", "Interior", 17699, None, None),
    ("Elisiário", "Interior", 3138, None, None),
    ("Embaúba", "Interior", 2323, None, None),
    ("Embu das Artes", "Grande SP", 250691, None, None),
    ("Embu-Guaçu", "Grande SP", 66970, None, None),
    ("Emilianópolis", "Interior", 3014, None, None),
    ("Engenheiro Coelho", "Interior", 19566, None, None),
    ("Espírito Santo do Pinhal", "Interior", 39816, None, None),
    ("Espírito Santo do Turvo", "Interior", 4157, None, None),
    ("Estiva Gerbi", "Interior", 11295, None, None),
    ("Estrela d\'Oeste", "Interior", 9417, None, None),
    ("Estrela do Norte", "Interior", 2703, None, None),
    ("Euclides da Cunha Paulista", "Interior", 7924, None, None),
    ("Fartura", "Interior", 16641, None, None),
    ("Fernando Prestes", "Interior", 5942, None, None),
    ("Fernandópolis", "Interior", 71186, None, None),
    ("Fernão", "Interior", 1656, None, None),
    ("Ferraz de Vasconcelos", "Grande SP", 179198, None, None),
    ("Flora Rica", "Interior", 1487, None, None),
    ("Floreal", "Interior", 2733, None, None),
    ("Florínea", "Interior", 3851, None, None),
    ("Flórida Paulista", "Interior", 12958, None, None),
    ("Franca", "Interior", 352536, None, None),
    ("Francisco Morato", "Grande SP", 165139, None, None),
    ("Franco da Rocha", "Grande SP", 144849, None, None),
    ("Gabriel Monteiro", "Interior", 2763, None, None),
    ("Garça", "Interior", 42110, None, None),
    ("Gastão Vidigal", "Interior", 3252, None, None),
    ("Gavião Peixoto", "Interior", 4702, None, None),
    ("General Salgado", "Interior", 10312, None, None),
    ("Getulina", "Interior", 10232, None, None),
    ("Glicério", "Interior", 4138, None, None),
    ("Guaimbê", "Interior", 5512, None, None),
    ("Guaiçara", "Interior", 11239, None, None),
    ("Guapiara", "Interior", 17071, None, None),
    ("Guapiaçu", "Interior", 21711, None, None),
    ("Guaraci", "Interior", 10350, None, None),
    ("Guarani d\'Oeste", "Interior", 1968, None, None),
    ("Guarantã", "Interior", 6427, None, None),
    ("Guararapes", "Interior", 31043, None, None),
    ("Guararema", "Grande SP", 31236, None, None),
    ("Guaratinguetá", "Vale do Paraíba", 118044, None, None),
    ("Guaraçaí", "Interior", 7441, None, None),
    ("Guareí", "Interior", 15013, None, None),
    ("Guariba", "Interior", 37498, None, None),
    ("Guarujá", "Grande SP", 287634, None, None),
    ("Guarulhos", "Grande SP", 1291771, None, None),
    ("Guará", "Interior", 18606, None, None),
    ("Guatapará", "Interior", 7320, None, None),
    ("Guaíra", "Interior", 39279, None, None),
    ("Guzolândia", "Interior", 4246, None, None),
    ("Gália", "Interior", 6380, None, None),
    ("Herculândia", "Interior", 9125, None, None),
    ("Holambra", "Interior", 15094, None, None),
    ("Hortolândia", "Interior", 236641, None, None),
    ("Iacanga", "Interior", 10437, None, None),
    ("Iacri", "Interior", 6131, None, None),
    ("Iaras", "Interior", 8010, None, None),
    ("Ibaté", "Interior", 32178, None, None),
    ("Ibirarema", "Interior", 6385, None, None),
    ("Ibirá", "Interior", 11690, None, None),
    ("Ibitinga", "Interior", 60033, None, None),
    ("Ibiúna", "Interior", 75605, None, None),
    ("Icém", "Interior", 7819, None, None),
    ("Iepê", "Interior", 7619, None, None),
    ("Igarapava", "Interior", 26212, None, None),
    ("Igaratá", "Vale do Paraíba", 10605, None, None),
    ("Igaraçu do Tietê", "Interior", 23106, None, None),
    ("Iguape", "Litoral", 29115, None, None),
    ("Ilha Comprida", "Litoral", 13419, None, None),
    ("Ilha Solteira", "Interior", 25549, None, None),
    ("Ilhabela", "Vale do Paraíba", 34934, None, None),
    ("Indaiatuba", "Interior", 255748, None, None),
    ("Indiana", "Interior", 5090, None, None),
    ("Indiaporã", "Interior", 4035, None, None),
    ("Inúbia Paulista", "Interior", 3615, None, None),
    ("Ipaussu", "Interior", 13712, None, None),
    ("Iperó", "Interior", 36459, None, None),
    ("Ipeúna", "Interior", 6831, None, None),
    ("Ipiguá", "Interior", 6761, None, None),
    ("Iporanga", "Interior", 4046, None, None),
    ("Ipuã", "Interior", 14454, None, None),
    ("Iracemápolis", "Interior", 21967, None, None),
    ("Irapuru", "Interior", 7085, None, None),
    ("Irapuã", "Interior", 6867, None, None),
    ("Itaberá", "Interior", 17983, None, None),
    ("Itajobi", "Interior", 16989, None, None),
    ("Itaju", "Interior", 3618, None, None),
    ("Itanhaém", "Litoral", 112476, None, None),
    ("Itaoca", "Interior", 3422, None, None),
    ("Itapecerica da Serra", "Grande SP", 158522, None, None),
    ("Itapetininga", "Interior", 157790, None, None),
    ("Itapeva", "Interior", 89728, None, None),
    ("Itapevi", "Grande SP", 232297, None, None),
    ("Itapira", "Interior", 72022, None, None),
    ("Itapirapuã Paulista", "Interior", 4306, None, None),
    ("Itaporanga", "Interior", 14085, None, None),
    ("Itapura", "Interior", 3979, None, None),
    ("Itapuí", "Interior", 13659, None, None),
    ("Itaquaquecetuba", "Grande SP", 369275, None, None),
    ("Itararé", "Interior", 44438, None, None),
    ("Itariri", "Litoral", 15528, None, None),
    ("Itatiba", "Interior", 121590, None, None),
    ("Itatinga", "Interior", 19070, None, None),
    ("Itaí", "Interior", 25180, None, None),
    ("Itirapina", "Interior", 16148, None, None),
    ("Itirapuã", "Interior", 5779, None, None),
    ("Itobi", "Interior", 8046, None, None),
    ("Itu", "Interior", 168240, None, None),
    ("Itupeva", "Interior", 70616, None, None),
    ("Ituverava", "Interior", 37571, None, None),
    ("Itápolis", "Interior", 39493, None, None),
    ("Jaborandi", "Interior", 6221, None, None),
    ("Jaboticabal", "Interior", 71821, None, None),
    ("Jacareí", "Vale do Paraíba", 240275, None, None),
    ("Jaci", "Interior", 7613, None, None),
    ("Jacupiranga", "Litoral", 16097, None, None),
    ("Jaguariúna", "Interior", 59347, None, None),
    ("Jales", "Interior", 48776, None, None),
    ("Jambeiro", "Vale do Paraíba", 6397, None, None),
    ("Jandira", "Grande SP", 118045, None, None),
    ("Jardinópolis", "Interior", 45282, None, None),
    ("Jarinu", "Interior", 37535, None, None),
    ("Jaú", "Interior", 133497, None, None),
    ("Jeriquara", "Interior", 3863, None, None),
    ("Joanópolis", "Interior", 12815, None, None),
    ("José Bonifácio", "Interior", 36633, None, None),
    ("João Ramalho", "Interior", 4371, None, None),
    ("Jumirim", "Interior", 3056, None, None),
    ("Jundiaí", "Interior", 443221, None, None),
    ("Junqueirópolis", "Interior", 20448, None, None),
    ("Juquitiba", "Grande SP", 27404, None, None),
    ("Juquiá", "Litoral", 17154, None, None),
    ("Júlio Mesquita", "Interior", 4254, None, None),
    ("Lagoinha", "Vale do Paraíba", 5083, None, None),
    ("Laranjal Paulista", "Interior", 26261, None, None),
    ("Lavrinhas", "Vale do Paraíba", 7171, None, None),
    ("Lavínia", "Interior", 9689, None, None),
    ("Leme", "Interior", 98161, None, None),
    ("Lençóis Paulista", "Interior", 66505, None, None),
    ("Limeira", "Interior", 291869, None, None),
    ("Lindóia", "Interior", 7014, None, None),
    ("Lins", "Interior", 74779, None, None),
    ("Lorena", "Vale do Paraíba", 84855, None, None),
    ("Lourdes", "Interior", 1950, None, None),
    ("Louveira", "Interior", 51847, None, None),
    ("Lucianópolis", "Interior", 2372, None, None),
    ("Lucélia", "Interior", 20061, None, None),
    ("Luiziânia", "Interior", 4701, None, None),
    ("Lupércio", "Interior", 3981, None, None),
    ("Lutécia", "Interior", 2661, None, None),
    ("Luís Antônio", "Interior", 12265, None, None),
    ("Macatuba", "Interior", 16829, None, None),
    ("Macaubal", "Interior", 7481, None, None),
    ("Macedônia", "Interior", 3963, None, None),
    ("Magda", "Interior", 3165, None, None),
    ("Mairinque", "Interior", 50027, None, None),
    ("Mairiporã", "Grande SP", 93853, None, None),
    ("Manduri", "Interior", 9871, None, None),
    ("Marabá Paulista", "Interior", 4573, None, None),
    ("Maracaí", "Interior", 12673, None, None),
    ("Marapoama", "Interior", 3292, None, None),
    ("Marinópolis", "Interior", 1860, None, None),
    ("Mariápolis", "Interior", 3513, None, None),
    ("Martinópolis", "Interior", 24881, None, None),
    ("Marília", "Interior", 237627, None, None),
    ("Matão", "Interior", 79033, None, None),
    ("Mauá", "Grande SP", 418261, None, None),
    ("Mendonça", "Interior", 6159, None, None),
    ("Meridiano", "Interior", 4572, None, None),
    ("Mesópolis", "Interior", 1952, None, None),
    ("Miguelópolis", "Interior", 19441, None, None),
    ("Mineiros do Tietê", "Interior", 11230, None, None),
    ("Mira Estrela", "Interior", 3126, None, None),
    ("Miracatu", "Litoral", 18553, None, None),
    ("Mirandópolis", "Interior", 27983, None, None),
    ("Mirante do Paranapanema", "Interior", 15917, None, None),
    ("Mirassol", "Interior", 63337, None, None),
    ("Mirassolândia", "Interior", 4669, None, None),
    ("Mococa", "Interior", 67681, None, None),
    ("Mogi Guaçu", "Interior", 153658, None, None),
    ("Mogi Mirim", "Interior", 92558, None, None),
    ("Mogi das Cruzes", "Grande SP", 451505, None, None),
    ("Mombuca", "Interior", 3722, None, None),
    ("Mongaguá", "Litoral", 61951, None, None),
    ("Monte Alegre do Sul", "Interior", 8627, None, None),
    ("Monte Alto", "Interior", 47574, None, None),
    ("Monte Aprazível", "Interior", 22280, None, None),
    ("Monte Azul Paulista", "Interior", 18151, None, None),
    ("Monte Castelo", "Interior", 4222, None, None),
    ("Monte Mor", "Interior", 64662, None, None),
    ("Monteiro Lobato", "Vale do Paraíba", 4138, None, None),
    ("Monções", "Interior", 1937, None, None),
    ("Morro Agudo", "Interior", 27933, None, None),
    ("Morungaba", "Interior", 13720, None, None),
    ("Motuca", "Interior", 4034, None, None),
    ("Murutinga do Sul", "Interior", 3737, None, None),
    ("Nantes", "Interior", 2660, None, None),
    ("Narandiba", "Interior", 5713, None, None),
    ("Natividade da Serra", "Vale do Paraíba", 6999, None, None),
    ("Nazaré Paulista", "Interior", 18217, None, None),
    ("Neves Paulista", "Interior", 9699, None, None),
    ("Nhandeara", "Interior", 9852, None, None),
    ("Nipoã", "Interior", 4750, None, None),
    ("Nova Aliança", "Interior", 6693, None, None),
    ("Nova Campina", "Interior", 8497, None, None),
    ("Nova Canaã Paulista", "Interior", 2032, None, None),
    ("Nova Castilho", "Interior", 1062, None, None),
    ("Nova Europa", "Interior", 9311, None, None),
    ("Nova Granada", "Interior", 19419, None, None),
    ("Nova Guataporanga", "Interior", 2156, None, None),
    ("Nova Independência", "Interior", 4609, None, None),
    ("Nova Luzitânia", "Interior", 2837, None, None),
    ("Nova Odessa", "Interior", 62019, None, None),
    ("Novais", "Interior", 4412, None, None),
    ("Novo Horizonte", "Interior", 38324, None, None),
    ("Nuporanga", "Interior", 7391, None, None),
    ("Ocauçu", "Interior", 4331, None, None),
    ("Olímpia", "Interior", 55074, None, None),
    ("Onda Verde", "Interior", 4771, None, None),
    ("Oriente", "Interior", 6085, None, None),
    ("Orindiúva", "Interior", 6024, None, None),
    ("Orlândia", "Interior", 38319, None, None),
    ("Osasco", "Grande SP", 728615, None, None),
    ("Oscar Bressane", "Interior", 2470, None, None),
    ("Osvaldo Cruz", "Interior", 31272, None, None),
    ("Ourinhos", "Interior", 103970, None, None),
    ("Ouro Verde", "Interior", 7779, None, None),
    ("Ouroeste", "Interior", 10294, None, None),
    ("Pacaembu", "Interior", 14877, None, None),
    ("Palestina", "Interior", 11476, None, None),
    ("Palmares Paulista", "Interior", 9650, None, None),
    ("Palmeira d\'Oeste", "Interior", 8903, None, None),
    ("Palmital", "Interior", 19594, None, None),
    ("Panorama", "Interior", 14964, None, None),
    ("Paraguaçu Paulista", "Interior", 41120, None, None),
    ("Paraibuna", "Vale do Paraíba", 17667, None, None),
    ("Paranapanema", "Interior", 19395, None, None),
    ("Paranapuã", "Interior", 4031, None, None),
    ("Parapuã", "Interior", 10580, None, None),
    ("Paraíso", "Interior", 6099, None, None),
    ("Pardinho", "Interior", 7153, None, None),
    ("Pariquera-Açu", "Litoral", 19233, None, None),
    ("Parisi", "Interior", 2892, None, None),
    ("Patrocínio Paulista", "Interior", 14512, None, None),
    ("Paulicéia", "Interior", 7955, None, None),
    ("Paulistânia", "Interior", 2090, None, None),
    ("Paulo de Faria", "Interior", 7400, None, None),
    ("Paulínia", "Interior", 110537, None, None),
    ("Pederneiras", "Interior", 44827, None, None),
    ("Pedra Bela", "Interior", 6557, None, None),
    ("Pedranópolis", "Interior", 2787, None, None),
    ("Pedregulho", "Interior", 15525, None, None),
    ("Pedreira", "Interior", 43112, None, None),
    ("Pedrinhas Paulista", "Interior", 2804, None, None),
    ("Pedro de Toledo", "Litoral", 11281, None, None),
    ("Penápolis", "Interior", 61679, None, None),
    ("Pereira Barreto", "Interior", 24095, None, None),
    ("Pereiras", "Interior", 8737, None, None),
    ("Peruíbe", "Litoral", 68352, None, None),
    ("Piacatu", "Interior", 5519, None, None),
    ("Piedade", "Interior", 52970, None, None),
    ("Pilar do Sul", "Interior", 27619, None, None),
    ("Pindamonhangaba", "Vale do Paraíba", 165428, None, None),
    ("Pindorama", "Interior", 14542, None, None),
    ("Pinhalzinho", "Interior", 15224, None, None),
    ("Piquerobi", "Interior", 3264, None, None),
    ("Piquete", "Vale do Paraíba", 12490, None, None),
    ("Piracaia", "Interior", 26029, None, None),
    ("Piracicaba", "Interior", 423323, None, None),
    ("Piraju", "Interior", 29436, None, None),
    ("Pirajuí", "Interior", 22431, None, None),
    ("Pirangi", "Interior", 10885, None, None),
    ("Pirapora do Bom Jesus", "Grande SP", 18370, None, None),
    ("Pirapozinho", "Interior", 25348, None, None),
    ("Pirassununga", "Interior", 73545, None, None),
    ("Piratininga", "Interior", 15108, None, None),
    ("Pitangueiras", "Interior", 33674, None, None),
    ("Planalto", "Interior", 4389, None, None),
    ("Platina", "Interior", 3025, None, None),
    ("Poloni", "Interior", 5592, None, None),
    ("Pompéia", "Interior", 20196, None, None),
    ("Pongaí", "Interior", 3395, None, None),
    ("Pontal", "Interior", 37607, None, None),
    ("Pontalinda", "Interior", 4127, None, None),
    ("Pontes Gestal", "Interior", 2387, None, None),
    ("Populina", "Interior", 4127, None, None),
    ("Porangaba", "Interior", 10451, None, None),
    ("Porto Feliz", "Interior", 56497, None, None),
    ("Porto Ferreira", "Interior", 52649, None, None),
    ("Potim", "Vale do Paraíba", 20392, None, None),
    ("Potirendaba", "Interior", 18496, None, None),
    ("Poá", "Grande SP", 103765, None, None),
    ("Pracinha", "Interior", 2578, None, None),
    ("Pradópolis", "Interior", 17078, None, None),
    ("Praia Grande", "Grande SP", 349935, None, None),
    ("Pratânia", "Interior", 5126, None, None),
    ("Presidente Alves", "Interior", 3804, None, None),
    ("Presidente Bernardes", "Interior", 14490, None, None),
    ("Presidente Epitácio", "Interior", 39505, None, None),
    ("Presidente Prudente", "Interior", 225668, None, None),
    ("Presidente Venceslau", "Interior", 35201, None, None),
    ("Promissão", "Interior", 35131, None, None),
    ("Quadra", "Interior", 3405, None, None),
    ("Quatá", "Interior", 13163, None, None),
    ("Queiroz", "Interior", 3265, None, None),
    ("Queluz", "Vale do Paraíba", 9159, None, None),
    ("Quintana", "Interior", 7038, None, None),
    ("Rafard", "Interior", 8965, None, None),
    ("Rancharia", "Interior", 28588, None, None),
    ("Redenção da Serra", "Vale do Paraíba", 4494, None, None),
    ("Regente Feijó", "Interior", 20145, None, None),
    ("Reginópolis", "Interior", 7662, None, None),
    ("Registro", "Litoral", 59947, None, None),
    ("Restinga", "Interior", 6404, None, None),
    ("Ribeira", "Interior", 3132, None, None),
    ("Ribeirão Bonito", "Interior", 10989, None, None),
    ("Ribeirão Branco", "Interior", 18627, None, None),
    ("Ribeirão Corrente", "Interior", 4608, None, None),
    ("Ribeirão Grande", "Interior", 7450, None, None),
    ("Ribeirão Pires", "Grande SP", 115559, None, None),
    ("Ribeirão Preto", "Interior", 698642, None, None),
    ("Ribeirão do Sul", "Interior", 4677, None, None),
    ("Ribeirão dos Índios", "Interior", 2025, None, None),
    ("Rifaina", "Interior", 4049, None, None),
    ("Rincão", "Interior", 9098, None, None),
    ("Rinópolis", "Interior", 9259, None, None),
    ("Rio Claro", "Interior", 201418, None, None),
    ("Rio Grande da Serra", "Grande SP", 44170, None, None),
    ("Rio das Pedras", "Interior", 31328, None, None),
    ("Riolândia", "Interior", 10309, None, None),
    ("Riversul", "Interior", 5599, None, None),
    ("Rosana", "Interior", 17440, None, None),
    ("Roseira", "Vale do Paraíba", 10832, None, None),
    ("Rubinéia", "Interior", 3833, None, None),
    ("Rubiácea", "Interior", 2700, None, None),
    ("Sabino", "Interior", 5112, None, None),
    ("Sagres", "Interior", 2474, None, None),
    ("Sales", "Interior", 6437, None, None),
    ("Sales Oliveira", "Interior", 11411, None, None),
    ("Salesópolis", "Grande SP", 15202, None, None),
    ("Salmourão", "Interior", 4808, None, None),
    ("Saltinho", "Interior", 8161, None, None),
    ("Salto", "Interior", 134319, None, None),
    ("Salto Grande", "Interior", 9050, None, None),
    ("Salto de Pirapora", "Interior", 43748, None, None),
    ("Sandovalina", "Interior", 3645, None, None),
    ("Santa Adélia", "Interior", 14018, None, None),
    ("Santa Albertina", "Interior", 6393, None, None),
    ("Santa Branca", "Vale do Paraíba", 13975, None, None),
    ("Santa Bárbara d\'Oeste", "Interior", 183347, None, None),
    ("Santa Clara d\'Oeste", "Interior", 2598, None, None),
    ("Santa Cruz da Conceição", "Interior", 4277, None, None),
    ("Santa Cruz da Esperança", "Interior", 2116, None, None),
    ("Santa Cruz das Palmeiras", "Interior", 28864, None, None),
    ("Santa Cruz do Rio Pardo", "Interior", 46442, None, None),
    ("Santa Ernestina", "Interior", 6118, None, None),
    ("Santa Fé do Sul", "Interior", 34794, None, None),
    ("Santa Gertrudes", "Interior", 23611, None, None),
    ("Santa Isabel", "Grande SP", 53174, None, None),
    ("Santa Lúcia", "Interior", 7149, None, None),
    ("Santa Maria da Serra", "Interior", 5243, None, None),
    ("Santa Mercedes", "Interior", 2956, None, None),
    ("Santa Rita d\'Oeste", "Interior", 2733, None, None),
    ("Santa Rita do Passa Quatro", "Interior", 24833, None, None),
    ("Santa Rosa de Viterbo", "Interior", 23411, None, None),
    ("Santa Salete", "Interior", 1645, None, None),
    ("Santana da Ponte Pensa", "Interior", 1670, None, None),
    ("Santana de Parnaíba", "Grande SP", 154105, None, None),
    ("Santo Anastácio", "Interior", 17963, None, None),
    ("Santo André", "Grande SP", 748919, None, None),
    ("Santo Antônio da Alegria", "Interior", 6775, None, None),
    ("Santo Antônio de Posse", "Interior", 23244, None, None),
    ("Santo Antônio do Aracanguá", "Interior", 8379, None, None),
    ("Santo Antônio do Jardim", "Interior", 6126, None, None),
    ("Santo Antônio do Pinhal", "Vale do Paraíba", 7133, None, None),
    ("Santo Expedito", "Interior", 3000, None, None),
    ("Santos", "Grande SP", 418608, None, None),
    ("Santópolis do Aguapeí", "Interior", 3899, None, None),
    ("Sarapuí", "Interior", 10369, None, None),
    ("Sarutaiá", "Interior", 3704, None, None),
    ("Sebastianópolis do Sul", "Interior", 3130, None, None),
    ("Serra Azul", "Interior", 12746, None, None),
    ("Serra Negra", "Interior", 29894, None, None),
    ("Serrana", "Interior", 43909, None, None),
    ("Sertãozinho", "Interior", 126887, None, None),
    ("Sete Barras", "Litoral", 12730, None, None),
    ("Severínia", "Interior", 14576, None, None),
    ("Silveiras", "Vale do Paraíba", 6186, None, None),
    ("Socorro", "Interior", 40122, None, None),
    ("Sorocaba", "Interior", 723682, None, None),
    ("Sud Mennucci", "Interior", 7355, None, None),
    ("Sumaré", "Interior", 279545, None, None),
    ("Suzano", "Grande SP", 307429, None, None),
    ("Suzanápolis", "Interior", 3408, None, None),
    ("São Bento do Sapucaí", "Vale do Paraíba", 11674, None, None),
    ("São Bernardo do Campo", "Grande SP", 810729, None, None),
    ("São Caetano do Sul", "Grande SP", 165655, None, None),
    ("São Carlos", "Interior", 254857, None, None),
    ("São Francisco", "Interior", 2602, None, None),
    ("São Joaquim da Barra", "Interior", 48558, None, None),
    ("São José da Bela Vista", "Interior", 7626, None, None),
    ("São José do Barreiro", "Vale do Paraíba", 3853, None, None),
    ("São José do Rio Pardo", "Interior", 52205, None, None),
    ("São José do Rio Preto", "Interior", 480393, None, None),
    ("São José dos Campos", "Vale do Paraíba", 697054, None, None),
    ("São João da Boa Vista", "Interior", 92547, None, None),
    ("São João das Duas Pontes", "Interior", 2580, None, None),
    ("São João de Iracema", "Interior", 1846, None, None),
    ("São João do Pau d\'Alho", "Interior", 2242, None, None),
    ("São Lourenço da Serra", "Grande SP", 16067, None, None),
    ("São Luiz do Paraitinga", "Vale do Paraíba", 10337, None, None),
    ("São Manuel", "Interior", 37289, None, None),
    ("São Miguel Arcanjo", "Interior", 32039, None, None),
    ("São Paulo", "Grande SP", 11451999, None, None),
    ("São Pedro", "Interior", 38256, None, None),
    ("São Pedro do Turvo", "Interior", 7217, None, None),
    ("São Roque", "Interior", 79484, None, None),
    ("São Sebastião", "Vale do Paraíba", 81595, None, None),
    ("São Sebastião da Grama", "Interior", 10441, None, None),
    ("São Simão", "Interior", 13442, None, None),
    ("São Vicente", "Grande SP", 329911, None, None),
    ("Tabapuã", "Interior", 11323, None, None),
    ("Tabatinga", "Interior", 14769, None, None),
    ("Taboão da Serra", "Grande SP", 273542, None, None),
    ("Taciba", "Interior", 6260, None, None),
    ("Taguaí", "Interior", 12669, None, None),
    ("Taiaçu", "Interior", 5677, None, None),
    ("Taiúva", "Interior", 6548, None, None),
    ("Tambaú", "Interior", 21435, None, None),
    ("Tanabi", "Interior", 25265, None, None),
    ("Tapiratiba", "Interior", 11816, None, None),
    ("Tapiraí", "Interior", 7996, None, None),
    ("Taquaral", "Interior", 2619, None, None),
    ("Taquaritinga", "Interior", 52260, None, None),
    ("Taquarituba", "Interior", 24350, None, None),
    ("Taquarivaí", "Interior", 6876, None, None),
    ("Tarabai", "Interior", 6536, None, None),
    ("Tarumã", "Interior", 14882, None, None),
    ("Tatuí", "Interior", 123942, None, None),
    ("Taubaté", "Vale do Paraíba", 310739, None, None),
    ("Tejupá", "Interior", 4127, None, None),
    ("Teodoro Sampaio", "Interior", 22173, None, None),
    ("Terra Roxa", "Interior", 7904, None, None),
    ("Tietê", "Interior", 37663, None, None),
    ("Timburi", "Interior", 2464, None, None),
    ("Torre de Pedra", "Interior", 2046, None, None),
    ("Torrinha", "Interior", 9335, None, None),
    ("Trabiju", "Interior", 1682, None, None),
    ("Tremembé", "Vale do Paraíba", 51173, None, None),
    ("Três Fronteiras", "Interior", 6804, None, None),
    ("Tuiuti", "Interior", 6778, None, None),
    ("Tupi Paulista", "Interior", 15854, None, None),
    ("Tupã", "Interior", 63928, None, None),
    ("Turiúba", "Interior", 1818, None, None),
    ("Turmalina", "Interior", 1669, None, None),
    ("Ubarana", "Interior", 5365, None, None),
    ("Ubatuba", "Vale do Paraíba", 92981, None, None),
    ("Ubirajara", "Interior", 5132, None, None),
    ("Uchoa", "Interior", 10394, None, None),
    ("União Paulista", "Interior", 1603, None, None),
    ("Uru", "Interior", 1387, None, None),
    ("Urupês", "Interior", 13744, None, None),
    ("Urânia", "Interior", 8833, None, None),
    ("Valentim Gentil", "Interior", 14098, None, None),
    ("Valinhos", "Interior", 126373, None, None),
    ("Valparaíso", "Interior", 24241, None, None),
    ("Vargem", "Interior", 10512, None, None),
    ("Vargem Grande Paulista", "Grande SP", 50415, None, None),
    ("Vargem Grande do Sul", "Interior", 40133, None, None),
    ("Vera Cruz", "Interior", 10176, None, None),
    ("Vinhedo", "Interior", 76540, None, None),
    ("Viradouro", "Interior", 17414, None, None),
    ("Vista Alegre do Alto", "Interior", 8109, None, None),
    ("Vitória Brasil", "Interior", 1794, None, None),
    ("Votorantim", "Interior", 127923, None, None),
    ("Votuporanga", "Interior", 96634, None, None),
    ("Várzea Paulista", "Interior", 115771, None, None),
    ("Zacarias", "Interior", 2692, None, None),
    ("Águas da Prata", "Interior", 7369, None, None),
    ("Águas de Lindóia", "Interior", 17930, None, None),
    ("Águas de Santa Bárbara", "Interior", 7177, None, None),
    ("Águas de São Pedro", "Interior", 2780, None, None),
    ("Álvares Florence", "Interior", 3915, None, None),
    ("Álvares Machado", "Interior", 27255, None, None),
    ("Álvaro de Carvalho", "Interior", 4808, None, None),
    ("Óleo", "Interior", 2512, None, None),
]


# Mayors — eleições municipais outubro 2024, mandato 2025-2028
# (name, party, term_start, term_end)
MAYORS_DATA = {
    "São Paulo": ("Ricardo Nunes", "MDB", 2025, 2028),
    "Guarulhos": ("Gustavo Henric Costa", "PP", 2025, 2028),
    "Campinas": ("Dário Saadi", "REPUBLICANOS", 2025, 2028),
    "São Bernardo do Campo": ("Marcelo Lima", "PODE", 2025, 2028),
    "São José dos Campos": ("Anderson Farias", "PP", 2025, 2028),
    "Santo André": ("Gilvan Junior", "SD", 2025, 2028),
    "Osasco": ("Rogério Lins", "PODE", 2025, 2028),
    "Sorocaba": ("Rodrigo Manga", "REPUBLICANOS", 2025, 2028),
    "Ribeirão Preto": ("Eduardo Lacera", "PSD", 2025, 2028),
    "Mauá": ("Marcelo Oliveira", "PT", 2025, 2028),
    "Mogi das Cruzes": ("Caio Cunha", "PODE", 2025, 2028),
    "São José do Rio Preto": ("Edinho Araújo", "MDB", 2025, 2028),
    "Diadema": ("José de Filippi", "PT", 2025, 2028),
    "Jundiaí": ("Gustavo Martinelli", "MDB", 2025, 2028),
    "Piracicaba": ("Luciano Almeida", "MDB", 2025, 2028),
    "Carapicuíba": ("Marcos Neves", "MDB", 2025, 2028),
    "Bauru": ("Suéllen Rosim", "REPUBLICANOS", 2025, 2028),
    "Santos": ("Lucas Mangas Bigi", "PL", 2025, 2028),
    "Mogi Guaçu": ("Walter Caveanha", "REPUBLICANOS", 2025, 2028),
    "Praia Grande": ("Carlos Persuhn", "PP", 2025, 2028),
    "Taubaté": ("Ortiz Junior", "PSD", 2025, 2028),
    "Franca": ("Alexandre Ferreira", "MDB", 2025, 2028),
    "Limeira": ("Denis Andia", "PL", 2025, 2028),
    "São Carlos": ("Netto Donato", "PSDB", 2025, 2028),
    "Americana": ("Chico Sardelli", "PL", 2025, 2028),
    "Araraquara": ("Edson Antonio Martins", "MDB", 2025, 2028),
    "Jacareí": ("Lucas Storino", "PSDB", 2025, 2028),
    "Presidente Prudente": ("Eduardo Albertassi", "MDB", 2025, 2028),
    "Marília": ("Daniel Alonso", "PODE", 2025, 2028),
    "São Vicente": ("Robson Rodrigues da Fonseca", "PSD", 2025, 2028),
}

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
    1: [  # Educação Pública com Efetividade, Qualidade e Acesso Ampliados
        ("Alcançar Índice de 42% de Estudantes com Nota Superior a 5 no Provão Paulista, mediante a Implantação dos Programas Sala do Futuro e Aluno Presente", "estudantes com nota <5", 94, 94, "2026-12", "A"),
        ("Ampliar a Oferta de Ensino Técnico Integrado na Rede Estadual, Alcançando 210 mil Vagas, com Programa Educação Profissional Paulista", "estudantes no EM integrado", 465000, 445200, "2026-12", "A"),
        ("Fortalecer a Cooperação com 100% dos Municípios Paulistas - Alfabetiza SP", "municípios atendidos", 645, 645, "2026-12", "A"),
        ("Instalar Salas de Recursos ou Espaços Multiuso em 2300 Escolas Estaduais, Garantindo a Implantação da Política de Educação Especial em Toda a Rede Estadual", "escolas com sala de recurso", 2300, 4675, "2026-12", "A"),
        ("Ofertar 187 mil Bolsas de Estudo em Programas de Extensão Curricular para Atender os Estudantes da Rede Estadual Buscando a Melhoria do Desempenho e Frequência Escolar", "estudantes participantes", 187000, 22792, "2026-12", "B"),
        ("Qualificar a Gestão de Pessoas da Secretaria da Educação", "servidores com gratificação", 78640, 60948, "2026-12", "B"),
        ("Realizar 3.050 Intervenções de Estrutura Física na Rede Estadual de Ensino", "intervenções em escolas", 3050, 4152, "2026-12", "A"),
        ("Fortalecer a Autogestão Escolar, com Participação da Comunidade, por meio do Programa Dinheiro Direto na Escola - PDDE", "APM com 50% recurso executado", 87, 87, "2026-12", "B"),
        ("Alcançar 92% de Jovens em Medidas Socioeducativas e Cautelar Certificados em Cursos de Qualificação Profissional, Mediante o Atendimento Integral à Educação", "% de adolescentes qualificados", 17, 17, "2026-12", "A"),
        ("Implantar as Ações de Melhoria da Convivência e Proteção Escolar em 4.800 Escolas da Rede Estadual", "escolas assistidas", 4800, 4981, "2026-12", "B"),
        ("Aperfeiçoar os Programas de Ensino Integral, ampliando a Oferta e Alcançando 1 Milhão de Estudantes", "estudantes em jornada integral", 1000000, 892041, "2026-12", "A"),
        ("Implantar o Programa Escolas Cívico-Militares", "escolas ativas no programa", 100, 100, "2026-12", "C"),
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
            progress = min(100.0, round((actual / planned * 100) if planned > 0 else 0, 1))

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


def _do_seed_geo(db: Session):
    """Seed mayors and municipalities (can be called standalone to reseed geo data)."""
    print("Seeding mayors and municipalities...")
    mayors_by_city = {}
    for city_name, (m_name, m_party, m_start, m_end) in MAYORS_DATA.items():
        mayor = Mayor(name=m_name, party=m_party, term_start=m_start, term_end=m_end)
        db.add(mayor)
        mayors_by_city[city_name] = mayor
    db.flush()

    municipalities = []
    for mname, region, pop, lat, lng in MUNICIPALITIES_DATA:
        mayor = mayors_by_city.get(mname)
        mun = Municipality(
            name=mname,
            region=region,
            population=pop,
            lat=lat,
            lng=lng,
            mayor_id=mayor.id if mayor else None,
        )
        db.add(mun)
        municipalities.append(mun)
    db.flush()
    return mayors_by_city, municipalities


def seed_all():
    # Create tables
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()

    try:
        # Check idempotency for main data
        if db.query(Deputy).count() > 0:
            # Auto-migrate: if municipalities < 600, truncate geo data and reseed
            mun_count = db.query(Municipality).count()
            if mun_count < 600:
                print(f"Found only {mun_count} municipalities. Truncating and reseeding geo data...")
                db.execute(text("DELETE FROM amendments"))
                db.execute(text("DELETE FROM budget_items WHERE mayor_id IS NOT NULL"))
                db.execute(text("DELETE FROM municipalities"))
                db.execute(text("DELETE FROM mayors"))
                db.commit()
                # Fall through to reseed municipalities/mayors below
                _do_seed_geo(db)
                db.commit()
                print("Geo data reseeded.")
            # Check if metas need seeding separately
            elif db.query(GoalGroup).count() == 0:
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

        mayors_by_city, municipalities = _do_seed_geo(db)

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
        for city_name, mayor in mayors_by_city.items():
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
