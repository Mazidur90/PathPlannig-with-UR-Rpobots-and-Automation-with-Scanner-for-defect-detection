import threading
import functions
from RobotiqGripper import robotiq_gripper_control
from API import URCB
import time
from API import FreeScanAPIv2
combo = FreeScanAPIv2()

def workflow1():
    functions.gripper_reconnect()
    ### GET CALIBRATION DATA ###
    X0, Y0 = functions._get_tray_first_pos()
    Z_DOWN, Z_UP = functions._get_height_down(), functions._get_height_up()
    RX, RY, RZ = 0, 0, 0  # TODO: Adjust RX, RY, RZ in system config

    # functions.move_middle_point()
    for y in range(4):
        Y = Y0 + (y - 1) * 122

        for x in range(16):
            if functions._get_height_object() <= 67:
                X = X0 + (x - 1) * 20
            else:
                X = X0 + (x - 1) * 40
                x += 1
            slot_nr = (y - 1) * 16 + x
            target_down = [X, Y, Z_DOWN, RX, RY, RZ]
            target_up = [X, Y, Z_UP, RX, RY, RZ]
            functions.pick_object(target_up, target_down)

            t_place = threading.Thread(target=functions.place_object, args=(target_up, target_down))
            t_place.start()
            t_place.join()
    functions.move_home()


def workflow2():
    functions.gripper_reconnect()
    functions.scanner_initialize()

    t_scanner_create_new_project = threading.Thread(target=functions.scanner_create_new_project)

    t_scanner_create_new_project.start()

    t_scanner_create_new_project.join()

    functions.getpos()
    functions.robot_move_L([0.24, 0.016, 0.25, 2.221, -2.221, 0])
    functions.getpos()

    functions.scanner_start_scan()


    t_scanner_end_scan = threading.Thread(target=functions.scanner_end_scan, args=(1,))
    t_scanner_end_scan.start()
    t_scanner_end_scan.join()

def workflow2_positiontracker():
    print(functions.getpos())
    print(functions.jointpos())

def workflow_0():
    ### GET CALIBRATION DATA ###
    X0, Y0 = functions._get_tray_first_pos()
    Z_DOWN, Z_UP = functions._get_height_down(), functions._get_height_up()
    RX, RY, RZ = 0, 0, 0  # TODO: Adjust RX, RY, RZ in system config

    # TODO: Initialize everything here
    #functions.scanner_initialize()

    functions.move_middle_point()
    for y in range(4):
        Y = Y0 + (y - 1) * 122

        for x in range(16):
            if functions._get_height_object() <= 67:
                X = X0 + (x - 1) * 20
            else:
                X = X0 + (x - 1) * 40
                x += 1
            slot_nr = (y - 1) * 16 + x
            target_down = [X, Y, Z_DOWN, RX, RY, RZ]
            target_up = [X, Y, Z_UP, RX, RY, RZ]
            functions.pick_object(target_up, target_down)
            t_scanner_create_new_project = threading.Thread(target=functions.scanner_create_new_project)
            t_robot_move_to_scanner_view = threading.Thread(target=functions.move_scanner_view)

            t_scanner_create_new_project.start()
            t_robot_move_to_scanner_view.start()
            t_robot_move_to_scanner_view.join()
            t_scanner_create_new_project.join()

           # functions.scan()

            t_scanner_end_scan = threading.Thread(target=functions.scanner_end_scan, args=(slot_nr,))
            t_place = threading.Thread(target=functions.place_object, args=(Z_DOWN, Z_UP))

            t_scanner_end_scan.start()
            t_place.start()
            t_scanner_end_scan.join()
            t_place.join()
    functions.move_home()

