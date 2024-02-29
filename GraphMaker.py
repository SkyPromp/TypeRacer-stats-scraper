import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors


class GraphMaker:
    def __init__(self, data):
        self.wpm, self.accuracy, self.attempt, self.score, self.place, self.date = data

    def plotWPM(self, pb_smooth_on: bool = True, pb_snap_on: bool = False, denoising_line: int = 10, average_on: bool = True):
        plt.figure()
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
        #plt.show()

        plt.savefig("./img/WPM.png")

    def histWPM(self):
        plt.figure()
        unique_values, counts = np.unique(self.wpm, return_counts=True)
        sorted_indices = np.argsort(unique_values)
        unique_values = unique_values[sorted_indices]
        counts = counts[sorted_indices]

        plt.bar(unique_values, counts)

        plt.title("Typing test speed distribution")
        plt.xlabel("Speed (WPM)")
        plt.ylabel("Amount of races")
        plt.yticks(np.arange(0, max(counts) + 1, int(max(counts / (6 if max(counts) > 6 else 1)))))

        #plt.show()

        plt.savefig("./img/histWPM.png")

    def plotAccuracy(self, denoising_line: int = 10, average_on: bool = True):
        plt.figure()
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
        #plt.show()

        plt.savefig("./img/Accuracy.png")

    def plotAccWPMCorrelation(self):
        plt.figure()
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
        #plt.show()

        plt.savefig("./img/AccWPM.png")

    def plotWPMAccCorrelation(self):
        plt.figure()
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
        plt.ylabel("Speed (WPM)")
        plt.xlabel("Amount of races")

        norm = mcolors.Normalize(vmin=least, vmax=max(self.accuracy))
        sm = plt.cm.ScalarMappable(cmap='RdYlGn', norm=norm)
        sm.set_array([])
        plt.colorbar(sm, ax=ax, orientation='vertical', label='Accuracy')

        #plt.show()

        plt.savefig("./img/WPMAcc.png")

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

            points.append([attempt, GraphMaker._average(local_points)])

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
        plt.figure()
        rounded = list(map(lambda x: round(x, 2), self.accuracy))

        _, counts = np.unique(rounded, return_counts=True)

        bins = np.arange(min(rounded), 1.01, 0.01)
        plt.hist(self.accuracy, bins=np.append(bins, 1.01))

        plt.title("Typing test accuracy distribution")
        plt.xlabel("Accuracy")
        plt.ylabel("Amount of races")
        plt.xticks(bins + 0.005, [f"{value:.2f}" for value in bins])
        plt.yticks(np.arange(0, max(counts) + 1, int(max(counts / (6 if max(counts) > 6 else 1)))))

        #plt.show()

        plt.savefig("./img/histAcc.png")

    def wpmAcc(self):
        plt.figure()
        least = min(self.attempt)
        most = max(self.attempt)

        if len(self.attempt) > 6000:
            s = 1
        else:
            s = 20

        fig, ax = plt.subplots()

        inter = list(map(lambda attempt_: (attempt_ - least) / float(most), self.attempt))
        plt.scatter(self.accuracy, self.wpm, c=inter, cmap="RdYlGn", s=s)

        plt.title("Speed/Accuracy")
        plt.ylabel("Speed (WPM)")
        plt.xlabel("Accuracy")

        norm = mcolors.Normalize(vmin=least, vmax=most)
        sm = plt.cm.ScalarMappable(cmap='RdYlGn', norm=norm)
        sm.set_array([])
        plt.colorbar(sm, ax=ax, orientation='vertical', label='Attempts')

        # plt.show()

        plt.savefig("./img/wpmAccRace.png")

    def plotDailyRaces(self):
        plt.figure()
        entries = {}

        for attempt, current_date in reversed(list(zip(self.attempt, self.date))):
            if current_date in entries:
                entries[current_date] += 1
            else:
                entries[current_date] = 1

        plt.title("Total races per day")
        plt.xticks(rotation=-90)
        plt.subplots_adjust(bottom=0.2)
        plt.bar(list(map(lambda x: x[0], entries.items())), list(map(lambda x: x[1], entries.items())))
        #plt.show()

        plt.savefig("./img/DailyRaces.png")
