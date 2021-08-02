import gym
from common_functions import process_state_image
import cv2 as cv
import numpy as np
is_pressed_left  = False # control left
is_pressed_right = False # control right
is_pressed_space = False # control gas
is_pressed_shift = False # control break
is_pressed_esc   = False # exit the game
is_pressed_enter = False

steering_wheel = 0 # init to 0
gas            = 0 # init to 0
break_system   = 0 # init to 0

low_H          = 56
low_S          = 0
low_V          = 0

high_H         = 113
high_S         = 150
high_V         = 255

posicionXAuto  = 199 
posicionYAutoy = 301

contIzquierda = 0
contDerecha = 0

def key_press(key, mod):
    global is_pressed_left
    global is_pressed_right
    global is_pressed_space
    global is_pressed_shift
    global is_pressed_esc
    global is_pressed_enter
    print("-------key_press---------:",key)
    
    if key == 65361:
        is_pressed_left = True
    if key == 65363:
        is_pressed_right = True
    if key == 32:
        is_pressed_space = True
    if key == 65505:
        is_pressed_shift = True
    if key == 65307:
        is_pressed_esc = True
    if key == 65293: 
        is_pressed_enter = True

def key_release(key, mod):
    global is_pressed_left
    global is_pressed_right
    global is_pressed_space
    global is_pressed_shift
    global is_pressed_enter
    print("-------key_release---------:",key)
    if key == 65361:
        is_pressed_left = False
    if key == 65363:
        is_pressed_right = False
    if key == 32:
        is_pressed_space = False
    if key == 65505:
        is_pressed_shift = False
    #if key == 65293: 
    #    is_pressed_enter = False

def update_action():
    global steering_wheel
    global gas
    global break_system
    print(";;;;;;;;;;;;;;;;;;;;;;;;;;",is_pressed_left ^ is_pressed_right )
    if is_pressed_left or is_pressed_right:
        if is_pressed_left:
            if steering_wheel > -1:
                steering_wheel -= 0.5
            else:
                steering_wheel = -1
        if is_pressed_right:
            if steering_wheel < 1:
                steering_wheel += 0.5
            else:
                steering_wheel = 1
    else:
        if abs(steering_wheel - 0) < 0.1:
            steering_wheel = 0
        elif steering_wheel > 0:
            steering_wheel -= 0.1
        elif steering_wheel < 0:
            steering_wheel += 0.1
    
    
    if is_pressed_space:
        if gas < 1:
            gas += 0.1
        else:
            gas = 1
    else:
        if gas > 0:
            gas -= 0.1
        else:
            gas = 0
    
    
    if is_pressed_shift:
        if break_system < 1:
            break_system += 0.1
        else:
            break_system = 1
    else:
        if break_system > 0:
            break_system -= 0.1
        else:
            break_system = 0

def procesamientoImagenOPENCV(state):
    global valorThreshold
    global low_H, low_S, low_V, high_H, high_S, high_V

    state = cv.resize(state, (400, 400))#Se puede omitir esta línea
    hsv = cv.cvtColor(state, cv.COLOR_BGR2HSV)
    
    hsv_threshold = cv.inRange(hsv, (65, 230, 170), (153, 255, 217))
    negada = cv.bitwise_not(hsv_threshold)
    #gray = cv.cvtColor(hsv, cv.COLOR_BGR2GRAY)
    #state = cv.cvtColor(state, cv.COLOR_BGR2GRAY)
    #state = state.astype(float)
    #Obtencion de color de carro y pista.     
    #resultado2 = cv.subtract(state, negada)    
    #addImagen = cv.absdiff(state, resultado2)
    #resultado2 = cv.add(state, negada)
    
    #cv.imshow('frame',resultado2)
    #cv.imshow('negada',negada)
    return hsv_threshold


def obtencionCentroDeMasaAuto(imagen):
    global posicionYAutoy
    global posicionXAuto
    #Ver dimension y canales de la imagen
    #print(imagen[5][5])
    imagenArray = np.array(imagen)
    valores = np.argwhere(imagenArray != 0)
    m = cv.moments(imagen)
    x = 0
    y = 0
    try:
        x = m['m10']/m['m00']
        y = m['m01']/m['m00']
        print('x=',x, 'y=',y)
    except: 
        print("Division para cero")
    x = posicionXAuto
    y = posicionYAutoy
    #return x,y
    #imagenArray = np.array(imagen)
    #matrizBlancos = np.where(imagenArray >= 30)
    #print("------------------", valores, "---------------")
    
    #for i in range(100,200):
    #    for j in range(100,200):
    #        if imagen[i, j] == 0  :
    #            print('pixel:', imagen[i, j]) 
     #       h, s, v = imagen[i, j]
    #        print('pixel:', h, s, v)
    #pass
    #return fondoConCamara


