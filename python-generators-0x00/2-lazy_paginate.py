seed = __import__('seed')

def paginate_users(page_size, offset):
    connection = seed.connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM user_data LIMIT {page_size} OFFSET {offset}")
    rows = cursor.fetchall()
    connection.close()
    return rows

def lazy_paginate(page_size):
    """Generator function that implements the paginate_users(page_size, offset) that will only fetch the next page when needed at an offset of 0"""
    offset = 0
    while True:
        page = paginate_users(page_size, offset)
        if not page:
            break
        yield page
        offset += page_size
