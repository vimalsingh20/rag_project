from db.mysql_store import get_all_chunks

chunks = get_all_chunks()

print(chunks[0])
print(chunks[1])