import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

from flask import Flask, render_template, request, redirect, url_for
import logging
import db

app = Flask(__name__)

# Página inicial com estatísticas
@app.route('/')
def pagina_inicial():
    stats = db.execute('''
        SELECT * FROM
            (SELECT COUNT(*) AS total_contratos FROM Contrato)
        JOIN
            (SELECT COUNT(*) AS total_vendedores FROM Vendedor)
        JOIN
            (SELECT COUNT(*) AS total_clientes FROM Cliente)
    ''').fetchone()
    return render_template('index.html', estatisticas=stats, pagina='home')


# Rotas de contratos
@app.route('/contratos/')
def listar_contratos():
    contratos = db.execute('''
        SELECT idContrato, dataPublicacao, dataCelebracao, objetoContrato
        FROM Contrato
        ORDER BY idContrato
    ''').fetchall()

    contrato_id = request.args.get('idContrato')
    if contrato_id:
        c = db.execute('SELECT idContrato, objetoContrato FROM Contrato WHERE idContrato=?', [contrato_id]).fetchone()
        if c:
            return redirect(f"/contratos/{c['idContrato']}/")
        else:
            return render_template('listar_contratos.html', contratos=contratos, pagina='contratos', erro="Contrato não encontrado")
    return render_template('listar_contratos.html', contratos=contratos, pagina='contratos')


@app.route('/contratos/<int:cid>/')
def detalhes_contrato(cid):
    contrato = db.execute('SELECT idContrato, objetoContrato FROM Contrato WHERE idContrato=?', [cid]).fetchone()

    detalhes = db.execute('''
        SELECT 
            c.precoContratual, c.prazoExecucao, c.centralizado, c.fundamentacao,
            v.idVendedor, v.designacao AS vendedor,
            cl.idCliente, cl.designacao AS cliente,
            m.idMun, m.nome AS municipio,
            d.idDist, d.nome AS distrito,
            p.idPais, p.nome AS pais,
            ac.descricao AS acordo, tp.descricao AS tipo_proc, cpv.descricao AS cpv,
            tc.descricao AS tipo_contrato
        FROM Contrato c
        JOIN ContratoVendedor cv ON cv.idContrato=c.idContrato
        JOIN Vendedor v ON cv.idVendedor=v.idVendedor
        JOIN Cliente cl ON cl.idCliente=c.idCliente
        JOIN Local l ON l.idContrato=c.idContrato
        JOIN Municipio m ON l.idMun=m.idMun
        JOIN Distrito d ON m.idDist=d.idDist
        JOIN Pais p ON d.idPais=p.idPais
        JOIN TipoProcedimento tp ON c.idTipoProc=tp.idTipoProc
        JOIN TipoContrato tc ON c.idContrato=tc.idContrato
        JOIN AcordoQuadro ac ON ac.idAcordo=c.idAcordo
        JOIN CP cp ON cp.idContrato=c.idContrato
        JOIN CPV cpv ON cpv.idCPV=cp.idCPV
        WHERE c.idContrato=?
        ORDER BY c.idContrato
    ''', [cid]).fetchall()

    return render_template('contrato.html', contrato=contrato, detalhes=detalhes, pagina='contratos')


# Rotas de vendedores
@app.route('/vendedores/')
def listar_todos_vendedores():
    vendedores = db.execute('''
        SELECT v.idVendedor, v.designacao, v.numFiscal, COUNT(cv.idVendedor) AS total_contratos
        FROM Vendedor v
        JOIN ContratoVendedor cv ON v.idVendedor=cv.idVendedor
        GROUP BY v.idVendedor
        ORDER BY v.idVendedor
    ''').fetchall()

    vid = request.args.get('idVendedor')
    vnome = request.args.get('nomeVendedor')

    if vid:
        vendedor = db.execute('SELECT idVendedor, designacao FROM Vendedor WHERE idVendedor=?', [vid]).fetchone()
        if vendedor:
            return redirect(f"/vendedores/{vendedor['idVendedor']}/")
        else:
            return render_template('listar_vendedores.html', vendedores=vendedores, pagina='vendedores', erro="Vendedor não encontrado")
    if vnome:
        vendedor = db.execute('SELECT idVendedor, designacao FROM Vendedor WHERE designacao=?', [vnome]).fetchone()
        if vendedor:
            return redirect(f"/vendedores/{vendedor['idVendedor']}/")
        else:
            return render_template('listar_vendedores.html', vendedores=vendedores, pagina='vendedores', erro="Vendedor não encontrado")

    return render_template('listar_vendedores.html', vendedores=vendedores, pagina='vendedores')


@app.route('/vendedores/<int:vid>/')
def detalhes_vendedor(vid):
    vendedor = db.execute('SELECT idVendedor, designacao FROM Vendedor WHERE idVendedor=?', [vid]).fetchone()
    contratos = db.execute('''
        SELECT c.idContrato, c.dataPublicacao, c.dataCelebracao, c.objetoContrato
        FROM Contrato c
        JOIN ContratoVendedor cv ON c.idContrato=cv.idContrato
        WHERE cv.idVendedor=?
        ORDER BY c.idContrato
    ''', [vid]).fetchall()
    return render_template('vendedor.html', vendedor=vendedor, contratos=contratos, pagina='vendedores')