def graficaDeCentroideImagen(nombreVentana,imagenUmbralizada):
    global posicionYAutoy
    global posicionXAuto
    cv.circle(imagenUmbralizada, (int(posicionXAuto),int(posicionYAutoy)), 3, (0, 0, 255), 5)
    #cv.imshow(nombreVentana,imagenUmbralizada)
    return imagenUmbralizada

def procesamientoImagenCalle(imagen):
    
    imagen = cv.resize(imagen, (400, 400))#Se puede omitir esta línea
    hsvCalle = cv.cvtColor(imagen, cv.COLOR_BGR2HSV)
    #hsv_threshold_calle = cv.inRange(hsvCalle, (16, 0, 0), (88, 124, 255))
    hsv_threshold_calle = cv.inRange(hsvCalle, (low_H, low_S, low_V), (high_H, high_S, high_V))
    
    negada = cv.bitwise_not(hsv_threshold_calle)
    #cv.imshow('negadaCalle',negada)
    return hsv_threshold_calle


def unionAutoMasBordes(imagenAuto, imagenBordes): 
    unionImagenes = cv.absdiff(imagenBordes, imagenAuto)
    #cv.imshow('frame', unionImagenes)
    return unionImagenes


def moverAuto(key):
    global is_pressed_left
    global is_pressed_right

    if key == 65361:
        is_pressed_left = True
    if key == 65363:
        is_pressed_right = True

def moverAutoRelease(key):
    global is_pressed_left
    global is_pressed_right
    if key == 65361:
        is_pressed_left = False
    if key == 65363:
        is_pressed_right = False
    


def controlDeteccionBordes2(unionImagenes, imagenAuto, imagenBordes):
    
    global contIzquierda
    global contDerecha  

    posicionMinAncho = posicionXAuto-15
    posicionMinAlto = posicionYAutoy-25
    posicionMaxAncho = posicionXAuto+15
    posicionMaxAlto = posicionYAutoy+25

    #Ancho  -----------
    posicionImin = posicionXAuto - 75
    posicionImax = posicionXAuto + 75
    #Alto |||||||||||
    posicionJmin = posicionYAutoy - 75
    posicionJmax = posicionYAutoy + 75
    cont = 0
    #i = ancho
    #j  = alto
    #imagenBordes = cv.circle(imagenBordes,(250,200), 2, 255, 2)    
    #imagenBordes = cv.circle(imagenBordes,(200,200), 2, 255, 2)  
    #imagenBordes = cv.circle(imagenBordes,(200,300), 2, 255, 2) 

    

    #while(contIzquierda != contDerecha):
    contIzquierda = 0
    contDerecha = 0
    for j in range(posicionJmin, posicionJmin+1): 
        for i in range(posicionImin, posicionImax):
            
            if imagenBordes[j][i] == 255 :
                print("j:",j , " pixel: ", imagenBordes[j][i], " i:",i)
                #
                if i < 180 :
                    #imagenBordes = cv.circle(imagenBordes,(i,j), 2, 255, 2) 
                    contIzquierda = contIzquierda+1
                else:
                    #imagenBordes = cv.circle(imagenBordes,(i,j), 2, 255, 2) 
                    contDerecha = contDerecha +1
            
    
    print("contIzquierda: ", contIzquierda)
    print("contDerecha: ", contDerecha)
   

    #imagenAuto = cv.rectangle(imagenAuto, (posicionMinAncho, posicionMinAlto)
    #                    , (posicionMaxAncho, posicionMaxAlto), 255, 1)
    

    
    #imagenBordes = cv.rectangle(imagenBordes, (posicionImin, posicionJmin)
    #                   , (posicionImax, posicionJmax), 255, 1)
                       
    cv.imshow('imagenAuto', imagenAuto)
    cv.imshow('imagenBordes', imagenBordes)                   
    cv.imshow('frame', unionImagenes)

   

