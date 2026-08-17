-- Desafio 05: Dimensão de datas e média real de vendas por dia da semana
-- Objetivo: Identificar o dia da semana com a pior média diária de vendas nas lojas físicas, corrigindo a ausência de dias sem vendas com uma dimensão de datas.
WITH 
--Identifica a data inicial e final das vendas físicas
limites_datas AS (
    SELECT 
        MIN(placed_at::date) AS data_inicio,
        MAX(placed_at::date) AS data_fim
    FROM orders
    WHERE channel = 'pos'
),

--Constrói a Dimensão de Datas contínua (dia a dia, sem pular nenhum dia)
dim_datas AS (
    SELECT 
        generate_series(data_inicio, data_fim, INTERVAL '1 day')::date AS data_referencia
    FROM limites_datas
),

--Calcula o faturamento diário consolidado (garantindo R$ 0,00 nos dias sem venda)
vendas_diarias AS (
    SELECT 
        d.data_referencia,
        COALESCE(SUM(o.total), 0) AS total_vendas_dia
    FROM dim_datas d
    LEFT JOIN orders o 
        ON d.data_referencia = o.placed_at::date 
       AND o.channel = 'pos'
    GROUP BY d.data_referencia
)

--Agrupa por dia da semana em português e calcula a média diária ponderada
SELECT 
    CASE EXTRACT(ISODOW FROM data_referencia)
        WHEN 1 THEN 'Segunda-feira'
        WHEN 2 THEN 'Terça-feira'
        WHEN 3 THEN 'Quarta-feira'
        WHEN 4 THEN 'Quinta-feira'
        WHEN 5 THEN 'Sexta-feira'
        WHEN 6 THEN 'Sábado'
        WHEN 7 THEN 'Domingo'
    END AS dia_semana,
    COUNT(data_referencia) AS qtd_dias_totais,
    SUM(total_vendas_dia) AS faturamento_total,
    ROUND(AVG(total_vendas_dia)::numeric, 2) AS media_vendas_diaria
FROM vendas_diarias
GROUP BY 
    EXTRACT(ISODOW FROM data_referencia),
    dia_semana
ORDER BY 
    media_vendas_diaria ASC; -- Pior média fica na primeira linha (topo)

--O dia da semana que foi regitrado com o pior dia de vendas foi a quinta feira, o que
--demonstra que, como o Sr. Almir pontuou, sem a dimensão de datas preenchendo os dias
--de faturamento zerado com 0, qualquer análise de média ficaria artificialmente 
--distorcida pelo viés dos dias com movimento.