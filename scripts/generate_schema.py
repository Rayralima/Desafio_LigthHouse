#importando bibliotecas
import csv
import re
import os

#função para descobrir o tipo de cada célula no arquivo csv
def descobrir_tipo(valor):
    #verificando se o valor é nulo
    if valor is None or valor.strip() == '':
        return None

    valor = valor.strip()

    #verificando se o valor é um número inteiro
    if re.match(r'^-?\d+$', valor):
        return 'INTEGER'

    #verificando se o valor é um número decimal
    if re.match(r'^-?\d+\.\d+$', valor):
        return 'NUMERIC'

    #verificando se o valor é no formato data e hora
    if re.match(r'^\d{4}-\d{2}-\d{2}(\s\d{2}:\d{2}:\d{2})?$', valor):
        return 'TIMESTAMP'

    #verificando se o valor é uma string
    return 'TEXT'

#função de promoção de tipos de dados, para que se um valor for do tipo INTEGER e outro do tipo NUMERIC, o tipo final seja NUMERIC
def promover_tipo(tipo_atual, tipo_novo):
    if tipo_atual is None:#verificação se o tipo atual é None, caso seja, retorna o tipo novo
        return tipo_novo
    if tipo_novo is None or tipo_atual == tipo_novo:#verificação se o tipo novo é None ou se o tipo atual é igual ao tipo novo, caso seja, retorna o tipo atual
        return tipo_atual

    #verificação se o tipo atual ou o tipo novo é do tipo TEXT, caso seja, retorna TEXT
    if tipo_atual == 'TEXT' or tipo_novo == 'TEXT':
        return 'TEXT'

    #verificação se o tipo atual é do tipo INTEGER e o tipo novo é do tipo NUMERIC, caso seja, retorna NUMERIC
    if set([tipo_atual, tipo_novo]) == set(['INTEGER', 'NUMERIC']):
        return 'NUMERIC'

    return 'TEXT'

#função de leitura e inspeção do arquivo csv, para descobrir o tipo de cada coluna
def analise_csv(caminho_csv):
    with open(caminho_csv, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)

        #lendo a primeira linha do arquivo csv para verificar o nome das colunas
        colunas = next(reader,None)
        if not colunas:
            return {}

        #mapa de tipos de dados das colunas
        tipos_colunas = {col.strip(): None for col in colunas}

        #lendo as linhas do arquivo csv descobrindo os tipos de dados de cada coluna
        for linha in reader:
            for nome_coluna, valor_celula in zip(colunas, linha):
                tipo_atual = tipos_colunas[nome_coluna.strip()]
                tipo_novo = descobrir_tipo(valor_celula)
                tipos_colunas[nome_coluna.strip()] = promover_tipo(tipo_atual, tipo_novo)

        #se a célular tiver vazia ou nula, o tipo da coluna será definido como TEXT
        for coluna, tipo in tipos_colunas.items():
            if tipo is None:
                tipos_colunas[coluna] = 'TEXT'
        return tipos_colunas

#função para varredura e geração do schema para todos os arquivos csv
def gerar_schema(pasta_dados, arquivo_saida_sql):

# Cria a pasta de destino do schema sql caso ela não exista
    pasta_destino = os.path.dirname(arquivo_saida_sql)
    if pasta_destino:
        os.makedirs(pasta_destino, exist_ok=True)
    
    comandos_sql = []

    # Percorre todos os arquivos na pasta de dados
    arquivos = [f for f in os.listdir(pasta_dados) if f.endswith('.csv')]
    arquivos.sort()  # Ordena os arquivos para garantir consistência na ordem de criação das tabelas
    for arquivo in arquivos:
        nome_tabela = os.path.splitext(arquivo)[0].lower()  # Nome da tabela será o nome do arquivo sem extensão, em minúsculas
        caminho_csv = os.path.join(pasta_dados, arquivo)

        #descobre os tipos de colunas do arquivo csv
        tipos = analise_csv(caminho_csv)

        #montando linhas e colunas no padrão SQL
        linhas_colunas = [f"    {coluna} {tipo}" for coluna, tipo in tipos.items()]

        #criação da instrução SQL para criação da tabela
        ddl = f'DROP TABLE IF EXISTS "{nome_tabela}" CASCADE;\n'
        ddl += f'CREATE TABLE "{nome_tabela}" (\n'
        ddl += ',\n'.join(linhas_colunas)
        ddl += '\n);\n'
        comandos_sql.append(ddl)

    #escrevendo o schema SQL no arquivo de saída
    with open(arquivo_saida_sql, mode='w', encoding='utf-8') as file:
        file.write('\n'.join(comandos_sql))
    print(f"Schema SQL gerado com sucesso em: {arquivo_saida_sql}")

#executando a função de geração do schema para todos os arquivos csv na pasta 'data' e salvando o schema no arquivo 'schema.sql'
if __name__ == "__main__":
    # 1. Pega o caminho da pasta onde este script está (/scripts)
    pasta_scripts = os.path.dirname(os.path.abspath(__file__))
    
    # 2. Sobe um nível para a raiz do projeto
    pasta_raiz = os.path.dirname(pasta_scripts)
    
    # 3. Aponta para as pastas 'data' e 'sql' na raiz
    pasta_dados = os.path.join(pasta_raiz, 'data')
    arquivo_sql = os.path.join(pasta_raiz, 'sql', 'schema.sql')

    print(f"Lendo dados de: {pasta_dados}")
    print(f"Salvando SQL em: {arquivo_sql}\n")
    
    gerar_schema(pasta_dados=pasta_dados, arquivo_saida_sql=arquivo_sql)