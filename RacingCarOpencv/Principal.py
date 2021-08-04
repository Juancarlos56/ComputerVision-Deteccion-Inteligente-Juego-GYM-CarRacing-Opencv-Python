import gym
from common_functions import process_state_image
import cv2 as cv
import PlayCarMethods 
from time import time
#import pyautogui
import numpy as np

if __name__ == '__main__':
    
    # Cargar de entorno de juego Car Racing en su version 0# 
    env = gym.make('CarRacing-v0')
    env.STATE_W = 400
    env.STATE_H = 400
    print(" env.STATE_W ", env.STATE_W)
    # inicio del juego almacenamos en una variable la carga del entorno # 
    state = env.reset()
    # Creacion de ventana la modificacion del espacio de color HSV
    cv.namedWindow('frame', cv.WINDOW_NORMAL)
    #cv.namedWindow('imagenAuto', cv.WINDOW_AUTOSIZE)
    #cv.namedWindow('imagenBordes', cv.WINDOW_AUTOSIZE)
    # Creacion de ventana para la imagen del juego  
    cv.namedWindow('imagenJuego', cv.WINDOW_NORMAL)
    
    # Recibir eventos del teclado al momento de precionar alguna techa y liberarla #
    env.unwrapped.viewer.window.on_key_press = PlayCarMethods.key_press
    env.unwrapped.viewer.window.on_key_release = PlayCarMethods.key_release

    # Creacion de trackbars para la manipulacion del espacio de color HSV 
    # Llamada a los metodos de cada espacio de color para la modificacion de los minimos valores para HSV
    cv.createTrackbar("low_H", 'frame' , PlayCarMethods.low_H, 180, PlayCarMethods.on_low_H_thresh_trackbar)
    cv.createTrackbar("low_S", 'frame' , PlayCarMethods.low_S, 255, PlayCarMethods.on_low_S_thresh_trackbar)
    cv.createTrackbar("low_V", 'frame' , PlayCarMethods.low_V, 255, PlayCarMethods.on_low_V_thresh_trackbar)
    # Llamada a los metodos de cada espacio de color para la modificacion de los maximos valores para HSV
    cv.createTrackbar("high_H", 'frame' , PlayCarMethods.high_H, 180, PlayCarMethods.on_high_H_thresh_trackbar)
    cv.createTrackbar("high_S", 'frame' , PlayCarMethods.high_S, 255, PlayCarMethods.on_high_S_thresh_trackbar)
    cv.createTrackbar("high_V", 'frame' , PlayCarMethods.high_V, 255, PlayCarMethods.on_high_V_thresh_trackbar)
    
    cont = 0
    total_recompensa = 0
    tiempo_transcurrido = 0

    # Tomada del tiempo para el video 
    start_time = time()
    # Generacion de un video .avi de la ventana del juego
    guardarVideo = cv.VideoWriter('videoImagenJuego.avi',cv.VideoWriter_fourcc(*'XVID'),60.0,(400,400))

    # Bucle para leer el entorno hasta que el usuario presione escape para salir del juego
    while not PlayCarMethods.presionar_esc:
        # Cargamos la nueva imagen del entorno para visualizarla 
        env.render()
        # Llamada al metodo Lectura del juego para obtener la imagen del juego 
        imagenJuego = PlayCarMethods.lecturaImagenJuego(state)
        # Presentacion de la imagen del juego en ventana 
        cv.imshow('imagenJuego', imagenJuego)
        # Llamada al metodo de procesamiento, retorno de imagen umbralizada de la parte del Auto
        imagenUmbralizadaAuto = PlayCarMethods.procesamientoImagenOPENCV(state)
        # Obtencion del centro de masa del auto punto en donde se encuentra el auto
        PlayCarMethods.obtencionCentroDeMasaAuto(imagenUmbralizadaAuto)
        # Graficacion del centro del auto 
        imagenUmbralizadaAuto = PlayCarMethods.graficaDeCentroideImagen(imagenUmbralizadaAuto)
        # Obtencion de imagen umbralizada, solo calles 
        imagenUmbralizadaCalle = PlayCarMethods.procesamientoImagenCalle(state)
        # Union de las imagenes umbralizadas tanto auto como calles para visualizacion
        PlayCarMethods.unionAutoMasBordes(imagenUmbralizadaAuto, imagenUmbralizadaCalle)
        # Obtencion de puntos blancos tanto en izquierda como derecha entre las esquinas definidas del auto
        PlayCarMethods.controlDeteccionBordes2(imagenUmbralizadaCalle)
        
        # Entrada al modo de juego automatico, el usuario debe de presionar enter 
        if (PlayCarMethods.is_pressed_enter == True):
            # Obtencion del valor absoluto de la resta entre los valores blancos entre izquierda y derecha             
            diferencia = abs(PlayCarMethods.contIzquierda - PlayCarMethods.contDerecha)
            print("Distancia: ", diferencia)
            
            # Comparacion: el lado izquierdo es mayor que el derecho y ademas el valor absoluto debe superar 
            # la distancia de 25 para que el auto se mueva hacia el lado derecho 
            if (PlayCarMethods.contIzquierda > PlayCarMethods.contDerecha and diferencia > 25):
                # Mover el auto hacia el lado derecho
                PlayCarMethods.moverAuto(65363)
                print("----------Mover a la derecha-----------")
                
                
            # Comparacion: el lado derecho es mayor que el izquierdo y ademas el valor absoluto debe superar 
            # la distancia de 25 para que el auto se mueva hacia el lado izquierdo    
            if (PlayCarMethods.contDerecha > PlayCarMethods.contIzquierda and diferencia > 25):
                # Mover el auto hacia el lado izquierdo
                PlayCarMethods.moverAuto(65361)
                print("----------Mover a la izquierda-----------")

            
            # Llamada al metodo para actualizacion de valores, volante, gas, y sistemas de frenos
            PlayCarMethods.update_action()
            # Creacion de un arreglo en donde se va a obtiene los valores actualizados del volante, gas, y sistemas de frenos 
            action = [PlayCarMethods.steering_wheel, PlayCarMethods.gas, PlayCarMethods.break_system]
            # Llamada al metodo de gym para la modificacion de la accion del carro 
            state, reward, done, info = env.step(action)
            cont += 1
            total_recompensa += reward
            print('Accion :[{:+.1f}, {:+.1f}, {:+.1f}] Recompensa: {:.3f}'.format(action[0], action[1], action[2], reward))
            PlayCarMethods.moverAutoRelease(65363)
            PlayCarMethods.moverAutoRelease(65361)
        else:   
            # Juego haciendo uso del teclado, no automizacion  
            PlayCarMethods.update_action()
            action = [PlayCarMethods.steering_wheel, PlayCarMethods.gas, PlayCarMethods.break_system]
            state, reward, done, info = env.step(action)
            cont += 1
            total_recompensa += reward
            print('Accion :[{:+.1f}, {:+.1f}, {:+.1f}] Recompensa: {:.3f}'.format(action[0], action[1], action[2], reward))
            
        # Verificacion si se ha terminado el espacio de juego 
        # Si se termino se restaura el juego desde un inicio 
        if done:
            print("Restart game after {} timesteps. Total Reward: {}".format(cont, total_recompensa))
            cont = 0
            total_recompensa = 0
            state = env.reset()
            continue
            
        
       
        # Escribir video de la ventana imagen de juego
        guardarVideo.write(imagenJuego)
        # Recuperacion del tiempo 
        tiempo_transcurrido = time() - start_time
        print("Tiempo terminado: %0.10f segundos." % tiempo_transcurrido)
        # Obtencion de un limite de tiempo transcurrido para dejar de grabar el video
        if(tiempo_transcurrido >= 60 ):
            # Imprension del tiempo real 
            print("Tiempo terminado: %0.10f segundos." % tiempo_transcurrido)
            break
    # Terminar de cerrar el entorno de gym
    env.close()