def workflow4():
    #functions.robot_move_L([0.24, 0.016, 0.25, 2.221, -2.221, 0])
    #functions.robot_move_L([0.3107679187711639, -0.1818467714828139,0.0021194330594270783, -0.05919128646205727, -3.1049933434071155, -0.09273317833500225])
    #functions.robot_move_J([-0.24574071565736944, -2.069308106099264, -1.8397448698626917, -0.8498156706439417, 1.6227962970733643, 1.3660279512405396])
    #time.sleep(2)
    #####HOME_1
    functions.robot_move_L([0.31619758809463433, -0.23312765298926058, 0.25013542473016676, -3.0080415947087578, 0.8036516482750797, 0.03352609972110365])
    time.sleep(2)
    #####Target_1_Pick
    functions.robot_move_L([0.31618183649022974, -0.23309232138322464, 0.15851988390207264, -3.0079484905649383, 0.8036188679211933, 0.03347547837391625])
    time.sleep(2)
    #####HOME_1
    functions.robot_move_L([0.31619758809463433, -0.23312765298926058, 0.25013542473016676, -3.0080415947087578, 0.8036516482750797, 0.03352609972110365])
    time.sleep(2)
    #####Intermediate
    functions.robot_move_L([0.3162065505223297, -0.46947138632561164, 0.25010905428045294, -3.008054416675748, 0.8036189357161755, 0.033521924353920166])
    time.sleep(2)
    functions.scanner_initialize()
    functions.scanner_create_new_project()
    functions.scanner_start_scan()
    
    ####ScannerView
    functions.robot_move_J([-1.2616093794452112, -1.6132691542254847, -1.7333501021014612, -1.0462973753558558, 2.3757400512695312, -2.9846378008471888])
    time.sleep(2)
    functions.robot_move_J([-1.1627190748797815, -1.3662822882281702, -1.8234265486346644, -1.5486825148211878, 1.5897613763809204, -1.4632723967181605])
    time.sleep(2)
    functions.robot_move_J([-1.1626713911639612, -1.36625844637026, -1.8233664671527308, -1.5487187544452112, 1.5897494554519653, 0.6100704669952393])
    time.sleep(2)
    functions.scanner_end_scan(1)
    #####Intermediate_return
    functions.robot_move_L([0.3162065505223297, -0.46947138632561164, 0.25010905428045294, -3.008054416675748, 0.8036189357161755, 0.033521924353920166])
    time.sleep(2)
    #####BACKTO_HOME_1
    functions.robot_move_L([0.31619758809463433, -0.23312765298926058, 0.25013542473016676, -3.0080415947087578, 0.8036516482750797, 0.03352609972110365])
    time.sleep(2)

    #####Target_1_Place
    functions.robot_move_L([0.31618183649022974, -0.23309232138322464, 0.15851988390207264, -3.0079484905649383, 0.8036188679211933, 0.03347547837391625])
    time.sleep(2)
    ################################BACKTO_HOME_1_finish one scan and proceed for the next one
    functions.robot_move_L([0.31619758809463433, -0.23312765298926058, 0.25013542473016676, -3.0080415947087578, 0.8036516482750797, 0.03352609972110365])
    time.sleep(2)

    ###################Start of the second scan

    

    """
    #####Target_1
    functions.robot_move_L([0.31618183649022974, -0.23309232138322464, 0.15851988390207264, -3.0079484905649383, 0.8036188679211933, 0.03347547837391625])
    time.sleep(2)
    functions.robot_move_L([0.07562369128701589, -0.5512446195209845, 0.3301940324583008, -0.6724970714286005, -1.805122032916916, 1.8109567980581904])
    time.sleep(2)
    functions.robot_move_J([-0.36923152605165654, -1.3653243223773401, -2.0619476477252405, -1.3099730650531214, 1.5913546085357666, 4.865048885345459])
    time.sleep(2)
    
    #functions.gripper_close()

    #####MOVEBACK_HOME_1
    functions.robot_move_J([-0.7728236357318323, -1.6399005095111292, -1.730999771748678, -2.7731359640704554, -0.06119424501527959, 3.003770112991333])
    time.sleep(2)
    functions.robot_move_J([-0.7728474775897425, -1.639876667653219, -1.7310956160174769, -2.773112122212545, -0.061230007802144826, 3.6199936866760254])
    time.sleep(2)

"""



    ########HOME2




    ########TARGET2


    
    #functions.move_home()

def Scanner_operations():
    functions.scanner_initialize()
    functions.scanner_create_new_project()
    functions.scanner_start_scan()
    functions.scanner_end_scan(1)







if __name__ == "__main__":
    
    #workflow2_positiontracker()
    #workflow4()
    Scanner_operations()
    #workflow1()
    # # ur = URCB("192.168.1.200", 10, 10, 10, 10 )
    # print(ur._get_pose())
    # gr = robotiq_gripper_control.RobotiqGripper()
    # gr.connect("192.168.1.200", 63352)
    # gr.open_gripper()
    # functions.getpos()
    # functions.getpos()
    # functions.robot_move_L([0.24, 0.016, 0.25, 2.221, -2.221, 0])
    # functions.getpos()

