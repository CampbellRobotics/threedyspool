from yoyo import step


steps = [
    step("""CREATE TABLE users (
        id TEXT PRIMARY KEY,
        email TEXT NOT NULL,
        displayName TEXT NOT NULL
    )"""),
    step("""CREATE TABLE jobs (
        id INT PRIMARY KEY,
        name TEXT NOT NULL,
        owner TEXT,
        date INT NOT NULL,
        usage TEXT NOT NULL,
        origUrl TEXT,
        stlUrl TEXT NOT NULL,
        thumbUrl TEXT,
        FOREIGN KEY(owner) REFERENCES user(id))
    """),
]
