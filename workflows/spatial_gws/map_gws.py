import os

import pastastore as pst


# fd = os.path.join(os.path.abspath(__file__), "..", "data", "Dawaco_db_v1")
fd = os.path.abspath(os.path.join(__file__, "..", "..", "localdb", "data", "20240715_Dawaco_db"))
conn = pst.PystoreConnector("dawaco_db", path=fd)
store = pst.PastaStore(name="dawaco_db", connector=conn)


fd2 = os.path.abspath(os.path.join(__file__, "..", "..", "localdb", "data", "20240715_Dawaco_pas_db"))
conn2 = pst.PasConnector(name="dawaco_pas_db", path=fd2)
pst.util.copy_database(conn, conn2)

print("hoi")
