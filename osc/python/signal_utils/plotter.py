import sys
from PyQt5.QtWidgets import QApplication
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class GenericPlotter:
    """
    Generic plotter for animating time-series data arrays.

    Each entry in data_configs must be a dict with:
      - data: numpy array of shape (N, M)
      - lock: threading.Lock protecting that array
      - title: subplot title (str)
      - labels: list of M labels, one per line
      - ylim: (ymin, ymax) tuple
    """
    def __init__(self, data_configs, plot_len, interval=50, text_func=None, text_position=(0.1, 0.99)):
        self.data_configs = data_configs
        self.plot_len = plot_len
        self.interval = interval
        self.text_func = text_func
        self.text_position = text_position

    def show(self):
        # Start Qt application
        app = QApplication(sys.argv)

        # Build subplots
        num_plots = len(self.data_configs)
        fig, axs = plt.subplots(num_plots, 1, figsize=(8, 6))
        if num_plots == 1:
            axs = [axs]

        # Prepare lines
        lines = []
        for ax, cfg in zip(axs, self.data_configs):
            ax.set_title(cfg['title'])
            line_objs = [ax.plot([], [], label=lbl)[0] for lbl in cfg['labels']]
            ax.legend()
            ax.set_xlim(0, self.plot_len)
            ax.set_ylim(*cfg['ylim'])
            ax.set_xlabel('Samples')
            ax.set_ylabel('Value')
            lines.append(line_objs)

        # Optional overlay text
        overlay = None
        if self.text_func:
            overlay = fig.text(
                self.text_position[0],
                self.text_position[1],
                "",
                ha='left', va='top',
                fontsize=10, color='green'
            )

        # Animation update
        def animate(frame):
            artists = []
            for cfg, objs in zip(self.data_configs, lines):
                with cfg['lock']:
                    data = cfg['data']
                    for i, ln in enumerate(objs):
                        ln.set_data(range(self.plot_len), data[:, i])
                artists.extend(objs)

            if overlay:
                try:
                    txt = self.text_func()
                except Exception:
                    txt = ''
                overlay.set_text(txt)
                artists.append(overlay)

            return artists

        # Keep animation reference alive
        self.ani = FuncAnimation(fig, animate, interval=self.interval, blit=False)
        plt.tight_layout()
        plt.show()