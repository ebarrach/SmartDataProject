from sqlalchemy import create_engine, text

engine = create_engine("mysql+pymysql://root:polyroot@localhost:3307/Relation")

with engine.connect() as conn:
    with open("init.sql", "r", encoding="utf-8") as file:
        sql_code = file.read()
    for statement in sql_code.split(";"):
        if statement.strip():
            conn.execute(text(statement))
    print("✅ Schéma et données injectés.")

