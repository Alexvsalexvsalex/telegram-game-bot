import random


class Match(object):

    def __init__(self, firstPlayer, secondPlayer):
        self.res = {firstPlayer: None, secondPlayer: None}
        self.winner = None

    def getPlayers(self):
        return list(self.res.keys())

    def getWinner(self):
        return self.winner

    def canBeChanged(self, player):
        return player in self.res and self.res[player] is None

    def setResult(self, player, res):
        self.res[player] = res
        val = None
        first = None
        for p in self.res:
            cur = self.res[p]
            if cur is None:
                return None
            if val is None:
                val = cur
                first = p
                continue
            if val == cur:
                return "!"
            if val < cur:
                self.winner = p
            else:
                self.winner = first
            return self.winner


class Tournament(object):

    def __init__(self):
        self.heap = [None]
        self.participants = set()
        self.isStartedFlag = False
        self.currentMatch = None

    def register(self, player):
        self.participants.add(player)

    def getParticipants(self):
        return list(self.participants)

    def canBeStarted(self):
        if len(self.participants) > 1:
            return True
        return False

    def isStarted(self):
        return self.isStartedFlag

    def start(self):
        self.isStartedFlag = True
        leaf = 1
        partCnt = len(self.participants)
        partLst = list(self.participants)
        while leaf < partCnt:
            self.heap.append(None)
            self.heap.append(None)
            leaf = leaf + 1
        random.shuffle(partLst)
        for i in range(1, partCnt + 1):
            self.heap[len(self.heap) - i] = partLst[i - 1]
        self.generateNextMatch()

    def generateNextMatch(self):
        self.currentMatch = Match(self.heap.pop(), self.heap.pop())

    def getCurrentMatch(self):
        if self.currentMatch.getWinner() is not None:
            self.heap[(len(self.heap) - 2) // 2 + 1] = self.currentMatch.getWinner()
            self.generateNextMatch()
        return self.currentMatch

    def isFinished(self):
        if len(self.heap) == 1 and self.heap[0] is not None:
            return True
        return False

    def getWinner(self):
        return self.heap[0]
