import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode

line = ''

try:
    connection = mysql.connector.connect(host='localhost',
                             database='gametamedealfinder',
                             user='root',
                             password='LrD3FZGUz5JXy5c')

    cursor = connection.cursor(buffered=True)
    
    cursor.execute("SELECT ItemName, PointValue FROM `ITEM LIST STEAM MARKET TF2`")

    items = cursor.fetchall()
    
    for item in items:
        name = item[0]
        points = item[1]
        
        sql_insert_query = """ INSERT INTO `ITEM LIST BACKPACK TF`
                  (`name`, `pointPrice`) VALUES (\"{}\",{})""".format(name, points)

        cursor.execute(sql_insert_query) # was result = ...
    print ("Records inserted successfully into table")
except mysql.connector.Error as error :
    connection.rollback() #rollback if any exception occured
    print("Failed inserting record into table {}".format(error))
finally:
    #closing database connection.
    if(connection.is_connected()):
        connection.commit()
        cursor.close()
        connection.close()
        print("MySQL connection is closed")
