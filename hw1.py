"""
Nate Peters
Hannah Smith
9/12/19
ISTA 331 HW1

This module is a simple book recommender system that uses
item-based collaborative filtering. 
"""

import pandas as pd, numpy as np, random, sqlite3

def get_purchase_matrix(conn):
    '''
    Makes matrix that maps customer id's sorted list of books they purchased.
    -------------------------------------------------------------------------
    PARAMETERS:
        conn - connection object to database
    RETURN: 
        purchase_dict(dict) - maps customer id's to list of books
    '''
    c = conn.cursor()
    purchase_dict = {}

    customer_list = [customer[0] for customer in c.execute('SELECT cust_id FROM Customers ORDER BY cust_id;').fetchall()] # ordered list of all customers
    for cust in customer_list:
        isbn_list = [isbn[0] for isbn in c.execute('SELECT DISTINCT isbn FROM Orders NATURAL JOIN OrderItems ' + 
        'WHERE Orders.cust_id = ? ORDER BY isbn;', (cust,)).fetchall()] # ordered list of ISBNs purchased by given customer
        purchase_dict[cust] = isbn_list

    return purchase_dict


def get_empty_count_matrix(conn):
    '''
    Makes count matrix of book isbns filled with zeros. 
    ---------------------------------------------------
    PARAMETERS:
        conn - connection object to database
    RETURN:
        (DataFrame) - column/index labels as book isbns and data as int 0's
    '''
    c = conn.cursor()
    isbn_list = [isbn[0] for isbn in c.execute('SELECT isbn FROM Books ORDER BY isbn;').fetchall()] #ordered list of all ISBNs
    return pd.DataFrame(np.zeros([len(isbn_list),len(isbn_list)], dtype=int), columns=isbn_list, index=isbn_list)


def fill_count_matrix(empty_matrix, purchase_matrix):
    '''
    Increments data in count matrix based on books/pairs of books
    purchased by users.
    -------------------------------------------------------------
    PARAMETERS:
        empty_matrix(DataFrame) - counts of books/pairs of books purchased 
        purchase_matrix(dict) - purchased books by each user
    RETURN:
        None
    '''
    for key in list(purchase_matrix.keys()):
        for i in range(len(purchase_matrix[key])):
            for j in range(i,len(purchase_matrix[key])):
                isbn1 = purchase_matrix[key][i]
                isbn2 = purchase_matrix[key][j]
                empty_matrix.loc[isbn1, isbn2] += 1 
                if isbn1 != isbn2: # if both isbns are different, increment the inverse location
                    empty_matrix.loc[isbn2, isbn1] += 1 


def make_probability_matrix(count_matrix):
    '''
    Makes conditional probability matrix with each value
    being the probability that customer purchased column book
    given customer purchased row book. 
    ---------------------------------------------------------
    PARAMETERS:
        count_matrix(DataFrame) - counts of books/pairs of books purchased
    RETURN: 
        prob_matrix(DataFrame) - conditional probability matrix
    '''
    prob_matrix = count_matrix.copy()

    for i in range(len(prob_matrix.columns)):
        denom = count_matrix.iloc[i,i] #denominator of probability formula
        prob_matrix.iloc[i,i] = -1 #sets diagonal locations to -1
        for j in range(len(prob_matrix.columns)):
            if i != j:
                prob_matrix.iloc[i,j] = count_matrix.iloc[i,j] / denom #probability formula

    return prob_matrix

def sparse_p_matrix(prob_matrix):
    '''
    Creates sparse probability matrix of ISBNs mapped to at most 15 books
    most likely to be purchased if key ISBN is purchased.
    ---------------------------------------------------------------------
    PARAMETERS:
        prob_matrix(DataFrame) - conditional probability matrix
    RETURN:
        sparse_p(dict) - Maps key ISBN to list of at most 15 ISBNs
    '''
    sparse_p = {}
    MAX_BOOKS = 15

    for i in range(len(prob_matrix.columns)):
        row = prob_matrix.iloc[i,:]
        row_probs = [[row[j], row.index[j]] for j in range(len(row.index))] #list of lists of probabilities and book ISBNs
        sorted_probs = sorted(row_probs, reverse=True)
        if len(sorted_probs) > MAX_BOOKS:
            sparse_p[prob_matrix.columns[i]] = [sorted_probs[k][1] for k in range(MAX_BOOKS)] #maps ISBN to list of 15 books
        else: # if less than 15 books
            sparse_p[prob_matrix.columns[i]] = [sorted_probs[k][1] for k in range(len(sorted_probs))] #maps ISBN to list of less than 15 books

    return sparse_p 

