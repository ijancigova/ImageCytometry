import cv2
import numpy as np
import math
import random
import Tracking


def parse_xml(file):
    # naplnenie matice mat suradnicami bodov podla framov. Ak je zadama aj matrix- naplni sa "pomocna matica" (i,j) obsahuju cisla framov, v ktorych sa nachadzaju body so suradnicami i,j
    print('Parsing: ' + file)
    from xml.dom import minidom
    xmldoc = minidom.parse(file)
    frames = xmldoc.getElementsByTagName('frame')
    particles = xmldoc.getElementsByTagName('particle')
    print('\tframes: ' + str(len(frames)))
    # print(len(particles))
    range_from = 0
    mat =[]
    total_count = 0

    for f in frames:
        frame = []
        number = int(f.attributes['number'].value)
        count = int(f.attributes['particlesCount'].value)
        total_count += count
        for p in range(range_from, (range_from + count)):
            # print(particles[p].attributes['number'].value+', '+particles[p].attributes['x'].value+', '+particles[p].attributes['y'].value)
            # par_number = int(particles[p].attributes['number'].value)
            par_x = int(particles[p].attributes['x'].value)
            par_y = int(particles[p].attributes['y'].value)
            # frame.append([par_number,par_x, par_y])

            frame.append([par_x, par_y, 0, number, 26, 26])
            # if (fill_matrix):
            #     matrix[par_x][par_y].append(int(number))
            #     total_count += 1

        mat.append(frame)
        range_from = range_from + int(count);
    print('\tparticles: ' + str(total_count) )
    print('\tdone')
    return mat


# ------------------------------------------------------------------------------------------
def parse_xml_anastroj(file):
    print('Parsing: ' + file)
    import xml.etree.ElementTree as ET
    tree = ET.parse(file)
    root = tree.getroot()
    number = -1
    from math import floor
    tracks = []
    src_names = []

    for child in root: # images in data
        for child2 in child: # image in images
            print(str(child2.find('src').text))
            src_names.append(child2.find('src').text)
            for child3 in child2: # boundingboxes in image
                if (child3.tag == 'boundingboxes'):
                    boundingboxes = child3
                    number += 1
                    for boundingbox in boundingboxes.iter('boundingbox'):
                        x_left = int(boundingbox.find('x_left_top').text)
                        y_left = int(boundingbox.find('y_left_top').text)
                        width = int(boundingbox.find('width').text)
                        height = int(boundingbox.find('height').text)
                        x = int((x_left + floor(width / 2)))
                        y = int((y_left + floor(height/2)))
                        track_id = -1

                        for att in boundingbox.iter('attribute'):
                            if (att.text != None):
                                track_id = (att.text)

                        if (track_id != -1):
                            if (str(track_id) != 'false'):
                                if (track_id >= str(len(tracks))):
                                    # for pre tolko, kolko ich treba este pridat
                                    print('TI ', (track_id))
                                    print('tracks: ', int(len(tracks)) + 1)
                                    count_to_add = int(track_id) - int(len(tracks)) + 1
                                    for i in range(count_to_add):
                                        track = []
                                        tracks.append(track)
                                tracks[int(track_id)].append([x, y, 1, number, width, height])

                        if (number >= len(mat)):
                            # for pre tolko, kolko ich treba este pridat
                            count_to_add = int(number) - int(len(mat)) + 1
                            for i in range(count_to_add):
                                frame = []
                                mat.append(frame)
                        if (track_id == -1):
                            mat[int(number)].append([x, y, 0, number, width, height])
                        else:
                            mat[int(number)].append([x, y, 1, number, width, height])
                    #number += 1


    print('--- *************** TRACKS: ************************** ---')
    print(tracks)
    print('- - - - - - - - - - - - - - - - - - - - - - - - ')
    print('--- ***************** MATRIX: ************************ ---')
    print(mat)
    print('- - - - - - - - - - - - - - - - - - - - - - - - ')
    print(src_names)
    return tracks, mat, src_names
# ------------------------------------------------------------------------------------------
def save_as_anastroj_file(tracks, src_names, file_name):
    print('save file as anastroj: ', file_name)
    import xml.etree.ElementTree as element
    from io import BytesIO
    from math import floor

    document = element.Element('outer')
    node = element.SubElement(document, 'inner')
    et = element.ElementTree(document)
    f = BytesIO()
    et.write(f, encoding='utf-8', xml_declaration=True)
    print(f.getvalue())  # your XML file, encoded as UTF-8
    #root = element.SubElement(et,"data")



    root = element.Element("data")
    images = element.SubElement(root, "images")

    for x in range(len(mat)):
        image = element.SubElement(images,"image")

        if (len(src_names) != 0):
            src = element.SubElement(image, "src")
            src.text = str(src_names[x])

        boundingboxes = element.SubElement(image,"boundingboxes")
        for y in range(len(mat[x])):
            boundingbox = element.SubElement(boundingboxes,"boundingbox")
            x_left_top = element.SubElement(boundingbox, "x_left_top")
            x_left_top.text = str(mat[x][y][0]- floor(mat[x][y][4]/2))

            y_left_top = element.SubElement(boundingbox, "y_left_top")
            y_left_top.text = str(mat[x][y][1] - floor(mat[x][y][5]/2))

            width = element.SubElement(boundingbox, "width")
            width.text = str(mat[x][y][4])

            height = element.SubElement(boundingbox, "height")
            height.text = str(mat[x][y][5])
            class_name = element.SubElement(boundingbox, "class", {"name": 'bunka'})
            attribute = element.SubElement(class_name, "attribute", {"name":'track_id'})

            for n in range(len(tracks)):
                if (mat[x][y] in tracks[n]):
                    attribute.text = str(n)

    tree = element.ElementTree(root)
    tree.write('output_tracking\/' + file_name + '.xml')
    print('Done')
# ------------------------------------------------------------------------------------------
def remove_one_cell_from_all_frame(mat): # zmaze 1 bunku z kazdeho framu - bunku vyberie nahodne
    from random import randint
    for frame in range(len(mat)):
        rnd = randint(0, len(mat[frame]) - 1)
        mat[frame].pop(rnd)
    return mat
# ------------------------------------------------------------------------------------------
def remove_some_cell_random(mat, count): # zmaze pocet bunku zadanych parametrom z matice - bunku vyberie nahodne
    from random import randint
    for i in range(count):
        rnd1 = randint(0, len(mat) - 1)
        rnd2 = randint(0, len(mat[rnd1]) - 1)
        print('-------------------------------------------')
        print("LEN: ", len(mat[rnd1])," RND: ", rnd1, " RND2: ", rnd2, " cell: ", mat[rnd1])
        mat[rnd1].pop(rnd2)
        print("LEN: ", len(mat[rnd1]), " RND: ", rnd1, " RND2: ", rnd2, " cell: ", mat[rnd1])
    return mat
