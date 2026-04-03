"""
Seed script for Casa Civil SP database.
Idempotent: checks if data exists before inserting.
"""
import os
import sys
import random
from sqlalchemy.orm import Session

# Ensure app is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, SessionLocal
from app.models import Base, Deputy, Municipality, Mayor, Amendment, Secretariat, BudgetItem, Program

# ---------------------------------------------------------------------------
# Raw data
# ---------------------------------------------------------------------------

DEPUTIES_DATA = [
    ("Agente Federal Danilo Balas", "PL", 94552, 300607, 48, False, 2, "/biografia/fotos/300607/678129ff534ded49f5d96881ab26868b6170b40819639502898b48ee6030c787.jpeg"),
    ("Alex Madureira", "PL", 74340, 300608, 77, False, 2, "/biografia/fotos/20230302-145402-id=546-GRD.jpg"),
    ("Altair Moraes", "REPUBLICANOS", 98515, 300609, 45, False, 2, "/biografia/fotos/20230315-141411-id=545-GRD.jpeg"),
    ("Ana Carolina Serra", "CIDADANIA", 195436, 300657, 10, False, 1, "/biografia/fotos/20230315-163915-id=1622-GRD.jpeg"),
    ("Ana Perugini", "PT", 79061, 300466, 70, False, 3, "/biografia/fotos/20230320-180813-id=81-GRD.jpg"),
    ("Analice Fernandes", "PSD", 90135, 300431, 55, False, 6, "/biografia/fotos/300431/69142319ee3fc052a205d625527ba5a8de9faa52aa1b643a8b3c0f41f886e1a7.jpeg"),
    ("André Bueno", "PL", 61953, 300694, 98, False, 1, "/biografia/fotos/300694/e887523d7aec18236fb4b9da8ef2e63fd9c728bc645aa04c5c1131fa9f4fd2c5.jpeg"),
    ("André do Prado", "PL", 216268, 300497, 7, False, 4, "/biografia/fotos/300497/2f42bf3f57458a3a37942214178dfc3d890395c8884ceb9979a0aea6f0a1850c.jpeg"),
    ("Andréa Werner", "PSB", 88820, 300658, 56, False, 1, "/biografia/fotos/300658/ec8711d9e474223bd1fdb27dbaff6fb7cab4ecb03d9f34023706fb4734e2868d.jpeg"),
    ("Atila Jacomussi", "UNIÃO", 58707, 300537, 89, False, 2, "/biografia/fotos/20230315-170109-id=265-GRD.jpg"),
    ("Barros Munhoz", "PSD", 86372, 300188, 58, False, 7, "/biografia/fotos/300188/c5f99a2bc1c4d2dfe5d72c8a24e6b9a242b03d5b61314284be308fee932813a6.jpeg"),
    ("Beth Sahão", "PT", 65407, 300435, 83, False, 6, "/biografia/fotos/20230317-110718-id=31-GRD.jpeg"),
    ("Bruna Furlan", "PSDB", 195436, 300659, 13, False, 1, "/biografia/fotos/20230315-170525-id=1641-GRD.jpeg"),
    ("Bruno Zambelli", "PL", 235305, 300660, 4, False, 1, "/biografia/fotos/20230511-162900-id=1644-GRD.jfif"),
    ("Caio França", "PSB", 105173, 300540, 43, False, 3, "/biografia/fotos/20230321-190741-id=267-GRD.jpg"),
    ("Capitão Telhada", "PP", 83438, 300661, 62, False, 1, "/biografia/fotos/20230315-173219-id=1648-GRD.png"),
    ("Carla Morando", "PSDB", 177773, 300614, 18, False, 2, "/biografia/fotos/20230315-142108-id=540-GRD.jpeg"),
    ("Carlão Pignatari", "PSD", 105245, 300499, 42, False, 4, "/biografia/fotos/300499/9717fd9e32cdb65c43f9558978d7a440bc407b053773de388c2f6f345989eba6.jpeg"),
    ("Carlos Giannazi", "PSOL", 276811, 300485, 2, False, 5, "/biografia/fotos/20230321-191048-id=148-GRD.jpg"),
    ("Clarice Ganem", "PODE", 59342, 300662, 87, False, 1, "/biografia/fotos/300662/d9362d62e29435984b085411f9c8dd4f482f95db5b129c476778773a9d4a0cd8.jpeg"),
    ("Conte Lopes", "PL", 192454, 300205, 14, False, 8, "/biografia/fotos/20230316-173502-id=180-GRD.jpg"),
    ("Dani Alonso", "PL", 80337, 300663, 69, False, 1, "/biografia/fotos/20230315-171350-id=1653-GRD.jpeg"),
    ("Daniel Soares", "UNIÃO", 81753, 300619, 68, False, 2, "/biografia/fotos/20230315-142647-id=535-GRD.jpg"),
    ("Danilo Campetti", "REPUBLICANOS", 52393, 300696, 108, False, 1, "/biografia/fotos/300696/a52f2209112bbe99acc4cb25b6f0c27e2a5367f51dec72159d16e452dc0e0417.jpeg"),
    ("Delegada Graciela", "PL", 68955, 300620, 79, False, 2, "/biografia/fotos/300620/b725bb9f2b1a490e2e6b490ae913be604ec542b36f1375ded387ba72d391e184.jpeg"),
    ("Delegado Olim", "PP", 201348, 300543, 9, False, 3, "/biografia/fotos/20230321-191240-id=263-GRD.jpg"),
    ("Dirceu Dalben", "PSD", 93397, 300650, 49, False, 2, "/biografia/fotos/20230324-122116-id=561-GRD.png"),
    ("Donato", "PT", 88022, 300664, 57, False, 1, "/biografia/fotos/20230321-130104-id=1655-GRD.png"),
    ("Dr. Eduardo Nóbrega", "PODE", 53607, 300665, 91, False, 1, "/biografia/fotos/20230315-171633-id=1657-GRD.jpg"),
    ("Dr. Elton", "UNIÃO", 46042, 300666, 120, False, 1, ""),
    ("Dr. Jorge do Carmo", "PT", 82054, 300623, 66, False, 2, "/biografia/fotos/20190315-162558-id=531-GRD.jpg"),
    ("Ediane Maria", "PSOL", 175617, 300667, 20, False, 1, "/biografia/fotos/20230427-144843-id=1654-GRD.jpg"),
    ("Edna Macedo", "REPUBLICANOS", 82932, 300318, 63, False, 4, "/biografia/fotos/20190315-152242-id=516-GRD.jpeg"),
    ("Edson Giriboni", "UNIÃO", 59087, 300449, 88, False, 5, "/biografia/fotos/300449/280f76c24a7653fb998a3811f59dbf282857f0f814f00ebc8dc51230dd9bcb70.jpeg"),
    ("Eduardo Suplicy", "PT", 807015, 300693, 1, False, 2, "/biografia/fotos/20230321-191506-id=987-GRD.jpg"),
    ("Emídio de Souza", "PT", 157834, 300395, 22, False, 5, "/biografia/fotos/20230315-145500-id=517-GRD.jpg"),
    ("Enio Tatto", "PT", 142785, 300440, 26, False, 6, "/biografia/fotos/20191112-192019-id=175-GRD.jpg"),
    ("Fabiana Bolsonaro", "PL", 65497, 300668, 82, False, 1, ""),
    ("Fábio Faria de Sá", "PODE", 51948, 300669, 111, False, 1, "/biografia/fotos/300669/c3164700a1d9a520ce2bd91f02475ecf7392825cc642755ced7be33b02771720.jpeg"),
    ("Felipe Franco", "UNIÃO", 90440, 300622, 54, False, 1, "/biografia/fotos/20200819-200938-id=532-GRD.jpeg"),
    ("Gil Diniz Bolsonaro", "PL", 196215, 300670, 12, False, 1, "/biografia/fotos/20230321-130525-id=1650-GRD.jpg"),
    ("Gilmaci Santos", "REPUBLICANOS", 96361, 300671, 47, False, 1, "/biografia/fotos/20230315-170849-id=1649-GRD.jpeg"),
    ("Guilherme Cortez", "PSOL", 45094, 300672, 121, False, 1, "/biografia/fotos/20230321-130905-id=1646-GRD.jpg"),
    ("Guto Zacarias", "MISSÃO", 152481, 300624, 24, False, 2, "/biografia/fotos/20191112-191414-id=530-GRD.jpg"),
    ("Itamar Borges", "MDB", 183480, 300625, 15, False, 1, "/biografia/fotos/20191114-174133-id=529-GRD.jpg"),
    ("Jorge Caruso", "MDB", 82209, 300626, 64, False, 1, "/biografia/fotos/20191112-192211-id=528-GRD.jpg"),
    ("Jorge Wilson Xerife do Consumidor", "REPUBLICANOS", 177614, 300627, 19, False, 2, "/biografia/fotos/300627/66d82bc48da44e2c5448551d036be98f99cfd27fb168bb98f10282156ae1b532.jpeg"),
    ("Leci Brandão", "PCdoB", 90496, 300513, 53, False, 4, "/biografia/fotos/20230718-161931-id=38-GRD.jpg"),
    ("Léo Oliveira", "MDB", 82145, 300264, 65, False, 5, "/biografia/fotos/300264/4480e5e51c390cae6caaa26e6692a785b08df07ff7caaed48d4a351f44e60171.jpeg"),
    ("Leonardo Siqueira", "NOVO", 90688, 300675, 51, False, 1, "/biografia/fotos/20230321-192007-id=1642-GRD.png"),
    ("Letícia Aguiar", "PL", 68556, 300631, 80, False, 2, "/biografia/fotos/20230315-150330-id=523-GRD.jpg"),
    ("Lucas Bove", "PL", 130451, 300676, 31, False, 1, "/biografia/fotos/20230315-170418-id=1640-GRD.jpg"),
    ("Luiz Claudio Marcolino", "PT", 70487, 300514, 78, False, 2, "/biografia/fotos/20230529-131249-id=1637-GRD.jpeg"),
    ("Luiz Fernando T. Ferreira", "PT", 141017, 300545, 27, False, 3, "/biografia/fotos/300545/b25d811e25a8378431dcab7c7b0e4fdb0e0a4989c68c339ba40d03c99abc2019.jpeg"),
    ("Major Mecca", "PL", 224462, 300633, 5, False, 2, "/biografia/fotos/20230322-111405-id=521-GRD.jpeg"),
    ("Marcelo Aguiar", "PL", 42898, 300698, 133, False, 1, "/biografia/fotos/300698/ef72b1b9553180987d06d13e9bb6d8e85e7b2555af8ae381438f8148f37ff6de.jpeg"),
    ("Márcia Lia", "PT", 108587, 300534, 39, False, 3, "/biografia/fotos/20230802-131346-id=281-GRD.jpg"),
    ("Marcio Nakashima", "PSD", 0, 300635, 0, True, 2, "/biografia/fotos/300635/e9bff5d91c252b6c5055f1d7e8fc6742223d6af479becb1f88a008887e4df549.jpeg"),
    ("Marco Aurelio Costa", "PP", 62483, 300636, 84, False, 1, "/biografia/fotos/20230802-132042-id=562-GRD.jpg"),
    ("Marcola Marinho", "UNIÃO", 83543, 300637, 61, False, 1, "/biografia/fotos/20230315-143154-id=536-GRD.jpg"),
    ("Marcos Damasio", "PL", 121289, 300638, 34, False, 2, "/biografia/fotos/20230323-095827-id=525-GRD.jpg"),
    ("Mario Covas Neto", "PSDB", 126882, 300641, 32, False, 2, "/biografia/fotos/300641/e3a9d7a84b3a9f0f9a1ed45ac6e8a4b60c59b0e7c9d0f35c42e218e7a4c1e8b.jpeg"),
    ("Milton Vieira Filho", "REPUBLICANOS", 113671, 300483, 38, False, 5, "/biografia/fotos/20230315-155218-id=148-GRD.jpg"),
    ("Morando", "PSDB", 168017, 300643, 21, False, 3, "/biografia/fotos/20230315-143720-id=533-GRD.jpg"),
    ("Murilo Busarello", "PODE", 66038, 300644, 81, False, 1, "/biografia/fotos/20230323-164427-id=566-GRD.jpg"),
    ("Nabil Bonduki", "PT", 89503, 300695, 52, False, 1, "/biografia/fotos/300695/7d1d3e71c5a24d2d5dddb9a1e52f6d31c1c71bba4e91ad4daed8a6da29c7e0a.jpeg"),
    ("Nonato", "PSD", 0, 300697, 0, True, 1, ""),
    ("Olim Filho", "PP", 115217, 300645, 37, False, 3, "/biografia/fotos/20230315-155823-id=560-GRD.jpg"),
    ("Orlando Morando", "PSDB", 142008, 300506, 28, False, 4, "/biografia/fotos/20230315-160254-id=153-GRD.jpg"),
    ("Paulo Fiorilo", "PT", 134441, 300471, 30, False, 7, "/biografia/fotos/20230315-161523-id=78-GRD.jpg"),
    ("Paulo Rodrigues", "REPUBLICANOS", 77524, 300648, 72, False, 1, "/biografia/fotos/20230321-132338-id=1643-GRD.jpeg"),
    ("Pedro Ichihara", "PODE", 115688, 300646, 36, False, 1, "/biografia/fotos/20230802-133053-id=568-GRD.jpg"),
    ("Projeto de Lei", "PL", 65392, 300699, 83, False, 1, ""),
    ("Rafa Zimbaldi", "CIDADANIA", 314213, 300492, 3, False, 3, "/biografia/fotos/20230315-162055-id=135-GRD.jpg"),
    ("Rafael Saraiva", "UNIÃO", 76312, 300651, 74, False, 1, "/biografia/fotos/20230315-163143-id=539-GRD.jpg"),
    ("Rednex Caires", "AVANTE", 63498, 300700, 86, False, 1, "/biografia/fotos/300700/ab7e2f9a5b7a4df5b49e8c3fd6a45d9a3e6f8b0d1a4e7c9b2d3e5f6a7b8c9d0.jpeg"),
    ("Reinaldo Alguz", "AVANTE", 56983, 300701, 94, False, 1, ""),
    ("Ricardo Madalena", "PL", 152313, 300703, 23, False, 2, "/biografia/fotos/300703/1a2b3c4d5e6f7890abcdef1234567890abcdef1234567890abcdef1234567890.jpeg"),
    ("Roberto Engler", "PL", 96403, 300647, 46, False, 2, "/biografia/fotos/20230315-165110-id=547-GRD.jpeg"),
    ("Rogério Santos", "PSD", 0, 300702, 0, True, 1, ""),
    ("Rubão", "PT", 100459, 300383, 44, False, 6, "/biografia/fotos/20230315-165740-id=513-GRD.jpg"),
    ("Samuel Higa", "PL", 107536, 300649, 41, False, 1, "/biografia/fotos/20230315-170124-id=565-GRD.jpg"),
    ("Sergio Lapena", "MDB", 88534, 300652, 55, False, 1, "/biografia/fotos/20230316-111953-id=560-GRD.jpg"),
    ("Simão Pedro", "PT", 85369, 300511, 59, False, 4, "/biografia/fotos/20230315-165428-id=148-GRD.jpg"),
    ("Sonaira Fernandes", "PL", 100756, 300689, 43, False, 2, "/biografia/fotos/20230315-165942-id=534-GRD.jpg"),
    ("Teonil Chaves", "AVANTE", 53792, 300704, 90, False, 1, ""),
    ("Thiago Auricchio", "PSD", 82519, 300508, 67, False, 3, "/biografia/fotos/20230315-171128-id=152-GRD.jpeg"),
    ("Vanderlei Cardoso", "PL", 146413, 300691, 25, False, 2, "/biografia/fotos/20230315-171358-id=548-GRD.jpeg"),
    ("Vinícius Camarinha", "PSB", 114685, 300655, 37, False, 2, "/biografia/fotos/20230315-171601-id=538-GRD.jpg"),
    ("Welington Fingenti", "MDB", 121289, 300653, 35, False, 2, "/biografia/fotos/20230321-191839-id=529-GRD.jpg"),
    ("Wesley Trajano", "REPUBLICANOS", 68782, 300705, 80, False, 1, ""),
    ("William Siqueira", "PL", 73682, 300706, 78, False, 1, ""),
]

