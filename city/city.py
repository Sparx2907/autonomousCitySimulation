import kivy

from kivy.animation import Animation
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scatter import Scatter
from kivy.uix.button import Button
from kivy.properties import NumericProperty, ListProperty
from kivy.clock import Clock
from kivy.core.window import Window
from random import randint
from random import random
from functools import partial

'''
car model : [id, where come from, where to go]
where to go: (turns, nbr way(0 or 1))
turns: forward(1),right(0),left(2)
intersec path[pos]:
            _|0   |_
                    3
           1_      _
             |   2|
'''

class Car(Widget):
    angle = NumericProperty(0)
    r = NumericProperty(0)
    g = NumericProperty(0)
    b = NumericProperty(0)
    def on_angle(self, item, angle):
        if angle == 360:
            item.angle = 0

class VertRoad(Widget):
    '''
    vertroad queue pos:
            |0   |
            |    |
            |   1|
    '''

    roadWidth = NumericProperty(0)
    roadLength = NumericProperty(0)
    queue = ListProperty([])

    def roadProg(self, queue, pathAnim):
        pathAnim = [
            [[] * self.roadLength],
            [[] * self.roadLength]
        ]
        c = self.center
        o = [c[0], c[1] + self.height/2]
        for i in range(0, len(pathAnim[0])):
            for j in range(0, 2):
                pathAnim[i].append((
                    c[0] + (j*2-1)*40,
                    (1-j)*(c[1] + 40*2*i + 40) + j*(self.height-(c[1] + 40*2*i + 40))
                ))
                self.add_widget(Car(pos=pathAnim[i][j]))



class HorizRoad(Widget):
    '''
    horizRoad queue pos:
            ________
                    1
           0________
    '''

    roadWidth = NumericProperty(0)
    roadLength = NumericProperty(0)
    queue = ListProperty([])

class Grass(Widget):
    pass

