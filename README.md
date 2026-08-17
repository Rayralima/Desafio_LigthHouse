# ⚓ LH Nautical - Data Engineering, Analytics & Machine Learning Challenge - Indicium IA

Projeto desenvolvido para solucionar desafios analíticos e de engenharia de dados para a **LH Nautical**, cobrindo desde a modelagem relacional e ingestão de dados em PostgreSQL até segmentação de clientes, séries temporais e sistemas de recomendação.

---

## 🛠️ Tecnologias e Ferramentas

* **Linguagens & Banco de Dados:** Python 3, SQL, PostgreSQL
* **Bibliotecas Python:** `pandas`, `numpy`, `scikit-learn`, `psycopg2`, `python-dotenv`
* **Conceitos:** Modelagem Relacional (OLTP/Dimensional), Séries Temporais, Prevenção de Data Leakage, Filtragem Colaborativa (Item-Item), Álgebra Linear (Similaridade de Cosseno).

---

## 📁 Estrutura do Repositório

```text
├── data/                      # Arquivos CSV brutos (orders, order_items, products, etc.)
├── sql/
│   ├── schema.sql             # DDL para criação das tabelas relacionais
│   ├── desafio04_elite.sql    # Query de segmentação de clientes fiéis (Elite)
│   ├── desafio05_datas.sql    # Criação da dimensão de datas e correção de viés
│   └── previsao_baseline.sql  # Implementação analítica da média móvel
├── scripts/
│   ├── ingestao.py            # Script de carga e validação dos dados no PostgreSQL
│   ├── previsao_demanda.py    # Modelo preditivo baseline de demanda (Média Móvel)
│   └── recomendacao.py        # Motor de recomendação por Similaridade de Cosseno
├── .env.example               # Exemplo de variáveis de ambiente de conexão
├── requirements.txt           # Dependências do projeto
└── README.md
```

## 🚀 Desafios e Soluções Implementadas
**1. Modelagem e Carga de Dados (251.864 Registros)**
* Estruturação do banco relacional em PostgreSQL normalizando as entidades: customers, products, product_variants, orders, order_items e payments.

* Pipeline de ingestão com checagem de integridade referencial e validação volumétrica consolidada.

**2. Segmentação de Clientes Elite (Desafio 04)**
* Objetivo: Mapear o padrão de compra dos clientes de alto valor com consumo diversificado.

* Metodologia:

 * Cálculo de Faturamento Total e Frequência por cliente para obtenção do Ticket Médio.

 * Aplicação de filtro de diversidade (HAVING COUNT(DISTINCT category_id) >= 13).

 * Identificação dos 10 clientes com maior Ticket Médio e consolidação das categorias com maior volume de itens adquiridos.

**3. Dimensão Calendário & Correção de Viés (Desafio 05)**
* Objetivo: Identificar o dia da semana com a pior média de vendas nas lojas físicas (pos), sem inflar métricas com a omissão de dias sem faturamento.

* Solução: Construção de uma dimensão de datas sintética no SQL cruzada via LEFT JOIN com a tabela transacional e aplicação de COALESCE(venda, 0) para contabilizar corretamente os dias em que a loja abriu mas teve faturamento zero no denominador da média.

**4. Previsão de Demanda & Avaliação de Erro (Desafio 06)**
* Produto Alvo: Bússola de Bordo 702

* Baseline: Média móvel dos 3 meses imediatamente anteriores (t−3,t−2,t−1).

* Prevenção de Data Leakage: Uso de shift(1) / ROWS BETWEEN 3 PRECEDING AND 1 PRECEDING para excluir estritamente o mês previsto da janela de cálculo.

* Avaliação: Cálculo do MAE (Mean Absolute Error) contra o período de teste (1º Trimestre de 2026), apontando a limitação de modelos reativos frente à sazonalidade do verão náutico.

**5. Motor de Recomendação de Produtos (Desafio 07)**
* Produto de Referência: Motor de Popa 1949

* Abordagem: Filtragem Colaborativa Item-Item.

*Mecanismo:

** Criação da matriz binária de interação Usuário × Produto com pd.crosstab.

** Transposição da matriz para representação vetorial de cada produto.

** Cálculo da Similaridade de Cosseno par a par com sklearn.metrics.pairwise.cosine_similarity.

** Extração do Top 5 produtos com maior correlação de coocorrência de compra.

## ⚙️ Como Executar o Projeto
1. Clone o repositório:
```bash
git clone [https://github.com/SEU_USUARIO/lh-nautical-data-challenge.git](https://github.com/SEU_USUARIO/lh-nautical-data-challenge.git)
cd lh-nautical-data-challenge
```
2. Crie e ative um ambiente virtual:
 ```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows
```
3. Instale as dependências:
 ```bash
pip install -r requirements.txt
```
4. Configure o banco de dados:
* Crie um arquivo .env na raiz baseado no .env.example:
 ```bash
DB_NAME=lh_nautical
DB_USER=postgres
DB_PASSWORD=sua_senha
DB_HOST=127.0.0.1
DB_PORT=5432
```
* Execute o schema.sql e o script de ingestão.

5. Execute os scripts analíticos:
 ```bash
python scripts/previsao_demanda.py
python scripts/recomendacao.py
```