MUNICIPALITIES_DATA = [
    # (name, region, population)
    ("São Paulo", "Grande SP", 12396372),
    ("Campinas", "Interior", 1223237),
    ("Santos", "Litoral", 433311),
    ("Ribeirão Preto", "Interior", 720294),
    ("Sorocaba", "Interior", 702490),
    ("São Bernardo do Campo", "Grande SP", 844483),
    ("Guarulhos", "Grande SP", 1379182),
    ("Osasco", "Grande SP", 700682),
    ("São José dos Campos", "Vale do Paraíba", 750183),
    ("Bauru", "Interior", 380442),
    ("Piracicaba", "Interior", 415458),
    ("São José do Rio Preto", "Interior", 466981),
    ("Mauá", "Grande SP", 478564),
    ("Mogi das Cruzes", "Grande SP", 464886),
    ("Diadema", "Grande SP", 424058),
    ("Carapicuíba", "Grande SP", 396973),
    ("Jundiaí", "Interior", 432242),
    ("Franca", "Interior", 360022),
    ("Presidente Prudente", "Interior", 234003),
    ("Marília", "Interior", 240032),
]

MAYORS_DATA = [
    # (name, party, term_start, term_end) — in same order as municipalities
    ("Ricardo Nunes", "MDB", 2021, 2024),
    ("Dário Saadi", "REPUBLICANOS", 2021, 2024),
    ("Rogério Santos", "PSDB", 2021, 2024),
    ("Eduardo Lacerda", "PSD", 2021, 2024),
    ("Rodrigo Manga", "REPUBLICANOS", 2021, 2024),
    ("Orlando Morando", "PSDB", 2021, 2024),
    ("Guti", "PSD", 2021, 2024),
    ("Rogério Lins", "PODE", 2021, 2024),
    ("Anderson Farias", "PP", 2021, 2024),
    ("Suéllen Rosim", "REPUBLICANOS", 2021, 2024),
    ("Luciano Almeida", "MDB", 2021, 2024),
    ("Edinho Araújo", "MDB", 2021, 2024),
    ("Marcelo Oliveira", "PT", 2021, 2024),
    ("Caio Cunha", "PODE", 2021, 2024),
    ("José de Filippi", "PT", 2021, 2024),
    ("Marcos Neves", "MDB", 2021, 2024),
    ("Luiz Fernando Machado", "PSDB", 2021, 2024),
    ("Alexandre Ferreira", "MDB", 2021, 2024),
    ("Eduardo Albertassi", "MDB", 2021, 2024),
    ("Daniel Alonso", "PODE", 2021, 2024),
]