class Intersec(Widget):

    global doNextMoveF
    global doNextMoveR
    doNextMoveF = []
    doNextMoveR = []
    roadWidth = NumericProperty(0)
    queue = ListProperty([])
    inter = ListProperty([])
    x = NumericProperty(0)
    y = NumericProperty(0)

    X = root.x
    Y = root.y
    inQueue = queue.get()[x][y]
    outQueue = [queue.get()[x-1][y][1], queue.get()[x][y-1][1], queue.get()[x+1][y][0], queue.get()[x][y+1][0]]

    def intersecProg(self, inQueue, outQueue, inter, *largs):

        self.add_widget(BG())
        c = self.center
        c = [c[0] - 20, c[1] - 20]
        nbrWays = 2
        animDur = 0.3
        roadAlign = 40
        dirToTake = ((1, 0), (0, 1), (-1, 0), (0, -1))
        startPos = (((0, 0), (0, 1)), ((3, 0), (2, 0)), ((3, 3), (3, 2)), ((0, 3), (1, 3)))
        endPos = (((0, 3), (0, 2)), ((0, 0), (1, 0)), ((3, 0), (3, 1)), ((3, 3), (2, 3)))

        pathAnim = [
            ((c[0] - roadAlign * 3, c[1] + roadAlign * 3), (c[0] - roadAlign, c[1] + roadAlign * 3), (c[0] + roadAlign, c[1] + roadAlign * 3), (c[0] + roadAlign * 3, c[1] + roadAlign * 3)),
            ((c[0] - roadAlign * 3, c[1] + roadAlign), (c[0] - roadAlign, c[1] + roadAlign), (c[0] + roadAlign, c[1] + roadAlign), (c[0] + roadAlign * 3, c[1] + roadAlign)),
            ((c[0] - roadAlign * 3, c[1] - roadAlign), (c[0] - roadAlign, c[1] - roadAlign), (c[0] + roadAlign, c[1] - roadAlign), (c[0] + roadAlign * 3, c[1] - roadAlign)),
            ((c[0] - roadAlign * 3, c[1] - roadAlign * 3), (c[0] - roadAlign, c[1] - roadAlign * 3), (c[0] + roadAlign, c[1] - roadAlign * 3), (c[0] + roadAlign * 3, c[1] - roadAlign * 3)),
        ]
        inQueueAnim = [
            ((c[0] - roadAlign * 3, c[1] + roadAlign * 11), (c[0] - roadAlign, c[1] + roadAlign * 11)),
            ((c[0] - roadAlign * 11, c[1] - roadAlign * 3), (c[0] - roadAlign * 11, c[1] - roadAlign)),
            ((c[0] + roadAlign * 3, c[1] - roadAlign * 11), (c[0] + roadAlign, c[1] - roadAlign * 11)),
            ((c[0] + roadAlign * 11, c[1] + roadAlign * 3), (c[0] + roadAlign * 11, c[1] + roadAlign))
        ]
        outQueueAnim = [
            ((c[0] + roadAlign * 3, c[1] + roadAlign * 11), (c[0] + roadAlign, c[1] + roadAlign * 11)),
            ((c[0] - roadAlign * 11, c[1] + roadAlign * 3), (c[0] - roadAlign * 11, c[1] + roadAlign)),
            ((c[0] - roadAlign * 3, c[1] - roadAlign * 11), (c[0] - roadAlign, c[1] - roadAlign * 11)),
            ((c[0] + roadAlign * 11, c[1] - roadAlign * 3), (c[0] + roadAlign * 11, c[1] - roadAlign))
        ]


        nbrCars = sum([len(way) for way in inQueue])
        def moveCar(car, futurePos, ttDur):
            oldPos = car[3].pos[:]
            angle = car[3].angle
            movex, movey = futurePos[0] - oldPos[0], futurePos[1] - oldPos[1]
            if movex < 0:
                correctAngle = 270
                if angle == 0: correctAngle = -90
            elif movex > 0:
                correctAngle = 90
            elif movey < 0:
                correctAngle = 0
                if angle == 270: correctAngle = 360
            else:
                correctAngle = 180

            def forwardAnim(futurePos, dur, *largs):
                doNextMoveR.pop()
                anim = Animation(pos=futurePos, duration=ttDur-dur)
                doNextMoveF.append(False)
                anim.start(largs[1])
                anim.bind(on_complete=partial(popNextMoveF))

            dur = ttDur*0.1
            if correctAngle == angle: dur = 0
            doNextMoveR.append(False)
            rotat = Animation(angle=correctAngle, duration=dur)
            rotat.start(car[3])
            rotat.bind(on_complete=partial(forwardAnim, futurePos, dur))


        def checkPass(currentPos, posToGo, time):
            if time in inter[posToGo[0]][posToGo[1]]:
                potBlocCar = inter[posToGo[0]][posToGo[1]][time]
                if potBlocCar[2][0] == 1 and potBlocCar[1][1] != potBlocCar[2][1]:  # check if goes forward and changes way
                    if (time+1) in inter[currentPos[0]][currentPos[1]]:
                        if potBlocCar[0] == inter[currentPos[0]][currentPos[1]][time+1][0]: # check if that car goes where you are
                            return True
            if (time + 1) in inter[posToGo[0]][posToGo[1]]:
                return True
            else:
                return False

        def popNextMoveF(anim, widget):
            doNextMoveF.pop()

        if len(doNextMoveF)+len(doNextMoveR) == 0:
            # move by 1 every car
            for x in range(0, nbrWays*2):
                for y in range(0, nbrWays * 2):
                    newInterCase = {}
                    if inter[x][y] != {0: []}:
                        for time, car in inter[x][y].items():
                            carDest = ((car[1][0] + car[2][0] + 1) % 4, car[2][1])
                            if endPos[carDest[0]][carDest[1]] == (x, y) and time == 0:
                                outQueue[carDest[0]][carDest[1]].append(car)            # move car to outqueue if reach destination
                                moveCar(car, outQueueAnim[carDest[0]][carDest[1]], animDur)
                            elif time != 0:
                                newInterCase.update({time - 1: car})                    # move by 1 on timeline in case
                        inter[x][y] = newInterCase                                     # change the state of the case
                        if 0 in inter[x][y]:
                            moveCar(newInterCase[0], pathAnim[x][y], animDur)
            newInQueue = []
            for road in inQueue:                         # remove or reduce timer for cars in inqueue
                newRoad = []
                for way in road:
                    itemToKeep = []
                    for i in range(0, len(way)):
                        item = way[i]
                        if item[1] != 0:
                            if item[1] != -1:
                                item[1] -= 1
                            itemToKeep.append(item)
                    newRoad.append(itemToKeep[:])
                newInQueue.append(newRoad[:])
            inQueue = newInQueue[:]

            # take care of queue (add paths for cars)
            for road in range(0, 4):
                for way in range(0, nbrWays):
                    for carIndex in range(0, len(inQueue[road][way])):
                        if inQueue[road][way][carIndex][1] == -1:
                            car = inQueue[road][way][carIndex][0]
                            doNotPath = True
                            markdown = 0
                            testPath = []
                            while doNotPath:                                # search for path
                                doNotPath = False
                                markdown += 1
                                x, y = startPos[car[1][0]][car[1][1]]
                                doNotPath = doNotPath or markdown in inter[x][y]
                                testPath = [markdown]

                                if car[2][0] != 1:                          # not forward
                                    futurePath = [(x, y)]
                                    for i in range(0, car[2][0] + abs(car[2][1] - int(car[2][0]*(1/2)))):         # go straight until facing exit
                                        x, y = x + dirToTake[car[1][0]][0], y + dirToTake[car[1][0]][1]
                                        futurePath.append((x, y))
                                        doNotPath = doNotPath or checkPass(futurePath[-2], (x, y), markdown + i)
                                        testPath.append(markdown + i + 1)

                                    x, y = futurePath[-1]
                                    markDone = car[2][0] + abs(car[2][1] - int(car[2][0]*(1/2)))
                                    for i in range(0, car[2][0] + abs(car[1][1] - int(car[2][0]*(1/2)))):        # straight after the turn towards exit
                                        turnDir = (car[1][0]+car[2][0]-1) % 4
                                        x, y = x + dirToTake[turnDir][0], y + dirToTake[turnDir][1]
                                        futurePath.append((x, y))
                                        doNotPath = doNotPath or checkPass(futurePath[-2], (x, y), markdown + i + markDone)
                                        testPath.append(markdown + i + markDone)


                                else:                                       # forward
                                    futurePath = [(x, y)]
                                    if car[1][1] != car[2][1]:      # if have to change way
                                        indexChange = 0
                                        doNotPath = True
                                        while doNotPath and indexChange < nbrWays*2:
                                            doNotPath = False
                                            testPath = []

                                            x, y = startPos[car[1][0]][car[1][1]]
                                            futurePath = [(x, y)]
                                            doNotPath = doNotPath or markdown in inter[x][y]
                                            testPath.append(markdown)

                                            for i in range(0, nbrWays*2):
                                                if i == indexChange:
                                                    changeMovX = startPos[car[1][0]][car[2][1]][0] - startPos[car[1][0]][car[1][1]][0]
                                                    changeMovY = startPos[car[1][0]][car[2][1]][1] - startPos[car[1][0]][car[1][1]][1]
                                                    x, y = x + changeMovX, y + changeMovY
                                                    doNotPath = doNotPath or (markdown + i) in inter[x][y]
                                                    testPath.append("front collide test: " + str(markdown + i))
                                                else:
                                                    x, y = x + dirToTake[car[1][0]][0], y + dirToTake[car[1][0]][1]
                                                futurePath.append((x, y))
                                                doNotPath = doNotPath or checkPass(futurePath[-2], (x, y), markdown + i)

                                                testPath.append(markdown + i + 1)
                                            indexChange += 1

                                    else:                           # if no change way
                                        for i in range(0, nbrWays * 2 - 1):
                                            x, y = x + dirToTake[car[1][0]][0], y + dirToTake[car[1][0]][1]
                                            futurePath.append((x, y))
                                            doNotPath = doNotPath or checkPass(futurePath[-2], (x, y), markdown + i)
                            for i in range(0, len(futurePath)):             # Add whole path at end timeline
                                x, y = futurePath[i]
                                if (markdown + i) in inter[x][y]:
                                    print("Error duplicate time key " + str(markdown + i))
                                    print("Newkey from" + str(car[0]))
                                    print("    tested " + str(testPath))
                                    print("    adding from " + str(markdown) + " to " + str(markdown + len(futurePath) - 1))
                                    print("Oldkey from" + str(inter[x][y][markdown + i][0]))
                                inter[x][y].update({markdown + i: car})

                            '''for i in range(0, 4):
                                for j in range(0, 4):
                                    print("In case " + str(i) + ", " + str(j))
                                    list = []
                                    for key, item in inter[i][j].items():
                                        list.append(str(key) + ": " + str(item[0]))
                                    print(list)'''

                            inQueue[road][way][carIndex][1] = markdown - 1  # Add when car exit inQueue
                            self.add_widget(car[3])
                            anim = Animation(pos=inQueueAnim[car[1][0]][car[1][1]], duration=0)
                            anim &= Animation(angle=90 * car[1][0], duration=0)
                            doNextMoveF.append(False)
                            anim.start(car[3])
                            anim.bind(on_complete=partial(popNextMoveF))

            '''print("This move:")
            for i in range(0, 4):
                for j in range(0, 4):
                    print("In case " + str(i) + ", " + str(j))
                    list = []
                    for key, item in inter[i][j].items():
                        list.append(str(key)+": "+str(item[0]))
                    print(list)'''

    # Clock.schedule_interval(partial(intersecProg, inQueue, outQueue, inter), 1 / 80)


