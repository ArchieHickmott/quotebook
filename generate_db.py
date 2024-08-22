import sqlite3

# Connect to the database
conn = sqlite3.connect('quote.db')
cursor = conn.cursor()

# Example quotes format: name, year, quote, likes, numlikes
quotes = [
    ('Albert Einstein', 1955, 'The important thing is not to stop questioning.', 100, 0),
    ('John Smith', 1955, 'Life is like riding a bicycle. To keep your balance you must keep moving.', 200, 0),
    ('Micheal', 1955, 'Imagination is more important than knowledge.', 300, 0),
    ('Username', 1955, 'Try not to', 400, 0),
    ('Albert Einstein', 1654, 'The only source of knowledge is experience.', 500, 0),
    ('Albert Einstein', 145, 'Anyone who has never made a mistake has never tried anything new.', 600, 0),
    ('Jesus', 0, 'If you can\'t explain it to a six year old, you don\'t understand it yourself.', 700, 0),
]

# Insert the example quotes into the quote table
cursor.executemany('INSERT INTO quotes VALUES (?,?,?,?,?)', quotes)

# Commit the changes and close the connection
conn.commit()
conn.close()