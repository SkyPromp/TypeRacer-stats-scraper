from math import floor
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors
from typing import List
from collections import Counter


class GraphMaker:
    def __init__(self, data: List[np.ndarray]):
        self.wpm, self.accuracy, self.attempt, self.score, self.place, self.date = data

    def plotWPM(self, pb_smooth_on: bool = True, pb_snap_on: bool = False, average_grouping: int = 10, average_on: bool = True):
        plt.figure()

        if average_grouping > len(self.attempt):
            average_grouping = len(self.attempt)

        plt.plot(self.attempt, self.wpm, label="Speed")

        plt.ylabel("Speed (WPM)")
        plt.xlabel("Amount of races")

        if pb_smooth_on:
            self._pbGradual(self.wpm, label="PB Speeds (WPM)")

        if pb_snap_on:
            self._pbSnap(self.wpm, label="PB Speeds (WPM)")

        if average_on:
            self._plotAverage(self.wpm)

        if average_grouping > 0:
            self._plotSmooth(self.wpm, average_grouping)

        plt.xlim(1, max(self.attempt))
        plt.legend()
        plt.title("Typing Speed")

        plt.savefig("./img/WPM.png")

    def histWPM(self):
        plt.figure()

        bins = np.arange(min(self.wpm), max(self.wpm), 1)
        plt.hist(self.wpm, bins=bins)

        plt.title("Typing test speed distribution")
        plt.xlabel("Speed (WPM)")
        plt.ylabel("Amount of races")

        plt.savefig("./img/histWPM.png")

    def plotAccuracy(self, average_grouping: int = 10, average_on: bool = True):
        plt.figure()

        if average_grouping > len(self.attempt):
            average_grouping = len(self.attempt)

        plt.plot(self.attempt, self.accuracy, label="Accuracy")

        plt.ylabel("Accuracy")
        plt.xlabel("Amount of races")

        if average_on:
            self._plotAverage(self.accuracy)

        if average_grouping > 0:
            self._plotSmooth(self.accuracy, average_grouping=average_grouping)

        plt.xlim(1, max(self.attempt))
        plt.ylim(top=1)
        plt.legend()
        ax2 = plt.gca().secondary_yaxis('right')

        ax2.set_yticks(plt.yticks()[0])
        plt.title("Typing Accuracy")

        plt.savefig("./img/Accuracy.png")

    def plotAccWPMCorrelation(self):
        plt.figure()
        slowest = min(self.wpm)
        fastest_rel = max(self.wpm)
        fig, ax = plt.subplots()

        if len(self.attempt) > 6000:
            s = 1
        else:
            s = 20

        if len(self.attempt) > 5e5:
            att, acc, indices = self._removeOverlapping(self.attempt, self.accuracy, 1/100, 1000/1.01)  # TODO: make thresholds dynamic

            plt.scatter(att, acc, c=np.interp(self.wpm[indices], (slowest, fastest_rel), (0, 1)), cmap="RdYlGn", s=s)
        else:
            plt.scatter(self.attempt, self.accuracy, c=np.interp(self.wpm, (slowest, fastest_rel), (0, 1)), cmap="RdYlGn", s=s)

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

        plt.savefig("./img/AccWPM.png")

    def plotWPMAccCorrelation(self):
        plt.figure()
        least = np.amin(self.accuracy)
        most = np.amax(self.accuracy)

        if len(self.attempt) > 6000:
            s = 1
        else:
            s = 20

        fig, ax = plt.subplots()

        if len(self.attempt) > 5e5:
            att, wpm, indices = self._removeOverlapping(self.attempt, self.wpm, 1 / 150, 1/3)  # TODO: make thresholds dynamic

            plt.scatter(att, wpm, c=np.interp(self.accuracy[indices], (least, most), (0, 1)), cmap="RdYlGn", s=s)
        else:
            plt.scatter(self.attempt, self.wpm, c=np.interp(self.accuracy, (least, most), (0, 1)), cmap="RdYlGn", s=s)

        plt.title("Typing Speed")
        plt.ylabel("Speed (WPM)")
        plt.xlabel("Amount of races")

        norm = mcolors.Normalize(vmin=least, vmax=most)
        sm = plt.cm.ScalarMappable(cmap='RdYlGn', norm=norm)
        sm.set_array([])
        plt.colorbar(sm, ax=ax, orientation='vertical', label='Accuracy')

        plt.savefig("./img/WPMAcc.png")

    @staticmethod
    def _removeOverlapping(data_x, data_y, x_threshold, y_threshold):
        data_x = np.round(data_x * x_threshold)/x_threshold
        data_y = np.round(data_y * y_threshold)/y_threshold

        zipped = np.column_stack((data_y, data_x))
        uniq_zip, indices = np.unique(zipped, axis=0, return_index=True)
        data_y, data_x = np.split(uniq_zip, 2, axis=1)
        data_y = np.squeeze(data_y)
        data_x = np.squeeze(data_x)

        return data_x, data_y, indices

    @staticmethod
    def _average(data):
        return sum(map(lambda y: y[1], data))/len(data)

    def _plotSmooth(self, data_source, average_grouping: int = 10, label=None, color="red"):
        plt.plot(self.attempt, self._runningAverageOfN(data_source, average_grouping), color=color, label=label if label is not None else f"Average of {average_grouping}", linewidth=1)

    def _runningAverageOfN(self, arr, n):
        return np.concatenate((self._runningAverage(arr[:n - 1]), np.convolve(arr, np.ones(n) / n, mode='valid')))

    @staticmethod
    def _runningAverage(data):
        return np.cumsum(data) / np.arange(1, len(data) + 1)

    def _plotAverage(self, data):
        plt.plot(self.attempt, self._runningAverage(data), color="lime", label="Average", linewidth=1)

    def _pbGradual(self, data_source, label: str = "PB"):
        zipped = np.column_stack((np.maximum.accumulate(data_source), self.attempt))
        unique, index = np.unique(zipped[:, 0], axis=0, return_index=True)

        pb_attempts = self.attempt[index]
        plt.plot(pb_attempts, unique, color="black", label="PB's", linewidth=1)

        total_attempts = len(self.attempt)

        for attempt, pb in zip(pb_attempts, unique):
            plt.axhline(y=pb, color="black", linestyle="--", linewidth=1, xmin=attempt / total_attempts)

        ax2 = plt.gca().secondary_yaxis('right')
        ax2.set_yticks(unique)
        plt.subplots_adjust(right=0.85)
        ax2.set_ylabel(label, rotation=270, labelpad=10, ha='center', va='center_baseline',
                       multialignment='center')

    def _pbSnap(self, data_source, label: str = "PB"):
        zipped = np.column_stack((np.maximum.accumulate(data_source), self.attempt))
        unique, index = np.unique(zipped[:, 0], axis=0, return_index=True)

        double = np.repeat(unique, 2)
        index_repeat = np.concatenate(([index[0]], np.repeat(index[1:], 2), [index[-1]]))
        pb_attempts = self.attempt[index_repeat]

        plt.plot(pb_attempts, double, color="black", label="PB's", linewidth=1)

        unique_indices = self.attempt[index][1:]

        for attempt, pb in zip(np.append(unique_indices, unique_indices[-1]), unique):
            plt.axhline(y=pb, color="black", linestyle="--", linewidth=1, xmin=attempt / len(self.attempt))

        ax2 = plt.gca().secondary_yaxis('right')
        ax2.set_yticks(unique)
        plt.subplots_adjust(right=0.85)
        ax2.set_ylabel(label, rotation=270, labelpad=10, ha='center', va='center_baseline',
                       multialignment='center')

    def histAccuracy(self):
        plt.figure()

        bins = np.arange(floor(min(self.accuracy) * 100) / 100, 1.01, 0.01)
        plt.hist(self.accuracy, bins=np.floor(bins * 100) / 100)

        plt.title("Typing test accuracy distribution")
        plt.xlabel("Accuracy")
        plt.ylabel("Amount of races")
        xticks = bins[::len(bins) // 10 if len(bins) > 10 else 1]
        plt.xticks(xticks + 0.005, [f"{value:.2f}" for value in xticks])

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

        acc, wpm, indices = self._removeOverlapping(self.accuracy[::-1], self.wpm[::-1], 1000, 1)
        indices = len(self.attempt) - indices - 1
        plt.scatter(acc, wpm, c=np.interp(self.attempt[indices], (least, most), (0, 1)), cmap="RdYlGn", s=s)

        plt.title("Speed/Accuracy")
        plt.ylabel("Speed (WPM)")
        plt.xlabel("Accuracy")

        norm = mcolors.Normalize(vmin=least, vmax=most)
        sm = plt.cm.ScalarMappable(cmap='RdYlGn', norm=norm)
        sm.set_array([])
        plt.colorbar(sm, ax=ax, orientation='vertical', label='Attempts')

        plt.savefig("./img/wpmAccRace.png")

    def plotDailyRaces(self):
        plt.figure()

        plt.bar(*zip(*Counter(self.date).items()))  # Faster than numpy only

        plt.title("Total races per day")
        plt.ylabel("Races")
        plt.xlabel("Time (in days)")

        plt.xticks(rotation=-90)
        plt.subplots_adjust(bottom=0.2)

        plt.savefig("./img/DailyRaces.png")
