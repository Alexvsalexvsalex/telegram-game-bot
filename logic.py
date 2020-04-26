import random


class Match(object):

    def __init__(self, firstPlayer, secondPlayer):
        self.first = firstPlayer
        self.second = secondPlayer
        self.winner = None

    def setWinner(self, winner):
        self.winner = winner

    def getFirstPlayer(self):
        return self.first

    def getSecondPlayer(self):
        return self.second

    def getWinner(self):
        return self.winner


class Tournament(object):

    def __init__(self):
        self.heap = [None]
        self.participiants = set()
        self.isStartedFlag = False

    def register(self, player):
        self.participiants.add(player)

    def getParticipiants(self):
        return list(self.participiants)

    def canBeStarted(self):
        if len(self.participiants) > 1:
            return True
        return False

    def isStarted(self):
        return self.isStartedFlag

    def start(self):
        self.isStartedFlag = True
        leaf = 1
        partCnt = len(self.participiants)
        partLst = list(self.participiants)
        while leaf < partCnt:
            self.heap.append(None)
            self.heap.append(None)
            leaf = leaf + 1
        random.shuffle(partLst)
        for i in range(1, partCnt + 1):
            self.heap[len(self.heap) - i] = partLst[i - 1]
        print(self.heap)

    def getCurrentMatch(self):
        return Match(self.heap.pop(), self.heap.pop())

    def receiveMatchWinner(self, match):
        self.heap[(len(self.heap) - 2) // 2 + 1] = match.getWinner()

    def isFinished(self):
        if len(self.heap) == 1:
            return True
        return False

    def getWinner(self):
        return self.heap[0]