# ------------------------------------------------------------------------------------------
# metoda generuje xml popisujuce vytvorene tracky. Hodnoty (suradnice, casovy udaj) su prepocitane na microm a microsec- podla simulacie
def generate_tracks_xml_real(tracks, file_name, frame_rate, pixel_size):

    import xml.etree.cElementTree as element
    XML_root = element.Element("RBC_tracking", tracksCount=str(len(tracks)))
    for x in range(len(tracks)):
        frame = element.SubElement(XML_root, "track", number=str(x), particlesCount=str(len(tracks[x])))
        for y in range(len(tracks[x])):
            x_xml = tracks[x][y][0] * pixel_size
            y_xml = tracks[x][y][1] * pixel_size
            time = tracks[x][y][3] * frame_rate
            element.SubElement(frame, "particle", x=str(x_xml), y=str(y_xml), time=str(time))

    tree = element.ElementTree(XML_root)

    tree.write('output_tracking\/'+file_name+'.xml')

# ------------------------------------------------------------------------------------------
def generate_tracks_xml(tracks, file_name):

    import xml.etree.cElementTree as element
    XML_root = element.Element("RBC_tracking", tracksCount=str(len(tracks)))
    for x in range(len(tracks)):
        frame = element.SubElement(XML_root, "track", number=str(x), particlesCount=str(len(tracks[x])))
        for y in range(len(tracks[x])):
            time = tracks[x][y][3]
            x_xml = tracks[x][y][0]
            y_xml = tracks[x][y][1]
            element.SubElement(frame, "particle", x=str(x_xml), y=str(y_xml), time=str(time))

    tree = element.ElementTree(XML_root)
    tree.write(file_name)
# -------------------------------------------------------------------------------
def get_velocity(point_a, point_b):
    distance = get_distance(point_a, point_b)
    t = math.fabs(point_b[2]-point_a[2])
    v = distance / t
    return v
# --------------------------------------------------------------------------------------------
def create_matrix(x, y):
    # vytvorenie prazdnej matice o velkosti XxY
    # print('Creating matrix...')
    matrix = [[] for i in range(x)]
    for i in range(x):
        matrix[i] = [[] for j in range(y)]
    return matrix
# -----------------------------------------------------------------------------------------
def create_flow_matrix(x, y):
    # vytvorenie prazdnej matice o velkosti XxY
    # print('Creating matrix...')
    matrix = [[] for i in range(x)]
    for i in range(x):
        matrix[i] = [[-1, []] for j in range(y)]
    return matrix
# -------------------------------------------------------------------------------
def draw_unresolved_points(unresolved,img,radius =1):
    print('unresolved points: '+str(len(unresolved)))
    for j in range(len(unresolved)):
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        x = unresolved[j][0]
        y = unresolved[j][1]
        cv2.circle(img, (x, y), radius, color,2)
    return img
# --------------------------------------------------------------------------------
def draw_points(mat, img, radius=1, first=-1, last=-1):
    count = 0
    if ((first == -1) and (last == -1)):
        # chceme vykreslit vsetky framy
        print('Frame: all.')
        for i in range(len(mat)):
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            for j in range(len(mat[i])):
                x = mat[i][j][0]
                y = mat[i][j][1]
                # s = str(j) + "" + str(i)
                cv2.circle(img, (x, y), radius, color, 1)
                count += 1
                # cv2.putText(img, s, (x + 5, y + 5), cv2.FONT_HERSHEY_PLAIN, 0.9, (255, 255, 255))
        print('Particles: ' + str(count))
    elif ((first != -1) and (last == -1)):
        # chceme vykreslit jeden konkretny frame
        print('Frame: ' + str(first))
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        for j in range(len(mat[first])):
            x = mat[first][j][0]
            y = mat[first][j][1]
            s = str(j)
            cv2.circle(img, (x, y), radius, color, 1)
            count += 1
            cv2.putText(img, s, (x + 5, y + 5), cv2.FONT_HERSHEY_PLAIN, 0.9, (255, 255, 255))
        print('Particles: ' + str(count))
    else:
        # chceme vykreslit seq frameov od - do
        print('Frame: ' + str(first) + '-' + str(last))
        for i in range(first, (last + 1)):
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            for j in range(len(mat[i])):
                x = mat[i][j][0]
                y = mat[i][j][1]
                s = str(i) + "." + str(j)
                cv2.circle(img, (x, y), radius, color, 1)
                count += 1
                cv2.putText(img, s, (x + 5, y + 5), cv2.FONT_HERSHEY_PLAIN, 0.9, (255, 255, 255))
        print('Particles: ' + str(count))
    return img
#     --------------------------------------------------------------------------------------------------------------
def draw_tracks(tracks, img, first=-1, last=-1):
    print('draw tracks: drawing...')
    if ((first == -1) and (last == -1)):
        # chceme vykreslit vsetky tracky
        print('Tracks: all: ' + str(len(tracks)))
        for i in range(len(tracks)):
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            for j in range(len(tracks[i]) - 1):
                cv2.line(img, (int(tracks[i][j][0]), int(tracks[i][j][1])), ((int(tracks[i][j + 1][0]), int(tracks[i][j + 1][1]))), color,
                        1)
                # cv2.putText(img,s,(x+5,y+5),cv2.FONT_HERSHEY_PLAIN,0.9,(255,255,255))

    elif ((first != -1) and (last == -1)):
        # chceme vykreslit jeden konkretny track
        print('Track: ' + str(first))
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        # print(len(tracks[first]))
        for j in range(len(tracks[first]) - 1):
            cv2.line(img, (int(tracks[first][j][0]), int(tracks[first][j][1])),
                     ((int(tracks[first][j + 1][0]), int(tracks[first][j + 1][1]))),(255,255,255), 1)
    else:
        # chceme vykreslit seq trackov od - do
        print('Tracks: ' + str(first) + '-' + str(last))
        for i in range(first, (last + 1)):
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            for j in range(len(tracks[i]) - 1):
                cv2.line(img, (int(tracks[i][j][0]), int(tracks[i][j][1])), (int(tracks[i][j + 1][0]), int(tracks[i][j + 1][1])), color,
                         1)

    return img
