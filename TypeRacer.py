import requests
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, date
import matplotlib.colors as mcolors
from time import time

from bs4 import BeautifulSoup


class TypeRacer:
    def __init__(self, username: str, universe: str = "play"):
        end_time = time()
        start_time = 0

        self.wpm = []
        self.accuracy = []
        self.attempt = []
        self.score = []
        self.place = []
        self.date = []
        self.text = []
        self.racers_amount = []
        self.skill_level = []

        try:
            while True:
                link = f"https://data.typeracer.com/games?playerId=tr:{username}&universe={universe}&startDate={start_time}&endDate={end_time}"
                data = requests.get(link).json()
                self.writeData(data)

                end_time = min(self.date) - 1

                print(self.attempt[-1])

                if min(self.attempt) == 1:
                    break

        except requests.exceptions.JSONDecodeError as e:
            print("invalid data")
            print(e)


        print("Done loading data.")

    async def getData(self, width, start, n, username, universe):
        start_time = start + width * n
        end_time = start + width * (n + 1) - 1

        timestamp = []

        wpm = []
        accuracy = []
        attempt = []
        score = []
        place = []
        timestamps = []
        text = []
        racers_amount = []
        skill_level = []

        last_time = 0

        try:
            while True:
                link = f"https://data.typeracer.com/games?playerId=tr:{username}&universe={universe}&startDate={start_time}&endDate={end_time}"
                data = requests.get(link).json()

                temp = self.writeDataSplit(data)

                if min(timestamp) != last_time:
                    wpm.append(temp[0])
                    accuracy.append(temp[1])
                    attempt.append(temp[2])
                    score.append(temp[3])
                    place.append(temp[4])
                    timestamps.append(temp[5])
                    text.append(temp[6])
                    racers_amount.append(temp[7])
                    skill_level.append(temp[8])

                    end_time = min(timestamp) - 1
                    last_time = min(timestamp)
                else:
                    break

        except requests.exceptions.JSONDecodeError as e:
            print("invalid data")
            print(e)

        print(wpm, accuracy, attempt, score, place, timestamp, text, racers_amount, skill_level, sep="\n")
        return wpm, accuracy, attempt, score, place, timestamp, text, racers_amount, skill_level

    def writeDataSplit(self, data):
        wpm = []
        accuracy = []
        attempt = []
        score = []
        place = []
        timestamp = []
        text = []
        racers_amount = []
        skill_level = []

        for unit in data:
            wpm.append(unit["wpm"])
            accuracy.append(unit["ac"])
            attempt.append(unit["gn"])
            score.append(unit["pts"])
            place.append(unit["r"])
            timestamp.append(unit["t"])
            text.append(unit["tid"])
            racers_amount.append(unit["np"])
            skill_level.append(unit["sl"])

        return wpm, accuracy, attempt, score, place, timestamp, text, racers_amount, skill_level

    def writeData(self, data):
        for unit in data:
            self.wpm.append(unit["wpm"])
            self.accuracy.append(unit["ac"])
            self.attempt.append(unit["gn"])
            self.score.append(unit["pts"])
            self.place.append(unit["r"])
            self.date.append(unit["t"])
            self.text.append(unit["tid"])
            self.racers_amount.append(unit["np"])
            self.skill_level.append(unit["sl"])

    def getStartDate(name):
        link = f"https://data.typeracer.com/pit/profile?user={name}"
        html = requests.get(link).text
        data = BeautifulSoup(html, 'lxml')
        data = data.find('div', class_="About").find_all("div")
        date = "Jan. 1, 1970"

        for div in data:
            title, info = div.find_all("span")
            if title.text == "Racing Since:":
                date = info.text

        months = ['Jan.', 'Feb.', 'March', 'April', 'May', 'June', 'July', 'Aug.', 'Sept.', 'Oct.', 'Nov.', 'Dec.']

        if date != "today":
            month, day, year = date.split(" ")
            day = int(day[:-1])
            month = months.index(month) + 1
            year = int(year)
            date = datetime(year, month, day)

        else:
            date = date.today()

        return date

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

    def plotWPM(self, pb_smooth_on: bool = True, pb_snap_on: bool = False, denoising_line: int = 10, average_on: bool = True):
        plt.plot(self.attempt, self.wpm, label="Speed")

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
        plt.yticks(np.arange(0, max(counts) + 1, int(max(counts / (6 if max(counts) > 6 else 1)))))

        plt.show()

    def plotAccuracy(self, denoising_line: int = 10, average_on: bool = True):
        plt.plot(self.attempt, self.accuracy, label="Accuracy")

        plt.ylabel("Accuracy")
        plt.xlabel("Amount of races")

        if denoising_line > 0:
            self._plotSmooth(self.accuracy, denoising_line=denoising_line)
        if average_on:
            self._plotAverage(self.accuracy)

        plt.xlim(1, max(self.attempt))
        plt.ylim(top=1)
        plt.legend()
        ax2 = plt.gca().secondary_yaxis('right')

        ax2.set_yticks(plt.yticks()[0])
        plt.title("Typing Accuracy")
        plt.show()

    def plotAccWPMCorrelation(self):
        slowest = min(self.wpm)
        fastest_rel = max(self.wpm) - slowest
        fig, ax = plt.subplots()

        if len(self.attempt) > 6000:
            s = 1
        else:
            s = 20

        inter = list(map(lambda speed: (speed - slowest) / float(fastest_rel), self.wpm))
        plt.scatter(self.attempt, self.accuracy, c=inter, cmap="RdYlGn", s=s)

        plt.ylabel("Accuracy")
        plt.xlabel("Amount of races")

        plt.xlim(1, max(self.attempt))
        plt.ylim(top=1)
        ax2 = plt.gca().secondary_yaxis('right')
        ax2.set_yticks(plt.yticks()[0])

        norm = mcolors.Normalize(vmin=slowest, vmax=max(self.wpm))
        sm = plt.cm.ScalarMappable(cmap='RdYlGn', norm=norm)
        sm.set_array([])

        plt.colorbar(sm, ax=ax, orientation='vertical', label='Speed', pad=0.1)

        plt.title("Typing Accuracy")
        plt.show()

    def plotWPMAccCorrelation(self):
        least = min(self.accuracy)
        most_rel = max(self.accuracy) - least
        if len(self.attempt) > 6000:
            s = 1
        else:
            s = 20

        fig, ax = plt.subplots()

        inter = list(map(lambda acc: (acc - least) / float(most_rel), self.accuracy))
        plt.scatter(self.attempt, self.wpm, c=inter, cmap="RdYlGn", s=s)

        plt.title("Typing Speed")
        plt.ylabel("WPM")
        plt.xlabel("Amount of races")

        norm = mcolors.Normalize(vmin=least, vmax=max(self.accuracy))
        sm = plt.cm.ScalarMappable(cmap='RdYlGn', norm=norm)
        sm.set_array([])
        plt.colorbar(sm, ax=ax, orientation='vertical', label='Accuracy')

        plt.show()

    @staticmethod
    def _average(data):
        return sum(map(lambda y: y[1], data))/len(data)

    def _plotSmooth(self, data_source, denoising_line: int = 10, label="Smooth", color="red"):
        local_points = []
        points = []

        for attempt, data in list(reversed(list(zip(self.attempt, data_source))))[1:]:
            local_points.append([attempt, data])
            if len(local_points) > denoising_line:
                local_points.pop(0)

            points.append([attempt, TypeRacer._average(local_points)])

        plt.plot(list(map(lambda x: x[0], points)), list(map(lambda x: x[1], points)), color=color, label=label, linewidth=1)

    def _plotAverage(self, data):
        self._plotSmooth(data, len(data), label="Average", color="green")

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
        plt.yticks(np.arange(0, max(counts) + 1, int(max(counts / (6 if max(counts) > 6 else 1)))))

        plt.show()

    def plotDailyRaces(self):
        months = ['Jan.', 'Feb.', 'March', 'April', 'May', 'June', 'July', 'Aug.', 'Sept.', 'Oct.', 'Nov.', 'Dec.']
        entries = {}

        for attempt, current_date in reversed(list(zip(self.attempt, self.date))):
            if current_date == "today":
                current_date = date.today()
            else:
                month, day, year = current_date.split(" ")
                day = int(day[:-1])
                month = months.index(month) + 1
                year = int(year)

                current_date = datetime(year, month, day)

            if current_date in entries:
                entries[current_date] += 1
            else:
                entries[current_date] = 1

        plt.title("Total races per day")
        plt.xticks(rotation=-90)
        plt.subplots_adjust(bottom=0.2)
        plt.bar(list(map(lambda x: x[0], entries.items())), list(map(lambda x: x[1], entries.items())))
        plt.show()

    def download(self, path: str):
        with open(path, "w") as f:
            for attempt, wpm, accuracy, score, place, date in zip(self.attempt, self.wpm, self.accuracy, self.score, self.place, self.date):
                f.write(f"{attempt};{wpm};{accuracy};{score};{place};{date}\n")
