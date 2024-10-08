import pickle

def to_pickle(data):
    try:
        with open('pickle_data/orders.pickle', 'rb') as file:
            existing_data = pickle.load(file)
    except (FileNotFoundError, EOFError):
        existing_data = [] 

    existing_data.append(data)

    with open('pickle_data/orders.pickle', 'wb') as file:
        pickle.dump(existing_data, file)

def from_pickle():
    try:
        with open('pickle_data/orders.pickle', 'rb') as file:
            return pickle.load(file)
    except (FileNotFoundError, EOFError):
        return []  