#  ------------------------------------------------------------------------------------------------------------------
def draw_track_points(tracks,num, img):
    print('Track: ' + str(num))
    global unresolved_from_tracking
    global mat
    colorTrack = (0, 0, 255)
    colorUnresolved = (255, 0, 0)   # modra
    colorInTrack = (0, 255, 0)  # zelena
    frame = tracks[num][-1][3] + 1
    print(len(tracks[num]))
    for j in range(len(tracks[num]) - 1):
        cv2.line(img, (tracks[num][j][0], tracks[num][j][1]),
                 ((tracks[num][j + 1][0], tracks[num][j + 1][1])), colorTrack, 1)
    print('Last point of track: '+str(tracks[num][-1][3]))

    for i in range(len(mat[frame])):
        if(mat[frame][i][2] == 0):
            x = mat[frame][i][0]
            y = mat[frame][i][1]
            print('unresolved'+str(mat[frame][i]))
            print('distance: '+str(get_distance([mat[frame][i][0],mat[frame][i][1]],[tracks[num][-1][0],tracks[num][-1][1]])))
            cv2.circle(img, (x, y), 1, colorUnresolved, 1)
        else:
            x = mat[frame][i][0]
            y = mat[frame][i][1]
            cv2.circle(img, (x, y), 1, colorInTrack, 1)

    return img
#  -------------------------------------------------------------------------------------------------------------------
##############################################################
# get_distance(a, b)
# This function solves distance between a, b
# inputs:points a and b
# returns: distance between a, b
def get_distance(a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)
# -------------------------------------------------------------------------------------------------
def get_vector(x2,y2,x1,y1):
    x=x2-x1
    y=y2-y1
    return [x,y]
# ------------------------------------------------------------------------------------------------------------------
def get_expected_point(point,vector_x,vector_y):
    x = point[0] + vector_x
    y = point[1] + vector_y
    return [x,y]
# -----------------------------------------------------
# vypocet vektoroveho sucinu
def get_cross_product(vector_v,vector,switch):
    if(switch):
        if(vector[0]*vector_v[1]-vector[1]*vector_v[0] > 0):
            return 1
        else:
            return -1
    else:
        if(vector_v[0] * vector[1] - vector_v[1] * vector[0] >0):
            return 1
        else:
            return -1
# --------------------------------------------------------------------------------------------------------------------
# skalarny sucin
def get_product(vector1, vector2):
    return vector1[0]*vector2[0] + vector1[1]*vector2[1]
# --------------------------------------------------------------------------------------------------------------------
def calculate_flow_matrix():

    print('calculating flow matrix')
    points = 0
    global flow_matrix
    # vypocet vektorov pre body, ktore su v trackoch
    for i in range(len(tracks)):
        for j in range(len(tracks[i]) - 1):
            points +=1
            x1 = tracks[i][j][0]
            x2 = tracks[i][j + 1][0]
            x = x2 - x1
            y1 = tracks[i][j][1]
            y2 = tracks[i][j + 1][1]
            y = y2 - y1
            calculate_point(x,y,tracks[i][j][0],tracks[i][j][1],flow_matrix)

        # nastavenie vektora posledneho bodu v tracku
        points += 1
        calculate_point(x,y,tracks[i][-1][0],tracks[i][-1][1],flow_matrix)


    return flow_matrix
# -------------------------------------------------------------------------------------------------------------------
def calculate_point(vector_x, vector_y, cor_x, cor_y, flow_matrix):
    count = flow_matrix[cor_x][cor_y][0]

    if (count == -1):
        flow_matrix[cor_x][cor_y][1] = [vector_x, vector_y]
        flow_matrix[cor_x][cor_y][0] = 1
    else:
        #                 vypocet priemerneho vektora
        avg_x = ((count * flow_matrix[cor_x][cor_y][1][0]) + vector_x) / (count + 1)
        avg_y = ((count * flow_matrix[cor_x][cor_y][1][1]) + vector_y) / (count + 1)
        flow_matrix[cor_x][cor_y][1] = [avg_x, avg_y]
        flow_matrix[cor_x][cor_y][0] += 1
# -------------------------------------------------------------------------------------------------------------------
def resolve_flow_matrix():
    # doplnit o body, ktore nie su v trackoch
    print('resolving flow matrix: calculating vector for not resolved points')
    global flow_matrix
    global unresolved_from_tracking
    no = 0
    for k in range(len(unresolved_from_tracking)):
        x = unresolved_from_tracking[k][0]
        y = unresolved_from_tracking[k][1]
        if(flow_matrix[x][y][0] == -1):
            resolve_point(x, y, 1)
    #     else:
    #         no += 1
    #
    # print('Pocet bodov, ktore sa nedopocitavaju: '+ str(no))
    print('\tdone')
# --------------------------------------------------------------------
def resolve_point(cor_x, cor_y,iter):
    global flow_matrix

    max_x = len(flow_matrix) - 1
    max_y = len(flow_matrix[0]) - 1

    range_end = iter * 2 + 1
    range_start = -1 * iter
    candidates_vectors = []
    candidates_cor = []
    sum_x = 0
    sum_y = 0
    sum_distance = 0

    # rozsah pre y
    for j in range(range_start, (range_end + range_start)):
        # pocitame cely riadok

        if (j == range_start or j == range_start * (-1)):
            for i in range(range_start, (range_end + range_start)):
                if((cor_x + i <= max_x and cor_x + i >= 0 ) and (cor_y + j <= max_y and cor_y + j >= 0 )):   #overit suradnice
                # if ((cor_x + i <= max_x ) and (cor_y + j <= max_y  )):
                    # print(str(cor_x + i )+ ' ' +str(cor_y + j))
                    if (flow_matrix[cor_x + i][cor_y + j][0] > 0):
                        candidates_vectors.append(flow_matrix[cor_x + i][cor_y + j][1])
                        candidates_cor.append([cor_x + i,cor_y + j])
        else:

            if((cor_x + range_start <= max_x  and cor_x + range_start >= 0) and (cor_y + j <= max_y and cor_y + j >=0)):

                if (flow_matrix[cor_x + range_start][cor_y + j][0] > 0):
                    candidates_vectors.append(flow_matrix[cor_x + range_start][cor_y + j][1])
                    candidates_cor.append([cor_x + range_start,cor_y + j])
                elif (cor_x - range_start <= max_x and cor_y + j <= max_y):
                    if(flow_matrix[cor_x - range_start][cor_y + j][0] > 0):
                        candidates_vectors.append(flow_matrix[cor_x - range_start][cor_y + j][1])
                        candidates_cor.append([cor_x - range_start,cor_y + j])

    if (len(candidates_vectors) == 0):
         resolve_point(cor_x, cor_y, iter + 1)
    else:

        for s in range(len(candidates_vectors)):
            # nascitanie suradnic
            distance = get_distance([cor_x,cor_y],candidates_cor[s])
            sum_x += (1 / distance) * candidates_vectors[s][0]
            sum_y += (1 / distance) * candidates_vectors[s][1]            # # nascitanie menovatela
            sum_distance += (1 /distance)
            flow_matrix[cor_x][cor_y][1] = [sum_x / sum_distance, sum_y / sum_distance]
            flow_matrix[cor_x][cor_y][0] = 0