# Rotas de clientes
@app.route('/clientes/')
def listar_todos_clientes():
    clientes = db.execute('''
        SELECT cl.idCliente, cl.designacao, cl.nif, COUNT(c.idContrato) AS total_contratos
        FROM Cliente cl
        JOIN Contrato c ON cl.idCliente=c.idCliente
        GROUP BY cl.idCliente
        ORDER BY cl.idCliente
    ''').fetchall()

    cid = request.args.get('idCliente')
    cnome = request.args.get('nomeCliente')

    if cid:
        cliente = db.execute('SELECT idCliente, designacao FROM Cliente WHERE idCliente=?', [cid]).fetchone()
        if cliente:
            return redirect(f"/clientes/{cliente['idCliente']}/")
        else:
            return render_template('listar_clientes.html', clientes=clientes, pagina='clientes', erro="Cliente não encontrado")
    if cnome:
        cliente = db.execute('SELECT idCliente, designacao FROM Cliente WHERE designacao=?', [cnome]).fetchone()
        if cliente:
            return redirect(f"/clientes/{cliente['idCliente']}/")
        else:
            return render_template('listar_clientes.html', clientes=clientes, pagina='clientes', erro="Cliente não encontrado")

    return render_template('listar_clientes.html', clientes=clientes, pagina='clientes')


@app.route('/clientes/<int:cid>/')
def detalhes_cliente(cid):
    cliente = db.execute('SELECT idCliente, designacao FROM Cliente WHERE idCliente=?', [cid]).fetchone()
    contratos = db.execute('''
        SELECT c.idContrato, c.dataPublicacao, c.dataCelebracao, c.objetoContrato
        FROM Contrato c
        JOIN Cliente cl ON c.idCliente=cl.idCliente
        WHERE cl.idCliente=?
        ORDER BY c.idContrato
    ''', [cid]).fetchall()
    return render_template('cliente.html', cliente=cliente, contratos=contratos, pagina='clientes')


# Rotas de países
@app.route('/pais/')
def listar_paises():
    paises = db.execute('''
        SELECT p.idPais, p.nome, COUNT(d.idDist) AS n_distritos
        FROM Pais p
        JOIN Distrito d ON d.idPais=p.idPais
        GROUP BY p.idPais
        ORDER BY p.idPais
    ''').fetchall()
    return render_template('listar_pais.html', paises=paises, pagina='pais')


@app.route('/pais/<int:pid>/')
def detalhes_pais(pid):
    pais = db.execute('SELECT idPais, nome FROM Pais WHERE idPais=?', [pid]).fetchone()
    distritos = db.execute('''
        SELECT d.idDist, d.nome, COUNT(m.idMun) AS n_municipios
        FROM Distrito d
        JOIN Municipio m ON m.idDist=d.idDist
        WHERE d.idPais=?
        GROUP BY d.idDist
        ORDER BY d.idDist
    ''', [pid]).fetchall()

    bandeira = url_for('static', filename=f'bandeiras/{pais["nome"].replace(" ", "_")}.jpg')
    return render_template('pais.html', pais=pais, distritos=distritos, pagina='pais', caminho_imagem=bandeira)


# Rotas de distritos
@app.route('/pais/distritos/<int:did>/')
def detalhes_distrito(did):
    distrito = db.execute('''
        SELECT d.idDist, d.nome, p.idPais, p.nome AS pais
        FROM Distrito d
        JOIN Pais p ON p.idPais=d.idPais
        WHERE d.idDist=?
    ''', [did]).fetchone()

    municipios = db.execute('''
        SELECT m.idMun, m.nome, COUNT(c.idContrato) AS n_contratos
        FROM Municipio m
        JOIN Local l ON l.idMun=m.idMun
        JOIN Contrato c ON c.idContrato=l.idContrato
        WHERE m.idDist=?
        GROUP BY m.idMun
        ORDER BY m.idMun
    ''', [did]).fetchall()

    return render_template('distrito.html', distrito=distrito, municipios=municipios, pagina='pais')


# Rotas de municípios
@app.route('/pais/distritos/municipios/<int:mid>/')
def detalhes_municipio(mid):
    municipio = db.execute('''
        SELECT m.idMun, m.nome, d.idDist, d.nome AS distrito, p.idPais, p.nome AS pais
        FROM Municipio m
        JOIN Distrito d ON d.idDist=m.idDist
        JOIN Pais p ON p.idPais=d.idPais
        WHERE m.idMun=?
    ''', [mid]).fetchone()

    contratos = db.execute('''
        SELECT c.idContrato, c.dataPublicacao, c.dataCelebracao, c.objetoContrato
        FROM Contrato c
        JOIN Local l ON l.idContrato=c.idContrato
        WHERE l.idMun=?
        ORDER BY c.idContrato
    ''', [mid]).fetchall()

    bandeira = url_for('static', filename=f'bandeiras/{municipio["pais"].replace(" ", "_")}.jpg')
    return render_template('municipio.html', municipio=municipio, contratos=contratos, pagina='pais', caminho_imagem=bandeira)


if __name__ == "__main__":
    db.connect()
    app.run(debug=True)