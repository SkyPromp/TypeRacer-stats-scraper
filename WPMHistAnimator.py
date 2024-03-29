import numpy as np
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from math import ceil


class WPMHistAnimator:
    def __init__(self, wpm):
        self.wpm = wpm
        self.fig, self.ax = plt.subplots()

        #self.bins = np.arange(min(self.wpm), max(self.wpm), 1)

        self.hist = None
        self.frame_step_size = None

        self.ax.set_title("Typing test wpm distribution")
        self.ax.set_xlabel("Typing speed (WPM)")
        self.ax.set_ylabel("Amount of races")

        binsize = ceil(ceil((max(self.wpm) - min(self.wpm)) / 50))
        self.bins = np.arange(min(self.wpm), max(self.wpm), binsize)
        self.fig.subplots_adjust(left=0.15)

    def _animate(self, i):
        if self.hist is not None:
            self.hist[2][0].remove()

        self.hist = self.ax.hist(self.wpm[:self.frame_step_size * i + 1], bins=self.bins, color="blue")  # TODO: make step_size non-linear

    def save_animation(self, filename, frame_step_size=None, duration_seconds=3):
        if frame_step_size is None:
            frame_step_size = len(self.wpm) // 36

        if frame_step_size == 0:
            frame_step_size = 1

        self.frame_step_size = frame_step_size
        max_frames = len(self.wpm) // frame_step_size
        ani = FuncAnimation(self.fig, self._animate, frames=max_frames, blit=False)
        ani.save(filename, writer='pillow', fps=max_frames // duration_seconds)
