# import pyodbc
# server = 'pwnka-a-we-acc-dawaco-sql.database.windows.net'
# database = 'Dawacotest'
# username ='bas.des.tombe@pwn.nl'
# Authentication='ActiveDirectoryInteractive'
# driver= '{ODBC Driver 17 for SQL Server}'
# conn = pyodbc.connect('DRIVER='+driver+
#                       ';SERVER='+server+
#                       ';PORT=1433;DATABASE='+database+
#                       ';UID='+username+
#                       ';AUTHENTICATION='+Authentication
#                       )

import pyodbc
import pandas as pd
server = 'pwnka-a-we-acc-dawaco-sql.database.windows.net'
database = 'Dawacotest'
Authentication='ActiveDirectoryInteractive'
driver= '{ODBC Driver 17 for SQL Server}'
conn = pyodbc.connect('DRIVER='+driver+
                      ';SERVER='+server+
                      ';PORT=1433;DATABASE='+database+
                      ';Trusted_Connection=yes'
                      )


print(conn)
q = "SELECT * FROM dbo.mp "

b = pd.read_sql_query(q, conn)
print(b)

