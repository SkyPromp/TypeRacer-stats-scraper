from bs4 import BeautifulSoup
import requests
import matplotlib.pyplot as plt
import numpy as np


class TypeRacer:
    def __init__(self, username: str):
        html = requests.get(f"https://data.typeracer.com/pit/race_history?user={username}&n=2147483647&startDate=&universe=").text
        data = (BeautifulSoup(html, 'lxml')
                .find_all('div', class_="Scores__Table__Row"))

        self.wpm = []
        self.accuracy = []
        self.attempt = []
        self.score = []
        self.place = []
        self.date = []

        for item in data:
            attempt, wpm, accuracy, score, place, date = [i.strip() for i in item.text.strip().split("\n") if i.strip()]
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

    def plotWPM(self, pb_smooth_on: bool = False, pb_snap_on: bool = False, denoising_line: int = 0, average_on: bool = False):
        plt.plot(self.attempt, self.wpm, label="wpm")

        plt.ylabel("Speed (WPM)")
        plt.xlabel("Amount of races")

        if pb_smooth_on:
            self._pbGradual(self.wpm, label="PB Speeds (WPM)")

        if pb_snap_on:
            self._pbSnap(self.wpm, label="PB Speeds (WPM)")

        if denoising_line > 0:
            self._plotSmooth(self.wpm, denoising_line)
        if average_on:
            self._plotAverage(self.wpm)
        plt.xlim(1, max(self.attempt))

        plt.legend()

        plt.title("Typing Speed")
        plt.show()

    def histWPM(self):
        unique_values, counts = np.unique(self.wpm, return_counts=True)
        sorted_indices = np.argsort(unique_values)
        unique_values = unique_values[sorted_indices]
        counts = counts[sorted_indices]

        plt.bar(unique_values, counts)

        plt.title("Typing test speed distribution")
        plt.xlabel("Speed (WPM)")
        plt.ylabel("Amount of races")
        plt.yticks(np.arange(0, max(counts) + 1, int(max(counts / 6))))

        plt.show()

    def plotAccuracy(self, denoising_line: int = 0, average_on: bool = False):
        plt.plot(self.attempt, self.accuracy, label="accuracy")

        plt.ylabel("Accuracy")
        plt.xlabel("Amount of races")

        if denoising_line > 0:
            self._plotSmooth(denoising_line)
        if average_on:
            self._plotAverage(self.accuracy)

        plt.xlim(1, max(self.attempt))
        plt.legend()
        plt.title("Typing Accuracy")
        plt.show()

    @staticmethod
    def _average(data):
        return sum(map(lambda y: y[1], data))/len(data)

    def _plotSmooth(self, data_source, denoising_line: int = 10):
        local_points = []
        points = []

        for attempt, data in list(reversed(list(zip(self.attempt, data_source))))[1:]:
            local_points.append([attempt, data])
            if len(local_points) > denoising_line:
                local_points.pop(0)

            points.append([attempt, TypeRacer._average(local_points)])

        plt.plot(list(map(lambda x: x[0], points)), list(map(lambda x: x[1], points)), color="red", label="smooth", linewidth=1)

    def _plotAverage(self, data):
        self._plotSmooth(data, len(data))

    def _pbGradual(self, data_source, label: str = "PB"):
        pb_score = 0
        pb = []

        for attempt, data in reversed(list(zip(self.attempt, data_source))):
            if data > pb_score:
                pb.append([attempt, data])
                pb_score = data
                plt.axhline(y=data, color="black", linestyle="--", linewidth=1, xmin=attempt / len(self.attempt))

        plt.plot(list(map(lambda x: x[0], pb)), list(map(lambda x: x[1], pb)), color="black", label="PB's", linewidth=1)

        ax2 = plt.gca().secondary_yaxis('right')
        ax2.set_yticks(list(map(lambda x: x[1], pb)))
        plt.subplots_adjust(right=0.85)
        ax2.set_ylabel(label, rotation=270, labelpad=10, ha='center', va='center_baseline',
                       multialignment='center')

    def _pbSnap(self, data_source, label: str = "PB"):
        pb_score = data_source[-1]
        pb = [[self.attempt[-1], pb_score]]

        for attempt, data in list(reversed(list(zip(self.attempt, data_source))))[1:]:
            if data > pb_score:
                plt.axhline(y=pb[-1][1], color="black", linestyle="--", linewidth=1, xmin=attempt / len(self.attempt))

                pb.append([attempt, pb_score])
                pb.append([attempt, data])
                pb_score = data

        pb.append([max(self.attempt), pb_score])

        plt.plot(list(map(lambda x: x[0], pb)), list(map(lambda x: x[1], pb)), color="black", label="PB's", linewidth=1)

        ax2 = plt.gca().secondary_yaxis('right')
        ax2.set_yticks(list(map(lambda x: x[1], pb)))
        plt.subplots_adjust(right=0.85)
        ax2.set_ylabel(label, rotation=270, labelpad=10, ha='center', va='center_baseline',
                       multialignment='center')

    def histAccuracy(self):
        rounded = list(map(lambda x: round(x, 2), self.accuracy))

        _, counts = np.unique(rounded, return_counts=True)

        bins = np.arange(min(rounded), 1.01, 0.01)
        plt.hist(self.accuracy, bins=np.append(bins, 1.01))

        plt.title("Typing test accuracy distribution")
        plt.xlabel("Accuracy")
        plt.ylabel("Amount of races")
        plt.xticks(bins + 0.005, [f"{value:.2f}" for value in bins])
        plt.yticks(np.arange(0, max(counts) + 1, int(max(counts / 6))))

        plt.show()
        
    def download(self, path: str):
        with open(path, "w") as f:
            for attempt, wpm, accuracy, score, place, date in zip(self.attempt, self.wpm, self.accuracy, self.score, self.place, self.date):
                f.write(f"{attempt};{wpm};{accuracy};{score};{place};{date}\n")
