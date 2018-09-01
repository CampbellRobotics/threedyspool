from yoyo import step


steps = [
    step("""CREATE TABLE users (
        id TEXT PRIMARY KEY,
        email TEXT NOT NULL,
        displayName TEXT NOT NULL,
        privlevel INT NOT NULL
    )"""),
    step("""CREATE TABLE jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        owner TEXT,
        date INTEGER NOT NULL,
        usage TEXT NOT NULL,
        thumbUrl TEXT,
        FOREIGN KEY(owner) REFERENCES users(id))
    """),
]
