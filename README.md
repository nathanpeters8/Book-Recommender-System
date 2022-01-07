# Book Recommender System
## Summary
 Takes a database with books and customer names, and recommends books based on the book and a customer's purchase history. Uses item-based collaboarative filtering.  

## Directions
 Run the python file. You will be greeted with a numbered list of all the books within the database. Input a book number to be shown a list of similar books to it. Press enter to go back to the book list. From the book list, if you press enter without any input, you will be shown a numbered list of customers that are also in the database. Here you can input a customer number where prompted to be shown that customer's purchase history, and two recommended books based on that history. Again press enter to go back to the customer list. From the list, pressing enter without input will end the program.

## Dependencies
- python: 3.6.5
- pandas: 0.25.3
- numpy: 1.14.3
- random
- sqlite3
 
## Directory
| File Name | Description |
| ----------- | ----------- |
| book_recommender.py | Python module |
| book_selection.png | Image of output displaying all books and asking for user's book selection |
| bookstore.db | SQL database consisting of 4 tables: Books, Customers, OrderItems, Orders |
| customer_recommended_books.png | Image of output displaying recommended books based off a customer's purchase history |
| customer_selection.png | Image of output displaying all the customers and asking for user's customer selection |
| similar_books.png | Image of output displaying books similar to a user selected book |
| README.md | Repository information |

## Sources
