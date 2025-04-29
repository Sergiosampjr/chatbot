# 1. Importações
import pandas as pd
import sqlite3
from vanna.remote import VannaDefault

# 2. Configurações
API_KEY = ''  # substitua pela sua chave real
MODEL_NAME = 'messi'
CSV_PATH = 'tweet_sentiment.csv'
DB_PATH = 'tweets.db'

# 3. Criar DB com os dados do CSV
df = pd.read_csv(CSV_PATH)
conn = sqlite3.connect(DB_PATH)
df.to_sql('tweets', conn, if_exists='replace', index=False)
conn.close()

# 4. Inicializar Vanna e conectar ao SQLite
vanna_model = VannaDefault(model=MODEL_NAME, api_key=API_KEY)
vanna_model.connect_to_sqlite(DB_PATH)

# 5. Treinar a Vanna com contexto
vanna_model.train(ddl="""
CREATE TABLE tweets (
    tweet_id INT,
    text TEXT,
    sentiment TEXT,
    created_at TIMESTAMP
);
""")

vanna_model.train(documentation="""
The 'tweets' table contains tweets collected for sentiment analysis.
- 'sentiment' column values: 'positive', 'negative', or 'neutral'.
- 'created_at' indicates when the tweet was posted.
""")

vanna_model.train(sql="""
SELECT sentiment, COUNT(*) AS count 
FROM tweets 
GROUP BY sentiment;
""")

vanna_model.train(sql="""
SELECT DATE(created_at) AS date, COUNT(*) AS count 
FROM tweets 
GROUP BY date 
ORDER BY date;
""")

vanna_model.train(
    question="How many positive tweets are there?",
    sql="SELECT COUNT(*) FROM tweets WHERE sentiment = 'positive';"
)

vanna_model.train(
    question="What is the most common sentiment?",
    sql="""
    SELECT sentiment, COUNT(*) AS count 
    FROM tweets 
    GROUP BY sentiment 
    ORDER BY count DESC 
    LIMIT 1;
    """
)

# 6. Fazer pergunta + executar SQL
sql, _, _ = vanna_model.ask("How many negative tweets are there?")
print("SQL gerada:", sql)

results = vanna_model.run_sql(sql)
print("Resultado:", results)
