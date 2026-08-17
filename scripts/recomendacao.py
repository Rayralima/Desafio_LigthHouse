# Objetivo: Criar um sistema de recomendação de produtos baseado em 
# similaridade de cosseno com o produto: Motor de Popa 1949.

#importando bibliotecas necessárias
import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity

#Carregando variáveis para conexão com o banco de dados
load_dotenv()

conn = psycopg2.connect(
    dbname=os.getenv('DB_NAME', 'postgres'),
    user=os.getenv('DB_USER', 'postgres'),
    password=os.getenv('DB_PASSWORD'),
    host=os.getenv('DB_HOST', '127.0.0.1'),
    port=os.getenv('DB_PORT', '5433')
)

#Extração das interações Cliente x Produto
query = """
SELECT DISTINCT
    o.customer_id,
    p.id AS product_id,
    p.name AS product_name
FROM orders o
INNER JOIN order_items oi ON o.id = oi.order_id
INNER JOIN product_variants pv ON oi.product_variant_id = pv.id
INNER JOIN products p ON pv.product_id = p.id
WHERE p.name NOT IN ('asdf');
"""

df_interactions = pd.read_sql(query, conn)
conn.close()

#Criação da Matriz de Interação Usuário x Produto (Linha: Cliente, Coluna: Produto)
# pd.crosstab já binariza a relação cliente x produto (presença: 1, ausência: 0)
# O pd.crosstab cruza duas colunas para montar uma tabela de frequência (estilo tabela dinâmica)
# Assim cada linha vira um cliente único e cada coluna vira um produto único, com 1 indicando
# que o cliente comprou o produto e 0 indicando que não comprou.
user_product_matrix = pd.crosstab(
    index=df_interactions['customer_id'],
    columns=df_interactions['product_name']
)

#Cálculo da Similaridade de Cosseno Produto x Produto (Foi transporto a matriz com .T)
# Transpondo a matriz original inverte as linhas e colunas, ou seja, agora cada linha
# representa um produto e cada coluna representa um cliente. Isso serve para que cada
# linha passe a ser um Produto representado pelo vetor de clientes que o compraram. 
# O cosine_similarity compara essas linhas e gera a matriz quadrada de Produto × Produto.
product_similarity_matrix = cosine_similarity(user_product_matrix.T)

# Conversão em DataFrame com nomes dos produtos nas linhas e colunas
df_similarity = pd.DataFrame(
    product_similarity_matrix,
    index=user_product_matrix.columns,
    columns=user_product_matrix.columns
)

# Rankeando os 5 produtos mais similares ao "Motor de Popa 1949"
target_product = "Motor de Popa 1949"

similar_products = (
    df_similarity[target_product]
    .drop(labels=[target_product])        # Desconsidera o próprio produto (Motor de Popa 1949) da lista de similares
    .sort_values(ascending=False)         # Ordena os produtos do mais similar para o menos similar
    .head(5)                              # Pega o Top 5
    .reset_index()
)

similar_products.columns = ['Produto Recomendado', 'Similaridade Cosseno']

# Exibindo o resultado formatado
print(f"\n TOP 5 Produtos Recomendados para: '{target_product}'")
print(similar_products.to_string(index=False))