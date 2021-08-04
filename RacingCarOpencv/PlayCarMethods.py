import gym
from common_functions import process_state_image
import cv2 as cv
import numpy as np

# Variables globales y publicas 
# Variables para obtener los eventes del teclado 
is_pressed_left  = False # tecla fecha izquierda
is_pressed_right = False# tecla fecha derecha
is_pressed_space = False # control gas
is_pressed_shift = False # control de sistema de frenos
presionar_esc   = False # exit the game
is_pressed_enter = False # Inicar juego en modo automatico

steering_wheel = 0 # comenzar en 0
gas            = 0 # comenzar en 0
break_system   = 0 # comenzar en 0

low_H          = 56 # Valores minimo para H
low_S          = 0 # Valores minimo para s
low_V          = 0 # Valores minimo para v

high_H         = 113 # Valores maximo para H
high_S         = 150 # Valores maximo para S
high_V         = 255 # Valores maximo para v

posicionXAuto  = 199 # Posicion del centro del auto en X
posicionYAutoy = 301 # Posicion del centro del auto en Y

contIzquierda = 0 # Contador de blancos para lado izquierdo
contDerecha = 0 # Contador de blancos para lado derecho

# Metodo para la deteccion de eventos del teclado
# Segun el numero de la letra, modificamos el valor de las
# Variables globales para el movimiento del auto
def key_press(key, mod):
    global is_pressed_left
    global is_pressed_right
    global is_pressed_space
    global is_pressed_shift
    global presionar_esc
    global is_pressed_enter
    # Activacion del teclado
    if key == 65361:
        is_pressed_left = True
    if key == 65363:
        is_pressed_right = True
    if key == 32:
        is_pressed_space = True
    if key == 65505:
        is_pressed_shift = True
    if key == 65307:
        presionar_esc = True
    if key == 65293: 
        is_pressed_enter = True

# Metodo para la liberacion de eventos del teclado
# Segun el numero de la letra, modificamos el valor de las
# Variables globales para el movimiento del auto
def key_release(key, mod):
    global is_pressed_left
    global is_pressed_right
    global is_pressed_space
    global is_pressed_shift
    global is_pressed_enter
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

# Metodo que nos sirve para modificar los valores 
# de gas, sistemas de frenos y volante del auto
def update_action():
    global steering_wheel
    global gas
    global break_system
    #Comparaciones para la modificacion del volante 
    # -1 gira el volante hacia la izquierda
    # 1 gira el volante hacia la derecha
    if is_pressed_left or is_pressed_right:
        if is_pressed_left:
            # Si el volante es menor al valor de -1, entonces se le suma -0.5 para mantenerlo en ese sentido
            if steering_wheel > -1:
                steering_wheel -= 0.5
            # De lo contrario el volante se mantiene en -1 cambiando el sentido del auto, estableciendo un limite
            else:
                steering_wheel = -1
        if is_pressed_right:
            # Si el volante es menor al valor de -1, entonces se le suma +0.5 para mantenerlo en ese sentido
            if steering_wheel < 1:
                steering_wheel += 0.5
            else:
             # De lo contrario el volante se mantiene en 1 cambiando el sentido del auto, estableciendo un limite
                steering_wheel = 1
    else:
        # Si no se presiona ninguna tecla entonces se mantiene de igual manera sin modificaciones significativas 
        if abs(steering_wheel - 0) < 0.1:
            steering_wheel = 0
        elif steering_wheel > 0:
            steering_wheel -= 0.1
        elif steering_wheel < 0:
            steering_wheel += 0.1
    
    # Contaracion para la aceleracion del auto
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
    
    # Comparacion para el frenado del auto
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
# Metodo para la modificacion del size de la imagen del auto, pasamos al espacio RGB#
def lecturaImagenJuego(state):
    state = cv.cvtColor(state, cv.COLOR_BGR2RGB)
    state = cv.resize(state, (400, 400))#Se puede omitir esta línea
    return state
# Metodo para realizar threshold a la imagen escalada, ademas cambio de espacio de color de BGR A HSV#
def procesamientoImagenOPENCV(state):
    global valorThreshold
    global low_H, low_S, low_V, high_H, high_S, high_V

    state = cv.resize(state, (400, 400))#Se puede omitir esta línea
    hsv = cv.cvtColor(state, cv.COLOR_BGR2HSV)
    hsv_threshold = cv.inRange(hsv, (65, 230, 170), (153, 255, 217))
    #negada = cv.bitwise_not(hsv_threshold)
    return hsv_threshold
