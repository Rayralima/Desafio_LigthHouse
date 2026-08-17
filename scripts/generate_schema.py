#Objetivo: Gerar o schema SQL para criação das tabelas no banco de dados

#Importando bibliotecas
import csv
import re
import os

#Função para descobrir o tipo de cada célula no arquivo csv
def descobrir_tipo(valor):
    #Verificando se o valor é nulo ou vazio
    if valor is None or valor.strip() == '':
        return None

    valor = valor.strip()

    #Verificando se o valor é um número inteiro
    if re.match(r'^-?\d+$', valor):
        num = int(valor)
        #Se for maior que o BIGINT (ex: chave de NFe de 44 dígitos), vira TEXT
        if abs(num) > 9223372036854775807:
            return 'TEXT'
        #Se ultrapassar o limite do INTEGER (32 bits), vira BIGINT
        if abs(num) > 2147483647:
            return 'BIGINT'
        return 'INTEGER'

    #Verificando se o valor é um número decimal
    if re.match(r'^-?\d+\.\d+$', valor):
        return 'NUMERIC'

    #Verificando se o valor é no formato data e hora
    if re.match(r'^\d{4}-\d{2}-\d{2}(\s\d{2}:\d{2}:\d{2})?$', valor):
        return 'TIMESTAMP'

    #Verificando se o valor é uma string
    return 'TEXT'

#Função de promoção de tipos de dados
def promover_tipo(tipo_atual, tipo_novo):
    #Se um dos tipos for None, retorna o outro
    if tipo_atual is None:
        return tipo_novo
    if tipo_novo is None or tipo_atual == tipo_novo:
        return tipo_atual

    #Se qualquer um for TEXT, o tipo final é TEXT
    if tipo_atual == 'TEXT' or tipo_novo == 'TEXT':
        return 'TEXT'

    #Se qualquer um for TIMESTAMP misturado com outro tipo não-data, vira TEXT
    if tipo_atual == 'TIMESTAMP' or tipo_novo == 'TIMESTAMP':
        return 'TEXT'

    #Hierarquia numérica: INTEGER < BIGINT < NUMERIC
    hierarquia_numerica = {'INTEGER': 1, 'BIGINT': 2, 'NUMERIC': 3}
    if tipo_atual in hierarquia_numerica and tipo_novo in hierarquia_numerica:
        if hierarquia_numerica[tipo_novo] > hierarquia_numerica[tipo_atual]:
            return tipo_novo
        return tipo_atual

    return 'TEXT'

#Função de leitura e inspeção do arquivo csv, para descobrir o tipo de cada coluna
def analise_csv(caminho_csv):
    with open(caminho_csv, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)

        #Lendo a primeira linha do arquivo csv para verificar o nome das colunas
        colunas = next(reader, None)
        if not colunas:
            return {}

        #Mapa de tipos de dados das colunas
        tipos_colunas = {col.strip(): None for col in colunas}

        #Lendo as linhas do arquivo csv descobrindo os tipos de dados de cada coluna
        for linha in reader:
            for nome_coluna, valor_celula in zip(colunas, linha):
                tipo_atual = tipos_colunas[nome_coluna.strip()]
                tipo_novo = descobrir_tipo(valor_celula)
                tipos_colunas[nome_coluna.strip()] = promover_tipo(tipo_atual, tipo_novo)

        #Se a coluna inteira for vazia/nula, o tipo padrão será TEXT
        for coluna, tipo in tipos_colunas.items():
            if tipo is None:
                tipos_colunas[coluna] = 'TEXT'
        return tipos_colunas

#Função para varredura e geração do schema para todos os arquivos csv
def gerar_schema(pasta_dados, arquivo_saida_sql):
    #Cria a pasta de destino do schema sql caso ela não exista
    pasta_destino = os.path.dirname(arquivo_saida_sql)
    if pasta_destino:
        os.makedirs(pasta_destino, exist_ok=True)
    
    comandos_sql = []

    #Percorre todos os arquivos na pasta de dados
    arquivos = [f for f in os.listdir(pasta_dados) if f.endswith('.csv')]
    arquivos.sort()  # Garante consistência na ordem de criação das tabelas

    for arquivo in arquivos:
        nome_tabela = os.path.splitext(arquivo)[0].lower()
        caminho_csv = os.path.join(pasta_dados, arquivo)

        #Descobre os tipos de colunas do arquivo csv
        tipos = analise_csv(caminho_csv)

        #Montando linhas e colunas no padrão SQL
        linhas_colunas = [f'    "{coluna}" {tipo}' for coluna, tipo in tipos.items()]

        # Criação da instrução SQL para criação da tabela
        ddl = f'DROP TABLE IF EXISTS "{nome_tabela}" CASCADE;\n'
        ddl += f'CREATE TABLE "{nome_tabela}" (\n'
        ddl += ',\n'.join(linhas_colunas)
        ddl += '\n);\n'
        comandos_sql.append(ddl)

    #Escrevendo o schema SQL no arquivo de saída
    with open(arquivo_saida_sql, mode='w', encoding='utf-8') as file:
        file.write('\n'.join(comandos_sql))
    print(f"Schema SQL gerado com sucesso em: {arquivo_saida_sql}")

#Executando a função de geração do schema
if __name__ == "__main__":
    pasta_scripts = os.path.dirname(os.path.abspath(__file__))
    pasta_raiz = os.path.dirname(pasta_scripts)
    pasta_dados = os.path.join(pasta_raiz, 'data')
    arquivo_sql = os.path.join(pasta_raiz, 'sql', 'schema.sql')

    print(f"Lendo dados de: {pasta_dados}")
    print(f"Salvando SQL em: {arquivo_sql}\n")
    
    gerar_schema(pasta_dados=pasta_dados, arquivo_saida_sql=arquivo_sql)