from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QColor

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class GraphCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig, self.ax = plt.subplots(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)

    # def update_plot(self, plot_datas):
    #     self.x = np.linspace(0, 10, len(plot_datas))
    #     self.y = np.sin(self.x)
    #     self.line, = self.ax.plot(self.x, self.y)

    #     self.ax.draw_artist(self.line)
    #     self.fig.canvas.draw()

    def update_plot(self, plot_datas : pd.DataFrame):
        sensor_colors = {
            'TGS2600'   : QColor(255, 0, 0, 127).name(), #ff0000
            'TGS2602'   : QColor(255, 120, 0, 127).name(), #ff7700
            'TGS816'    : QColor(255, 240, 0, 127).name(), #ffee00
            'TGS813'    : QColor(128, 255, 0, 127).name(), #80ff00
            'MQ8'       : QColor(0, 255, 0, 127).name(), #00ff00
            'TGS2611'   : QColor(0, 255, 200, 127).name(), #00ffc8
            'TGS2620'   : QColor(0, 0, 255, 127).name(), #0000ff
            'TGS822'    : QColor(150, 0, 255, 127).name(), #9600ff
            'MQ135'     : QColor(230, 0, 255, 127).name(), #ee00ff
            'MQ3'       : QColor(35, 0, 105, 127).name(), #230069
        }

        for sensor_key in sensor_colors.keys():
            plot_data = plot_datas[sensor_key].to_list()
            color = sensor_colors[sensor_key]

            x = np.linspace(0, 10, len(plot_data))
            y = plot_data
            line, = self.ax.plot(x, y, color=color)

            self.ax.draw_artist(line)
        
        self.fig.canvas.draw()
        