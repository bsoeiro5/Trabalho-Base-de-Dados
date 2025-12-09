import pandas as pd
import sqlite3
import os

def create_schema(cur):
    sql_schema = """
    CREATE TABLE IF NOT EXISTS Pais (
        idPais INTEGER PRIMARY KEY,
        nome VARCHAR2(255)
    );

    CREATE TABLE IF NOT EXISTS Distrito (
        idDist INTEGER PRIMARY KEY,
        nome VARCHAR2(255),
        idPais INTEGER,
        FOREIGN KEY(idPais) REFERENCES Pais (idPais)
    );

    CREATE TABLE IF NOT EXISTS Municipio (
        idMun INTEGER PRIMARY KEY,
        nome VARCHAR2(255),
        idDist INTEGER, 
        FOREIGN KEY(idDist) REFERENCES Distrito (idDist)
    );

    CREATE TABLE IF NOT EXISTS AcordoQuadro(
        idAcordo INTEGER PRIMARY KEY,
        descricao VARCHAR2(255)
    );

    CREATE TABLE IF NOT EXISTS TipoContrato(
        idTipoCont INTEGER PRIMARY KEY,
        descricao VARCHAR2(255)
    );

    CREATE TABLE IF NOT EXISTS CPV(
        idCPV INTEGER PRIMARY KEY,
        descricao VARCHAR2(255)
    );

    CREATE TABLE IF NOT EXISTS TipoProcedimento(
        idTipoProc INTEGER PRIMARY KEY,
        descricao VARCHAR2(255)
    );

    CREATE TABLE IF NOT EXISTS Adjudicante(
        idAdjudicante INTEGER PRIMARY KEY,
        nif INTEGER,
        designacao VARCHAR2(255)
    );

    CREATE TABLE IF NOT EXISTS Adjudicatario(
        idAdjudicatario INTEGER PRIMARY KEY,
        numFiscal TEXT,
        designacao VARCHAR2(255)
    );

    CREATE TABLE IF NOT EXISTS Contrato (
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

    CREATE TABLE IF NOT EXISTS ContratoAdjudicatario(
        idContrato INTEGER,
        idAdjudicatario INTEGER,
        PRIMARY KEY(idContrato,idAdjudicatario),
        FOREIGN KEY (idContrato) REFERENCES Contrato (idContrato),
        FOREIGN KEY (idAdjudicatario) REFERENCES Adjudicatario (idAdjudicatario)
    );

    CREATE TABLE IF NOT EXISTS Local(
        idContrato INTEGER,
        idMun INTEGER,
        PRIMARY KEY(idContrato,idMun),
        FOREIGN KEY (idContrato) REFERENCES Contrato (idContrato),
        FOREIGN KEY (idMun) REFERENCES Municipio (idMun)
    );

    CREATE TABLE IF NOT EXISTS Tipo(
        idContrato INTEGER,
        idTipoCont INTEGER,
        PRIMARY KEY(idContrato,idTipoCont),
        FOREIGN KEY (idContrato) REFERENCES Contrato (idContrato),
        FOREIGN KEY (idTipoCont) REFERENCES TipoContrato (idTipoCont)
    );

    CREATE TABLE IF NOT EXISTS CP(
        idContrato INTEGER,
        idCPV INTEGER,
        PRIMARY KEY(idContrato,idCPV),
        FOREIGN KEY (idContrato) REFERENCES Contrato (idContrato),
        FOREIGN KEY (idCPV) REFERENCES CPV (idCPV)
    );
    """
    cur.executescript(sql_schema)

def Pais(pais:str,cur):
    cur.execute('SELECT idPais FROM Pais WHERE nome = ?', [pais])
    res = cur.fetchone()
    if res:
        return res[0]
    else:
        cur.execute('INSERT INTO Pais (nome) VALUES (?)', [pais])
        return cur.lastrowid
    
def Distrito(dist:str,idPais:int,cur):
    cur.execute('SELECT idDist FROM Distrito WHERE nome = ?', [dist])
    res = cur.fetchone()
    if res:
        return res[0]
    else:
        cur.execute('INSERT INTO Distrito (nome, idPais) VALUES (?, ?)', [dist,idPais])
        return cur.lastrowid
    
def Municipio(muni:str,idDist:int,cur):
    cur.execute('SELECT idMun FROM Municipio WHERE nome = ?', [muni])
    res = cur.fetchone()
    if res:
        return res[0]
    else:
        cur.execute('INSERT INTO Municipio (nome, idDist) VALUES (?, ?)', [muni,idDist])
        return cur.lastrowid

