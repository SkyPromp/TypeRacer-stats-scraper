from datetime import datetime
from numpy import array


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

                if int(attempt) > 50000100:
                    continue

                self.wpm.append(int(wpm))
                self.accuracy.append(float(accuracy))
                self.attempt.append(int(attempt))
                self.score.append(int(score))
                self.place.append(place)
                self.date.append(datetime.strptime(date, "%Y-%m-%d %H:%M:%S\n"))

    def getData(self):
        data = self.wpm, self.accuracy, self.attempt, self.score, self.place, self.date
        return list(map(lambda d: array(list(reversed(d))), data))
