import logging
import sqlite3
import re
import os
from flask import g # Importacao crucial para o contexto

# Mantem o teu caminho absoluto, agora corrigido
DB_FILE = '/Users/rodri/Documents/GitHub/Trabalho-Base-de-Dados/PovoamentoBD/BaseDados.db' 

def get_db():
    if 'db' not in g:
        # Abre a ligacao UMA VEZ por pedido do Flask
        if not os.path.exists(DB_FILE):
             logging.error(f"Ficheiro de Base de Dados nao encontrado em: {DB_FILE}")
             
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        g.db = conn 
        logging.info('Connected to database (via g)')
    
    return g.db

def execute(sql, args=None):
    # Obtem a ligacao e um cursor para este pedido
    conn = get_db()
    cursor = conn.cursor()
    
    sql = re.sub(r'\s+', ' ', sql)
    logging.info('SQL: {} Args: {}'.format(sql, args))
    
    return cursor.execute(sql, args) if args is not None else cursor.execute(sql)

def close_db(e=None):
    # Fecha a ligacao no fim do pedido
    db = g.pop('db', None) 
    
    if db is not None:
        db.close()
        logging.info('Closed database connection (via g)')