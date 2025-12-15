import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

from flask import Flask, render_template, request, redirect, url_for
import logging
import db
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db.DB_FILE = os.path.join(BASE_DIR, '..', 'BaseDados.db')

@app.route('/')
def home():
    stats = db.execute('''
        SELECT * FROM
            (SELECT COUNT(*) AS n_contratos FROM Contrato)
        JOIN
            (SELECT COUNT(*) AS n_adjudicatarios FROM Adjudicatario)
        JOIN
            (SELECT COUNT(*) AS n_adjudicantes FROM Adjudicante)
    ''').fetchone()
    return render_template('index.html', stats=stats)


@app.route('/contratos/')
def contratos():
    contratos_lista = db.execute('''
        SELECT 
            idContrato, 
            SUBSTR(dataPublicacao, 1, 10) AS dataPublicacao, 
            SUBSTR(dataCelebracao, 1, 10) AS dataCelebracao, 
            objetoContrato
        FROM Contrato
        ORDER BY idContrato
        LIMIT 200
    ''').fetchall()

    contrato_id = request.args.get('idContrato')
    if contrato_id:
        c = db.execute('SELECT idContrato, objetoContrato FROM Contrato WHERE idContrato=?', [contrato_id]).fetchone()
        if c:
            return redirect(f"/contratos/{c['idContrato']}/")
        else:
            return render_template('listar_contratos.html', contratos=contratos_lista, erro="Contrato não encontrado")
            
    return render_template('listar_contratos.html', contratos=contratos_lista)

@app.route('/contratos/<int:cid>/')
@app.route('/contratos/<int:cid>/')
def detalhes_contrato(cid):
    contrato = db.execute('''
        SELECT 
            c.idContrato, 
            c.prazoExecucao, 
            c.precoContratual, 
            c.centralizado, 
            c.fundamentacao, 
            c.objetoContrato,
            SUBSTR(c.dataPublicacao, 1, 10) AS dataPublicacao, 
            SUBSTR(c.dataCelebracao, 1, 10) AS dataCelebracao, 
            c.idAcordo, 
            c.idTipoProc, 
            c.idAdjudicante,
            adj.designacao as nomeAdjudicatario, 
            adj.idAdjudicatario,
            cl.designacao as nomeAdjudicante, 
            cl.idAdjudicante,
            tc.descricao as tipoContrato,
            tp.descricao as tipoProcedimento,
            aq.descricao as acordoQuadro
        FROM Contrato c
        LEFT JOIN ContratoAdjudicatario ca ON c.idContrato = ca.idContrato
        LEFT JOIN Adjudicatario adj ON ca.idAdjudicatario = adj.idAdjudicatario
        LEFT JOIN Adjudicante cl ON c.idAdjudicante = cl.idAdjudicante
        LEFT JOIN Tipo t ON c.idContrato = t.idContrato
        LEFT JOIN TipoContrato tc ON t.idTipoCont = tc.idTipoCont
        LEFT JOIN TipoProcedimento tp ON c.idTipoProc = tp.idTipoProc
        LEFT JOIN AcordoQuadro aq ON c.idAcordo = aq.idAcordo
        WHERE c.idContrato=?
    ''', [cid]).fetchone()
    
    locais = db.execute('''
        SELECT m.nome as municipio, d.nome as distrito
        FROM Local l
        JOIN Municipio m ON l.idMun = m.idMun
        JOIN Distrito d ON m.idDist = d.idDist
        WHERE l.idContrato = ?
    ''', [cid]).fetchall()
    
    return render_template('contrato.html', contrato=contrato, locais=locais)


@app.route('/adjudicatarios/')
def adjudicatarios():
    lista = db.execute('''
        SELECT a.idAdjudicatario, a.designacao, a.numFiscal, COUNT(ca.idAdjudicatario) AS total_contratos
        FROM Adjudicatario a
        JOIN ContratoAdjudicatario ca ON a.idAdjudicatario = ca.idAdjudicatario
        GROUP BY a.idAdjudicatario
        ORDER BY total_contratos DESC
        LIMIT 200
    ''').fetchall()

    aid = request.args.get('idAdjudicatario')
    anome = request.args.get('nomeAdjudicatario')

    if aid:
        a = db.execute('SELECT idAdjudicatario FROM Adjudicatario WHERE idAdjudicatario=?', [aid]).fetchone()
        if a: return redirect(f"/adjudicatarios/{a['idAdjudicatario']}/")
    
    if anome:
        a = db.execute('SELECT idAdjudicatario FROM Adjudicatario WHERE designacao LIKE ?', [f'%{anome}%']).fetchone()
        if a: return redirect(f"/adjudicatarios/{a['idAdjudicatario']}/")

    return render_template('listar_adjudicatarios.html', adjudicatarios=lista)

