import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QScrollArea,
                             QCheckBox, QLabel, QGridLayout, QComboBox, QToolButton, QMenu, QAction, QLineEdit, QWidgetAction, QTextEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import pyqtgraph as pg


class SensorApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the main window
        self.setWindowTitle("Sensor Selection Interface")
        self.setGeometry(100, 100, 1000, 600)
        self.setStyleSheet("background-color: #d3d3d3;")

        # Set up the central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Left Panel - Sensor Selection
        sensor_layout = QVBoxLayout()
        sensor_label = QLabel("ALL SENSORS")
        sensor_label.setFont(QFont("Arial", 16))
        sensor_label.setAlignment(Qt.AlignLeft)
        sensor_layout.addWidget(sensor_label)

        # Toggle Button for All Sensors
        self.all_sensors_checkbox = QCheckBox()
        self.all_sensors_checkbox.setChecked(False)
        self.all_sensors_checkbox.stateChanged.connect(self.toggle_all_sensors)
        sensor_layout.addWidget(self.all_sensors_checkbox)

        # Scroll Area for individual sensors
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.sensor_list_widget = QWidget()
        self.sensor_list_layout = QVBoxLayout(self.sensor_list_widget)

        # Sensor Checkboxes
        self.sensor_buttons = []
        sensors = ["TGS2600", "TGS2602", "TGS816", "TGS813", "MQ8", "TGS2611", "TGS2620", "TGS822", "MQ135", "MQ3"]
        for sensor in sensors:
            sensor_button = QCheckBox(sensor)
            sensor_button.setStyleSheet("padding: 10px; font-size: 14px;")
            sensor_button.stateChanged.connect(self.update_all_sensors_checkbox)
            self.sensor_list_layout.addWidget(sensor_button)
            self.sensor_buttons.append(sensor_button)

        scroll.setWidget(self.sensor_list_widget)
        sensor_layout.addWidget(scroll)

        # Add left panel layout to main layout
        main_layout.addLayout(sensor_layout)

        # Right Panel - Graph Area & Selections
        right_layout = QVBoxLayout()

        # Top Buttons (AI Selection, Feature Selection, Hardware)
        button_layout = QHBoxLayout()

        # Switch between Default and Custom
        self.switch_combo = QComboBox()
        self.switch_combo.addItems(["Default", "Custom"])
        self.switch_combo.setFont(QFont("Arial", 12))
        self.switch_combo.setStyleSheet("background-color: #00FF99; padding: 10px; border-radius: 10px;")
        self.switch_combo.currentIndexChanged.connect(self.toggle_hardware_button)
        button_layout.addWidget(self.switch_combo)

        # AI Selection Dropdown
        ai_selection_combo = QComboBox()
        ai_selection_combo.addItems(["NN", "Random Forest", "SVM"])
        ai_selection_combo.setFont(QFont("Arial", 12))
        ai_selection_combo.setStyleSheet("background-color: #00FF99; padding: 10px; border-radius: 10px;")
        button_layout.addWidget(ai_selection_combo)

        # Feature Selection Dropdown with Checkboxes
        feature_selection_button = QToolButton()
        feature_selection_button.setText("FEATURE SELECTION")
        feature_selection_button.setFont(QFont("Arial", 12))
        feature_selection_button.setStyleSheet("background-color: #00FF99; padding: 10px; border-radius: 10px;")
        feature_selection_button.setPopupMode(QToolButton.InstantPopup)

        feature_menu = QMenu()
        features = ["stddev", "max", "min", "mean", "kurtosis"]
        for feature in features:
            action = QAction(feature, self)
            action.setCheckable(True)
            feature_menu.addAction(action)
        feature_selection_button.setMenu(feature_menu)
        button_layout.addWidget(feature_selection_button)

        # Hardware Dropdown with Inhale and Exhale Insert Box
        self.hardware_button = QToolButton()
        self.hardware_button.setText("HARDWARE")
        self.hardware_button.setFont(QFont("Arial", 12))
        self.hardware_button.setStyleSheet("background-color: #00FF99; padding: 10px; border-radius: 10px;")
        self.hardware_button.setPopupMode(QToolButton.InstantPopup)

        hardware_menu = QMenu()
        inhale_action = QWidgetAction(self)
        inhale_widget = QWidget()
        inhale_layout = QHBoxLayout()
        inhale_label = QLabel("Inhale (s): ")
        inhale_edit = QLineEdit()
        inhale_edit.setMaximumWidth(50)
        inhale_layout.addWidget(inhale_label)
        inhale_layout.addWidget(inhale_edit)
        inhale_widget.setLayout(inhale_layout)
        inhale_action.setDefaultWidget(inhale_widget)
        hardware_menu.addAction(inhale_action)

        exhale_action = QWidgetAction(self)
        exhale_widget = QWidget()
        exhale_layout = QHBoxLayout()
        exhale_label = QLabel("Exhale (s): ")
        exhale_edit = QLineEdit()
        exhale_edit.setMaximumWidth(50)
        exhale_layout.addWidget(exhale_label)
        exhale_layout.addWidget(exhale_edit)
        exhale_widget.setLayout(exhale_layout)
        exhale_action.setDefaultWidget(exhale_widget)
        hardware_menu.addAction(exhale_action)

        self.hardware_button.setMenu(hardware_menu)
        button_layout.addWidget(self.hardware_button)

        # Initially lock the Hardware button if Default is selected
        self.toggle_hardware_button()

        right_layout.addLayout(button_layout)

        # Graph Area using PyQtGraph
        self.graph_widget = pg.PlotWidget()
        self.graph_widget.setBackground('w')
        right_layout.addWidget(self.graph_widget)

        # Prediction Result Area
        prediction_result_label = QLabel("Prediction Result:")
        prediction_result_label.setFont(QFont("Arial", 14))
        right_layout.addWidget(prediction_result_label)

        self.prediction_result_text = QTextEdit()
        self.prediction_result_text.setFixedHeight(100)
        self.prediction_result_text.setReadOnly(True)
        right_layout.addWidget(self.prediction_result_text)

        # Add right panel layout to main layout
        main_layout.addLayout(right_layout)

    def toggle_all_sensors(self, state):
        for sensor_button in self.sensor_buttons:
            sensor_button.setChecked(state == Qt.Checked)

    def update_all_sensors_checkbox(self):
        all_checked = all(sensor_button.isChecked() for sensor_button in self.sensor_buttons)
        self.all_sensors_checkbox.setChecked(all_checked)

    def toggle_hardware_button(self):
        if self.switch_combo.currentText() == "Default":
            self.hardware_button.setEnabled(False)
        else:
            self.hardware_button.setEnabled(True)


# Main Application Loop
def main():
    app = QApplication(sys.argv)
    window = SensorApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