# -------------------------------------------------------------------------------------------------------------------
def predicting_tracking(max_dist, pa_parallel, pa_vertical):
    tracks = []
    unresolved = []
    print('predicting tracking: making tracks...')
    for f in range(len(mat) - 1):
        for i in range(len(mat[f])):
            # vytvaranie trackov : ak bod nie je oznaceny, vytvori novy track
            prev = False
            if (mat[f][i][2] == 0):
                mat[f][i][2] = 1
                track_index = len(tracks) #- 1 #............
                tracks.append([mat[f][i]])
            else:
                prev = True
                for n in range(len(tracks)):
                    if (mat[f][i] in tracks[n]):
                        track_index = n

            # ----------------------spajanie do trackov
            counter = 0
            for j in range(len(mat[f + 1])):
                x = mat[f][i][0]
                y = mat[f][i][1]
                if(prev):
                    # ocakavany bod
                    x = 2 * x - tracks[track_index][-2][0]
                    y = 2 * y - tracks[track_index][-2][1]

                    # kandidat
                    point_X = mat[f + 1][j]
                    point_D = [x,y]
                    point_C = [tracks[track_index][-1][0],tracks[track_index][-1][1]]

                    v = [point_X[0]-point_D[0], point_X[1]-point_D[1]]
                    v_size = get_distance(point_D,point_X)
                    p = [x-point_C[0], y-point_C[1]]
                    if(get_distance(point_D,point_C) == 0):
                        distance = get_distance([x, y], mat[f + 1][j])
                        if (distance <= max_dist):
                            counter += 1
                            if (counter > 1):
                                break
                            frame = f + 1
                            point = j
                    else:
                        vector_parallel = math.fabs(get_product(v,p))/get_distance(point_D,point_C)
                        # print('vector parallel: ' + str(vector_parallel))
                        # print('v size: ' + str(v_size))
                        vector_vertical = math.sqrt(round(v_size,5)**2-round(vector_parallel,5)**2 )

                        if (vector_parallel <= pa_parallel and vector_vertical <= pa_vertical):
                            counter += 1
                            if (counter > 1):
                                break
                            frame = f + 1
                            point = j
                else:
                    distance = get_distance([x,y], mat[f + 1][j])
                    if (distance <= max_dist ):
                        counter += 1
                        if (counter > 1):
                            break
                        frame = f + 1
                        point = j

            # ak bol uz pouzity tak ho nespajam

            if (counter == 1 and mat[frame][point][2] == 0):
                # prev_x = tracks[track_index][-1][0]
                # prev_y = tracks[track_index][-1][1]
                mat[frame][point][2] = 1
                tracks[track_index].append(mat[frame][point])

            else:
                # --------------------------- ODSTRANENIE JEDNOPRVKOVYCH TRACKOV
                if (len(tracks[track_index]) == 1):
                    tracks.pop(track_index)
                    mat[f][i][2] = 0
                    unresolved.append(mat[f][i])
    # vylepsit nepriradene prvky posledneho framu
    for i in range(len(mat[-1])):
        if (mat[-1][i][2] == 0):
            unresolved.append(mat[-1][i])

    print('\tnumber of tracks '+ str(len(tracks)))
    # print('Odstranenych bolo: '+str(removed))

    return tracks, unresolved

# ---------------------------------------------------------------------------------------------
def simple_tracking(max_dist):
    print('simple tracking: making tracks...')
    tracks = []
    unresolved = []
    for f in range(len(mat) - 1):
        for i in range(len(mat[f])):
            # vytvaranie trackov : ak bod nie je oznaceny, vytvori novy track
            if (mat[f][i][2] == 0):
                mat[f][i][2] = 1
                track_index = len(tracks)
                tracks.append([mat[f][i]])
            else:
                for n in range(len(tracks)):
                    if (mat[f][i] in tracks[n]):
                        track_index = n

            # ----------------------spajanie do trackov
            counter = 0
            for j in range(len(mat[f + 1])):
                distance = get_distance(mat[f][i], mat[f + 1][j])
                if (distance <= max_dist):
                    counter += 1
                    if (counter > 1):
                        break
                    frame = f + 1
                    point = j
            # ak bol uz pouzity tak ho nespajam

            if (counter == 1 and mat[frame][point][2] == 0):
                mat[frame][point][2] = 1
                tracks[track_index].append(mat[frame][point])
            else:
                # --------------------------- ODSTRANENIE JEDNOPRVKOVYCH TRACKOV
                if (len(tracks[track_index]) == 1):
                    tracks.pop(track_index)
                    mat[f][i][2] = 0
                    unresolved.append(mat[f][i])
    # vylepsit nepriradene prvky posledneho framu
    for i in range(len(mat[-1])):
        if (mat[-1][i][2] == 0):
            unresolved.append(mat[-1][i])

    # print('Pocet trackov: '+ str(len(tracks)))
    # print('Odstranenych bolo: '+str(removed))
    print('simple tracking: done. '+str(len(tracks))+ ' tracks')
    return tracks, unresolved
# ----------------------------------------------------------------------------
def simple_joining(tracks,threshold):
    print('simple joining with threshold set to '+str(threshold)+' and '+str(len(tracks))+ ' tracks : ')
    print('\tcalculating...')
    original_tracks = []
    pairs = []

    # konce porovnavame so zaciatkami
    for last in range(len(tracks)):
        candidates = []
        favorite = [-1]
        best_match = threshold
        for first in range(len(tracks)):
            if (last == first):
                continue
            # prvotna kontrola spajania trackov: cisla framov.
            last_frame_num = tracks[last][-1][3]
            first_frame_num = tracks[first][0][3]
            if (last_frame_num == first_frame_num - 1):
                # druha kontrola: poloha vektora
                if(can_join(last, first, tracks )):
                    candidates.append(first)

        if(len(candidates)>0):
            # spomedzi kandidatov sa vyberie favorita
            vector = flow_matrix[tracks[last][-1][0]][tracks[last][-1][1]][1]
            point = get_expected_point(tracks[last][-1], vector[0], vector[1])
            # print('candidates for '+str(last)+': '+str(candidates))
            for c in range(len(candidates)):
                distance = get_distance(point,tracks[candidates[c]][0])
                if( distance < best_match):
                    best_match = distance
                    favorite = [last, candidates[c], distance]

            if(favorite != [-1]):
                pairs.append(favorite)
            else:
                original_tracks.append(last)
                # print(str(last)+' prisiel o kandidatov. V spajani nebude zaciatkom.')

        # track pre ktory neexistuje kandidat na spojenie- ostane nespojeny
        else:
            original_tracks.append(last)
            # print('no candidates for '+str(last))

    # treba z originalov vyhodit tracky ktore sa nakoniec stali koncami
    for o in range(len(pairs)):
        if(original_tracks.count(pairs[o][1])>0):
            # print('odstranuje sa '+str(pairs[o][1]))
            original_tracks.remove(pairs[o][1])

    # print('Adepts for merging: '+str(len(pairs))+'\n'+str(pairs))
    # print('No merging: '+str(len(original_tracks))+'\n'+str(original_tracks))
    print('\tadepts for merging: ' + str(len(pairs)))
    print('\tdone')
    return pairs, original_tracks
