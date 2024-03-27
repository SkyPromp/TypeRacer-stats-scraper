from datetime import datetime
from numpy import array
from csv import reader


class LoadFileStats:
    def __init__(self, filename: str):
        self.wpm = []
        self.accuracy = []
        self.attempt = []
        self.score = []
        self.place = []
        self.date = []

        with open(filename) as file:
            for line in file:
                attempt, wpm, accuracy, score, place, date = line.split(";")

                self.wpm.append(int(wpm) * 100)
                self.accuracy.append(int((accuracy[0] + accuracy[2:]).ljust(4, "0")))
                self.attempt.append(int(attempt))
                self.score.append(int(score))
                self.place.append(place)
                self.date.append(datetime.strptime(date, "%Y-%m-%d %H:%M:%S\n"))

    def getData(self):
        data = self.wpm, self.accuracy, self.attempt, self.score, self.place, self.date
        return list(map(lambda d: array(list(reversed(d))), data))
