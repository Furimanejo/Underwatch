from PyQt5.QtWidgets import * 
from PyQt5.QtCore import *

import time
import sys
import asyncio
import os
import buttplug.client as bp
from overwatch_cv import * 

class AsyncWorker(QRunnable):  
  def __init__(self, funtion):
    super(AsyncWorker, self).__init__()
    self.function = funtion

  @pyqtSlot()
  def run(self):
    asyncio.run(self.function())

class CustomSlider(QWidget):
  def __init__(self, value, parent = None):
    super().__init__(parent)

    self.spinbox = QSpinBox(self)
    self.spinbox.setMaximum(100)
    self.spinbox.setValue(value)
    self.spinbox.valueChanged.connect(self.value_changed)

    self.slider = QSlider(Qt.Orientation.Horizontal, self)
    self.slider.setMaximum(100)
    self.slider.setValue(value)
    self.slider.valueChanged.connect(self.value_changed)

    layout = QHBoxLayout()
    layout.addWidget(self.spinbox)
    layout.addWidget(self.slider)
    self.setLayout(layout)

  def value_changed(self, value):
    self.spinbox.setValue(value)
    self.slider.setValue(value)

  def value(self):
    return self.spinbox.value()

class Underwatch(QMainWindow):
  def __init__(self) -> None:
    super(Underwatch, self).__init__()

    self.setWindowTitle("Underwatch")
    self.resize(600, 400)
    widget = QWidget(self)
    self.setCentralWidget(widget)
    self.main_layout = QVBoxLayout()
    widget.setLayout(self.main_layout)
    self.show()
    
    # Buttplug box
    buttplug_box = QGroupBox("Buttplug Option", self)
    self.main_layout.addWidget(buttplug_box)
    buttplug_layout = QGridLayout()
    buttplug_box.setLayout(buttplug_layout)

    self.try_connect = False
    connect_btn = QPushButton("Connect to Intiface")
    connect_btn.clicked.connect(self.set_try_connect)
    buttplug_layout.addWidget(connect_btn, 0, 0)

    # Slider box
    sliders_box = QGroupBox("Gameplay Options", self)
    self.main_layout.addWidget(sliders_box)
    self.sliders_layout = QGridLayout()
    sliders_box.setLayout(self.sliders_layout)

    self.decay_slider = CustomSlider(10)
    self.sliders_layout.addWidget(QLabel("Decay"), 0, 0)
    self.sliders_layout.addWidget(self.decay_slider, 0, 1)

    self.elimination_slider = CustomSlider(50)
    self.sliders_layout.addWidget(QLabel("Elimination"), 1, 0)
    self.sliders_layout.addWidget(self.elimination_slider, 1 , 1)

    self.assist_slider = CustomSlider(30)
    self.sliders_layout.addWidget(QLabel("Assist"), 2, 0)
    self.sliders_layout.addWidget(self.assist_slider, 2, 1)

    self.saves_slider = CustomSlider(50)
    self.sliders_layout.addWidget(QLabel("Saved"), 3, 0)
    self.sliders_layout.addWidget(self.saves_slider, 3, 1)

    # Loop stuff
    self.score = 0
    self.client = bp.ButtplugClient("Underwatch")
    self.overwatch_cv = OverwatchCV()
    self.threadpool = QThreadPool()
    self.async_worker = AsyncWorker(self.async_loop)
    self.threadpool.start(self.async_worker)

    # Overlay
    self.overlay = QWidget()
    self.overlay.setWindowFlags(
        Qt.WindowType.WindowTransparentForInput | 
        Qt.WindowStaysOnTopHint | 
        Qt.FramelessWindowHint | 
        Qt.Tool)
    self.overlay.setAttribute(Qt.WA_TranslucentBackground)
    self.overlay.setGeometry(0, 0, self.overwatch_cv.width, self.overwatch_cv.height)
    self.score_label = QLabel("Score Label", self.overlay)
    self.score_label.setStyleSheet("color: magenta; font-size: 16pt")
    self.score_label.move(int(0.1 * self.overwatch_cv.width), int(0.95 * self.overwatch_cv.height))
    self.overlay.show()

  def closeEvent(self, event) -> None:
    os._exit(0)

  async def async_loop(self):
    last_update = time.time()
    while(True):
      delta_time = time.time() - last_update
      last_update = time.time()

      self.overwatch_cv.capture_popup_frame()
      elims = self.overwatch_cv.detect_eliminations()
      assists = self.overwatch_cv.detect_assists()
      saves = self.overwatch_cv.detect_saves()

      frame_score = 0
      popup_duration = 2.8
      frame_score += self.elimination_slider.value() * elims / popup_duration
      frame_score += self.assist_slider.value() * assists / popup_duration
      frame_score += self.saves_slider.value() * saves / popup_duration
      if(frame_score == 0):
        frame_score -= self.decay_slider.value()

      cv_time = time.time() - last_update
      self.score += delta_time * frame_score
      self.score = max(self.score, 0)

      text = "Score: " + str(int(self.score))
      if(elims > 0):
        text += " +Elimination x" + str(elims)
      if(assists > 0):
        text += " +Assist x" + str(assists)
      if(saves > 0):
        text += " +Save x" + str(saves)
      text += "\nCV: " + str(int(cv_time*1000)) + "ms"
      self.score_label.setText(text)
      self.score_label.adjustSize()

      if(self.try_connect):
        await self.connect()
        self.try_connect = False

      time_before_next_send = .2 - cv_time
      await asyncio.sleep(time_before_next_send)
      await self.send_value_to_toys()

  def set_try_connect(self):
    self.try_connect = True

  async def connect(self):
    self.connector = bp.websocket_connector.ButtplugClientWebsocketConnector("ws://127.0.0.1:12345")
    try:
      await self.client.connect(self.connector)
      await self.client.start_scanning()
    except bp.ButtplugClientConnectorError as e:
      print(e.message)

  async def send_value_to_toys(self):
    value = min(self.score/100 , 1)
    for device in self.client.devices.values():
      if "VibrateCmd" in device.allowed_messages.keys():
          await device.send_vibrate_cmd(value)

app = QApplication(sys.argv)
underwatch = Underwatch()
sys.exit(app.exec())