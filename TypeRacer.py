from bs4 import BeautifulSoup
import requests
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, date
import matplotlib.colors as mcolors


class TypeRacer:
    def __init__(self, username: str, universe: str = ""):
        amount = 1550  # n=2147483647
        link = "https://data.typeracer.com/pit/race_history"
        next_link = f"{link}?user={username}&n={amount}&startDate=&universe={universe}"

        self.wpm = []
        self.accuracy = []
        self.attempt = []
        self.score = []
        self.place = []
        self.date = []

        i = 0

        while True:
            html = requests.get(next_link).text
            data = BeautifulSoup(html, 'lxml')
            self.retrieveData(data.find_all('div', class_="Scores__Table__Row"))
            print(i)  # TODO: display progress by scraping total race count
            i += 1

            try:
                next_link = data.find('div', class_="themeContent pit").find_all("span")[-1]
                if next_link.text == """\n\n          load older results »\n        \n""":
                        next_link = link + next_link.find("a").get("href")
                else:
                    break
            except AttributeError as e:
                break
            except IndexError as e:
                break

        print("Done loading data.")

    def retrieveData(self, data):
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

        for attempt, accuracy, wpm in list(reversed(list(zip(self.attempt, self.accuracy, self.wpm)))):
            interpolated_value = self.lerp(1, 0, (wpm - slowest) / float(fastest_rel))
            plt.scatter(attempt, accuracy, color=(interpolated_value, 1 - interpolated_value, 0))

        plt.ylabel("Accuracy")
        plt.xlabel("Amount of races")

        plt.xlim(1, max(self.attempt))
        plt.ylim(top=1)
        ax2 = plt.gca().secondary_yaxis('right')
        ax2.set_yticks(plt.yticks()[0])

        norm = mcolors.Normalize(vmin=slowest, vmax=fastest_rel)
        sm = plt.cm.ScalarMappable(cmap='RdYlGn', norm=norm)
        sm.set_array([])

        plt.colorbar(sm, ax=ax, orientation='vertical', label='Speed', pad=0.1)

        plt.title("Typing Accuracy")
        plt.show()

    def plotWPMAccCorrelation(self):
        least = min(self.accuracy)
        most_rel = max(self.accuracy) - least
        fig, ax = plt.subplots()

        for attempt, accuracy, wpm in list(reversed(list(zip(self.attempt, self.accuracy, self.wpm)))):
            interpolated_value = self.lerp(1, 0, (accuracy - least) / float(most_rel))
            plt.scatter(attempt, wpm, color=(interpolated_value, 1 - interpolated_value, 0))

        plt.title("Typing Speed")
        plt.ylabel("WPM")
        plt.xlabel("Amount of races")

        norm = mcolors.Normalize(vmin=least, vmax=most_rel)
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

    def lerp(self, a, b, t):
        return a + (b - a) * t

    def download(self, path: str):
        with open(path, "w") as f:
            for attempt, wpm, accuracy, score, place, date in zip(self.attempt, self.wpm, self.accuracy, self.score, self.place, self.date):
                f.write(f"{attempt};{wpm};{accuracy};{score};{place};{date}\n")
