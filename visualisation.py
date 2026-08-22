try:
    import pygame
except Exception as e:
    print(e)

# class Visualitation:
#     def __init__(self, )

pygame.init()

screen = pygame.display.set_mode((800, 600))


if __name__ == "__main__":
    from parsing import Parse
    from algorithm import Dijkstra

    x = Parse("config.txt")
    if 1 == x.file_cleaner():
        exit(1)
    try:
        nb_drones, zones, metadic, connections, meta_connection_dic, end, start = x.parse_arguments()
    except Exception as e:
        print(e)
        exit(1)
    else:
        if zones is None or meta_connection_dic is None or connections is None or meta_connection_dic is None:
            exit(1)
        # print(metadic)
        p = Dijkstra(nb_drones=nb_drones,zones=zones,metadic=metadic,connections=connections,meta_connection_dic=meta_connection_dic, end=end, start=start)
        p.multi_path_finding()
        exit(0)