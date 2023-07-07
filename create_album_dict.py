def cad(elements):
    '''pass list of tuples, containing data about tracks and related albums
       and then create dict where key is album name and value is list of its content
    '''
    albums = {}
    for el in elements:
        name = list(el)[-1]
        if name in albums.keys():
            albums[name].append((el[0],el[1],el[2]))
        else:
            albums[name] = []
            albums[name].append((el[0],el[1],el[2]))
    return albums
