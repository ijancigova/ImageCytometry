from Tracking import *

b1 = [10,10,1,1]
b2 = [15,15,1,2]
b3 = [20,20,1,3]

b4 = [15, 30, 1, 7]
b5 = [15, 35, 1, 8]

b6 = [27,22,1,6]
b7 = [31,22,1,7]
b8 = [35,20,1,8]
b9 = [38,18,1,9]
b10 = [43,15,1,10]
b11 = [45,14,1,11]
b12 = [49,11,1,12]
b13 = [53,8,1,13]
b14 = [55,6,1,14]


b1 = [10,10,1,1]
b2 = [15,15,1,2]
b3 = [20,20,1,3]

b4 = [30, 30, 1, 5]
b5 = [20, 30, 1, 6]

b6 = [30,25,1,6]
b7 = [33,22,1,7]
b8 = [37,19,1,8]
b9 = [40,17,1,9]

tracks = [[b1,b2,b3],[b4,b5],[b6,b7,b8,b9,b10,b11]]
#tracks = [[b1,b2,b3],[b4,b5],[b6,b7,b8,b9,b10,b11]]
un = []
merge_tracks(tracks, un, 5,50)

# TODO 1 track blizsie, iny smer, 2 track dalej podobny smer
# 3-4 body
# 3 testy
# 45° track
