import sys
import collections
import time
import random

from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg
import numpy as np

try:
    import can
except ImportError:  # allow running without python-can
    can = None


class Oscilloscope(QtWidgets.QWidget):
    """Simple real-time oscilloscope for CAN voltage data."""

    WINDOW_SECONDS = 1  # width of the view in seconds
    SAMPLE_RATE = 500  # expected max sample rate in Hz

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CAN Oscilloscope")
        self.setStyleSheet(
            """
            QWidget { background-color: #1e1e1e; color: #e0e0e0; }
            QPushButton { background-color: #2d2d30; border: 1px solid #3e3e42; padding: 6px; }
            QPushButton:pressed { background-color: #007acc; }
            """
        )

        # Graph setup
        self.plot = pg.PlotWidget()
        self.plot.setBackground('k')
        self.plot.setYRange(0, 5)  # assume 0-5V range
        self.curve = self.plot.plot(pen=pg.mkPen('#00fffc', width=2))

        # Data storage
        self.data = collections.deque(maxlen=self.SAMPLE_RATE * self.WINDOW_SECONDS)

        # Control buttons
        self.start_btn = QtWidgets.QPushButton("Start")
        self.stop_btn = QtWidgets.QPushButton("Stop/Freeze")
        self.trigger_input = QtWidgets.QDoubleSpinBox()
        self.trigger_input.setRange(0, 5)
        self.trigger_input.setValue(0)
        self.trigger_input.setSingleStep(0.1)
        self.trigger_btn = QtWidgets.QPushButton("Set Trigger")

        controls = QtWidgets.QHBoxLayout()
        controls.addWidget(self.start_btn)
        controls.addWidget(self.stop_btn)
        controls.addWidget(QtWidgets.QLabel("Trigger [V]:"))
        controls.addWidget(self.trigger_input)
        controls.addWidget(self.trigger_btn)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.plot)
        layout.addLayout(controls)

        self.start_btn.clicked.connect(self.start)
        self.stop_btn.clicked.connect(self.stop)
        self.trigger_btn.clicked.connect(self.apply_trigger)

        # Timer for updates
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)

        # CAN bus setup
        self.simulate = False
        self.bus = None
        if can is not None:
            try:
                self.bus = can.interface.Bus(channel='can0', bustype='socketcan')
            except can.CanError:
                self.simulate = True
        else:
            self.simulate = True

        self.running = False
        self.trigger_level = None
        self.triggered = False

    def apply_trigger(self):
        self.trigger_level = self.trigger_input.value()
        self.triggered = False

    def start(self):
        self.running = True
        self.data.clear()
        self.triggered = False
        self.timer.start(int(1000 / self.SAMPLE_RATE))

    def stop(self):
        self.running = False
        self.timer.stop()

    def read_value(self):
        """Read raw 16-bit value from CAN or simulation."""
        if self.simulate:
            # Simulate sine wave with noise
            t = time.time()
            value = int((np.sin(2 * np.pi * 1 * t) + 1) * 0x1FF + random.randint(-5, 5))
            return max(0, min(0x3FF, value))
        if self.bus is None:
            return None
        msg = self.bus.recv(timeout=0.001)
        if msg and len(msg.data) >= 2:
            return int.from_bytes(msg.data[:2], byteorder='big')
        return None

    def update_plot(self):
        if not self.running:
            return
        raw = self.read_value()
        if raw is None:
            return
        volts = raw / 0x3FF  # 0x3FF corresponds to 1V
        if self.trigger_level is not None and not self.triggered:
            if volts >= self.trigger_level:
                self.triggered = True
            else:
                return
        self.data.append(volts)
        x = np.linspace(0, self.WINDOW_SECONDS, len(self.data))
        self.curve.setData(x, list(self.data))


def main():
    app = QtWidgets.QApplication(sys.argv)
    osc = Oscilloscope()
    osc.resize(800, 400)
    osc.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
