from bs4 import BeautifulSoup
import requests
import matplotlib.pyplot as plt


class TypeRacer:
    def __init__(self, username: str):
        html = requests.get(f"https://data.typeracer.com/pit/race_history?user={username}&n=2147483647&startDate=&universe=").text
        data = BeautifulSoup(html, 'lxml')
        del html
        jobs = data.find_all('div', class_="Scores__Table__Row")
        del data
        self.wpm = []
        self.accuracy = []
        self.attempt = []
        self.score = []
        self.place = []
        self.date = []
        for job in jobs:
            attempt, wpm, accuracy, score, place, date = [i.strip() for i in job.text.strip().split("\n") if i.strip()]
            self.wpm.append(int(wpm.split(" ")[0]))
            self.accuracy.append((round(float(accuracy.replace("%", ""))/100, 3)))
            self.attempt.append(int(attempt))
            self.score.append(int(score))
            self.place.append(place)
            self.date.append(date)

    def getAttempt(self):
        return self.attempt

    def getWPM(self):
        return self.wpm

    def getAccuracy(self):
        return self.accuracy

    def getScore(self):
        return self.score

    def getPlace(self):
        return self.place

    def getDate(self):
        return self.date

    def getAll(self):
        return self.attempt, self.wpm, self.accuracy, self.score, self.place, self.date

    def plotWPM(self):
        plt.plot(self.attempt, self.wpm)
        plt.title("WPM")
        plt.show()

    def plotAccuracy(self):
        plt.plot(self.attempt, self.accuracy)
        plt.title("accuracy")
        plt.show()