def on_low_H_thresh_trackbar(val):
    global low_H
    low_H = val

def on_high_H_thresh_trackbar(val):
    global high_H
    high_H = val

def on_low_S_thresh_trackbar(val):
    global low_S
    low_S = val

def on_high_S_thresh_trackbar(val):
    global high_S
    high_S = val

def on_low_V_thresh_trackbar(val):
    global low_V
    low_V = val

def on_high_V_thresh_trackbar(val):
    global high_V
    high_V = val 

if __name__ == '__main__':
    
    

    env = gym.make('CarRacing-v0')
    state = env.reset()
    cv.namedWindow('frame', cv.WINDOW_AUTOSIZE)
    #cv.namedWindow('negada', cv.WINDOW_AUTOSIZE)
    #cv.namedWindow('negadaCalle', cv.WINDOW_AUTOSIZE)
    #cv.namedWindow('centroMasaAuto', cv.WINDOW_AUTOSIZE)
    init_state = procesamientoImagenOPENCV(state)
    env.unwrapped.viewer.window.on_key_press = key_press
    env.unwrapped.viewer.window.on_key_release = key_release

    cv.createTrackbar("low_H", 'frame' , low_H, 180, on_low_H_thresh_trackbar)
    cv.createTrackbar("low_S", 'frame' , low_S, 255, on_low_S_thresh_trackbar)
    cv.createTrackbar("low_V", 'frame' , low_V, 255, on_low_V_thresh_trackbar)

    cv.createTrackbar("high_H", 'frame' , high_H, 180, on_high_H_thresh_trackbar)
    cv.createTrackbar("high_S", 'frame' , high_S, 255, on_high_S_thresh_trackbar)
    cv.createTrackbar("high_V", 'frame' , high_V, 255, on_high_V_thresh_trackbar)
    
    counter = 0
    total_reward = 0
    while not is_pressed_esc:
        env.render()
        
        
        imagenUmbralizadaAuto = procesamientoImagenOPENCV(state)
        obtencionCentroDeMasaAuto(imagenUmbralizadaAuto)
        imagenUmbralizadaAuto = graficaDeCentroideImagen('centroMasaAuto', imagenUmbralizadaAuto)
        
        imagenUmbralizadaCalle = procesamientoImagenCalle(state)
        imagenUmbrealizada = unionAutoMasBordes(imagenUmbralizadaAuto, imagenUmbralizadaCalle)
        
        controlDeteccionBordes2(imagenUmbrealizada, imagenUmbralizadaAuto, imagenUmbralizadaCalle)
        
        if (is_pressed_enter == True):
            
            update_action()
            if (contIzquierda > contDerecha):
                #while contDerecha < contIzquierda:
                #mover a la derecha
                #moverAuto(65363)
                
                #steering_wheel = steering_wheel+0.2
                print("----------Mover a la derecha-----------")
                
                
                
            if (contDerecha > contIzquierda):
                #while contIzquierda < contDerecha:
                
                #mover a la izquierda
                moverAuto(65361)
                #moverAutoRelease(65361)
                #steering_wheel = steering_wheel-0.2
                print("----------Mover a la izquierda-----------")
               
            update_action()
            action = [steering_wheel, gas, break_system]
            print(" Volante, gas, sistema de frenos ", steering_wheel, gas, break_system)
            state, reward, done, info = env.step(action)
            counter += 1
            total_reward += reward
            print('Action:[{:+.1f}, {:+.1f}, {:+.1f}] Reward: {:.3f}'.format(action[0], action[1], action[2], reward))

        else:     
            update_action()
            action = [steering_wheel, gas, break_system]
            print(" +++++++++++++++++++++++++++++++++++++++++++++++")
            print(" Volante, gas, sistema de frenos ", steering_wheel, gas, break_system)
            state, reward, done, info = env.step(action)
            counter += 1
            total_reward += reward
            print('Action:[{:+.1f}, {:+.1f}, {:+.1f}] Reward: {:.3f}'.format(action[0], action[1], action[2], reward))
            
    
        if done:
            print("Restart game after {} timesteps. Total Reward: {}".format(counter, total_reward))
            counter = 0
            total_reward = 0
            state = env.reset()
            continue
            
        moverAutoRelease(65363)
        moverAutoRelease(65361)
    env.close()
