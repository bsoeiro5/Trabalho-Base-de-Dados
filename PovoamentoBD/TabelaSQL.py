import pandas as pd
import sqlite3
import os

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'BaseDados.db')

def create_schema(conn):
    cursor = conn.cursor()
    tables = [
        "ContratoAdjudicatario", "Local", "Tipo", "CP",
        "Contrato", "Adjudicatario", "Adjudicante",
        "TipoProcedimento", "CPV", "TipoContrato", "AcordoQuadro",
        "Municipio", "Distrito", "Pais"
    ]
    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")

    sql_schema = """
    CREATE TABLE Pais (
        idPais INTEGER PRIMARY KEY AUTOINCREMENT,
        nome VARCHAR2(255) UNIQUE
    );
    CREATE TABLE Distrito (
        idDist INTEGER PRIMARY KEY AUTOINCREMENT,
        nome VARCHAR2(255),
        idPais INTEGER,
        FOREIGN KEY(idPais) REFERENCES Pais (idPais)
    );
    CREATE TABLE Municipio (
        idMun INTEGER PRIMARY KEY AUTOINCREMENT,
        nome VARCHAR2(255),
        idDist INTEGER,
        FOREIGN KEY(idDist) REFERENCES Distrito (idDist)
    );
    CREATE TABLE AcordoQuadro(
        idAcordo INTEGER PRIMARY KEY AUTOINCREMENT,
        descricao VARCHAR2(255) UNIQUE
    );
    CREATE TABLE TipoContrato(
        idTipoCont INTEGER PRIMARY KEY AUTOINCREMENT,
        descricao VARCHAR2(255) UNIQUE
    );
    CREATE TABLE CPV(
        idCPV INTEGER PRIMARY KEY AUTOINCREMENT,
        descricao VARCHAR2(255) UNIQUE
    );
    CREATE TABLE TipoProcedimento(
        idTipoProc INTEGER PRIMARY KEY AUTOINCREMENT,
        descricao VARCHAR2(255) UNIQUE
    );
    CREATE TABLE Adjudicante(
        idAdjudicante INTEGER PRIMARY KEY AUTOINCREMENT,
        nif INTEGER UNIQUE,
        designacao VARCHAR2(255)
    );
    CREATE TABLE Adjudicatario(
        idAdjudicatario INTEGER PRIMARY KEY AUTOINCREMENT,
        numFiscal TEXT UNIQUE,
        designacao VARCHAR2(255)
    );
    CREATE TABLE Contrato (
        idContrato INTEGER PRIMARY KEY,
        prazoExecucao INTEGER,
        precoContratual FLOAT,
        centralizado CHAR(3),
        fundamentacao VARCHAR2(255),
        objetoContrato VARCHAR2(255),
        dataPublicacao DATE,
        dataCelebracao DATE,
        idAcordo INTEGER,
        idTipoProc INTEGER,
        idAdjudicante INTEGER,
        FOREIGN KEY (idAdjudicante) REFERENCES Adjudicante (idAdjudicante),
        FOREIGN KEY (idAcordo) REFERENCES AcordoQuadro (idAcordo),
        FOREIGN KEY (idTipoProc) REFERENCES TipoProcedimento(idTipoProc)
    );
    CREATE TABLE ContratoAdjudicatario(
        idContrato INTEGER,
        idAdjudicatario INTEGER,
        PRIMARY KEY(idContrato,idAdjudicatario),
        FOREIGN KEY (idContrato) REFERENCES Contrato (idContrato),
        FOREIGN KEY (idAdjudicatario) REFERENCES Adjudicatario (idAdjudicatario)
    );
    CREATE TABLE Local(
        idContrato INTEGER,
        idMun INTEGER,
        PRIMARY KEY(idContrato,idMun),
        FOREIGN KEY (idContrato) REFERENCES Contrato (idContrato),
        FOREIGN KEY (idMun) REFERENCES Municipio (idMun)
    );
    CREATE TABLE Tipo(
        idContrato INTEGER,
        idTipoCont INTEGER,
        PRIMARY KEY(idContrato,idTipoCont),
        FOREIGN KEY (idContrato) REFERENCES Contrato (idContrato),
        FOREIGN KEY (idTipoCont) REFERENCES TipoContrato (idTipoCont)
    );
    CREATE TABLE CP(
        idContrato INTEGER,
        idCPV INTEGER,
        PRIMARY KEY(idContrato,idCPV),
        FOREIGN KEY (idContrato) REFERENCES Contrato (idContrato),
        FOREIGN KEY (idCPV) REFERENCES CPV (idCPV)
    );
    """
    cursor.executescript(sql_schema)
    conn.commit()
    print("Esquema criado.")

