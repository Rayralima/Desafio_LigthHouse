-- DESAFIO 04: ANÁLISE DE CLIENTES DE ELITE E MAPEAMENTO DE CATEGORIAS
-- Objetivo: Identificar o Top 10 de clientes com maior Ticket Médio entre aqueles
--           que compraram em pelo menos 13 categorias distintas, identificando
--           em seguida qual categoria concentra o maior volume total de itens comprados

-- Primeiro foi agrupado o total gasto por cliente e a quantidade de pedidos diferentes
--SELECT
	--customer_id,
	--SUM(total) AS faturamento_total,
	--COUNT(DISTINCT id) AS frequencia
--FROM orders
--GROUP BY customer_id
--ORDER BY faturamento_total DESC

--Verificando quantas categorias o cliente comprou
-- Faz a 'ponte': orders -> order_items -> product_variants -> products
-- Conta a quantidade de category_id diferentes por cliente
--SELECT 
    --o.customer_id,
    --COUNT(DISTINCT p.category_id) AS qtd_categorias
--FROM orders o
--INNER JOIN order_items oi ON o.id = oi.order_id
--INNER JOIN product_variants pv ON oi.product_variant_id = pv.id
--INNER JOIN products p ON pv.product_id = p.id
--GROUP BY o.customer_id
--ORDER BY qtd_categorias DESC;

--Juntando as duas métricas e fazendo o filtro dos clientes elite com >= 13 categorias
-- usando subqueries e calculo do ticket Médio
--SELECT 
    --f.customer_id,
    --f.faturamento_total,
    --f.frequencia,
    --ROUND((f.faturamento_total / f.frequencia)::numeric, 2) AS ticket_medio,
    --d.qtd_categorias
--FROM (
    --SELECT customer_id, SUM(total) AS faturamento_total, COUNT(DISTINCT id) AS frequencia
    --FROM orders
    --GROUP BY customer_id
--) f
--INNER JOIN (
    --SELECT o.customer_id, COUNT(DISTINCT p.category_id) AS qtd_categorias
    --FROM orders o
    --INNER JOIN order_items oi ON o.id = oi.order_id
    --INNER JOIN product_variants pv ON oi.product_variant_id = pv.id
    --INNER JOIN products p ON pv.product_id = p.id
    --GROUP BY o.customer_id
--) d ON f.customer_id = d.customer_id
--WHERE d.qtd_categorias >= 13
--ORDER BY ticket_medio DESC, f.customer_id ASC
--LIMIT 10;

-- Query completa para o desafio 04
-- IDENTIFICAÇÃO DE CLIENTES DE ELITE E PADRÃO DE CONSUMO

WITH 
-- Calcular o faturamento total e o volume de transações por cliente
faturamento_frequencia AS (
    SELECT 
        customer_id,
        SUM(total) AS faturamento_total,       -- Soma de todos os pedidos do cliente
        COUNT(DISTINCT id) AS frequencia      -- Contagem de pedidos únicos realizados
    FROM orders
    GROUP BY customer_id
),

-- Mapear a diversidade de categorias exploradas por cada cliente
-- Relação: orders -> order_items -> product_variants -> products
diversidade_categorias AS (
    SELECT 
        o.customer_id,
        -- Conta apenas IDs de categoria únicos evitando duplicidade em compras da mesma categoria
        COUNT(DISTINCT p.category_id) AS qtd_categorias
    FROM orders o
    INNER JOIN order_items oi ON o.id = oi.order_id
    INNER JOIN product_variants pv ON oi.product_variant_id = pv.id
    INNER JOIN products p ON pv.product_id = p.id
    GROUP BY o.customer_id
),

-- Consolidar métricas e aplicar o critério de corte de Elite
-- Premissa: Apenas clientes com 13 ou mais categorias distintas
clientes_elite AS (
    SELECT 
        f.customer_id,
        f.faturamento_total,
        f.frequencia,
        -- Ticket Médio = Faturamento Total dividido pelo número de transações
        (f.faturamento_total / f.frequencia) AS ticket_medio,
        d.qtd_categorias
    FROM faturamento_frequencia f
    INNER JOIN diversidade_categorias d ON f.customer_id = d.customer_id
    WHERE d.qtd_categorias >= 13               -- Filtro de corte de diversidade
),

-- Isolar o Top 10 Clientes com maior Ticket Médio
-- Regra de Desempate: Se houver empate no Ticket Médio, menor customer_id vem primeiro
top_10_elite AS (
    SELECT 
        customer_id,
        ticket_medio,
        qtd_categorias
    FROM clientes_elite
    ORDER BY 
        ticket_medio DESC,                     -- 1º critério: maior ticket médio
        customer_id ASC                        -- 2º critério (desempate): menor ID
    LIMIT 10                                   -- Apenas os 10 primeiros colocados
)

-- Identificar a categoria líder em volume de itens para o grupo Top 10
SELECT 
    c.id AS category_id,
    c.name AS nome_categoria,
    -- Soma a quantidade total de produtos comprados nesta categoria por esse grupo
    SUM(oi.quantity) AS total_itens_comprados
FROM top_10_elite elite
-- Faz o caminho reverso partindo apenas dos 10 clientes selecionados:
INNER JOIN orders o ON elite.customer_id = o.customer_id
INNER JOIN order_items oi ON o.id = oi.order_id
INNER JOIN product_variants pv ON oi.product_variant_id = pv.id
INNER JOIN products p ON pv.product_id = p.id
INNER JOIN categories c ON p.category_id = c.id
GROUP BY 
    c.id, 
    c.name
ORDER BY 
    total_itens_comprados DESC                 -- Ordena da mais comprada para a menos comprada
LIMIT 1;                                       -- Retorna apenas a categoria campeã