# --------------------------------------------------------------------------------------------
def can_join(last, first, tracks):
    # global tracks

    vector_2 = get_vector(tracks[first][1][0], tracks[first][1][1], tracks[first][0][0], tracks[first][0][1])
    vector_1 = get_vector(tracks[last][-1][0], tracks[last][-1][1], tracks[last][-2][0], tracks[last][-2][1])
    vector_v = get_vector(tracks[first][0][0], tracks[first][0][1], tracks[last][-1][0], tracks[last][-1][1])

    product_v1_v = get_cross_product(vector_v, vector_1, True)
    product_v_v2 = get_cross_product(vector_v, vector_2, False)

    if (product_v1_v + product_v_v2 == 0):
        #     v nie je medzi v1 a v2
        return False
    else:
        return True
# --------------------------------------------------------------------------------------------
def can_append_start(track, unresolved):
    global flow_matrix
    vector_2 = get_vector(track[1][0], track[1][1], track[0][0], track[0][1])
    vector_1 = flow_matrix[unresolved[0]][unresolved[1]][1]
    vector_v = get_vector(track[0][0], track[0][1],unresolved[0], unresolved[1])

    product_v1_v = get_cross_product(vector_v, vector_1, True)
    product_v_v2 = get_cross_product(vector_v, vector_2, False)

    if (product_v1_v + product_v_v2 == 0):
        #     v nie je medzi v1 a v2
        return False
    else:
        return True
# --------------------------------------------------------------------------------------------
def can_append_end(track, unresolved):
    global flow_matrix
    vector_2 = flow_matrix[unresolved[0]][unresolved[1]][1]
    vector_1 = get_vector(track[-2][0], track[-2][1], track[-1][0], track[-1][1])
    vector_v = get_vector(unresolved[0], unresolved[1],track[-1][0], track[-1][1])

    product_v1_v = get_cross_product(vector_v, vector_1, True)
    product_v_v2 = get_cross_product(vector_v, vector_2, False)

    if (product_v1_v + product_v_v2 == 0):
        #     v nie je medzi v1 a v2
        return False
    else:
        return True
# --------------------------------------------------------------------------------------------
def check_duplicity(adepts_for_merging):
    print('check duplicity: looking for duplicities in adepts for merging')
    ends = [item[1] for item in adepts_for_merging]
    not_unique = set([x for x in ends if ends.count(x) > 1])
    if(len(not_unique) == 0):
        print('\tNO DUPLICITY')
        return adepts_for_merging
    else:
        print('\t' + str(len(not_unique))+ ' duplicities' )
        print('\t'+'solving...')

    distances = [item[2] for item in adepts_for_merging]

    size = len(not_unique)
    duplicates = []

    new_merging = adepts_for_merging.copy()
    for k in range(size):
        value = not_unique.pop()
        # print(value)
        duplicates.append([i for i,x in enumerate(ends) if x==value])

    # print(duplicates)
    for d in range(len(duplicates)):
        for p in range(len(duplicates[d])-1):
            if( distances[duplicates[d][p]] > distances[duplicates[d][p+1]]):
                new_merging.remove(adepts_for_merging[duplicates[d][p]])

            else:
                new_merging.remove(adepts_for_merging[duplicates[d][p+1]])


    print('\tdone')
    return new_merging
# ---------------------------------------------------------------------------------------------
def merge(start,end):
    merged_track = start.copy()
    for i in range(len(end)):
        merged_track.append(end[i])
    return merged_track
# ------------------------------------------------------------------------------------------------
def check_tracks_after_merging(tracks_to_check):

    error = False
    for i in range(len(tracks_to_check)):
        for j in range(len(tracks_to_check[i])-1):
            if(tracks_to_check[i][j][3] > tracks_to_check[i][j+1][3]):
                error = True
    if(error):
        print('!!!!!! THERE IS ERROR IN MERGED TRACKS !!!!!!')
        return False
    else:
        print('Everything is ok with merged tracks. Count: '+str(len(tracks_to_check)))
        return True
# -------------------------------------------------------------------------------------------------
def merge_tracks(tracks_for_merging, not_merging, tracks):
    print('merge tracks: merging tracks...')
    tracks_after_merging = []
    for x in range(len(tracks_for_merging)):
        start = tracks_for_merging[x][0]
        end = tracks_for_merging[x][1]
        # print('spajanie '+ str(start)+' '+str(end))
        merged_track = merge(tracks[start], tracks[end])



        for z in range(2,len(tracks_for_merging[x])):
            # print('pripojenie '+str(tracks_for_merging[x][z]))
            merged_track = merge(merged_track, tracks[tracks_for_merging[x][z]])

        tracks_after_merging.append(merged_track)
        # print(merged_track)
    for y in range(len(not_merging)):
        tracks_after_merging.append(tracks[not_merging[y]])
    print('\tdone')
    if(check_tracks_after_merging(tracks_after_merging)):
        return tracks_after_merging
# -------------------------------------------------------------------------------------------------
def find_multiple_merge(adepts):
    series = []
    for_remove = []
    print('searching for multiple merge in ' + str(len(adepts))+ ' adepts')
    for r in range(len(adepts)):
        adepts[r][2] = 0

    for i in range(len(adepts)):
        found = True
        if(adepts[i][2] == 0):
            index = len(series)
            adepts[i][2] = 1
            new =[adepts[i][0],adepts[i][1]]
            series.append(new)

            while(found):
                found = False
                for j in range(len(adepts)):

                    if(adepts[j][2] == 0):
                        if(series[index][-1] == adepts[j][0]):
                            found = True
                            adepts[j][2] = 1
                            series[index].append(adepts[j][1])


    # total = 0
    # total_multiple = 0
    # total_pair = 0
    # for s in range(len(series)):
    #     if(len(series[s]) == 2):
    #         total += 1
    #         total_pair += 1
    #     else:
    #         total += (len(series[s])-1)
    #         total_multiple += (len(series[s])-1)
    #         # print(series[s])
    #
    # print('kontrola '+ str(total)+ ' nasobne: '+str(total_multiple)+ ' dvojice: '+str(total_pair)+'\n nove spojenia '+str(len(series)))
    # print('\tfind multiple merge: '+str(series))
    print('\tdone')
    return series

