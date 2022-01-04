-- SELECT statements always return a new table
SELECT first || ' ' || last FROM Customers;
SELECT first || ' ' || last AS name FROM Customers;
SELECT * FROM Customers;
-- We can SELECT from more than one table
SELECT * FROM Customers, Orders;
-- What was that!!??  Every row in table 1 matched with every row in table 2
-- Cross join or Cartesian product.  If tbl 1 has M rows and tbl 2 has n rows,
-- tbl 1 X tbl 2 has M * N rows.  Never want this.
-- Let's get a list of customers and their orders:
SELECT last, order_num FROM Customers, Orders
    WHERE Customers.cust_id = Orders.cust_id;
-- This is called an implicit inner join.  We are joining the tables
-- on a relationship between the tables and SELECTING from the resulting table.
-- Let's do it using explicit join syntax:
SELECT last, order_num FROM Customers INNER JOIN Orders
    ON Customers.cust_id = Orders.cust_id;
-- An inner join on an equality condition is also called an equijoin.
-- In this case, we're joining using an equijoin on all
-- of the columns that have the same name.  Which means we can use this syntax:
SELECT last, order_num FROM Customers NATURAL JOIN Orders;
-- So we can do the same thing in a number of ways.  If performance is an
-- issue, try them all to see which is fastest.  If the dbms actually
-- makes the cross product and then filters it, that would be really slow.
-- The more complicated the query, the more likely something like that could
-- happen, and different syntax might make a huge difference.
SELECT last, order_num FROM Customers NATURAL JOIN Orders ORDER BY last;
-- How many orders did each customer make?
SELECT last, COUNT(*) AS num_orders FROM Customers NATURAL JOIN Orders 
    GROUP BY last ORDER BY last;
-- Who are our best customers?
SELECT last, COUNT(*) AS num_orders FROM Customers NATURAL JOIN Orders 
    GROUP BY last ORDER BY num_orders DESC LIMIT 5;
-- Only the very best customers:
SELECT last, num_orders FROM (SELECT last, COUNT(*) AS num_orders FROM Customers NATURAL JOIN Orders 
    GROUP BY last) WHERE num_orders = (SELECT MAX(OrderCnt) FROM (SELECT COUNT(*) AS OrderCnt 
    FROM Orders GROUP BY cust_id));
-- That's nasty, switch to having:
SELECT last, COUNT(*) AS num_orders FROM Customers NATURAL JOIN Orders 
    GROUP BY last HAVING num_orders = (SELECT MAX(OrderCnt) FROM (SELECT COUNT(*) AS OrderCnt 
    FROM Orders GROUP BY cust_id));

-- The hardest one from hw1:
-- Get all of the unique isbn's ordered by a given customer:
SELECT DISTINCT isbn FROM Orders NATURAL JOIN OrderItems 
    WHERE Orders.cust_id = 1 ORDER BY isbn;


    