@app.route('/adjudicatarios/<int:aid>/')
def detalhes_adjudicatario(aid):
    adjudicatario_data = db.execute('SELECT * FROM Adjudicatario WHERE idAdjudicatario=?', [aid]).fetchone()
    
    contratos = db.execute('''
        SELECT c.idContrato, c.dataPublicacao, c.dataCelebracao, c.objetoContrato
        FROM Contrato c
        JOIN ContratoAdjudicatario ca ON c.idContrato=ca.idContrato
        WHERE ca.idAdjudicatario=?
        ORDER BY c.dataCelebracao DESC
    ''', [aid]).fetchall()
    
    return render_template('adjudicatario.html', adjudicatario=adjudicatario_data, contratos=contratos)


@app.route('/adjudicantes/')
def adjudicantes():
    lista = db.execute('''
        SELECT cl.idAdjudicante, cl.designacao, cl.nif, COUNT(c.idContrato) AS total_contratos
        FROM Adjudicante cl
        JOIN Contrato c ON cl.idAdjudicante=c.idAdjudicante
        GROUP BY cl.idAdjudicante
        ORDER BY total_contratos DESC
        LIMIT 200
    ''').fetchall()

    cid = request.args.get('idAdjudicante')
    cnome = request.args.get('nomeAdjudicante')

    if cid:
        c = db.execute('SELECT idAdjudicante FROM Adjudicante WHERE idAdjudicante=?', [cid]).fetchone()
        if c: return redirect(f"/adjudicantes/{c['idAdjudicante']}/")
    
    if cnome:
        c = db.execute('SELECT idAdjudicante FROM Adjudicante WHERE designacao LIKE ?', [f'%{cnome}%']).fetchone()
        if c: return redirect(f"/adjudicantes/{c['idAdjudicante']}/")

    return render_template('listar_adjudicantes.html', adjudicantes=lista)

@app.route('/adjudicantes/<int:cid>/')
def detalhes_adjudicante(cid):
    adjudicante_data = db.execute('SELECT * FROM Adjudicante WHERE idAdjudicante=?', [cid]).fetchone()
    
    contratos = db.execute('''
        SELECT c.idContrato, c.dataPublicacao, c.dataCelebracao, c.objetoContrato
        FROM Contrato c
        WHERE c.idAdjudicante=?
        ORDER BY c.dataCelebracao DESC
    ''', [cid]).fetchall()
    
    return render_template('adjudicante.html', adjudicante=adjudicante_data, contratos=contratos)


@app.route('/pais/')
def paises():
    paises_lista = db.execute('''
        SELECT idPais, nome 
        FROM Pais 
        ORDER BY idPais
    ''').fetchall()
    
    return render_template('listar_pais.html', paises=paises_lista)

@app.route('/pais/distritos/<int:did>/')
def detalhes_distrito(did):
    distrito = db.execute('SELECT * FROM Distrito WHERE idDist=?', [did]).fetchone()
    municipios = db.execute('SELECT * FROM Municipio WHERE idDist=?', [did]).fetchall()
    return render_template('distrito.html', distrito=distrito, municipios=municipios)


@app.route('/perguntas/')
def perguntas():
    return render_template('listar_perguntas.html')

@app.route('/perguntas/1')
def pergunta_1():

    texto_da_pergunta = "Qual o número total de contratos e o preço médio contratual?"

    resposta = db.execute('''
        SELECT COUNT(idContrato) AS TotalContratos, ROUND(AVG(precoContratual), 2) AS PrecoMedioContrato
        FROM Contrato;
    ''').fetchall()
    
    return render_template(
        'detalhes_pergunta.html', 
        resposta=resposta, 
        page='perguntas', 
        pergunta=texto_da_pergunta 
    )