class CityApp(App):

    global citySize
    global roadLength
    global ttLength
    global roadWidth

    citySize = 5
    roadLength = 10
    roadWidth = 320
    ttLength = (int(citySize / 2) + citySize % 2) * roadWidth + int(citySize / 2) * roadLength * 40 * 2

    def build(self):

        city = BoxLayout(orientation='vertical', size=(ttLength, ttLength), size_hint=(None, None))
        inQueue = []
        currentMat = []
        city.add_widget(VertRoad(roadWidth=roadWidth, roadLength=roadLength*40*2))
        '''for x in range(0, citySize):
            row = BoxLayout(orientation='horizontal', size=(ttLength, roadWidth * abs(x%2-1) + roadLength * 40 * 2 * (x%2)), size_hint=(None, None))
            inQueue.append([])
            currentMat.append([])
            for y in range(0, citySize):
                if x%2 == 0 and y%2 == 0:       # intersec
                    inQueue[x].append([[[], []], [[], []], [[], []], [[], []]])
                    currentMat[x].append([
                        [{}, {}, {}, {}],
                        [{}, {}, {}, {}],
                        [{}, {}, {}, {}],
                        [{}, {}, {}, {}]
                    ])
                    row.add_widget(Intersec(roadWidth=roadWidth, inQueue=inQueue,x=x, y=y, inter=currentMat[x][y]))
                elif y%2 == 1 and x%2 == 0:    # horizontal road
                    inQueue[x].append([[[], []], [[], []]])
                    row.add_widget(HorizRoad(roadWidth=roadWidth, roadLength=roadLength*40*2, queue=inQueue[x][y]))
                elif x%2 == 1 and y%2 == 0:           # vertical road
                    inQueue[x].append([[[], []], [[], []]])
                    row.add_widget(VertRoad(roadWidth=roadWidth, roadLength=roadLength*40*2, queue=inQueue[x][y]))
                else:
                    inQueue[x].append("Empty")
                    currentMat[x].append("Empty")
                    row.add_widget(Grass(size=(roadLength*40*2, roadLength*40*2)))
            city.add_widget(row)'''
        scatter = Scatter()
        scatter.add_widget(city)
        return scatter


if __name__ == '__main__':
    CityApp().run()