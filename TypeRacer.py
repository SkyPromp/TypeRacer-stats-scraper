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

    def plotWPM(self, pb_on=False, denoising_line=0):
        plt.plot(self.attempt, self.wpm, label="wpm")

        plt.ylabel("Speed (WPM)")
        plt.xlabel("Amount of races")

        if pb_on:
            pb_wpm = 0
            pb = []

            for attempt, wpm in reversed(list(zip(self.attempt, self.wpm))):
                if wpm > pb_wpm:
                    pb.append([attempt, wpm])
                    pb_wpm = wpm
                    plt.axhline(y=wpm, color="black", linestyle="--", label="PB Line", linewidth=1, xmin=attempt/len(self.attempt))

            plt.plot(list(map(lambda x: x[0], pb)), list(map(lambda x: x[1], pb)), color="black", label="pb's", linewidth=1)

            ax2 = plt.gca().secondary_yaxis('right')
            ax2.set_yticks(list(map(lambda x: x[1], pb)))
            plt.subplots_adjust(right=0.85)
            ax2.set_ylabel("PB Speed (WPM)", rotation=270, labelpad=10, ha='center', va='center_baseline',
                           multialignment='center')

        if denoising_line > 0:
            local_points = []
            points = []

            average = lambda x: sum(map(lambda y: y[1], x))/len(x)

            for attempt, wpm in list(reversed(list(zip(self.attempt, self.wpm))))[1:]:
                local_points.append([attempt, wpm])
                if len(local_points) > denoising_line:
                    local_points.pop(0)

                points.append([attempt, average(local_points)])

            plt.plot(list(map(lambda x: x[0], points)), list(map(lambda x: x[1], points)), color="red", label="smooth", linewidth=1)

        plt.xlim(0, max(self.attempt))

        plt.title("Typing Speed")
        plt.show()

    def plotAccuracy(self, denoising_line=0):
        plt.plot(self.attempt, self.accuracy)

        plt.ylabel("Accuracy")
        plt.xlabel("Amount of races")

        if denoising_line > 0:
            local_points = []
            points = []

            average = lambda x: sum(map(lambda y: y[1], x))/len(x)

            for attempt, accuracy in list(reversed(list(zip(self.attempt, self.accuracy))))[1:]:
                local_points.append([attempt, accuracy])
                if len(local_points) > denoising_line:
                    local_points.pop(0)

                points.append([attempt, average(local_points)])

            plt.plot(list(map(lambda x: x[0], points)), list(map(lambda x: x[1], points)), color="black", label="smooth", linewidth=1)

        plt.xlim(0, max(self.attempt))
        plt.title("Typing Accuracy")
        plt.show()
        
    def download(self, path):
        with open(path, "w") as f:
            for attempt, wpm, accuracy, score, place, date in zip(self.attempt, self.wpm, self.accuracy, self.score, self.place, self.date):
                f.write(f"{attempt};{wpm};{accuracy};{score};{place};{date}\n")