@app.route('/perguntas/2')
def pergunta_2():
   
    texto_da_pergunta = "Quantos contratos têm um prazo de execução superior a um ano?"

    resposta = db.execute('''
        SELECT COUNT(idContrato) AS ContratosMaisDeUmAno
        FROM Contrato
        WHERE prazoExecucao > 365; 
    ''').fetchall()

    return render_template(
        'detalhes_pergunta.html', 
        resposta=resposta, 
        page='perguntas', 
        pergunta=texto_da_pergunta
    )


@app.route('/perguntas/3')
def pergunta_3():

    texto_da_pergunta = "Quantos contratos estão identificados como centralizados?"

    resposta = db.execute('''
        SELECT COUNT(Contrato.idContrato) AS 'Número de Contratos Centralizados'
        FROM Contrato
        WHERE Contrato.centralizado='Sim'; 
    ''').fetchall()
    
    return render_template(
        'detalhes_pergunta.html',
        resposta=resposta,
        page = 'perguntas',
        pergunta=texto_da_pergunta
    )


@app.route('/perguntas/4')
def pergunta_4():

    texto_da_pergunta = "Qual é a quantidade de contratos por tipo de procedimento, ordenada do mais frequente para o menos frequente?"

    resposta = db.execute('''
        SELECT TipoProcedimento.descricao AS TipoProcedimento, COUNT(Contrato.idContrato) AS Quantidade
        FROM TipoProcedimento
        JOIN Contrato ON Contrato.idTipoProc = TipoProcedimento.idTipoProc
        GROUP BY TipoProcedimento.descricao
        ORDER BY Quantidade DESC; 
    ''').fetchall()
    
    return render_template(
        'detalhes_pergunta.html',
        resposta=resposta,
        page = 'perguntas',
        pergunta=texto_da_pergunta
    )


@app.route('/perguntas/5')
def pergunta_5():

    texto_da_pergunta = "Qual é o contrato com o maior preço contratual, incluindo o adjudicante e o objeto associado?"

    resposta = db.execute('''
        SELECT Adjudicante.designacao AS Adjudicante, Contrato.objetoContrato AS Objeto, Contrato.precoContratual AS ValorContrato
        FROM Contrato
        JOIN Adjudicante ON Contrato.idAdjudicante = Adjudicante.idAdjudicante
        ORDER BY Contrato.precoContratual DESC
        LIMIT 1;
    ''').fetchall()
    
    return render_template(
        'detalhes_pergunta.html',
        resposta=resposta,
        page = 'perguntas',
        pergunta=texto_da_pergunta
    )


@app.route('/perguntas/6')
def pergunta_6():

    texto_da_pergunta = "Quais são os municípios que têm mais de 100 contratos associados e quantos contratos têm cada um?"

    resposta = db.execute('''
        SELECT Municipio.nome AS Municipio, COUNT(Contrato.idContrato) AS NumContratos
        FROM Municipio
        JOIN Local ON Municipio.idMun = Local.idMun
        JOIN Contrato ON Local.idContrato = Contrato.idContrato
        GROUP BY Municipio.nome
        HAVING NumContratos > 100
        ORDER BY NumContratos DESC;  
    ''').fetchall()
    
    return render_template(
        'detalhes_pergunta.html',
        resposta=resposta,
        page = 'perguntas',
        pergunta=texto_da_pergunta
    )


@app.route('/perguntas/7')
def pergunta_7():

    texto_da_pergunta = "Quais são os contratos associados a códigos CPV cuja descrição contém a expressão 'bases de dados'?"

    resposta = db.execute('''
        SELECT Contrato.idContrato, Contrato.objetoContrato, Contrato.precoContratual
        FROM Contrato
        JOIN CP ON Contrato.idContrato = CP.idContrato
        JOIN CPV ON CP.idCPV = CPV.idCPV
        WHERE CPV.descricao LIKE '%bases de dados%'
        ORDER BY Contrato.idContrato;
    ''').fetchall()
    
    return render_template(
        'detalhes_pergunta.html',
        resposta=resposta,
        page = 'perguntas',
        pergunta=texto_da_pergunta
    )


