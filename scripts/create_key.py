import os, secrets, hashlib, sqlite3

# Localmente usa ./key.db; no Docker usa DB_PATH já definido no ambiente do container
caminho_db = os.environ.get("DB_PATH", "./key.db")

def criar_banco() -> None:
    with sqlite3.connect(caminho_db) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS ApiKey(
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          key TEXT NOT NULL,
                          created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                          status INTEGER DEFAULT 1)""")

def criar_chave() -> tuple[str, str]:
    chave_bruta = secrets.token_urlsafe()
    hash_ = hashlib.sha256(chave_bruta.encode()).hexdigest()
    return chave_bruta, hash_

def armazenar_chave(hash_key: str) -> None:
    with sqlite3.connect(caminho_db) as conn:
        conn.execute("INSERT INTO ApiKey (key) VALUES(?)", (hash_key,))

if __name__ == "__main__":
    criar_banco()
    for _ in range(11):
        chave_bruta, hash_ = criar_chave()
        armazenar_chave(hash_)
        print(f"\nChave gerada: {chave_bruta}")
        print("Guarde esta chave — o hash é armazenado, a chave original não pode ser recuperada.\n")
