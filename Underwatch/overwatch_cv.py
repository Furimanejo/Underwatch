import dxcam
# from PIL import ImageGrab
import numpy as np
import cv2 as cv
import os, sys
import time 

class OverwatchCV:
  def __init__(self):
    # PIL
    # frame = ImageGrab.grab()
    # self.width = frame.width
    # self.height = frame.height

    # DXCAM
    self.frame_grabber = dxcam.create(output_color="BGR")
    frame = self.frame_grabber.grab()
    self.width = frame.shape[1]
    self.height = frame.shape[0]

    self.use_black_and_white_popups = True
    self.elimination_template = self.load_template("elimination.png", self.use_black_and_white_popups)
    self.assist_template = self.load_template("assist.png", self.use_black_and_white_popups)
    # self.eliminated_template = self.load_template("you_were_eliminated.png", self.use_black_and_white_popups)
    self.saved_template = self.load_template("saved.png", self.use_black_and_white_popups)
    self.potg_template = self.load_template("potg.png")
    self.killcam_template = self.load_template("killcam.png")

  def load_template(self, file_name, make_binary = False):
    path = os.path.join(os.path.abspath("."), "templates", file_name)
    template = cv.imread(path)
    if(make_binary == True):
      template = self.white_range(template)
    height = int(template.shape[0] * self.height / 1080)
    width =  int(template.shape[1] * self.width / 1920)
    return cv.resize(template, (width, height))

  def white_range(self, mat):
    min = 150
    return cv.inRange(mat, (min, min, min), (255, 255, 255))
  
  def black_range(self, mat):
    max = 165
    return cv.inRange(mat, (0,0,0), (max, max, max))

  def start_cam(self):
    self.frame_grabber.start(target_fps=10)

  def capture_frame(self):
    self.frame = self.frame_grabber.get_latest_frame()

  def match_template(self, frame, template):
    result = cv.matchTemplate(frame, template, cv.TM_CCOEFF_NORMED)
    minVal, maxVal, minLoc, maxLoc = cv.minMaxLoc(result)
    return (maxVal > .85)

  def is_killcam_or_potg(self):
    top = int(25/1080*self.height)
    bottom = int(80/1080*self.height)
    left = int(35/1920*self.width)
    right =int(120/1920*self.width)
    crop = self.frame[top:bottom, left:right]

    if(self.match_template(crop, self.killcam_template)):
      return True
    return self.match_template(crop, self.potg_template)

  def count_popups(self):
    left = int(670 * self.width / 1920 ) 
    top = int(750 * self.height / 1080 )
    width = int(480 * self.width / 1920 ) 
    height = int(100 * self.height / 1080)
    popups = self.frame[top:top+height,left:left+width]
    one_third = int(height/3)
    two_thirds = int(2*height/3)
    
    elims = 0
    assists = 0
    saves = 0
    for popup in (popups[0:one_third, 0:width], popups[one_third:two_thirds, 0:width], popups[two_thirds:height, 0:width]):
      white = self.white_range(popup)
      popup_found, elim, assist, save = self.identify_popup(white)
      if (popup_found):
        elims += elim
        assists += assist
        saves += save
        continue
      black = self.black_range(popup)
      popup_found, elim, assist, save = self.identify_popup(black)
      if (popup_found):
        elims += elim
        assists += assist
        saves += save
      else:
        break

    return elims, assists, saves

  def identify_popup(self, frame):
    if(self.match_template(frame, self.elimination_template)):
      return True, 1, 0, 0
    if(self.match_template(frame, self.assist_template)):
      return True, 0, 1, 0
    if(self.match_template(frame, self.saved_template)):
      return True, 0, 0, 1
    return False, 0, 0, 0