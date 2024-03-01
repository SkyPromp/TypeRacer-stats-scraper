import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors
from typing import List


class GraphMaker:
    def __init__(self, data: List[np.ndarray]):
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
        data_y = np.array(list(map(lambda x: round(x * y_threshold) / y_threshold, data_y)))
        data_x = np.array(list(map(lambda x: round(x * x_threshold) / x_threshold, data_x)))

        zipped = np.column_stack((data_y, data_x))
        uniq_zip, indices = np.unique(zipped, axis=0, return_index=True)
        data_y, data_x = np.split(uniq_zip, 2, axis=1)
        data_y = np.squeeze(data_y)
        data_x = np.squeeze(data_x)

        return data_x, data_y, indices

    @staticmethod
    def _average(data):
        return sum(map(lambda y: y[1], data))/len(data)

    def _plotSmooth(self, data_source, denoising_line: int = 10, label="Smooth", color="red"):
        plt.plot(self.attempt, self._runningAverage(data_source, denoising_line), color=color, label=label, linewidth=1)

    def _runningAverage(self, arr, n):
        data = np.empty(n - 1, dtype="float64")
        for i in range(1, n):
            np.put(data, i - 1, np.convolve(arr[:i + 1], np.ones(i) / i, mode='valid'))

        return np.concatenate((data, np.convolve(arr, np.ones(n) / n, mode='valid')))

    def _plotAverage(self, data):
        self._plotSmooth(data, len(data), label="Average", color="green")

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

    def _pbSnap(self, data_source, label: str = "PB"):  # TODO: fix (not approximating, no unique...) also add the axhline's back
        pb = np.maximum.accumulate(data_source)
        plt.plot(self.attempt, pb, color="black", label="PB's", linewidth=1)

        ax2 = plt.gca().secondary_yaxis('right')
        ax2.set_yticks(np.unique(pb))
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

        if len(self.attempt) > 5e5:
            # Doesn't need to remove anything because of the amount of overlapping datapoints with this plot style
            # TODO: reverse arrays to get the newest races on top (to get full colordata resolutien)
            acc, wpm, indices = self._removeOverlapping(self.accuracy, self.wpm, 1000, 1)

            plt.scatter(acc, wpm, c=np.interp(self.attempt[indices], (least, most), (0, 1)), cmap="RdYlGn", s=s)
        else:
            plt.scatter(self.accuracy, self.wpm, c=np.interp(self.attempt, (least, most), (0, 1)), cmap="RdYlGn", s=s)

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
        entries = {}

        for attempt, current_date in list(zip(self.attempt, self.date)):
            if current_date in entries:
                entries[current_date] += 1
            else:
                entries[current_date] = 1

        plt.title("Total races per day")
        plt.xticks(rotation=-90)
        plt.subplots_adjust(bottom=0.2)
        plt.bar(list(map(lambda x: x[0], entries.items())), list(map(lambda x: x[1], entries.items())))

        plt.savefig("./img/DailyRaces.png")