#upravit nezaradene body podla matice MAT
def try_resolve_2(tracks, matrix, threshold):
    num = 0
    for track_index in range(len(tracks)):
        candidates_start = []
        candidates_end = []
        favorite_start = None
        favorite_end = None
        best_match_start = threshold
        best_match_end = threshold
        frame_last = tracks[track_index][-1][3]
        frame_first = tracks[track_index][0][3]
        # ak nieje posledny frame hlada sa bod na spojenie
        if frame_last != len(matrix) - 1:
            for unresolved_index in range(len(matrix[frame_last + 1])):
                # bod musi byt nezaradeny
                if matrix[frame_last + 1][unresolved_index][2] == 0 and \
                    can_append_end(tracks[track_index], matrix[frame_last + 1][unresolved_index]):
                    candidates_end.append( matrix[frame_last + 1][unresolved_index])
        if frame_first != 0:
            for unresolved_index in range(len(matrix[frame_first - 1])):
                # bod musi byt nezaradeny
                if matrix[frame_first - 1][unresolved_index][2] == 0 and \
                        can_append_start(tracks[track_index], matrix[frame_first - 1][unresolved_index]):
                    candidates_start.append(matrix[frame_first - 1][unresolved_index])
        # print(candidates_end)
        # print(candidates_start)
        # prechadzanie kandidatov na zaciatky
        if len(candidates_start) > 0:
            # hladanie bodu najblizsieho k ocakavanej hodnote
            for c in range(len(candidates_start)):
                vector = flow_matrix[candidates_start[c][0]][candidates_start[c][1]][1]
                x = candidates_start[c][0]
                y = candidates_start[c][1]
                point = get_expected_point([x, y], vector[0], vector[1])
                distance = get_distance(point, tracks[track_index][0])
                if distance < best_match_start:
                    best_match_start = distance
                    # pamatame si iba index
                    favorite_start = candidates_start[c]
        # prehladavanie kandidatov na konce
        if len(candidates_end) > 0:
            # hladanie bodu najblizsieho k ocakavanej hodnote
            for c in range(len(candidates_end)):
                vector = flow_matrix[tracks[track_index][-1][0]][tracks[track_index][-1][1]][1]
                x = tracks[track_index][-1][0]
                y = tracks[track_index][-1][1]
                point = get_expected_point([x, y], vector[0], vector[1])
                distance = get_distance(point, candidates_end[c])
                if distance < best_match_end:
                    best_match_end = distance
                    favorite_end = candidates_end[c]

        if favorite_start is not None:
            # kandidata pripojime na zaciatok
            # print('================ pripajame na zaciatok tracku '+str(t)+' '+ str(tracks[t])+' bod: ' +str(unresolved[favorite_start]))
            num += 1
            favorite_start[2] = 1
            tracks[track_index].insert(0, favorite_start)
            # print(str(tracks[t]))
        if favorite_end is not None:
            num += 1
            # print('================ pripajame na koniec tracku'+str(t)+' '+ str(tracks[t])+' bod: ' +str(unresolved[favorite_end]))
            favorite_end[2] = 1
            tracks[track_index].append(favorite_end)

    print('Resolved points=' + str(num))
    return num
# ---------------------------------------------------------------------------------------------
def try_resolve(tracks, unresolved, threshold):
    print('try ro resolve points with threshold set to '+str(threshold)+', '+str(len(tracks))+ ' tracks and '+str(len(unresolved))+' unresolved : calculating...')
    num = 0
    for t in range(len(tracks)):
        candidates_start = []
        candidates_end = []
        favorite_start = -1
        favorite_end = -1
        best_match_start = threshold
        best_match_end = threshold
        for u in range(len(unresolved)):
    #           skusime pripojit na koniec tracku:kontrola naslednosti framu
    #         print(unresolved[u])
            if(unresolved[u][2] == 0):
                if((tracks[t][0][3] -1) == unresolved[u][3] ):
                    if(can_append_start(tracks[t],unresolved[u])):
                        candidates_start.append([u,unresolved[u]])
                elif(tracks[t][-1][3] == (unresolved[u][3] - 1)):
                    if(can_append_end(tracks[t],unresolved[u])):
                        candidates_end.append([u,unresolved[u]])

        # prechadzanie kandidatov na zaciatky
        if(len(candidates_start) > 0):
    #         hladanie bodu najblizsieho k ocakavanej hodnote
            for c in range(len(candidates_start)):
                vector = flow_matrix[candidates_start[c][1][0]][candidates_start[c][1][1]][1]
                x = candidates_start[c][1][0]
                y = candidates_start[c][1][1]
                point = get_expected_point([x,y],vector[0],vector[1])
                distance = get_distance(point,tracks[t][0])
                if(distance < best_match_start):
                    best_match_start = distance
                    # pamatame si iba index
                    favorite_start = candidates_start[c][0]
        # prehladavanie kandidatov na konce
        if (len(candidates_end) > 0):

            #         hladanie bodu najblizsieho k ocakavanej hodnote
            for c in range(len(candidates_end)):
                vector = flow_matrix[tracks[t][-1][0]][tracks[t][-1][1]][1]
                x = tracks[t][-1][0]
                y = tracks[t][-1][1]
                point = get_expected_point([x,y], vector[0],vector[1])
                distance = get_distance(point, candidates_end[c][1])
                if (distance < best_match_end):
                    best_match_end = distance
                    favorite_end = candidates_end[c][0]

        if(favorite_start != -1 ):
    #         kandidata pripojime na zaciatok
    #         print('================ pripajame na zaciatok tracku '+str(t)+' '+ str(tracks[t])+' bod: ' +str(unresolved[favorite_start]))
            num += 1
            unresolved[favorite_start][2] = 1
            tracks[t].insert(0,unresolved[favorite_start])
            # print(str(tracks[t]))
        if(favorite_end != -1):
            num += 1
            # print('================ pripajame na koniec tracku'+str(t)+' '+ str(tracks[t])+' bod: ' +str(unresolved[favorite_end]))
            unresolved[favorite_end][2] = 1
            tracks[t].append(unresolved[favorite_end])
            # print(str(tracks[t]))

    new_unresolved = []
    for u in range(len(unresolved)):
        if(unresolved[u][2] == 0):
            new_unresolved.append(unresolved[u])

    print('resolved '+str(num)+' points, unresolved: '+str(len(new_unresolved))+ ' tracks: '+str(len(tracks)))

    return tracks,new_unresolved
# -------------------------------------------------------------------------------------------------
def get_points_in_flow_matrix():
    not_in_tracks = 0
    in_tracks = 0
    global flow_matrix
    for i in range(len(flow_matrix)):
        for j in range(len(flow_matrix[i])):
            if(flow_matrix[i][j][0] == 0):
                not_in_tracks += 1
            elif(flow_matrix[i][j][0] != -1):
                in_tracks += flow_matrix[i][j][0]

    print('====== POINTS IN FLOW MATRIX ======')
    print('in tracks: '+str(in_tracks))
    print('not in tracks: ' + str(not_in_tracks))
    print('total: ' + str(not_in_tracks+in_tracks))
