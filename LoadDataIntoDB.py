import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode

line = ''

try:
    connection = mysql.connector.connect(host='localhost',
                             database='gametamedealfinder',
                             user='root',
                             password='LrD3FZGUz5JXy5c')

    with open('item_list_file_complete.txt', 'r') as item_list:
        with open('point_price_list_file_complete.txt', 'r') as point_list:
            item_name = item_list.readline().rstrip()
            point_price = point_list.readline().rstrip()
            
            while len(item_name) != 0:
                sql_insert_query = """ INSERT INTO `ITEM LIST`
                          (`ITEM NAME`, `POINT VALUE`) VALUES (\"{}\",{})""".format(item_name, point_price)
                # print(sql_insert_query)
                cursor = connection.cursor()
                result  = cursor.execute(sql_insert_query)
                item_name = item_list.readline().rstrip()
                """for i in range(len(item_name)):
                    if item_name[i] == '\'':
                        item_name = item_name[:i] + '\\\'' + item_name[(i + 1):]
                        break"""
                point_price = point_list.readline().rstrip()
    print ("Record inserted successfully into table")
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