def get_cust_id(conn):
    '''
    Gets customer id based on user input.
    -------------------------------------
    PARAMETERS:
        conn - connection object to database
    RETURN: 
        (int) - customer id
    '''
    c = conn.cursor()

    print('CID       Name')
    print('-----     -----')
    rows = c.execute('SELECT * FROM Customers;').fetchall()
    for row in rows:
        print("    " + str(row[0]) + "     " + row[1] + ", " + row[2]) #prints each customer id, last name, and first name
    print('---------------')

    cust_id = str(input('Enter customer number or enter to quit: '))
    if cust_id != '': #if customer number inputted
        return rows[int(cust_id)-1][0] #customer id

def purchase_history(id, isbn_list, conn):
    '''
    Gets customer's purchase history of book titles.
    ------------------------------------------------
    PARAMETERS: 
        id(int) - customer id
        isbn_list(list) - given customer's purchased ISBNs
        conn - connection object to database
    RETURN:
        titles(str) - purchase history for customer with book titles
    '''
    c = conn.cursor()
    MAX_CHARS = 80
    titles = ''

    for name in c.execute('SELECT first,last FROM Customers WHERE cust_id == ?;', (id,)).fetchall():
        first,last = name[0], name[1] #gets first/last name of given customer

    header = 'Purchase history for ' + first + ' ' + last
    titles += header + '\n'
    titles += '-' * len(header) + '\n'

    for isbn in isbn_list:
        book = c.execute('SELECT book_title FROM Books WHERE isbn == ?;', (isbn,)).fetchall() #gets book title with given isbn
        book = list(book[0])
        titles += book[0][:MAX_CHARS]+'\n'

    titles += '-' * 40 + '\n'
    return titles

def get_recent(id, conn):
    '''
    Gets random ISBN from customer's most recent order.
    ---------------------------------------------------
    PARAMETERS:
        id(int) - customer's id
        conn - connection object to database
    RETURN:
        (str) - random ISBN from customer's most recent order
    '''
    c = conn.cursor()
    for recent_order in c.execute('SELECT order_num FROM Orders WHERE cust_id = ? ' +
    'ORDER BY order_date DESC LIMIT 1;', (id, )).fetchall(): #gets most recent order from given customer
        recent_order = recent_order[0]

    books = c.execute('SELECT isbn FROM OrderItems WHERE order_num = ?;', (recent_order,)).fetchall() #gets ISBNs from most recent order
    books_list = [book[0] for book in books] #makes list of the ISBNs
    return books_list[random.randrange(len(books_list))] 


def get_recommendation(id, sparse_p_matrix, isbn_list, conn):
    '''
    Gets two books most similar to random recently purchased book.
    --------------------------------------------------------------
    PARAMETERS:
        id(int) - customer id
        sparse_p_matrix(dict) - sparse probability matrix
        isbn_list(list) - given customer's purchased ISBNs
        conn - connection object to database
    RETURN:
        recommendations - at least 2 recommended book titles 
        for given purchased ISBN
    '''
    c = conn.cursor()
    MAX_CHARS = 80
    rand_book = get_recent(id, conn)

    for name in c.execute('SELECT first,last FROM Customers WHERE cust_id == ?;', (id,)).fetchall():
        first, last = name[0], name[1] #gets first/last name from given customer

    header = 'Recommendations for ' + first + ' ' + last
    recommendations = header + '\n' + ('-' * len(header) + '\n')
    similar_books = sparse_p_matrix[rand_book].copy()
    recomm_books = [isbn for isbn in similar_books if isbn not in isbn_list][:2] #list of at most 2 recommended non-purchased ISBNs for given ISBN and customer
    if len(recomm_books) == 0: #if all recommended books are already purchased
        return recommendations + 'Out of ideas, go to Amazon\n'

    all_titles = isbn_to_title(conn) #dictionary of book titles mapped to their ISBNs
    for i in range(len(recomm_books)):
        recommendations += all_titles[recomm_books[i][:MAX_CHARS]] + '\n'

    return recommendations
 

