from PIL import ImageGrab
import numpy as np
import cv2 as cv
import os

class ComputerVision:
  def __init__(self):
    # PIL
    frame = ImageGrab.grab()
    self.width = frame.width
    self.height = frame.height

    # DXCAM
    # self.frame_grabber = dxcam.create(output_color="BGR")
    # frame = self.frame_grabber.grab()
    # self.width = frame.shape[1]
    # self.height = frame.shape[0]

    self.elimination_template = self.load_template("elimination.png")
    self.assist_template = self.load_template("assist.png")
    self.eliminated_template = self.load_template("you_were_eliminated.png")
    self.saved_template = self.load_template("saved.png")
    
  def load_template(self, file_name):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"templates",file_name)
    template = cv.imread(path)
    height = int(template.shape[0] * self.height / 1080)
    width =  int(template.shape[1] * self.width / 1920)
    return cv.resize(template, (width, height))

  def capture_popup_frame(self):
    region = (.35*self.width, .68*self.height, .6*self.width, .8*self.height)
    frame = ImageGrab.grab(bbox=region)
    # frame = self.frame_grabber.grab(bbox=region) # DXCAM
    frame = np.array(frame)
    frame = cv.cvtColor(frame, cv.COLOR_RGB2BGR) # PIL
    self.frame = frame

  def detect_eliminations(self):
    result = cv.matchTemplate(self.frame, self.elimination_template, cv.TM_CCOEFF_NORMED)
    cv.threshold(result, .85, 255, cv.THRESH_BINARY, result)
    result = result.astype(np.uint8)
    contours = cv.findContours(result, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)[-2]
    return len(contours)

  def detect_assists(self):
    result = cv.matchTemplate(self.frame, self.assist_template, cv.TM_CCOEFF_NORMED)
    cv.threshold(result, .85, 255, cv.THRESH_BINARY, result)
    result = result.astype(np.uint8)
    contours = cv.findContours(result, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)[-2]
    return len(contours)

  def detect_saves(self):
    result = cv.matchTemplate(self.frame, self.saved_template, cv.TM_CCOEFF_NORMED)
    cv.threshold(result, .85, 255, cv.THRESH_BINARY, result)
    result = result.astype(np.uint8)
    contours = cv.findContours(result, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)[-2]
    return len(contours)

  def detect_eliminated(self):
    result = cv.matchTemplate(self.frame, self.eliminated_template, cv.TM_CCOEFF_NORMED)
    minVal, maxVal, minLoc, maxLoc = cv.minMaxLoc(result)
    return maxVal > .85

  def display(self, image):
    cv.imshow("image", self.frame)
    cv.waitKey(1)