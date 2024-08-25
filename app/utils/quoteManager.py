from .databaseManager import db 
from datetime import datetime
from datetime import datetime
import random

'''
Database structure is as follows:
users(id, name, email, password_hash, created_at, plevel)
quotes(id, author, year, quote, likes)
reports(id, user_id, quote_id, reason, details, status)
logs(id, user_id, action, message)
likes(user_id, quote_id)
comments(user_id, quote_id, comment)
'''

class QuoteManager:
    def __init__(self):
        self.db = db
    
    def get_quote(self, quote_id: int=-1):
        '''
        Get a quote from the database.
        :param quote_id: The ID of the quote.
        '''
        if quote_id == -1:
            return self.db.query('SELECT * FROM quotes ORDER BY RANDOM() LIMIT 1')[0]
        
        return self.db.query('SELECT * FROM quotes WHERE id = ?', (quote_id,))[0]
    
    def qotd(self):
        '''
        Get the quote of the day, is the same for all calls on the same day.
        '''
        quotes = self.db.query('SELECT * FROM quotes')
        random.seed(datetime.now().day)
        return quotes[random.randint(0, len(quotes) - 1)]
    
    def orderd_by_likes(self):
        '''
        Get all quotes ordered by likes.
        '''
        return self.db.query('SELECT * FROM quotes ORDER BY likes DESC')
    
    def create_quote(self, author: str, quote: str, year: int=datetime.now().year):
        '''
        Create a quote in the database.
        :param author: The author of the quote.
        :param year: The year of the quote.
        :param quote: The quote.
        '''
        return self.db.query('INSERT INTO quotes (author, year, quote, likes) VALUES (?, ?, ?, ?)', (author, year, quote, 0))
    
    def update_quote(self, quote_id: int, author: str=None, quote: str=None, year: int=None):
        '''
        Update a quote in the database.
        :param quote_id: The ID of the quote.
        :param author: The author of the quote.
        :param year: The year of the quote.
        :param quote: The quote.
        '''
        for item in [author, quote, year]:
            if item is None:
                item = self.get_quote(quote_id)[[author, quote, year].index(item)]
        
        self.db.query('UPDATE quotes SET author = ?, quote = ?, year = ? WHERE id = ? ', (author, quote, year, quote_id))

        return self.db.query('SELECT * FROM quotes WHERE id = ?', (quote_id,))[0]
    
    def delete_quote(self, quote_id: int):
        '''
        Delete a quote from the database.
        :param quote_id: The ID of the quote.
        '''
        self.db.query('DELETE FROM quotes WHERE id = ?', (quote_id,))

    def like_quote(self, user_id: int, quote_id: int):
        '''
        Like a quote.
        :param user_id: The ID of the user.
        :param quote_id: The ID of the quote.
        '''
        return self.db.query('INSERT INTO likes (user_id, quote_id) VALUES (?, ?)', (user_id, quote_id))
    
    def unlike_quote(self, user_id: int, quote_id: int):
        '''
        Unlike a quote.
        :param user_id: The ID of the user.
        :param quote_id: The ID of the quote.
        '''
        return self.db.query('DELETE FROM likes WHERE user_id = ? AND quote_id = ?', (user_id, quote_id))
    
    def get_liked(self, user_id: int, quote_id: int):
        '''
        Check if a user has liked a quote.
        :param user_id: The ID of the user.
        :param quote_id: The ID of the quote.
        '''
        return self.db.query('SELECT * FROM likes WHERE user_id = ? AND quote_id = ?', (user_id, quote_id))
    
    def search(self, query: str, search_field: str=None, order_by: str=None):
        '''
        Search for a quote.
        :param query: The query to search for.
        '''
        if order_by is None: order_by = "likes DESC"
        if query == "": quotes = self.db.query(f'SELECT * FROM quotes ORDER BY {order_by}')
        elif search_field: quotes = self.db.query(f'SELECT * FROM quotes WHERE {search_field} LIKE ? ORDER BY {order_by}', (f'%{query}%',))
        else: quotes = self.db.query(f'SELECT * FROM quotes WHERE author LIKE ? OR year LIKE ? OR quote LIKE ? ORDER BY {order_by}', tuple(f'%{query}%' for _ in range(3)))
        
        quotes = [i[1:] for i in quotes]
        return quotes
        
qm = QuoteManager()
