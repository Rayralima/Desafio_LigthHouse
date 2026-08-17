-- Desafio 06: Fazer um modelo preditivo do produto "Bússola de bordo 702"
-- Objetivo: Fazer uma média móvel da quantidade do produtoque a LH Nautical irá vender
-- no próximo mês para que seja feito o ajuste nas compras com os fornecedores.
-- Período analizado:
-- Janeiro/2026: Média de Outubro, Novembro e Dezembro de 2025.
-- Fevereiro/2026: Média de Novembro/2025, Dezembro/2025 e Janeiro/2026.
-- Março/2026: Média de Dezembro/2025, Janeiro/2026 e Fevereiro/2026.
-- Período de Teste: 1º Trimestre de 2026 (Jan, Fev, Mar)

WITH 
--Unificação das 4 tabelas e agregação das vendas mensais do produto alvo
vendas_mensais AS (
    SELECT 
        DATE_TRUNC('month', o.placed_at)::date AS mes,
        SUM(oi.quantity) AS qtd_vendida
    FROM orders o
    INNER JOIN order_items oi ON o.id = oi.order_id
    INNER JOIN product_variants pv ON oi.product_variant_id = pv.id
    INNER JOIN products p ON pv.product_id = p.id
    WHERE p.name = 'Bússola de Bordo 702'
    GROUP BY DATE_TRUNC('month', o.placed_at)::date
),

--Construção do Baseline: Média Móvel dos 3 meses imediatamente anteriores
serie_temporal AS (
    SELECT 
        mes,
        qtd_vendida,
        ROUND(AVG(qtd_vendida) OVER (
            ORDER BY mes 
            ROWS BETWEEN 3 PRECEDING AND 1 PRECEDING
        )::numeric, 2) AS previsao_baseline
    FROM vendas_mensais
),

--Filtragem do 1º Trimestre de 2026 e cálculo dos erros absolutos
previsoes_teste AS (
    SELECT 
        mes,
        qtd_vendida AS real,
        previsao_baseline AS previsao,
        ABS(qtd_vendida - previsao_baseline) AS erro_absoluto
    FROM serie_temporal
    WHERE mes BETWEEN '2026-01-01' AND '2026-03-31'
)

--Exibição das previsões mensais e do MAE consolidado
SELECT 
    mes,
    real,
    previsao,
    erro_absoluto,
    ROUND(AVG(erro_absoluto) OVER ()::numeric, 2) AS mae_geral
FROM previsoes_teste
ORDER BY mes;

-- Respostas das perguntas do desafio:
--
-- a. O baseline é adequado para esse produto?
-- Não para uso em produção, serve apenas como régua comparativa
-- inicial (baseline). O modelo errou mais de 40 unidades em 
-- Janeiro/2026 (previu 38.67 e vendeu 79), o que causaria ruptura 
-- severa de estoque em pleno pico de verão náutico.
--
-- b. Como o baseline foi construído?
-- Foi calculada a média aritmética móvel simples das quantidades
-- vendidas nos 3 meses imediatamente anteriores a cada mês previsto:
-- Jan/2026: Média de Outubro, Novembro e Dezembro de 2025.
-- Fev/2026: Média de Novembro/2025, Dezembro/2025 e Janeiro/2026.
-- Mar/2026: Média de Dezembro/2025, Janeiro/2026 e Fevereiro/2026.
--
-- c. Cite uma limitação desse método.
-- Incapacidade de antecipar sazonalidade: O modelo é puramente
-- reativo e trata meses com pesos idênticos. Ele não consegue
-- prever picos sazonais (como o aumento de demanda no verão)
-- antes que eles aconteçam, reagindo sempre com meses de atraso.
-- Uma solução seria aplicar um modelo de previsão mais sofisticado,
-- como o modelo de regressão linear com variáveis sazonais, utilizando
-- Machine Learning com Engenharia de Features (Feature Engineering) 
-- com algorítimos como: XGBoost, LightGBM, Random Forest, etc. Isso
-- possibilitaria a antecipação de picos sazonais e a redução 
-- do erro de previsão.
--
-- d. Como evitou data leakage (vazamento de dados)?
-- Definindo a janela da window function como ROWS BETWEEN 3 
-- PRECEDING AND 1 PRECEDING. Essa cláusula restringe o cálculo
-- da média móvel estritamente às 3 linhas anteriores (t−3,t−2,t−1
-- (sendo t = Linha Atual do mês analizado)) e exclui explicitamente
-- o registro atual (CURRENT ROW), garantindo que o valor real do
-- próprio mês previsto não seja utilizado na previsão.