# Metodo para obtener el centro del auto de la imagen del auto con threshold# 
def obtencionCentroDeMasaAuto(imagen):
    global posicionYAutoy
    global posicionXAuto
    
    # promedio de las intensidades de los píxeles de una imagen, para la obtencion del centroide del auto
    m = cv.moments(imagen)
    x = 0
    y = 0
    try:
        # Obtencion de posicion del valor x 
        x = m['m10']/m['m00']
        # Obtencion de posicion del valor y
        y = m['m01']/m['m00']
        print('x=',x, 'y=',y)
    except: 
        print("Division para cero")
    # Modificamos los valores globales de X y Y con los nuevos valores
    posicionXAuto = int(x)  
    posicionYAutoy = int(y)  

# Metodo para la graficacion del centroide del auto#
def graficaDeCentroideImagen(imagenUmbralizada):
    global posicionYAutoy
    global posicionXAuto
    cv.circle(imagenUmbralizada, (int(posicionXAuto),int(posicionYAutoy)), 3, (0, 0, 255), 5)
    return imagenUmbralizada

# Metodo para realizar threshold a la imagen escalada con TRACKBARS, ademas cambio de espacio de color de BGR A HSV#
def procesamientoImagenCalle(imagen):
    # Uso de valores utilizados en trackbars para modificacion del espacio de color HSV#
    imagen = cv.resize(imagen, (400, 400))#Se puede omitir esta línea
    hsvCalle = cv.cvtColor(imagen, cv.COLOR_BGR2HSV)
    hsv_threshold_calle = cv.inRange(hsvCalle, (low_H, low_S, low_V), (high_H, high_S, high_V))
    #negada = cv.bitwise_not(hsv_threshold_calle)
    return hsv_threshold_calle

# Metodo para la union de dos imagenes bordes mas auto con threshold
def unionAutoMasBordes(imagenAuto, imagenBordes): 
    unionImagenes = cv.absdiff(imagenBordes, imagenAuto)
    cv.imshow('frame', unionImagenes)
    

# Funcion para el movimiento del auto dependiendo de la llave pasada 
# 65361 = izquierda
# 65363 = derecha
# 32 = acelerar
# 65505 = frenar
def moverAuto(key):
    global is_pressed_left
    global is_pressed_right
    global is_pressed_shift
    global is_pressed_space
    if key == 65361:
        is_pressed_left = True
    if key == 65363:
        is_pressed_right = True
    if key == 32:
        is_pressed_space = True
    if key == 65505:
        is_pressed_shift = True

# Funcion para liberar el movimiento del auto dependiendo de la llave pasada 
# 65361 = izquierda
# 65363 = derecha
# 32 = acelerar
# 65505 = frenar
def moverAutoRelease(key):
    global is_pressed_left
    global is_pressed_right
    global is_pressed_shift
    global is_pressed_space
    if key == 65361:
        is_pressed_left = False
    if key == 65363:
        is_pressed_right = False
    if key == 32:
        is_pressed_space = False
    if key == 65505:
        is_pressed_shift = False

# Metodo para controlar al auto y la calle, para evitar salirnos de ella #
def controlDeteccionBordes2(imagenBordes):
    
    global contIzquierda
    global contDerecha  
    # Creamos un rectangulo alrededor del auto y su centroide para saber hasta donde se puede mover el auto#
    #Ancho  -----------
    posicionImin = posicionXAuto - 75
    posicionImax = posicionXAuto + 75
    #Alto |||||||||||
    posicionJmin = posicionYAutoy - 75
    # Creacion de contadores para ver ubicacion del auto 
    contIzquierda = 0
    contDerecha = 0
    # Bucles para manipulacion de pixeles #
    # Solo necesitamos recorrer la primera posicion en el alto de la imagen # 
    # en el ancho si recorremos el ancho de nuestro rectangulo generado 
    for j in range(posicionJmin, posicionJmin+1): 
        for i in range(posicionImin, posicionImax):
            
            # ahora buscados en donde existan pixeles de color blanco 
            if imagenBordes[j][i] == 255 :
                #print("j:",j , " pixel: ", imagenBordes[j][i], " i:",i)
                # si los pixeles son menores que 180 entonces estos corresponden al contador izquierda
                if i < 180 :
                    #imagenBordes = cv.circle(imagenBordes,(i,j), 2, 255, 2) 
                    contIzquierda = contIzquierda+1
                # si los pixeles son mayores o iguales que 180 entonces estos corresponden al contador derecha
                else:
                    #imagenBordes = cv.circle(imagenBordes,(i,j), 2, 255, 2) 
                    contDerecha = contDerecha +1
    print("contIzquierda: ", contIzquierda)
    print("contDerecha: ", contDerecha)
    #cv.imshow('imagenAuto', imagenAuto)
    #cv.imshow('imagenBordes', imagenBordes)                   
    

# Metodos para modificacion de valores haciendo uso de trackbars#
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
