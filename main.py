import threading
import functions


def workflow():
    ### GET CALIBRATION DATA ###
    X0, Y0 = functions._get_tray_first_pos()
    Z_DOWN, Z_UP = functions._get_height_down(), functions._get_height_up()
    RX, RY, RZ = 0, 0, 0  # TODO: Adjust RX, RY, RZ in system config

    # TODO: Initialize everything here
    functions.scanner_initialize()

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

            functions.scan()

            t_scanner_end_scan = threading.Thread(target=functions.scanner_end_scan, args=(slot_nr,))
            t_place = threading.Thread(target=functions.place_object, args=(Z_DOWN, Z_UP))

            t_scanner_end_scan.start()
            t_place.start()
            t_scanner_end_scan.join()
            t_place.join()
    functions.move_home()
    # TODO: Release everything here


if __name__ == "__main__":
    workflow()