def NovoLocal(local: str, cur):
    groups = local.split('|')
    matriz = [list(map(str.strip, group.split(','))) for group in groups]
    idsMun = []

    for linha in matriz:
        if(len(linha) == 1):
            linha.append(linha[0])
            linha.append(linha[0])
        elif(len(linha) == 2):
            linha.append(linha[1])
        
        idPais = Pais(linha[0], cur)
        idDist = Distrito(linha[1], idPais, cur)
        idMuni = Municipio(linha[2], idDist, cur)
        idsMun.append(idMuni)
    return idsMun

def CPV(desc:str,cur):
    groups = desc.split('|')
    idsCPV = []
    for linha in groups:
        cur.execute('SELECT idCPV FROM CPV WHERE descricao = ?', [linha.strip()])
        res = cur.fetchone()
        if res: idsCPV.append(res[0])
        else: 
            cur.execute('INSERT INTO CPV (descricao) VALUES (?)', [linha.strip()])
            idsCPV.append(cur.lastrowid)
    return idsCPV

def TipoContrato(desc:str,cur):
    groups = desc.split('|')
    idsTipoCont = []
    for linha in groups:
        cur.execute('SELECT idTipoCont FROM TipoContrato WHERE descricao = ?', [linha.strip()])
        res = cur.fetchone()
        if res: idsTipoCont.append(res[0])
        else:
            cur.execute('INSERT INTO TipoContrato (descricao) VALUES (?)', [linha.strip()])
            idsTipoCont.append(cur.lastrowid)
    return idsTipoCont

def TipoProcedimento(desc:str,cur):
    cur.execute('SELECT idTipoProc FROM TipoProcedimento WHERE descricao = ?',[desc])
    res = cur.fetchone()
    if res: return res[0]
    else:
        cur.execute('INSERT INTO TipoProcedimento (descricao) VALUES (?)',[desc])
        return cur.lastrowid

def AcordoQuadro(desc,cur):
    if pd.isna(desc):
        cur.execute('SELECT idAcordo FROM AcordoQuadro WHERE descricao IS NULL')
    else:
        cur.execute('SELECT idAcordo FROM AcordoQuadro WHERE descricao = ?', [desc])
    res=cur.fetchone()

    if res: return res[0]
    else: 
        cur.execute('INSERT INTO AcordoQuadro (descricao) VALUES (?)',[desc])
        return cur.lastrowid

def Adjudicatario(dados,cur):
    idsAdjudicatario = []
    if pd.isna(dados):
        numFiscal = '0'
        designacao = 'Indeterminado'
        cur.execute('SELECT idAdjudicatario FROM Adjudicatario WHERE numFiscal = ? AND designacao = ?', [numFiscal, designacao])
        res = cur.fetchone()
        if res: idsAdjudicatario.append(res[0])
        else:
            cur.execute('INSERT INTO Adjudicatario (numFiscal, designacao) VALUES (?,?)', [numFiscal, designacao])
            idsAdjudicatario.append(cur.lastrowid)

    else:
        groups = dados.split('|')
        for linha in groups:
            linha = linha.split('-',maxsplit = 1)
            numFiscal, designacao = linha[0].strip(), linha[1].strip()

            cur.execute('SELECT idAdjudicatario FROM Adjudicatario WHERE numFiscal = ? AND designacao = ?', [numFiscal, designacao])
            res = cur.fetchone()
            if res: idsAdjudicatario.append(res[0])
            else:
                cur.execute('INSERT INTO Adjudicatario (numFiscal, designacao) VALUES (?,?)', [numFiscal, designacao])
                idsAdjudicatario.append(cur.lastrowid)
    return idsAdjudicatario

def Adjudicante(dados,cur):
    groups = dados.split('-',maxsplit = 1)
    nif, designacao = groups[0].strip(), groups[1].strip()
    cur.execute('SELECT idAdjudicante FROM Adjudicante WHERE nif = ? AND designacao = ?', [nif, designacao])
    res = cur.fetchone()
    if res: return res[0]
    else:
        cur.execute('INSERT INTO Adjudicante (nif, designacao) VALUES (?, ?)', [nif, designacao])
        return cur.lastrowid