########################## HELPER FUNCTIONS ##################################

def isbn_to_title(conn):
    c = conn.cursor()
    query = 'SELECT isbn, book_title FROM Books;'
    return {row['isbn']: row['book_title'] for row in c.execute(query).fetchall()}

def select_book(itt):
    isbns = sorted(itt)
    print('All books:')
    print('----------')
    for i, isbn in enumerate(isbns):
        print(' ', i, '-->', isbn, itt[isbn][:60])
    print('-' * 40)
    selection = input('Enter book number or return to quit: ')
    return isbns[int(selection)] if selection else None
    
def similar_books(key, cm, pm, itt, spm): # an isbn, count_matrix, p_matrix, isbn_to_title
    bk_lst = []
    for isbn in cm.columns:
        if key != isbn:
            bk_lst.append((cm.loc[key, isbn], isbn))
    bk_lst.sort(reverse=True)
    print('Books similar to', itt[key] + ':')
    print('-----------------' + '-' * (len(itt[key]) + 1))
    for i in range(5):
        print(str(i) + ':')
        print(' ', bk_lst[i][0], '--', itt[bk_lst[i][1]][:80])
        print('  spm:', itt[spm[key][i]][:80])
        print('  p_matrix:', pm.loc[key, bk_lst[i][1]])

############################### MAIN #####################################        
    
def main1():
    conn = sqlite3.connect('bookstore.db')
    conn.row_factory = sqlite3.Row
    purchase_matrix = get_purchase_matrix(conn)
    count_matrix = get_empty_count_matrix(conn)
    fill_count_matrix(count_matrix, purchase_matrix)
    p_matrix = make_probability_matrix(count_matrix)
    spm = sparse_p_matrix(p_matrix)
    ######
    itt = isbn_to_title(conn)
    selection = select_book(itt)
    while selection:
        similar_books(selection, count_matrix, p_matrix, itt, spm)
        input('Enter to continue:')
        selection = select_book(itt)
    ######
    cid = get_cust_id(conn)
    while cid:
        print()
        titles = purchase_history(cid, purchase_matrix[cid], conn)
        print(titles)
        print(get_recommendation(cid, spm, purchase_matrix[cid], conn))
        input('Enter to continue:')
        cid = get_cust_id(conn)
    
def main2():
    conn = sqlite3.connect('bookstore.db')
    conn.row_factory = sqlite3.Row
    
    purchase_matrix = get_purchase_matrix(conn)
    print('*' * 20, 'Purchase Matrix', '*' * 20)
    print(purchase_matrix)
    print()
    
    count_matrix = get_empty_count_matrix(conn)
    print('*' * 20, 'Empty Count Matrix', '*' * 20)
    print(count_matrix)
    print()
    
    fill_count_matrix(count_matrix, purchase_matrix)
    print('*' * 20, 'Full Count Matrix', '*' * 20)
    print(count_matrix)
    print()
    
    p_matrix = make_probability_matrix(count_matrix)
    print('*' * 20, 'Probability Matrix', '*' * 20)
    print(p_matrix)
    print()
    
    spm = sparse_p_matrix(p_matrix)
    print('*' * 20, 'Sparse Probability Matrix', '*' * 20)
    print(spm)
    print()
    
    ######
    itt = isbn_to_title(conn)
    print('*' * 20, 'itt dict', '*' * 20)
    print(itt)
    print()
    
    selection = select_book(itt)
    while selection:
        similar_books(selection, count_matrix, p_matrix, itt, spm)
        input('Enter to continue:')
        selection = select_book(itt)

    cid = get_cust_id(conn)
    while cid:
        print()
        titles = purchase_history(cid, purchase_matrix[cid], conn)
        print(titles)
        print(get_recommendation(cid, spm, purchase_matrix[cid], conn))
        input('Enter to continue:')
        cid = get_cust_id(conn)

    
if __name__ == "__main__":
    main1()
    
    
    
    
    
    
    
    
