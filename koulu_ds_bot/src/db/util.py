def fetch_to_dict(cursor, row):
    '''
        Turn sqlite fetch into dict
    '''
    data = {}
    for i, col in enumerate(cursor.description):
        data[col[0]] = row[i]
    return data
