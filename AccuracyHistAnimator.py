import numpy as np
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from math import floor


class AccuracyHistAnimator:
    def __init__(self, accuracy):
        self.accuracy = np.floor(accuracy * 100) / 100
        self.fig, self.ax = plt.subplots()

        self.bins = np.floor(np.arange(floor(min(self.accuracy) * 100) / 100, 1.011, 0.01) * 100) / 100
        self.hist = None
        self.frame_step_size = None

        self.ax.set_title("Typing test accuracy distribution")
        self.ax.set_xlabel("Accuracy (%)")
        self.ax.set_ylabel("Amount of races")

        xtick_bins = np.delete(self.bins, np.argwhere(self.bins > 1.005))
        self.xticks = self.bins[::len(xtick_bins) // 10 if len(xtick_bins) > 10 else 1]
        self.ax.set_xticks(self.xticks + 0.005)
        self.ax.set_xticklabels([f"{round(100*value)}" for value in self.xticks])

        self.fig.subplots_adjust(left=0.15)

    def _animate(self, i):
        if self.hist is not None:
            self.hist[2][0].remove()
        self.hist = self.ax.hist(self.accuracy[:self.frame_step_size * i + 1], bins=self.bins, color="blue")  # TODO: make step_size non-linear

    def save_animation(self, filename, frame_step_size=None, duration_seconds=3):
        if frame_step_size is None:
            frame_step_size = len(self.accuracy) // 36

        if frame_step_size == 0:
            frame_step_size = 1

        self.frame_step_size = frame_step_size
        max_frames = len(self.accuracy) // frame_step_size
        ani = FuncAnimation(self.fig, self._animate, frames=max_frames, blit=False)
        ani.save(filename, writer='pillow', fps=max_frames // duration_seconds)
