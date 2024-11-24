import time
from datetime import datetime

import API

import configparser

#############################
### CONFIG READ FUNCTIONS ###
#############################
def _get_system_settings(key, value):
    config_system = configparser.ConfigParser()
    config_system.read('CONFIG_SYSTEM.ini')
    return config_system.get(key, value)


def _get_calibration_settings(key, value):
    config_calibration = configparser.ConfigParser()
    config_calibration.read('CONFIG_CALIBRATION.ini')
    return config_calibration.get(key, value)

#######################
### SYSTEM SETTINGS ###
#######################
def _get_tray() -> str:
    return str(_get_calibration_settings("Tray", "side"))


def _get_tray_first_pos() -> 'tuple[float, float]':
    if _get_tray() == "A":
        return float(_get_calibration_settings("CalibrationTrayA", "x0")), float(
            _get_calibration_settings("CalibrationTrayA", "y0"))
    elif _get_tray() == "B":
        return float(_get_calibration_settings("CalibrationTrayB", "x0")), float(
            _get_calibration_settings("CalibrationTrayB", "y0"))


def _get_tray_middle_point():
    """
    :return: X, Y, Z coordinates, of middle tray
    """
    X, Y = _get_tray_first_pos()
    slots_along_X = int(_get_calibration_settings("System", "slotsAlongX"))
    slots_along_Y = int(_get_calibration_settings("System", "slotsAlongY"))
    distance_x = float(_get_calibration_settings("System", "slotsAlongX"))
    distance_y = float(_get_calibration_settings("System", "slotsAlongX"))
    X += (slots_along_X / 2) * (distance_x / 2)
    Y += (slots_along_Y / 2) * (distance_y / 2)
    Z = 300  # TODO Arrange height before testing
    return X, Y, Z


def _get_height_down() -> float:
    h_object = _get_height_object()
    Z_DOWN = h_object - 5  # TODO Arrange height before testing but 5mm is enough to grab
    return Z_DOWN


def _get_height_up() -> float:
    h_down = _get_height_down()
    h_object = _get_height_object()
    Z_UP = h_down + h_object + 45  # TODO Arrange height before testing, part should be easily operated
    return Z_UP


def _get_max_height() -> float:
    return float(_get_calibration_settings("System", "maxHeight"))


def _get_height_object():
    return float(_get_calibration_settings("Object", "objectHeight"))


def get_joints_home():
    joints = []
    for key in ['J1', 'J2', 'J3', 'J4', 'J5', 'J6']:
        joints.append(float(_get_calibration_settings('System', key)))
    return joints


###############
### GRIPPER ###
###############

gripper = API.RobotiqHandE(
    IP=str(_get_system_settings("Gripper", "IP")),
    PORT=int(_get_system_settings("Gripper", "PORT"))
)



def _gripper_has_object() -> bool:
    return gripper._has_object()


def gripper_reconnect():
    gripper.connect()
    gripper.activate()
    # if not gripper._is_connected():
    #     gripper.connect()
    # if not gripper._is_active():
    #     gripper.activate()


def gripper_open():
    """"
    h = _get_height_object()
    max_h = _get_max_height()
    if h > max_h:
        gripper.move(67)  # TODO check suitable gripper open distance
    elif h <= max_h:
        gripper.move(67)  # TODO check suitable gripper open distance
"""
    gripper.open()

def gripper_close():
    gripper.close()


def gripper_configure():
    # TODO: set force and speed here
    pass


#######################
### ROBOT INTERFACE ###
#######################

robot = API.URCB(
    _get_system_settings("Robot", "IP"),
    _get_system_settings("Robot", "speedLinear"),
    _get_system_settings("Robot", "speedJoint"),
    _get_system_settings("Robot", "accLinear"),
    _get_system_settings("Robot", "accJoint"),
    # _get_system_settings("Robot", "blend")
)

def robot_move_L(values: 'list[float]'):
    robot.move_L(values)


def robot_move_J(values: 'list[float]'):
    robot.move_J(values)


def getpos():
    pos = robot._get_pose()
    print(pos)

def jointpos():
    J_pose = robot._get_joints()
    print(J_pose)
    #print(j_pose)



#########################
### SCANNER INTERFACE ###
#########################
#
#

scanner = API.FreeScanAPIv2()

def scanner_initialize():
    scanner.Sn3DInitialize(2)
    scanner.Sn3DLaunchService()
    time.sleep(8)
    scanner.Sn3DSetScanMode(int(_get_system_settings("Scanner", "scanMode")))
    time.sleep(1)


def scanner_create_new_project():
    scanner.Sn3DNewProject(_get_system_settings("Scanner", "projectPath"),
                           int(_get_system_settings("Scanner", "scanMode")))
    time.sleep(1)
    # TODO: get issue with this function (SetScanPars); check with R&D
    scanner.Sn3DSetScanPars(True, False, False)
    time.sleep(3)
    scanner.Sn3DEnterScan(int(_get_system_settings("Scanner", "scanMode")))
    time.sleep(3)
    #scanner.Sn3DSetLaserGrade(int(_get_system_settings("Scanner", "scanLaserType")))
    scanner.Sn3DSetLaserGrade(0)
    time.sleep(1)
    scanner.Sn3DSetBrightness(int(_get_system_settings("Scanner", "scanBrightness")))
    time.sleep(1)
    scanner.Sn3DSetScanObject(int(_get_system_settings("Scanner", "scanObjectType")))
    time.sleep(1)


def scanner_start_scan():
    # scanner.Sn3DEnterScan(int(_get_system_settings("Scanner", "scanMode")))
    # time.sleep(2)
    scanner.Sn3DStartScan()
    time.sleep(10)


def scanner_end_scan(slot_nr):
    scanner.Sn3DPauseScan()
    scanner.Sn3DEndScan()
    current_time = datetime.now().strftime("%Y%m%d_%H%M")
    # TODO: Issue with Sn3DSaveMesh; check with R&D
    scanner.Sn3DSaveMesh(_get_calibration_settings("Object", "partName") + f"_{slot_nr}__{current_time}",
                         _get_system_settings("Scanner", "ascSavePath"))
    time.sleep(5)
    scanner.Sn3DEndScan()


# TODO: Implement ControlX command line functionality

##################
### OPERATIONS ###
##################

def initialize():
    gripper_reconnect()
    # scanner_initialize()


def pick_object(up, down):
    gripper_open()
    robot_move_L(up)
    robot_move_L(down)
    gripper_close()
    if _gripper_has_object() is False:
        gripper_open()
        robot_move_L(up)
        # TODO: Finish program here. Raise INFO no more part to scan
        pass
    if robot._get_safety_mode() == 2:
        # TODO: Finish program here. Raise ERROR robot emergency state
        pass
    robot_move_L(up)


def place_object(up, down):
    move_middle_point()
    robot_move_L(up)
    robot_move_L(down)
    gripper_open()
    robot_move_L(up)


def move_home():  # TODO
    robot_move_J(get_joints_home())


def move_middle_point():
    X, Y, Z = _get_tray_middle_point()
    robot_move_J(
        [X, Y, Z]
    )  # general position


def move_scanner_view():
    X, Y, Z, RX, RY, RZ = 0, 0, 0, 0, 0, 0
    robot_move_J([X, Y, Z, RX, RY, RZ])  # first position of scan path


# def scan():
#     scanner.Sn3DStartScan()
#     # TODO: Create scanning path.
#     scanner.Sn3DPauseScan()
#     pass


def if_slot_empty():
    move_home()


def if_protective_stopped():
    pass
