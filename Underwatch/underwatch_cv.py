from PIL import ImageGrab
import numpy as np
import cv2 as cv

class ComputerVision:
  def __init__(self):
    frame = ImageGrab.grab()
    self.width = frame.width
    self.height = frame.height
    self.elimination_template = cv.imread(r".\templates\elimination.png")
    self.assist_template = cv.imread(r".\templates\assist.png")
    self.eliminated_template = cv.imread(r".\templates\you_were_eliminated.png")
    
  def capture_frame(self):
    region = (.35*self.width, .68*self.height, .6*self.width, .8*self.height)
    frame = ImageGrab.grab(bbox=region)
    frame = np.array(frame)
    self.frame = cv.cvtColor(frame, cv.COLOR_RGB2BGR)

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

  def detect_eliminated(self):
    result = cv.matchTemplate(self.frame, self.eliminated_template, cv.TM_CCOEFF_NORMED)
    minVal, maxVal, minLoc, maxLoc = cv.minMaxLoc(result)
    return maxVal > .85

  def display(self, image):
    cv.imshow("image", self.frame)
    cv.waitKey(1)