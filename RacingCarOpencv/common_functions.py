import cv2 as cv
import numpy as np


def nothing(x):
    pass


def process_state_image(state):
    state = cv.cvtColor(state, cv.COLOR_BGR2HSV)
    state = cv.cvtColor(state, cv.COLOR_BGR2GRAY)
    state = state.astype(float)
    
    state = cv.resize(state, (400, 400))#Se puede omitir esta línea
    
  

    return state

def generate_state_frame_stack_from_queue(deque):
    frame_stack = np.array(deque)
    # Move stack dimension to the channel dimension (stack, x, y) -> (x, y, stack)
    return np.transpose(frame_stack, (1, 2, 0))
