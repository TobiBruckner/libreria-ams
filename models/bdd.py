import sqlite3

conn = sqlite3.connect('libreria.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS libro (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               nombre TEXT NOT NULL,
               autor TEXT NOT NULL,
               descripcion TEXT NOT NULL,
               precio INTEGER NOT NULL
               
               )
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS cliente (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               nombre TEXT NOT NULL,
               apellido TEXT NOT NULL,
               mail TEXT NOT NULL,
               contraseña TEXT NOT NULL

               
               
               )
''')

libro = [
    {"nombre": "Cien años de soledad", "autor": "Gabriel García Márquez", "descripcion": "Historia de la familia Buendía en Macondo.", "precio": 12500},
    {"nombre": "Don Quijote de la Mancha", "autor": "Miguel de Cervantes", "descripcion": "Sátira de las novelas de caballería.", "precio": 15800},
    {"nombre": "1984", "autor": "George Orwell", "descripcion": "Distopía sobre vigilancia y control total.", "precio": 9900},
    {"nombre": "Orgullo y prejuicio", "autor": "Jane Austen", "descripcion": "Crítica social con romance en la Inglaterra del XIX.", "precio": 8700},
    {"nombre": "El principito", "autor": "Antoine de Saint-Exupéry", "descripcion": "Poético y filosófico sobre amistad e inocencia.", "precio": 6500},
    {"nombre": "Harry Potter y la piedra filosofal", "autor": "J.K. Rowling", "descripcion": "Inicio de la saga mágica mundialmente famosa.", "precio": 11200},
]

cursor.executemany("INSERT INTO libro (nombre, autor, descripcion, precio) VALUES (?, ?, ?, ?)",
               [(lib["nombre"], lib["autor"], lib["descripcion"], lib["precio"]) for lib in libro]
               )

cliente = [
    {"nombre": "Myriam", "apellido": "González", "mail": "myriamgonzalez18@hotmail.com", "contraseña": "1234"},
    {"nombre": "Javier", "apellido": "Bruckner", "mail": "javibruckner70@gmail.com", "contraseña": "12345"}
]

cursor.executemany("INSERT INTO cliente (nombre, apellido, mail, contraseña) VALUES (?, ?, ?, ?)",
               [(cli["nombre"], cli["apellido"], cli["mail"], cli["contraseña"]) for cli in cliente]
)


cursor.execute("DELETE FROM cliente where id = 26")

cursor.execute("SELECT * FROM libro")
libro = cursor.fetchall()

print("Lista de libros: ")
for lib in libro:
    print(lib)

cursor.execute("UPDATE libro SET precio = ? WHERE nombre = ?", (10000, "1984"))



conn.commit()

conn.close()





