import pandas as pd
import sqlite3

def Pais(pais:str,cur):
    '''Verifica se existe o pais e retorna o valor do id'''
    cur.execute('SELECT idPais FROM Pais WHERE nome = ?', [pais])
    res = cur.fetchone()
    if res:
        return res[0]
    else:
        cur.execute('INSERT INTO Pais (nome) VALUES (?)', [pais])
        return cur.lastrowid
    
def Distrito(dist:str,idPais:int,cur):
    '''Verifica se existe o distrito e retorna o valor do id'''
    cur.execute('SELECT idDist FROM Distrito WHERE nome = ?', [dist])
    res = cur.fetchone()
    if res:
        return res[0]
    else:
        cur.execute('INSERT INTO Distrito (nome, idPais) VALUES (?, ?)', [dist,idPais])
        return cur.lastrowid
    
def Municipio(muni:str,idDist:int,cur):
    '''Verifica se existe o municipio e retorna o valor do id'''
    cur.execute('SELECT idMun FROM Municipio WHERE nome = ?', [muni])
    res = cur.fetchone()
    if res:
        return res[0]
    else:
        cur.execute('INSERT INTO Municipio (nome, idDist) VALUES (?, ?)', [muni,idDist])
        return cur.lastrowid

def NovoLocal(local: str, cur):
    """Cria um novo local de execução se ainda não existir"""
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
    '''Adiciona a descrição do CPV à Base de dados'''
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
    '''Adiciona a descrição do Tipo de Contrato à Base de dados'''
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
    '''Adiciona a descrição do Tipo de Procedimento à Base de dados'''
    cur.execute('SELECT idTipoProc FROM TipoProcedimento WHERE descricao = ?',[desc])
    res = cur.fetchone()
    if res: return res[0]
    else:
        cur.execute('INSERT INTO TipoProcedimento (descricao) VALUES (?)',[desc])
        return cur.lastrowid


def AcordoQuadro(desc,cur):
    '''Adiciona a descrição do Acordo Quadro à Base de dados'''
    
    if pd.isna(desc):
        cur.execute('SELECT idAcordo FROM AcordoQuadro WHERE descricao IS NULL')
    else:
        cur.execute('SELECT idAcordo FROM AcordoQuadro WHERE descricao = ?', [desc])
    res=cur.fetchone()

    if res: return res[0]
    else: 
        cur.execute('INSERT INTO AcordoQuadro (descricao) VALUES (?)',[desc])
        return cur.lastrowid


def Vendedor(dados,cur):
    '''Adiciona os dados do Vendedor à Base de dados'''
    idsVendedor = []
    if pd.isna(dados):
        numFiscal = '0'
        designacao = 'Indeterminado'
        cur.execute('SELECT idVendedor FROM Vendedor WHERE numFiscal = ? AND designacao = ?', [numFiscal, designacao])
        res = cur.fetchone()
        if res: idsVendedor.append(res[0])
        else:
            cur.execute('INSERT INTO Vendedor (numFiscal, designacao) VALUES (?,?)', [numFiscal, designacao])
            idsVendedor.append(cur.lastrowid)

    else:
        groups = dados.split('|')
        for linha in groups:
            linha = linha.split('-',maxsplit = 1)
            numFiscal, designacao = linha[0].strip(), linha[1].strip()

            cur.execute('SELECT idVendedor FROM Vendedor WHERE numFiscal = ? AND designacao = ?', [numFiscal, designacao])
            res = cur.fetchone()
            if res: idsVendedor.append(res[0])
            else:
                cur.execute('INSERT INTO Vendedor (numFiscal, designacao) VALUES (?,?)', [numFiscal, designacao])
                idsVendedor.append(cur.lastrowid)
    return idsVendedor


def Cliente(dados,cur):
    '''Adiciona os dados do Cliente à Base de dados'''
    groups = dados.split('-',maxsplit = 1)
    nif, designacao = groups[0].strip(), groups[1].strip()
    cur.execute('SELECT idCliente FROM Cliente WHERE nif = ? AND designacao = ?', [nif, designacao])
    res = cur.fetchone()
    if res: return res[0]
    else:
        cur.execute('INSERT INTO Cliente (nif, designacao) VALUES (?, ?)', [nif, designacao])
        return cur.lastrowid


def Contrato(idCont, dataPubl, dataCele, prazo, funda, centralizado, objetoContr, preco,idtipoProc,idacordoQuadro,idCliente,cur):
    '''Trocar contrato com o novo idCliente'''
    cur.execute('SELECT idContrato FROM Contrato WHERE idContrato = ?', [idCont])
    res = cur.fetchone()

    if res:
        return res[0]
    else:
        dataPubl = f"{dataPubl}"     
        dataCele = f"{dataCele}" 
        cur.execute('INSERT INTO Contrato (idContrato, prazoExecucao, precoContratual, centralizado, fundamentacao, objetoContrato, dataPublicacao, dataCelebracao,idAcordo,idTipoProc,idCliente) VALUES (?,?,?,?,?,?,?,?,?,?,?)',
                    [idCont, prazo, preco, centralizado, funda, objetoContr, dataPubl, dataCele,idacordoQuadro,idtipoProc,idCliente])
        return cur.lastrowid


def ContratoVendedor(idContrato,idsVendedor,cur):
    for idVend in idsVendedor:
        cur.execute('INSERT INTO ContratoVendedor (idContrato,idVendedor) VALUES (?,?)',[idContrato,idVend])
        

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
    df = pd.read_excel("ContratosPublicos2024.xlsx")
    con = sqlite3.connect('BaseDados.db')
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    for index, row in df.iterrows():
        #Localizacao
        local = row['localExecucao']
        idsMun = NovoLocal(local,cur)

        #CPV
        descCPV = row['cpv']
        idsCPV = CPV(descCPV,cur)

        #TipoContrato
        descTipoContrato = row['tipoContrato']
        idsTipoCont = TipoContrato(descTipoContrato,cur)

        #TipoProcedimento
        descTipoProcedimento = row['tipoprocedimento']
        idtipoProc = TipoProcedimento(descTipoProcedimento,cur)
        
        #AcordoQuadro
        descAcordoQuadro = row['DescrAcordoQuadro']
        idacordoQuadro = AcordoQuadro(descAcordoQuadro,cur)

        #Cliente
        dadosCliente = row['adjudicante']
        idCliente = Cliente(dadosCliente,cur) 

        #Contrato
        idCont = row['idcontrato']
        preco = row['precoContratual']
        dataPubl = row['dataPublicacao']
        dataCele = row['dataCelebracaoContrato']
        prazo = row['prazoExecucao']
        funda = row['fundamentacao']
        centralizado = row['ProcedimentoCentralizado']
        objetoContr = row['objectoContrato']
        idContrato = Contrato(idCont,dataPubl,dataCele,prazo,funda,centralizado,objetoContr,preco,idtipoProc,idacordoQuadro,idCliente,cur)

        #Vendedor
        dadosVendedor = row['adjudicatarios']
        idsVendedor = Vendedor(dadosVendedor,cur)

        #ContratoVendedor        
        ContratoVendedor(idContrato,idsVendedor,cur)

        #Local
        Local(idContrato,idsMun,cur)

        #Tipo
        Tipo(idContrato,idsTipoCont,cur)

        #CP
        CP(idContrato,idsCPV,cur)

    con.commit()
    con.close()
    
if __name__ == '__main__':
    main()