
def object_id_generator():
    n = 1
    while True:
        yield n
        n += 1


generator = object_id_generator()
