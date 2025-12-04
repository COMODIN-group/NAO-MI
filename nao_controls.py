#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

"""Example: Use run Method"""

import qi
import argparse
import sys
import time

def connect(session, ip, port):
    
    try:
        session.connect("tcp://" + ip + ":" + str(port))
        return True
    except RuntimeError:
        return False

def play_sound(session, eng, ip, port, sound):
    
    session.connect("tcp://" + ip + ":" + str(port))
    
    # Get the service ALAnimationPlayer.
    animation_player_service = session.service("ALAnimationPlayer")

    
    if eng:
        if sound == 'inicio':
            future = animation_player_service.run("nao_moves-af3dd1/Start")
        elif sound == 'acomenzar':
            future = animation_player_service.run("nao_moves-af3dd1/Letsbegin")
        elif sound == 'fin':
            future = animation_player_service.run("nao_moves-af3dd1/End")
        else:
            print 'Sonido no reconocido'
    else:
        if sound == 'inicio':
            animation_player_service.run("nao_moves-af3dd1/Inicio")
        elif sound == 'acomenzar':
            animation_player_service.run("nao_moves-af3dd1/Vamosacomenzar")
        elif sound == 'fin':
            animation_player_service.run("nao_moves-af3dd1/Fin")
        else:
            print 'Sonido no reconocido'
    

def move_arms(session, ip, port, move):
    """
    This example uses the run method.
    """

    session.connect("tcp://" + ip + ":" + str(port))
    
    # Get the service ALAnimationPlayer.
    animation_player_service = session.service("ALAnimationPlayer")

    if move == 'both':
        animation_player_service.run("nao_moves-af3dd1/Both_up")
    elif move == 'left':
        animation_player_service.run("nao_moves-af3dd1/Left_up")
    elif move == 'right':
        animation_player_service.run("nao_moves-af3dd1/Right_up")
    elif move == 'ready':
        animation_player_service.run("nao_moves-af3dd1/okey")
    elif move == 'rest':
        motion_service = session.service("ALMotion")
        motion_service.rest()
    elif move == 'wakeup':
        motion_service = session.service("ALMotion")
        motion_service.wakeUp()
    else:
        print 'Movimiento no reconocido'
        
                          
    # play an animation, this will return when the animation is finished
    # animation_player_service.run("nao_moves-af3dd1/Both_up")
    #time.sleep(5)
    #animation_player_service.run("nao_moves-af3dd1/Left_up")
    #time.sleep(5)
    #animation_player_service.run("nao_moves-af3dd1/Right_up")

    # play an animation, this will return right away
    #future = animation_player_service.run("animations/Stand/Gestures/Hey_1", _async=True)
    # wait the end of the animation
    #future.value()

    # play an animation, this will return right away
    #future = animation_player_service.run("animations/Stand/Gestures/Hey_1", _async=True)
    # stop the animation
    #future.cancel()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type=int, default=0,
                        help="Check: 0, Sound: 1, Move: 2")
    parser.add_argument("--move", type=str, default='both',
                        help="Move to execute")
    parser.add_argument("--sound", type=str, default='inicio',
                        help="Sound to play")
    parser.add_argument("--english", type=bool, default=False,
                        help="False: Spanish, True: English")
    parser.add_argument("--ip", type=str, default="192.168.1.101",
                        help="Robot IP address. On robot or Local Naoqi: use '192.168.1.101'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")

    args = parser.parse_args()
    session = qi.Session()

    if args.mode == 0:
        flag = connect(session, args.ip, args.port)
        print flag
    elif args.mode == 1:
        play_sound(session, args.english, args.ip, args.port, args.sound)
    else:
        move_arms(session, args.ip, args.port, args.move)
    