SECRETARIATS_DATA = [
    ("Secretaria de Educação", "SEDUC", "Renato Feder"),
    ("Secretaria de Saúde", "SES", "Eleuses Paiva"),
    ("Secretaria de Segurança Pública", "SSP", "Guilherme Derrite"),
    ("Secretaria de Infraestrutura e Meio Ambiente", "SIMA", "Natália Resende"),
    ("Secretaria de Desenvolvimento Regional", "SDR", "Marco Vinholi"),
    ("Secretaria de Fazenda", "SEFAZ", "Samuel Kinoshita"),
    ("Secretaria de Cultura e Economia Criativa", "SECE", "Marilia Marton"),
    ("Secretaria de Habitação", "SEHAB", "Marcelo Branco"),
    ("Secretaria de Agricultura", "SAA", "Itamar Borges"),
    ("Secretaria de Transportes Metropolitanos", "STM", "Diego Basei"),
]

# budget base values in billions
BUDGET_BASES = {
    "SEDUC": 70.0,
    "SES": 50.0,
    "SSP": 22.0,
    "SIMA": 15.0,
    "SDR": 12.0,
    "SEFAZ": 10.0,
    "SECE": 3.5,
    "SEHAB": 8.0,
    "SAA": 4.0,
    "STM": 18.0,
}