# -------------------------------------------------------------------------------------------------
def get_point_tracking(tracks):
    resolved_tracking = 0
    unresolved_tracking = 0

    global mat
    for t in range(len(tracks)):
        resolved_tracking += len(tracks[t])
    unresolved_tracking = len(unresolved_from_tracking)
    print('====== POINTS AFTER SIMPLE TRACKING ======')
    print('in tracks: '+str(resolved_tracking))
    print('not in tracks: ' + str(unresolved_tracking))
    print('total: ' + str(unresolved_tracking+resolved_tracking))
    print('====== POINTS IN MATRIX ======')
    used = 0
    not_used = 0
    for i in range(len(mat)):
        for j in range(len(mat[i])):
            if(mat[i][j][2] == 0):
                not_used += 1
            else:
                used += 1
    print('in tracks: ' + str(used))
    print('not in tracks: ' + str(not_used))
    print('total: ' + str(not_used + used))
# -----------------------------------------------------------------------------------------------




# -------------------------------------------------------------------------------------------------
# #  ZISTIT OZAJSTNE ROZLISENIE OBRAZKU
# frame_rate = 1/30
# pixel_size = 1/3
# # simulation
# # sim_x = 160
# # sim_y = 200
#
# # video
# resolution_x = 1280
# resolution_y = 720
#
# # resolution_x = 320
# # resolution_y = 240
# #
# # resolution_x = 800
# # resolution_y = 600
#
# tracks = []
# unresolved_from_tracking = []
# mat =[]
# # # unresolved = []
# #
# imgP = np.zeros((resolution_y, resolution_x, 3), np.uint8)
# imgT = np.zeros((resolution_y, resolution_x, 3), np.uint8)
# # imgTP = np.zeros((resolution_y, resolution_x, 3), np.uint8)
#
# # img_simulation_tracks = np.zeros((sim_y, sim_x, 3), np.uint8)
# # img_video_tracks = np.zeros((int(resolution_y*pixel_size), int(resolution_x*pixel_size), 3), np.uint8)
# # # mat = parse_xml('export_imageJ_320x240.xml')
# mat = parse_xml('export_U_shape.xml')
# # # mat = parse_xml('final_export_800x600px.xml')
# # # mat = parse_xml('export_800x600_redukcny_radius_12px.xml')
# #
# tracks, unresolved_from_tracking = predicting_tracking(12, 12, 3)
# # # # tracks, unresolved_from_tracking = predicting_tracking(12, 8, 8)
# flow_matrix = create_flow_matrix(resolution_x, resolution_y)
# calculate_flow_matrix()
# resolve_flow_matrix()
# # #
# # # # get_points_in_flow_matrix()
# # # # get_point_tracking()
# incJ = 1
# merged_tracks = tracks.copy()
# while(True):
#     print('========================================== KOLO ' +str(incJ)+'. JOINING ======================================')
#     adepts,original_tracks = simple_joining(merged_tracks, 12)
#     if (len(adepts) == 0):
#         print('there is nothing to merge ')
#         break
#     new_adepts = check_duplicity(adepts)
#     final = find_multiple_merge(new_adepts)
#     merged_tracks_w = merge_tracks(final,original_tracks,merged_tracks)
#     merged_tracks = merged_tracks_w.copy()
#
#     incJ += 1
#
# incR = 1
# print('================================================== KOLO ' +str(incR)+'. RESOLVE ==============================================')
# new_merged, new_unresolved = try_resolve(merged_tracks,unresolved_from_tracking,12)
#
#
# # generate_tracks_xml(merged_tracks_w2,'tracks_test_px.xml')
# generate_tracks_xml_real(new_merged,'tracks_test_real_U_shape.xml',frame_rate, pixel_size)
# generate_tracks_xml(new_merged,'tracks_test_U_shape.xml')

# track_point = draw_track_points(tracks,13,imgTP)
# points_img = draw_unresolved_points(unresolved_from_tracking,imgP)
# tracks_img = draw_tracks(new_merged,imgT)
# long_tracks = []
# for i in range(len(new_merged)):
#     if(len(new_merged[i])>10):
#       long_tracks.append(new_merged[i])
#
# tracks_img = draw_tracks(long_tracks,imgT)
# cv2.imshow('merged_tracks', tracks_img)
# cv2.imshow('points', points_img)
# cv2.imwrite('img\dip_tracks.png',tracks_img)
# cv2.imwrite('img\dip_points.png',points_img)
#
# parsed_tracks = parse_xml_tracks('tracks_test_real_U_shape.xml')
# get_results_simulation(parsed_tracks)
# imgTP = np.zeros((int(720*pixel_size), int(1280*pixel_size), 3), np.uint8)
# # imgTP = np.zeros((int(720), int(1280), 3), np.uint8)
#
# tracksP_img = draw_tracks(parsed_tracks,imgTP)
# cv2.line(tracksP_img, (int(772*pixel_size), int(580*pixel_size)),(int(880*pixel_size),int(688*pixel_size)), (0, 255, 255), 1)
# cv2.line(tracksP_img, (int(706*pixel_size), int(375*pixel_size)),(int(906*pixel_size),int(375*pixel_size)), (0, 255, 255), 1)
# cv2.line(tracksP_img, (int(772*pixel_size), int(62*pixel_size)),(int(880*pixel_size),int(169*pixel_size)), (0, 255, 255), 1)

#  =====================================NACITANIE TRACKOV ZO SIMULACIE A ICH VYKRESLENIE SPOLU S CIARAMI
# parsed_tracks_simulation = parse_xml_tracks('simulation_tracks5.xml')
# get_results_simulation(parsed_tracks_simulation)
# img_sim_tracks = draw_tracks(parsed_tracks_simulation,img_simulation_tracks)
# # H!
# cv2.line(img_sim_tracks, (67,195),(95,167), (0, 255, 255), 1)
#
# cv2.line(img_sim_tracks, (67,100),(95,100), (0, 255, 255), 1)
# # v skutocnosti hranica H3
# cv2.line(img_sim_tracks, (95,5),(67,32), (0, 255, 255), 1)
# # cv2.imwrite('img\simulation_tracks5.png',img_sim_tracks)
# cv2.imshow('tracks from simulation', img_sim_tracks)
# =======================================================================================================

