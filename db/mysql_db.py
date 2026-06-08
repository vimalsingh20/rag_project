import mysql.connector
def get_connection():
    conn = mysql.connector.connect(
        host ='localhost',
        user ='root',
        password = '975615',
        database = 'rag_db',
        
        
    )
    
    print("My sql connected sucessfully")
    return conn