PROGRAMS_DATA = [
    ("Escola em Tempo Integral", "Ampliação da jornada escolar em período integral nas escolas estaduais de São Paulo.", 1, 2022, None, 4_800_000_000.0, "ativo"),
    ("Bolsa do Povo", "Programa de transferência de renda para famílias em situação de vulnerabilidade social.", 2, 2021, None, 2_100_000_000.0, "ativo"),
    ("Educação SP Digital", "Transformação digital das escolas estaduais com tablets, conectividade e formação docente.", 1, 2023, None, 1_200_000_000.0, "ativo"),
    ("Habita SP", "Programa habitacional para famílias de baixa renda com subsídios e parcerias com municípios.", 8, 2022, None, 3_400_000_000.0, "ativo"),
    ("Infra SP", "Modernização de rodovias, pontes e estrutura viária do estado de São Paulo.", 4, 2021, 2025, 6_700_000_000.0, "ativo"),
    ("Verde Perto", "Recuperação de áreas degradadas, reflorestamento e pagamento por serviços ambientais.", 4, 2022, 2024, 850_000_000.0, "concluido"),
    ("Agro São Paulo", "Fomento ao agronegócio familiar e modernização do setor rural paulista.", 9, 2023, None, 620_000_000.0, "ativo"),
    ("Metrô SP Expansão", "Expansão das linhas de metrô e trem metropolitano na Região Metropolitana de São Paulo.", 10, 2021, None, 12_500_000_000.0, "ativo"),
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
        for i, (mname, region, pop) in enumerate(MUNICIPALITIES_DATA):
            mun = Municipality(
                name=mname,
                region=region,
                population=pop,
                mayor_id=mayors[i].id,
            )
            db.add(mun)
            municipalities.append(mun)
        db.flush()

        print("Seeding secretariats...")
        secretariats = []
        for name, acronym, sec_name in SECRETARIATS_DATA:
            s = Secretariat(name=name, acronym=acronym, secretary_name=sec_name)
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
            base = BUDGET_BASES.get(sec.acronym, 10.0) * 1_000_000_000
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

        # ~55 amendments linking deputies to municipalities
        random.seed(99)
        amendment_combinations = set()
        count = 0
        while count < 55:
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
