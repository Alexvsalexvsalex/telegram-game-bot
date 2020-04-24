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
        self.participiants = []

    def register(self, player):
        self.participiants.append(player)

    def getAdmin(self):
        return self.participiants[0]

    def start(self):
        leaf = 1
        partCnt = len(self.participiants)
        while leaf < partCnt:
            self.heap.append(None)
            self.heap.append(None)
            leaf = leaf + 1
        random.shuffle(self.participiants)
        for i in range(1, partCnt + 1):
            self.heap[partCnt - i] = self.participiants[i - 1]

    def getCurrentMath(self):
        return Match(self.heap.pop(), self.heap.pop())

    def receiveMathWinner(self, match):
        self.heap[(len(self.heap) - 1) / 2 + 1] = match.getWinner()

    def isFinished(self):
        if len(self.heap == 1):
            return True
        return False

    def getWinner(self):
        return self.heap[0]