def get_or_create(cursor, table, column, value, parent_col=None, parent_id=None):
    if value is None or str(value).strip() == '' or str(value).lower() == 'nan':
        return None
    value = str(value).strip()
    query = f"SELECT rowid FROM {table} WHERE {column} = ?"
    args = [value]
    if parent_col and parent_id:
        query += f" AND {parent_col} = ?"
        args.append(parent_id)
    cursor.execute(query, args)
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        insert_query = f"INSERT INTO {table} ({column}"
        if parent_col:
            insert_query += f", {parent_col}"
        insert_query += ") VALUES (?"
        if parent_col:
            insert_query += ", ?"
        insert_query += ")"
        cursor.execute(insert_query, args)
        return cursor.lastrowid

def parse_entity(entity_str):
    if pd.isna(entity_str): return None, None
    parts = str(entity_str).split(' - ', 1)
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    return None, str(entity_str).strip()

def format_date(date_val):
    if pd.isna(date_val):
        return None
    return str(date_val)

def povoar_bd(file_path):
    if not os.path.exists(file_path):
        print(f"Ficheiro {file_path} nao encontrado.")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    create_schema(conn)

    if file_path.endswith('.xlsx'):
        df = pd.read_excel(file_path)
    else:
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding='latin1')
    
    count = 0
    for index, row in df.iterrows():
        try:
            id_acordo = get_or_create(cursor, 'AcordoQuadro', 'descricao', row['DescrAcordoQuadro'])
            id_tipo_proc = get_or_create(cursor, 'TipoProcedimento', 'descricao', row['tipoprocedimento'])
            
            local_str = str(row['localExecucao'])
            parts = [p.strip() for p in local_str.split(',')]
            id_pais = None
            id_dist = None
            id_mun = None
            if len(parts) >= 1:
                id_pais = get_or_create(cursor, 'Pais', 'nome', parts[0])
            if len(parts) >= 2 and id_pais:
                id_dist = get_or_create(cursor, 'Distrito', 'nome', parts[1], 'idPais', id_pais)
            if len(parts) >= 3 and id_dist:
                id_mun = get_or_create(cursor, 'Municipio', 'nome', parts[2], 'idDist', id_dist)
            
            nif_adj, nome_adj = parse_entity(row['adjudicante'])
            id_adjudicante = None
            if nif_adj:
                cursor.execute("SELECT idAdjudicante FROM Adjudicante WHERE nif = ?", (nif_adj,))
                res = cursor.fetchone()
                if res:
                    id_adjudicante = res[0]
                else:
                    cursor.execute("INSERT INTO Adjudicante (nif, designacao) VALUES (?, ?)", (nif_adj, nome_adj))
                    id_adjudicante = cursor.lastrowid

            data_pub = format_date(row['dataPublicacao'])
            data_cel = format_date(row['dataCelebracaoContrato'])

            cursor.execute("""
                INSERT OR IGNORE INTO Contrato (
                    idContrato, prazoExecucao, precoContratual, centralizado, 
                    fundamentacao, objetoContrato, dataPublicacao, dataCelebracao, 
                    idAcordo, idTipoProc, idAdjudicante
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row['idcontrato'], row['prazoExecucao'], row['precoContratual'], 
                row['ProcedimentoCentralizado'], row['fundamentacao'], row['objectoContrato'],
                data_pub, data_cel,
                id_acordo, id_tipo_proc, id_adjudicante
            ))
            
            nif_vend, nome_vend = parse_entity(row['adjudicatarios'])
            if nif_vend:
                cursor.execute("SELECT idAdjudicatario FROM Adjudicatario WHERE numFiscal = ?", (nif_vend,))
                res = cursor.fetchone()
                if res:
                    id_vend = res[0]
                else:
                    cursor.execute("INSERT INTO Adjudicatario (numFiscal, designacao) VALUES (?, ?)", (nif_vend, nome_vend))
                    id_vend = cursor.lastrowid
                cursor.execute("INSERT OR IGNORE INTO ContratoAdjudicatario (idContrato, idAdjudicatario) VALUES (?, ?)", (row['idcontrato'], id_vend))

            id_tipo_cont = get_or_create(cursor, 'TipoContrato', 'descricao', row['tipoContrato'])
            if id_tipo_cont:
                cursor.execute("INSERT OR IGNORE INTO Tipo (idContrato, idTipoCont) VALUES (?, ?)", (row['idcontrato'], id_tipo_cont))

            id_cpv = get_or_create(cursor, 'CPV', 'descricao', row['cpv'])
            if id_cpv:
                cursor.execute("INSERT OR IGNORE INTO CP (idContrato, idCPV) VALUES (?, ?)", (row['idcontrato'], id_cpv))

            if id_mun:
                cursor.execute("INSERT OR IGNORE INTO Local (idContrato, idMun) VALUES (?, ?)", (row['idcontrato'], id_mun))

            count += 1
            if count % 1000 == 0:
                conn.commit()

        except Exception as e:
            print(f"Erro na linha {index}: {e}")
            continue

    conn.commit()
    conn.close()
    print(f"Concluido. Total: {count}")

if __name__ == "__main__":
    xlsx_file = "ContratosPublicos2024.xlsx"
    if os.path.exists(xlsx_file):
        povoar_bd(xlsx_file)
    else:
        print(f"Ficheiro {xlsx_file} nao encontrado.")