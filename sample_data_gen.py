

with engine.connect() as conn:
    conn.execute(text("""
        CREATE TABLE employees (
            id INTEGER PRIMARY KEY, -- AUTOINCREMENT,
            name TEXT NOT NULL,
            department TEXT,
            salary REAL NOT NULL,
            hire_date DATE NOT NULL
        )
    """))

    conn.execute(text("""
        CREATE TABLE departments (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            budget REAL
        )
    """))

    #Insert into sample data
    conn.execute(text("""
        INSERT INTO departments (name, budget) VALUES
            ('Engineering', 500000),
            ('Marketing', 200000),
            ('Sales', 300000),
            ('HR', 150000)
    """))

    conn.execute(text("""
        INSERT INTO employees (name, department, salary, hire_date) VALUES 
            ('Allen Kupoluyi', 'Engineering', 75000, '2023-01-15'),
            ('Demilade Smith', 'Marketing', 65000, '2023-02-20'),
            ('Akan Daniel', 'Sales', 55000, '2023-03-10'),
            ('Chikezie Brown', 'Engineering', 80000, '2023-01-25'),
            ('Charlie Bilal', 'HR', 50000, '2023-04-05')
    """))

    conn.commit()