@app.route('/perguntas/8')
def pergunta_8():

    texto_da_pergunta = "Quais são os cinco adjudicatários com o maior valor total de contratos, considerando a soma dos preços contratuais?"

    resposta = db.execute('''
        SELECT Adjudicatario.designacao AS Adjudicatario, Adjudicatario.numFiscal AS NIF, ROUND(SUM(Contrato.precoContratual), 2) AS ValorTotal
        FROM Adjudicatario
        JOIN ContratoAdjudicatario ON Adjudicatario.idAdjudicatario = ContratoAdjudicatario.idAdjudicatario
        JOIN Contrato ON ContratoAdjudicatario.idContrato = Contrato.idContrato
        GROUP BY Adjudicatario.designacao, Adjudicatario.numFiscal
        ORDER BY ValorTotal DESC
        LIMIT 5;
    ''').fetchall()
    
    return render_template(
        'detalhes_pergunta.html',
        resposta=resposta,
        page = 'perguntas',
        pergunta=texto_da_pergunta
    )


@app.route('/perguntas/9')
def pergunta_9():

    texto_da_pergunta = "Quais são os distritos (do país com ID 1) cujo valor total gasto em contratos ultrapassa 35 milhões?"

    resposta = db.execute('''
        SELECT Distrito.nome AS Distrito, ROUND(SUM(Contrato.precoContratual), 2) AS ValorTotalGasto
        FROM Distrito
        JOIN Municipio ON Distrito.idDist = Municipio.idDist
        JOIN Local ON Municipio.idMun = Local.idMun
        JOIN Contrato ON Local.idContrato = Contrato.idContrato
        WHERE Distrito.idPais = 1
        GROUP BY Distrito.nome
        HAVING ValorTotalGasto > 35000000
        ORDER BY ValorTotalGasto DESC;  
    ''').fetchall()
    
    return render_template(
        'detalhes_pergunta.html',
        resposta=resposta,
        page = 'perguntas',
        pergunta=texto_da_pergunta
    )


@app.route('/perguntas/10')
def pergunta_10():

    texto_da_pergunta = "Quais são os adjudicantes que possuem contratos com adjudicatários cujo NIF não começa por '5' ou que não têm NIF registado?"

    resposta = db.execute('''
        SELECT DISTINCT Adjudicante.designacao AS Adjudicante, Adjudicante.nif AS NIF_Adjudicante
        FROM Adjudicante
        JOIN Contrato ON Contrato.idAdjudicante = Adjudicante.idAdjudicante
        JOIN ContratoAdjudicatario ON ContratoAdjudicatario.idContrato = Contrato.idContrato
        JOIN Adjudicatario ON ContratoAdjudicatario.idAdjudicatario = Adjudicatario.idAdjudicatario
        WHERE Adjudicatario.numFiscal NOT LIKE '5%' OR Adjudicatario.numFiscal IS NULL;  
    ''').fetchall()
    
    return render_template(
        'detalhes_pergunta.html',
        resposta=resposta,
        page = 'perguntas',
        pergunta=texto_da_pergunta
    )


@app.route('/perguntas/11')
def pergunta_11():

    texto_da_pergunta = "Qual é o valor médio dos contratos para cada tipo de procedimento, ordenado do maior para o menor?"

    resposta = db.execute('''
        SELECT TipoProcedimento.descricao as 'Tipo de Procedimento', round(AVG(Contrato.precoContratual),2) AS 'Média do Valor do Contrato'
        FROM Contrato
        JOIN TipoProcedimento ON Contrato.idTipoProc = TipoProcedimento.idTipoProc
        GROUP BY TipoProcedimento.descricao
        ORDER BY AVG(Contrato.precoContratual) DESC;
    ''').fetchall()
    
    return render_template(
        'detalhes_pergunta.html',
        resposta=resposta,
        page = 'perguntas',
        pergunta=texto_da_pergunta
    )


@app.route('/perguntas/12')
def pergunta_12():

    texto_da_pergunta = "Qual é o preço médio dos contratos por município, considerando apenas municípios pertencentes ao país com ID 1?"

    resposta = db.execute('''
        SELECT Municipio.nome AS Municipio, ROUND(AVG(Contrato.precoContratual), 2) AS PrecoMedioContrato
        FROM Municipio
        JOIN Local ON Municipio.idMun = Local.idMun
        JOIN Contrato ON Local.idContrato = Contrato.idContrato
        JOIN Distrito ON Municipio.idDist = Distrito.idDist
        WHERE Distrito.idPais = 1
        GROUP BY Municipio.nome
        ORDER BY PrecoMedioContrato DESC;
    ''').fetchall()
    
    return render_template(
        'detalhes_pergunta.html',
        resposta=resposta,
        page = 'perguntas',
        pergunta=texto_da_pergunta
    )


if __name__ == "__main__":
    app.run(debug=True)