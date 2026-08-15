import csv
import os
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import cursor as PgCursor
from psycopg2.extras import execute_values
from dotenv import load_dotenv

# Carrega as variáveis para o banco de dados
load_dotenv()

DB_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'postgres'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST', '127.0.0.1'),
    'port': os.getenv('DB_PORT', '5433')
}

#função que executa o schema.sql para criar o banco de dados e as tabelas
def criar_tabelas(cursor, arquivo_schema):
    #lendo o arquiivo schema.sql e executando o comando DDL para criar as tabelas no banco de dados
    with open(arquivo_schema, mode='r', encoding='utf-8') as f:
        schema_sql = f.read()
    cursor.execute(schema_sql)
    print("Tabelas criadas com sucesso!")

#função que carrega os arquivos csv e insere os dados nas tabelas correspondentes no banco de dados
def carregar_dados(cursor: PgCursor, caminho_csv: str, nome_tabela: str):
    with open(caminho_csv, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)

        #lendo a primeira linha para obter os nomes das colunas
        colunas = next(reader, None)
        if not colunas:
            print(f" O arquivo {caminho_csv} está vazio ou não possui cabeçalho.")
            return
        
        colunas = [col.strip() for col in colunas]  #removendo espaços em branco dos nomes das colunas

        linhas = []
        for linha in reader:
            #converter textos vazios para None para evitar problemas de inserção no banco de dados
            linha_tratada = [None if valor.strip() == '' else valor.strip() for valor in linha]
            linhas.append(linha_tratada)
        if not linhas:
            print(f"O arquivo {caminho_csv} não possui dados para inserir.")
            return

        # Monta a query de inserção
        colunas_formatadas = sql.SQL(', ').join([sql.Identifier(col) for col in colunas])
        query = sql.SQL('INSERT INTO {} ({}) VALUES %s').format(
            sql.Identifier(nome_tabela),
            colunas_formatadas
        )

        # Executa a inserção em lote usando execute_values para melhor performance
        execute_values(cursor, query, linhas)
        print(f"Dados do arquivo {caminho_csv} inseridos com sucesso na tabela {nome_tabela}.")

#função principal que executa a pipeline de criação do banco de dados e carregamento dos dados
def main():
    #localização das pastas de dados e do arquivo schema.sql
    pasta_scripts = os.path.dirname(os.path.abspath(__file__))
    pasta_raiz = os.path.dirname(pasta_scripts)
    pasta_dados = os.path.join(pasta_raiz, 'data')
    arquivo_schema = os.path.join(pasta_raiz, 'sql', 'schema.sql')

    print(f"Conectando ao banco de dados {DB_CONFIG['dbname']} na porta {DB_CONFIG['port']}...")
    conn = psycopg2.connect(
        dbname=DB_CONFIG['dbname'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port'],
        client_encoding='utf-8'
    )
    cursor = conn.cursor()

    try:
        #criação das tabelas no banco de dados a partir do schema.sql
        criar_tabelas(cursor, arquivo_schema)

        #carregamento dos dados dos arquivos csv para as tabelas correspondentes
        arquivos_csv = [f for f in os.listdir(pasta_dados) if f.endswith('.csv')]
        arquivos_csv.sort()  # Ordena os arquivos para garantir consistência na ordem de inserção

        print(f"Carregando dados para as tabelas correspondentes...")
        for arquivo in arquivos_csv:
            nome_tabela = os.path.splitext(arquivo)[0].lower()  # Nome da tabela será o nome do arquivo sem extensão, em minúsculas
            caminho_csv = os.path.join(pasta_dados, arquivo)
            print(f"Carregando dados do arquivo {caminho_csv} para a tabela {nome_tabela}...")
            carregar_dados(cursor, caminho_csv, nome_tabela)

        #comfirmando as alterações e salvando no banco de dados
        conn.commit()
        print("Dados carregados com sucesso!")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()