def Contrato(idCont, dataPubl, dataCele, prazo, funda, centralizado, objetoContr, preco,idtipoProc,idacordoQuadro,idAdjudicante,cur):
    cur.execute('SELECT idContrato FROM Contrato WHERE idContrato = ?', [idCont])
    res = cur.fetchone()

    if res:
        return res[0]
    else:
        dataPubl = f"{dataPubl}"     
        dataCele = f"{dataCele}" 
        cur.execute('INSERT INTO Contrato (idContrato, prazoExecucao, precoContratual, centralizado, fundamentacao, objetoContrato, dataPublicacao, dataCelebracao,idAcordo,idTipoProc,idAdjudicante) VALUES (?,?,?,?,?,?,?,?,?,?,?)',
                    [idCont, prazo, preco, centralizado, funda, objetoContr, dataPubl, dataCele,idacordoQuadro,idtipoProc,idAdjudicante])
        return cur.lastrowid

def ContratoAdjudicatario(idContrato,idsAdjudicatario,cur):
    for idAdj in idsAdjudicatario:
        cur.execute('INSERT INTO ContratoAdjudicatario (idContrato,idAdjudicatario) VALUES (?,?)',[idContrato,idAdj])
        
def Local(idContrato,idsMun,cur):
    for idMun in idsMun:
        cur.execute('SELECT idContrato,idMun FROM Local WHERE idContrato = ? AND idMun = ?', [idContrato,idMun])
        res = cur.fetchone()
        if not res:
            cur.execute('INSERT INTO Local (idContrato,idMun) VALUES (?,?)',[idContrato,idMun])

def Tipo(idContrato,idsTipoCont,cur):
    for idTipoCont in idsTipoCont:
        cur.execute('INSERT INTO Tipo (idContrato,idTipoCont) VALUES (?,?)',[idContrato,idTipoCont])

def CP(idContrato,idsCPV,cur):
    for idCPV in idsCPV:
        cur.execute('INSERT INTO CP (idContrato,idCPV) VALUES (?,?)',[idContrato,idCPV])

def main():
    # Caminho absoluto para o teu ficheiro no Mac
    caminho = "/Users/bernardosoeiro/faculdade/2ano/1semestre/bdados/Trabalho-Base-de-Dados/ContratosPublicos2024.xlsx"
        
    try:
        df = pd.read_excel(caminho)
    except FileNotFoundError:
        print(f"ERRO CRÍTICO: Não foi possível encontrar o ficheiro em:\n{caminho}")
        print("Confirma se o nome do ficheiro está correto na pasta.")
        return

    # Garante que cria a DB no mesmo local onde o script está a correr, ou num caminho específico
    # Se quiseres a DB na mesma pasta do Excel:
    caminho_db = "/Users/bernardosoeiro/faculdade/2ano/1semestre/bdados/Trabalho-Base-de-Dados/BaseDados.db"
    
    con = sqlite3.connect(caminho_db)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    print("A criar esquema e a inserir dados... (isto pode demorar um pouco)")
    create_schema(cur)

    for index, row in df.iterrows():
        local = row['localExecucao']
        idsMun = NovoLocal(local,cur)

        descCPV = row['cpv']
        idsCPV = CPV(descCPV,cur)

        descTipoContrato = row['tipoContrato']
        idsTipoCont = TipoContrato(descTipoContrato,cur)

        descTipoProcedimento = row['tipoprocedimento']
        idtipoProc = TipoProcedimento(descTipoProcedimento,cur)
        
        descAcordoQuadro = row['DescrAcordoQuadro']
        idacordoQuadro = AcordoQuadro(descAcordoQuadro,cur)

        dadosAdjudicante = row['adjudicante']
        idAdjudicante = Adjudicante(dadosAdjudicante,cur) 

        idCont = row['idcontrato']
        preco = row['precoContratual']
        dataPubl = row['dataPublicacao']
        dataCele = row['dataCelebracaoContrato']
        prazo = row['prazoExecucao']
        funda = row['fundamentacao']
        centralizado = row['ProcedimentoCentralizado']
        objetoContr = row['objectoContrato']
        idContrato = Contrato(idCont,dataPubl,dataCele,prazo,funda,centralizado,objetoContr,preco,idtipoProc,idacordoQuadro,idAdjudicante,cur)

        dadosAdjudicatario = row['adjudicatarios']
        idsAdjudicatario = Adjudicatario(dadosAdjudicatario,cur)

        ContratoAdjudicatario(idContrato,idsAdjudicatario,cur)

        Local(idContrato,idsMun,cur)

        Tipo(idContrato,idsTipoCont,cur)

        CP(idContrato,idsCPV,cur)

    con.commit()
    con.close()
    print(f"Sucesso! Base de dados criada em: {caminho_db}")

if __name__ == '__main__':
    main()