#  =====================================NACITANIE TRACKOV Z VIDEA A ICH VYKRESLENIE SPOLU S CIARAMI
# parsed_tracks_simulation = parse_xml_tracks('test_priesecnik_U.xml')
# pixel_size = 1/3
# parsed_tracks = parse_xml_tracks('output_tracking\/povodna_detekcia _3.xml')
# results=get_results_video(parsed_tracks)
# write_results_to_file('output_velocity\/test.txt',results)
#
# img_video_tracks = np.zeros((int(720*pixel_size), int(1280*pixel_size), 3), np.uint8)
# img_video_tracks = draw_tracks(parsed_tracks,img_video_tracks)
# cv2.line(img_video_tracks, (int(772*pixel_size), int(62*pixel_size)),(int(880*pixel_size),int(169*pixel_size)), (0, 255, 255), 1)
# cv2.line(img_video_tracks, (int(771*pixel_size), int(62*pixel_size)),(int(880*pixel_size),int(170*pixel_size)), (0, 0, 255), 1)
# cv2.line(img_video_tracks, (int(773*pixel_size), int(62*pixel_size)),(int(880*pixel_size),int(168*pixel_size)), (255, 0, 255), 1)
#
# cv2.line(img_video_tracks, (int(772*pixel_size), int(350*pixel_size)),(int(880*pixel_size),int(350*pixel_size)), (0, 255, 255), 1)
# cv2.line(img_video_tracks, (int(772*pixel_size), int(580*pixel_size)),(int(880*pixel_size),int(688*pixel_size)), (0, 255, 255), 1)
#
# cv2.imshow('tracks from video', img_video_tracks)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
# ========================================================================



# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////

print('------------------------------------------')
print('------------------------------------------')
print('------------------------------------------')
print('------------------------------------------')
# file_name = input('File name for parse: [export_1280x720_3_30_radius_12.xml]')
#file_name = 'export_1280x720_3_30_radius_12.xml'
file_name = 'anastroj_1280x720_3_30_radius_12.xml'
#file_name = 'anastroj_1280x720_3_30_12px.xml'
#--toto nie, to je ine:
# file_name = 'export_800x600_3_30_12px.xml'
resolution = file_name.split('_')
x,y = resolution[1].split('x')

frame_rate = 1/int(resolution[3])
pixel_size = 1/int(resolution[2])

tracks = []
unresolved_from_tracking = []
mat =[]
src_names = []

if (resolution[0] == 'anastroj'):
    tracks, mat, src_names = parse_xml_anastroj('input_tracking\/'+file_name)
else:
    mat = parse_xml('input_tracking\/'+file_name)

# zmaze niektore bunky z anastroja - z matice mat !!!!!!!!!!!!!!
#mat = remove_one_cell_from_all_frame(mat)
#mat = remove_one_cell_from_all_frame(mat)
mat = remove_some_cell_random(mat, 50)

if (str(len(tracks) == '0')):
    print('-----------------------------------------------------------------------------------------------')
    #parameters = input('Parameters (dist a b) for simple tracking: [12,8,8]')
    parameters = '12 8 8'
    parameters = parameters.split(' ')
    dist = int(parameters[0])
    a = int(parameters[1])
    b = int(parameters[2])
    tracks, unresolved_from_tracking = predicting_tracking(dist, a, b)

flow_matrix = create_flow_matrix(int(x), int(y))
calculate_flow_matrix()
resolve_flow_matrix()

merged_tracks = tracks.copy()
print('-----------------------------------------------------------------------------------------------')

# join_dist = input('Parameter (dist) for joining tracks: [12]')
join_dist = '12'
join = True

while(join):

  adepts, original_tracks = simple_joining(merged_tracks, int(join_dist))
  if (len(adepts) == 0):
    print('There is nothing to merge. ')
    break

  new_adepts = check_duplicity(adepts)
  final = find_multiple_merge(new_adepts)
  merged_tracks_w = merge_tracks(final,original_tracks,merged_tracks)
  merged_tracks = merged_tracks_w.copy()

  # repeat_join = input('Would you like to repeat joining with new set of tracks?')
  repeat_join = 'y'
  if (repeat_join == 'y' or repeat_join == 'yes' or repeat_join == 'Y' or repeat_join == 'YES'):
      join = True
  else:
      join = False
print('-----------------------------------------------------------------------------------------------')
# resolve_dist = input('Parameter (dist) for resolve points: [12]')
resolve_dist = '12'
resolve = True

while resolve:
  num = try_resolve_2(merged_tracks, mat, int(resolve_dist))
  if num == 0:
      break

'''new_merged, new_unresolved = try_resolve(merged_tracks, unresolved_from_tracking, int(resolve_dist)) #TODO mat pouzit
  if (len(new_unresolved) == len(unresolved_from_tracking)):
    print('No points resolved. ')
    break
  merged_tracks = new_merged.copy()
  unresolved_from_tracking = new_unresolved.copy()
  repeat_resolve = input('Would you like to repeat resolving?')
  repeat_resolve = 'y'

  if (repeat_resolve == 'y' or repeat_resolve == 'yes' or repeat_resolve == 'Y' or repeat_resolve == 'YES'):
      resolve = True
  else:
      resolve = False'''


print('-----------------------------------------------------------------------------------------------')
# file_xml = input('File name for export: ')
file_xml = "some_file.xml"
generate_tracks_xml_real(merged_tracks,file_xml,frame_rate, pixel_size)
print('-----------------------------------------------------------------------------------------------')

# --- ***
show = 'y'
save = input('1 Would you like to save as anastroj file?')
if (save == 'y' or save == 'yes' or save == 'Y' or save == 'YES'):
    file_name = input('1 File name for anastroj export: ')
    save_as_anastroj_file(tracks, src_names, file_name)

if (show == 'y' or show == 'yes' or show == 'Y' or show == 'YES'):
    name = input('1 File name for img:')
    img_tracks = np.zeros((int(y), int(x), 3), np.uint8)
    img = draw_tracks(merged_tracks, img_tracks)

    cv2.imwrite('img\/'+name+'.png', img)
    cv2.imshow('1 Final tracks from tracking', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
# --- ***


# show = input('Would you like to show and save img of final tracks?')
show = 'y'
Tracking.merge_tracks(merged_tracks, unresolved_from_tracking, 10, 12)

save = input('Would you like to save as anastroj file?')
#save = 'y'
if (save == 'y' or save == 'yes' or save == 'Y' or save == 'YES'):
    file_name = input('File name for anastroj export: ')
    save_as_anastroj_file(tracks, src_names, file_name)

if (show == 'y' or show == 'yes' or show == 'Y' or show == 'YES'):
    name = input('File name for img:')
    img_tracks = np.zeros((int(y), int(x), 3), np.uint8)
    img = draw_tracks(merged_tracks, img_tracks)

    cv2.imwrite('img\/'+name+'.png', img)
    cv2.imshow('Final tracks from tracking', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
print('-----------------------------------------------------------------------------------------------')