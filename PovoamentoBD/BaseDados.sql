CREATE TABLE Pais (
    idPais INTEGER PRIMARY KEY,
    nome VARCHAR2(255)
);

CREATE TABLE Distrito (
    idDist INTEGER PRIMARY KEY,
    nome VARCHAR2(255),
    idPais INTEGER,
    FOREIGN KEY(idPais) REFERENCES Pais (idPais)
);

CREATE TABLE Municipio (
    idMun INTEGER PRIMARY KEY,
    nome VARCHAR2(255),
    idDist INTEGER, 
    FOREIGN KEY(idDist) REFERENCES Distrito (idDist)
);

CREATE TABLE AcordoQuadro(
    idAcordo INTEGER PRIMARY KEY,
    descricao VARCHAR2(255)
);

CREATE TABLE TipoContrato(
    idTipoCont INTEGER PRIMARY KEY,
    descricao VARCHAR2(255)
);

CREATE TABLE CPV(
    idCPV INTEGER PRIMARY KEY,
    descricao VARCHAR2(255)
);

CREATE TABLE TipoProcedimento(
    idTipoProc INTEGER PRIMARY KEY,
    descricao VARCHAR2(255)
);

CREATE TABLE Cliente(
    idCliente INTEGER PRIMARY KEY,
    nif INTEGER,
    designacao VARCHAR2(255)
);

CREATE TABLE Vendedor(
    idVendedor INTEGER PRIMARY KEY,
    numFiscal TEXT,
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
    idCliente INTEGER,
    FOREIGN KEY (idCliente) REFERENCES Cliente (idCliente),
    FOREIGN KEY (idAcordo) REFERENCES AcordoQuadro (idAcordo),
    FOREIGN KEY (idTipoProc) REFERENCES TipoProcedimento(idTipoProc)
);

CREATE TABLE ContratoVendedor(
    idContrato INTEGER,
    idVendedor INTEGER,
    PRIMARY KEY(idContrato,idVendedor),
    FOREIGN KEY (idContrato) REFERENCES Contrato (idContrato),
    FOREIGN KEY (idVendedor) REFERENCES Vendedor (idVendedor)
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