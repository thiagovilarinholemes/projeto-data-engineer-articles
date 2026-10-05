"""
Criação da tabela Silver de artigos científicos.
"""

from app.database.database import get_connection


def create_silver_table(): 
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS silver_articles (
            id SERIAL PRIMARY KEY,

            source TEXT NOT NULL,
            source_id TEXT NOT NULL,

            title TEXT,
            authors TEXT[],
            abstract TEXT,

            publication_year INTEGER,

            doi TEXT,
            source_name TEXT,
            pdf_url TEXT,

            open_access BOOLEAN DEFAULT FALSE,

            ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processed_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            UNIQUE (source, source_id)
        );
        """
    )

    connection.commit()

    cursor.close()
    connection.close()

    print("Tabela silver_articles criada/verificada.")