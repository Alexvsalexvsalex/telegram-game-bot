import random


class Statistic(object):

    def __init__(self):
        self.dict_names = ["tournament_points", "number_matches", "number_wins", "sum_value"]
        self.data = {}
        for d in self.dict_names:
            self.data[d] = {}

    def register_throw(self, name, value):
        self.data["number_matches"][name] += 1
        self.data["sum_value"][name] += value

    def register_win(self, name):
        self.data["number_wins"][name] += 1

    def register_tournament_winner(self, name):
        self.data["tournament_points"][name] += self.data["number_matches"][name]

    def get_full_statistic(self):
        players = self.data["number_matches"].keys()
        res = {}
        for p in players:
            res[p] = {}
            for d in self.dict_names:
                res[p][d] = self.data[d][p]
        return res


class Match(object):

    def __init__(self, first_player, second_player, statistic):
        self.res = {first_player: None, second_player: None}
        self.winner = None
        self.statistic = statistic

    def get_players(self):
        return list(self.res.keys())

    def get_winner(self):
        return self.winner

    def can_be_changed(self, player):
        return player in self.res and self.res[player] is None

    def set_result(self, player, res):
        self.res[player] = res
        self.statistic.register_throw(player, res)
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
                for u in self.res:
                    self.res[u] = None
                return "!"
            if val < cur:
                self.winner = p
                self.statistic.register_win(p)
            else:
                self.winner = first
                self.statistic.register_win(first)
            return self.winner


class Tournament(object):

    def __init__(self):
        self.heap = [None]
        self.participants = set()
        self.isStartedFlag = False
        self.currentMatch = None
        self.statistic = Statistic()

    def register(self, player):
        self.participants.add(player)

    def get_participants(self):
        return list(self.participants)

    def can_be_started(self):
        if len(self.participants) > 1:
            return True
        return False

    def is_started(self):
        return self.isStartedFlag

    def start(self):
        self.isStartedFlag = True
        leaf = 1
        part_cnt = len(self.participants)
        part_lst = list(self.participants)
        while leaf < part_cnt:
            self.heap.append(None)
            self.heap.append(None)
            leaf = leaf + 1
        random.shuffle(part_lst)
        for i in range(1, part_cnt + 1):
            self.heap[len(self.heap) - i] = part_lst[i - 1]
        self.generate_next_match()

    def generate_next_match(self):
        self.currentMatch = Match(self.heap.pop(), self.heap.pop(), self.statistic)

    def set_winner_of_last_match(self):
        self.heap[(len(self.heap) - 2) // 2 + 1] = self.currentMatch.getWinner()

    def get_current_match(self):
        if self.currentMatch.getWinner() is not None:
            self.set_winner_of_last_match()
            if not self.is_finished():
                self.generate_next_match()
        return self.currentMatch

    def is_finished(self):
        if len(self.heap) == 1:
            if self.currentMatch.getWinner() is not None:
                self.set_winner_of_last_match()
                self.statistic.register_tournament_winner(self.heap[0])
                return True
        return False

    def get_winner(self):
        return self.heap[0]

    def get_stats(self):
        return self.statistic.get_full_statistic()
