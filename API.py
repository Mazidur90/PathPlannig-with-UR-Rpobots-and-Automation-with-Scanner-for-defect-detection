import configparser
import ctypes
import datetime
import json
import logging
import os
import subprocess
import time
from math import radians
from threading import Event
from psutil import process_iter
from rtde_control import RTDEControlInterface as RTDEControl
from rtde_receive import RTDEReceiveInterface as RTDEReceive
from RobotiqGripper import robotiq_gripper_control
import STRUCTURE


class FreeScanAPIv2:
    SDK_ERROR = {
        0x00000000: "SNSDK_ERR_OK",
        0x00000001: "SNSDK_ERR_NOTINITIALIZED",
        0x00000002: "SNSDK_ERR_INITIALIZEFAILED",
        0x00000003: "SNSDK_ERR_ALREADYINITIALIZED",
        0x00000004: "SNSDK_ERR_SAVEFAILED_TYPEERROR",
        0x00000005: "SNSDK_ERR_CHECKDEVICEFAILED_PLENOTRIGHT",
        0x00000006: "SNSDK_ERR_CHECKDEVICEFAILED_NODEVICEFOUND",
        0x00000007: "SNSDK_ERR_OPENORCREATSLNFAILED",
        0x00000008: "SNSDK_ERR_ENTERSCANFAILED",
        0x00000009: "SNSDK_ERR_SCANFAILED",
        0x0000000A: "SNSDK_ERR_ENDSCANFAILED",
        0x0000000B: "SNSDK_ERR_MESHFAILED",
        0x0000000C: "SNSDK_ERR_EXITSCANFAILED",
        0x0000000D: "SNSDK_ERR_CANCELSCANFAILED",
        0x0000000E: "SNSDK_ERR_SAVEFAILED",
        0x00000010: "SNSDK_ERR_CREATNEWPROJECTFAILED",
        0x00000011: "SNSDK_ERR_WORKRANGE",
        0x00000012: "SNSDK_ERR_UNIMPLEMENTED",
        0x00000013: "SNSDK_ERR_NULLFUNCTION",
        0x00000014: "SNSDK_ERR_STARTPLUGIN_FAIL",
        0x00000015: "SNSDK_ERR_NULLDATA",
        0x00000016: "SNSDK_ERR_NULLSERVICE",
        0x00000017: "SNSDK_ERR_OUTOFMEMORY",
        0x00000018: "SNSDK_ERR_UNKNOWN",
        0x00000019: "SNSDK_ERR_INVALIDINPUT",
        0x0000001A: "SNSDK_ERR_TOOFEW_SCANDATA",
        0x0000001B: "SNSDK_ERR_OPTIMIZE_POINT_FAIL",
        0x10000000: "SNSDK_ERR_PROCESSERROR"
    }

    DLL_FUNCTIONS = {
        "Sn3DCaliCalculate": "?Sn3DCaliCalculate@@YAHPEAX@Z",
        "Sn3DCaliSnapImage": "?Sn3DCaliSnapImage@@YAHPEAX@Z",
        "Sn3DCancelScan": "?Sn3DCancelScan@@YAHPEAX@Z",
        "Sn3DChangeBrightStep": "?Sn3DChangeBrightStep@@YAHPEAXH@Z",
        "Sn3DChangeScanMode": "?Sn3DChangeScanMode@@YAHPEAXH@Z",
        "Sn3DClearScan": "?Sn3DClearScan@@YAHPEAX_N@Z",
        "Sn3DCloseDevice": "?Sn3DCloseDevice@@YAHPEAX@Z",
        "Sn3DConfirmMesh": "?Sn3DConfirmMesh@@YAHPEAX@Z",
        "Sn3DConnectDevice": "?Sn3DConnectDevice@@YAHPEAX@Z",
        "Sn3DEndScan": "?Sn3DEndScan@@YAHPEAX@Z",
        "Sn3DEnterCali": "?Sn3DEnterCali@@YAHPEAX@Z",
        "Sn3DEnterScan": "?Sn3DEnterScan@@YAHPEAXW4ScanType@@@Z",
        "Sn3DEnterScanModePage": "?Sn3DEnterScanModePage@@YAHPEAX@Z",
        "Sn3DEnterScanPage": "?Sn3DEnterScanPage@@YAHPEAX@Z",
        "Sn3DExitScan": "?Sn3DExitScan@@YAHPEAX@Z",
        "Sn3DGetBrightnessRange": "?Sn3DGetBrightnessRange@@YAHPEAXAEAH1@Z",
        "Sn3DGetCurrentBrightness": "?Sn3DGetCurrentBrightness@@YAHPEAXAEAH@Z",
        "Sn3DGetCurrentLEDDutyCycle": "?Sn3DGetCurrentLEDDutyCycle@@YAHPEAXAEAH@Z",
        "Sn3DGetDeviceIsOnline": "?Sn3DGetDeviceIsOnline@@YAHPEAX@Z",
        "Sn3DGetSceneData": "?Sn3DGetSceneData@@YAHPEAUSN3D_SCENE_DATA@@@Z",
        "Sn3DGlobalOptimization": "?Sn3DGlobalOptimization@@YAHPEAX@Z",
        "Sn3DImproFramePoint": "?Sn3DImproFramePoint@@YAHPEAXPEBD@Z",
        "Sn3DInitialize": "?Sn3DInitialize@@YAHPEAPEAXH@Z",
        "Sn3DMesh": "?Sn3DMesh@@YAHPEAXPEAUFreeScanMeshPar@@@Z",
        "Sn3DNewProject": "?Sn3DNewProject@@YAHPEAXPEAUNewProject@@@Z",
        "Sn3DOpenOrCreateSolution": "?Sn3DOpenOrCreateSolution@@YAHPEAXPEAUOpenOrCreateSln@@@Z",
        "Sn3DOpenProject": "?Sn3DOpenProject@@YAHPEAXPEBDW4ScanType@@@Z",
        "Sn3DPauseScan": "?Sn3DPauseScan@@YAHPEAX@Z",
        "Sn3DPreviewScan": "?Sn3DPreviewScan@@YAHPEAX@Z",
        "Sn3DReConnectDevice": "?Sn3DReConnectDevice@@YAHPEAX@Z",
        "Sn3DRegisterCallback": "?Sn3DRegisterCallback@@YAHP6AXHHPEAX_K0@Z0@Z",
        "Sn3DRegisterSceneDataCallback": "?Sn3DRegisterSceneDataCallback@@YAHP6AXPEAX@Z0@Z",
        "Sn3DRelease": "?Sn3DRelease@@YAHPEAPEAX@Z",
        "Sn3DSaveData": "?Sn3DSaveData@@YAHPEAXPEAUSaveData@@@Z",
        "Sn3DSaveMesh": "?Sn3DSaveMesh@@YAHPEAXPEAUFreeSaveMeshPar@@@Z",
        "Sn3DSendMessage": "?Sn3DSendMessage@@YAHPEAXPEBD111_KPEADPEA_K@Z",
        "Sn3DSetBrightness": "?Sn3DSetBrightness@@YAHPEAXH@Z",
        "Sn3DSetCalibMode": "?Sn3DSetCalibMode@@YAHPEAXH@Z",
        "Sn3DSetCameraPositionCallBack": "?Sn3DSetCameraPositionCallBack@@YAHPEAXP6AXPEAUSn3DCameraPosition@@0@Z0@Z",
        "Sn3DSetCurrentLEDDutyCycle": "?Sn3DSetCurrentLEDDutyCycle@@YAHPEAXH@Z",
        "Sn3DSetDeviceBrightness": "?Sn3DSetDeviceBrightness@@YAHPEAXPEAUDeviceBrightness@@@Z",
        "Sn3DSetDeviceEventCallBack": "?Sn3DSetDeviceEventCallBack@@YAHPEAXP6AXW4DeviceEvent@@0@Z0@Z",
        "Sn3DSetDeviceStatusCallBack": "?Sn3DSetDeviceStatusCallBack@@YAHPEAXP6AXPEAUDeviceStatus@@0@Z0@Z",
        "Sn3DSetEnablePseudoColor": "?Sn3DSetEnablePseudoColor@@YAHPEAX_N@Z",
        "Sn3DSetFrameCountCallBack": "?Sn3DSetFrameCountCallBack@@YAHPEAXP6AXH0@Z0@Z",
        "Sn3DSetFrameRateCallBack": "?Sn3DSetFrameRateCallBack@@YAHPEAXP6AXH0@Z0@Z",
        "Sn3DSetImagasCallBack": "?Sn3DSetImagasCallBack@@YAHPEAXP6AXHPEBEHHH0@Z0@Z",
        "Sn3DSetIncreasePointCloudCallBack": "?Sn3DSetIncreasePointCloudCallBack@@YAHPEAXP6AXPEAUSn3DIncreasePointCloud@@0@Z0@Z",
        "Sn3DSetIsHighSpeed": "?Sn3DSetIsHighSpeed@@YAHPEAX_N@Z",
        "Sn3DSetIsIncFramework": "?Sn3DSetIsIncFramework@@YAHPEAX_N@Z",
        "Sn3DSetLEDBrightness": "?Sn3DSetLEDBrightness@@YAHPEAXH@Z",
        "Sn3DSetLaserGrade": "?Sn3DSetLaserGrade@@YAHPEAXH@Z",
        "Sn3DSetMaskBackGround": "?Sn3DSetMaskBackGround@@YAHPEAXH_N@Z",
        "Sn3DSetPointCountCallBack": "?Sn3DSetPointCountCallBack@@YAHPEAXP6AXH0@Z0@Z",
        "Sn3DSetScanDistCallBack": "?Sn3DSetScanDistCallBack@@YAHPEAXP6AXN0@Z0@Z",
        "Sn3DSetScanMode": "?Sn3DSetScanMode@@YAHPEAXH@Z",
        "Sn3DSetScanObject": "?Sn3DSetScanObject@@YAHPEAXH@Z",
        "Sn3DSetScanPars": "?Sn3DSetScanPars@@YAHPEAXPEAUScanPars@@@Z",
        "Sn3DSetTooFlatStatusCallBack": "?Sn3DSetTooFlatStatusCallBack@@YAHPEAXP6AX_N0@Z0@Z",
        "Sn3DSetTrackLostStatusCallBack": "?Sn3DSetTrackLostStatusCallBack@@YAHPEAXP6AX_N0@Z0@Z",
        "Sn3DSetWholePointCloudCallBack": "?Sn3DSetWholePointCloudCallBack@@YAHPEAXP6AXPEAUSn3DPointCloud@@@Z0@Z",
        "Sn3DSetWorkRange": "?Sn3DSetWorkRange@@YAHPEAXMM@Z",
        "Sn3DStartProcessVideoData": "?Sn3DStartProcessVideoData@@YAHPEAX@Z",
        "Sn3DStartScan": "?Sn3DStartScan@@YAHPEAX@Z",
        "Sn3DStopCalib": "?Sn3DStopCalib@@YAHPEAXH@Z",
        "Sn3DStopProcessVideoData": "?Sn3DStopProcessVideoData@@YAHXZ",
        "Sn3DUndoMesh": "?Sn3DUndoMesh@@YAHPEAX@Z"
    }

    def __init__(self):
        """ Constructor

        :param SDKCWrapper: dsakjdhska aksjfhca

        """
        self.DEVICE_HANDLE = None
        self.SDKCWrapper = ctypes.CDLL(self._get_sdk_config("Path", "dllPath"))
        self.HSN3DSDKSERVICE = ctypes.c_void_p
        self.CALLBACKFUNC = ctypes.CFUNCTYPE(None, ctypes.c_int, ctypes.c_int, ctypes.c_void_p, ctypes.c_size_t,
                                             ctypes.c_void_p)

        # Callback events
        self.SDK_Callback_Event_EnterScan = Event()
        self.SDK_Callback_Event_NewProject = Event()
        self.SDK_Callback_Event_Init = Event()
        self.SDK_Callback_Event_PauseScan = Event()
        self.SDK_Callback_Event_Exit = Event()
        self.SDK_Callback_Event_Save = Event()
        self.SDK_Callback_Event_EndScan = Event()

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        log_filename = datetime.datetime.now().strftime('SDK_%Y-%m-%d_%H-%M-%S.log')
        #log_file_path = os.path.join("log/", log_filename)
        self.file_handler = logging.FileHandler('freescan.log')
        self.file_handler.setLevel(logging.DEBUG)
        self.console_handler = logging.StreamHandler()
        self.console_handler.setLevel(logging.INFO)
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.file_handler.setFormatter(self.formatter)
        self.console_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)
        self.logger.addHandler(self.console_handler)
        ### Robot Parameters
        self.SPEED_J, self.SPEED_L = 0.5,0.2

    def _get_sdk_config(self, key, value):
        config = configparser.ConfigParser()
        config.read('CONFIG_SDK.ini')
        return config.get(key, value)

    def _handle_sdk_response(self, result, function):
        self.logger.info(f"{function} ")
        if result == 0:
            self.logger.info(f"{function} function successfully received from FreeScan SDK. (result=0)")
            self.logger.info(f"{function} function starts...")
            if function == "Sn3DInitialize":
                pass
            elif function == "Sn3DSetScanMode":
                self.SDK_Callback_Event_EnterScan.wait()
            elif function == "Sn3DNewProject":
                self.SDK_Callback_Event_NewProject.wait()
            elif function == "Sn3DEndScan":
                self.SDK_Callback_Event_EndScan.wait()
            elif function == "Sn3DPauseScan":
                self.SDK_Callback_Event_PauseScan.wait()
            elif function == "Sn3DSaveMesh":
                self.SDK_Callback_Event_Save.wait()

            else:
                self.logger.info(f"{function} has no need_wait.")
            self.logger.info(f"{function} function successfully executed by FreeScan SDK.")
        elif result == 1:
            self.logger.error(f"{function} function failed to receive. (result=1)")
        else:
            self.logger.error(f"{function} failed with error code: {result}")
        return result

    def _handle_function(self, name: str, argument_types: list, result_type, *args, **kwargs):
        func = getattr(self.SDKCWrapper, self.DLL_FUNCTIONS.get(name))
        func.argtypes = argument_types
        func.restype = result_type
        result = func(self.DEVICE_HANDLE, *args)
        self._handle_sdk_response(result, name)

    # TODO: in future it might be needed to integrate this interface to have more flexibility
    # def Sn3DSendMessage(self, ):
    #     func = getattr(self.SDKCWrapper, "?Sn3DSendMessage@@YAHPEAXPEBD111_KPEADPEA_K@Z")
    #     func.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p,
    #                      ctypes.c_size_t, ctypes.c_char_p, ctypes.POINTER(ctypes.c_size_t)]
    #     func.restype = ctypes.c_int
    #     result = func(self.DEVICE_HANDLE, szVersion, szMsgType, szZMQTopic, pMsg, stLen, pResult, pstResultLen)
    #     # TODO
    #     if result == 0:
    #         print("EnterScan succeeded.")
    #         self.SDK_Callback_Event_EnterScan.wait()
    #         print("EnterScan confirmed.")
    #     else:
    #         print(f"EnterScan failed with error code: {result}")
    #     return result

    def Sn3DLaunchService(self):
        function = "Sn3DLaunchService"
        path = self._get_sdk_config("Path", "freescanExePath")
        for proc in process_iter(attrs=['name']):
            if proc.name() == 'FreeScan.exe':
                self.logger.error(f"{function} function can not start, FreeScan.exe is already running.")
                return None
        if not os.path.exists(path):
            self.logger.error(f"{function} function can not start, FreeScan.exe Executable not found at: {path}.")
            return None
        process_dir = os.path.dirname(path)
        process = subprocess.Popen(path, cwd=process_dir)
        self.SDK_Callback_Event_Init.wait()
        self.logger.info(f"{function} completed. Software is open.")

        return process

    def Sn3DInitialize(self, device_type: int) -> bool:
        """
        Initialize the SDK.

        :param device_type: The type of device. 1 for UE Pro, 2 for Combo.
        :return: None
        """
        hService = self.HSN3DSDKSERVICE()
        function = "Sn3DInitialize"
        func = getattr(self.SDKCWrapper, "?Sn3DInitialize@@YAHPEAPEAXH@Z")
        func.argtypes = [ctypes.POINTER(self.HSN3DSDKSERVICE), ctypes.c_int]
        func.restype = ctypes.c_int
        result = func(ctypes.byref(hService), device_type)
        time.sleep(1)
        if result == 0:
            self.logger.info(f"{function} function successfully received from FreeScan SDK. (result=0)")
            self.DEVICE_HANDLE = hService
            self.SDK_Register_Callback(self.SDK_Wrapper_Callback)
        else:
            print(f"Initialization failed with error code: {result}")
            self.logger.error(f"{function} function failed with error code: {result}.")
            return False
        return True

    def Sn3DSetScanMode(self, scan_mode: int) -> None:
        """
        Set the scanning mode in the Enter Scan page.

        :param scan_mode: The scanning mode. 0 for laser, 2 for IR.
        :return: None
        """
        self._handle_function("Sn3DSetScanMode",
                              [ctypes.c_void_p, ctypes.c_int],
                              ctypes.c_int,
                              scan_mode)

    def Sn3DNewProject(self, project_path: str, scan_mode: int):
        """
        Create a new project.

        Call this function when in the Create/Open Project page or anytime after.

        :param project_path: The path where the project will be saved.
        :param scan_mode: The scan mode. 0 for laser, 2 for IR.
        :return: None
        """
        LPNewProject = ctypes.POINTER(STRUCTURE.STR_NEWPROJECT)
        newProject = STRUCTURE.STR_NEWPROJECT(
            szSlnDirPath=project_path.encode(),
            iScanMode=scan_mode
        )
        self._handle_function("Sn3DNewProject",
                              [ctypes.c_void_p, LPNewProject],
                              ctypes.c_int,
                              ctypes.byref(newProject)
                              )

    def Sn3DEnterScan(self, scan_mode: int):
        func = getattr(self.SDKCWrapper, "?Sn3DEnterScan@@YAHPEAXW4ScanType@@@Z")
        func.argtypes = [ctypes.c_void_p, ctypes.c_int]
        func.restype = ctypes.c_int
        result = func(self.DEVICE_HANDLE, scan_mode)
        if result == 0:
            print("EnterScan succeeded.")
            self.SDK_Callback_Event_EnterScan.wait()
            print("EnterScan confirmed.")
        else:
            print(f"EnterScan failed with error code: {result}")
        return result

    # def Sn3DStartScan(self) -> None:
    #     self._handle_function("Sn3DStartScan",
    #                           [ctypes.c_void_p],
    #                           ctypes.c_int
    #                           )
        
    def Sn3DStartScan(self):
        func = getattr(self.SDKCWrapper, "?Sn3DStartScan@@YAHPEAX@Z")
        func.argtypes = [ctypes.c_void_p]
        func.restype = ctypes.c_int
        result = func(self.DEVICE_HANDLE)
        if result == 0:
            print("StartScan succeeded.")
            # self.SDK_Callback_Event_StartScan.wait()
            print("StartScan confirmed.")
        else:
            print(f"StartScan failed with error code: {result}")
        return result

    def Sn3DPauseScan(self):
        self._handle_function("Sn3DPauseScan",
                              [ctypes.c_void_p],
                              ctypes.c_int
                              )

    def Sn3DCancelScan(self):
        self._handle_function("Sn3DCancelScan",
                              [ctypes.c_void_p],
                              ctypes.c_int
                              )

    def Sn3DEndScan(self) -> None:
        self._handle_function("Sn3DEndScan",
                              [ctypes.c_void_p],
                              ctypes.c_int
                              )

    def Sn3DSetScanPars(self, scan_point_cloud: bool, scan_markers: bool, scan_photogrammetry: bool):
        """

        :param scan_photogrammetry:
        :param scan_markers:
        :param scan_point_cloud:
        :return:
        """
        LPScanPars = ctypes.POINTER(STRUCTURE.STR_SCANPARS)
        scanParameters = STRUCTURE.STR_SCANPARS(
            scanPointCloud=False,
            scanMarkers=False,
            scanPhotographic=False
        )
        scanParameters = STRUCTURE.STR_SCANPARS(
            scanPointCloud=scan_point_cloud,
            scanMarkers=scan_markers,
            scanPhotographic=scan_photogrammetry
        )
        self._handle_function("Sn3DSetScanPars",
                              [ctypes.c_void_p, LPScanPars],
                              ctypes.c_int,
                              ctypes.byref(scanParameters)
                              )

    def Sn3DSetBrightness(self, level: int) -> None:
        """
        Set the brightness level of the scanner.

        :param level: The level of brightness in the range 0-17.
        :return: None
        """
        self._handle_function("Sn3DChangeBrightStep",
                              [ctypes.c_void_p, ctypes.c_int],
                              ctypes.c_int,
                              level)

    def Sn3DSetScanObject(self, index: int) -> None:
        """
        Set the scan object type.

        :param index: The index representing the scan object type.
                      0 for normal, 1 for reflective, 2 for black.
        :return: None
        """
        self._handle_function("Sn3DSetScanObject",
                              [ctypes.c_void_p, ctypes.c_int],
                              ctypes.c_int,
                              index)

    def Sn3DSetLaserGrade(self, index) -> None:
        """
        Set the scan object type.

        :param index: The index representing the scan object type.
                      0 for cross lines, 1 for parallel lines, 2 for single line.
        :return: None
        """
        self._handle_function("Sn3DSetLaserGrade",
                              [ctypes.c_void_p, ctypes.c_int],
                              ctypes.c_int,
                              int(index))

    def Sn3DSaveMesh(self, file_name: str, folder_path: str):
        """
        Save the scanning data and specify the format to save.

        :param file_name: The name under which the data will be saved.
        :param folder_path: The path where the data will be saved.
        :return: None
        """
        LPFreeSaveMeshPar = ctypes.POINTER(STRUCTURE.STR_SAVEPARS)
        saveParameters = STRUCTURE.STR_SAVEPARS(
            fileName=file_name.encode(),
            folderPath=folder_path.encode(),
            format="10000000".encode(),
            method="save".encode(),
            postpageVisible=True,
            saveAscFile=1,
            saveStlFile=0,
            saveObjFile=0,
            savePlyFile=0,
            saveP3File=0,
            save3MfFile=0,
            saveTxtFile=0,
            saveCsvFile=0
        )
        self._handle_function("Sn3DSaveMesh",
                              [ctypes.c_void_p, LPFreeSaveMeshPar],
                              ctypes.c_int,
                              ctypes.byref(saveParameters)
                              )

        # func = getattr(self.SDKCWrapper, "?Sn3DSetScanPars@@YAHPEAXPEAUScanPars@@@Z")
        # func.argtypes = [ctypes.c_void_p, LPFreeSaveMeshPar]
        # func.restype = ctypes.c_int
        # saveParameters = STRUCTURE.STR_SAVEPARS(
        #     fileName=file_name.encode(),
        #     folderPath=folder_path.encode(),
        #     format=r"saveAscFile",
        #     method=r"save",
        #     postpageVisible=True,
        #     saveAscFile=True,
        #     saveStlFile=False,
        #     saveObjFile=False,
        #     savePlyFile=False,
        #     saveP3File=False,
        #     save3MfFile=False,
        #     saveTxtFile=False,
        #     saveCsvFile=False
        # )
        # result = func(self.DEVICE_HANDLE, ctypes.byref(saveParameters))
        # if result == 0:
        #     print("SaveMesh succeeded.")
        #     self.SDK_Callback_Event_Save.wait()
        #     print("SaveMesh confirmed.")
        # else:
        #     print(f"SaveMesh failed with error code: {result}")
        # return result

    def SDK_Wrapper_Callback(self, iEventType, iExtendData, pData, stDataLen, pUserData):
        if pData and stDataLen > 0:
            buffer = ctypes.cast(pData, ctypes.POINTER(ctypes.c_char * stDataLen)).contents
            data_bytes = bytes(buffer)
            data_str = data_bytes.decode('utf-8')
            try:
                data_json = json.loads(data_str)
                # print(data_json)
                if data_json.get('cmd') == 'showMaximized':
                    self.SDK_Callback_Event_Init.set()
                elif data_json.get('cmd') == 'sdkScanPageSwitched':
                    self.SDK_Callback_Event_EnterScan.set()
                elif data_json.get('cmd') == 'newProjectFinish':
                    self.SDK_Callback_Event_NewProject.set()
                elif data_json.get('cmd') == 'generatePointCloudResult' and data_json.get('result') == 0:
                    self.SDK_Callback_Event_EndScan.set()
                elif data_json.get('cmd') == 'renderFinished':
                    self.SDK_Callback_Event_PauseScan.set()
                elif data_json.get('method') == 'saveMeshFinished' and data_json.get('Result') == '0':
                    self.SDK_Callback_Event_Save.set()

                # add other functiosn

                # elif data_json.get('cmd') == 'quitApp':
                #    self.SDK_Callback_Event_Exit.set()

            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                print(f"Raw data: {data_str}")
        else:
            print("No data received")

    def SDK_Register_Callback(self, callback_func):
        register_callback_func = getattr(self.SDKCWrapper, "?Sn3DRegisterCallback@@YAHPEAXP6AXHH0_K0@Z0@Z")
        register_callback_func.argtypes = [ctypes.c_void_p, self.CALLBACKFUNC, ctypes.c_void_p]
        register_callback_func.restype = ctypes.c_int
        c_callback = self.CALLBACKFUNC(callback_func)
        self._callback_ref = c_callback
        result = register_callback_func(self.DEVICE_HANDLE, c_callback, None)
        time.sleep(1)
        if result == 0:
            self.logger.info("Callback registered successfully.")
        else:
            self.logger.error(f"Callback registration failed with error code: {result}")



########################################################################################################################

########################################################################################################################

class URCB:
    def __init__(self, IP, speed_linear, speed_joint, acc_linear, acc_joint):
        self.IP = str(IP)
        self.SPEED_L = speed_linear
        self.SPEED_J = speed_joint
        self.ACC_L = acc_linear
        self.ACC_J = acc_joint
        # self.BLEND = blend
        # self.URControl = RTDEControl(self.IP, 500, RTDEControl.FLAG_VERBOSE | RTDEControl.FLAG_UPLOAD_SCRIPT)
        # self.URReceive = RTDEReceive.RTDEReceiveInterface(self.IP)
        # 创建RTDEControlInterface实例
        self.URControl = RTDEControl(self.IP)
        # 创建RTDEReceiveInterface实例
        self.URReceive = RTDEReceive(self.IP)


    def _convert_degrees_to_radians(self, degrees_list):
        return [radians(angle) for angle in degrees_list]

    def _is_joints_within_safety_limits(self, joints_list):
        return self.URControl.isJointsWithinSafetyLimits(joints_list)

    def _is_pose_within_safety_limits(self, pose_list) -> bool:
        return self.URControl.isPoseWithinSafetyLimits(pose_list)

    def _is_ur_connected(self) -> bool:
        return self.URControl.isConnected()

    def _get_safety_mode(self) -> int:
        return int(self.URReceive.getSafetyMode())

    def _get_joints(self) -> 'list[float]':
        return self.URReceive.getActualQ()

    def _get_pose(self) -> 'list[float]':
        return self.URReceive.getActualTCPPose()
        # return self.URReceive.getTargetTCPPose()

    
    #
    # def move_L(self, targetL: list[float]):
    #     if self._is_joints_within_safety_limits(targetL):
    #         return self.URControl.moveL(targetL, self.SPEED_L, self.ACC_L)
    #     else:
    #         return False


    def move_L(self, targetL: 'list[float]'):
        if self._is_joints_within_safety_limits(targetL):
            return self.URControl.moveL(targetL,0.5, 0.2)
        else:
            return False

    def move_J(self, targetJ: 'list[float]'):
        if self._is_joints_within_safety_limits(targetJ):
            return self.URControl.moveJ(targetJ, 0.5, 0.2)
        else:
            return False

    def move_J_path(self, targetsJ):
        pass



########################################################################################################################

########################################################################################################################


class RobotiqHandE:
    def __init__(self, IP: str, PORT: int):
        self.IP = IP
        self.PORT = PORT
        self.gripper = robotiq_gripper_control.RobotiqGripper()
        self.connect()
        # if not self.gripper.is_active():
        #     self.gripper.activate()

    # def __init__(self):
    #     self.IP = "192.168.1.200"
    #     self.PORT = 63352
    #     self.gripper = robotiq_gripper_control.RobotiqGripper()
    #     self.connect()
    #     if not self.gripper.is_active():
    #         self.gripper.activate()

    def _is_connected(self) -> bool:
        if self.gripper.GripperStatus(3):
            return True
        else:
            return False

    def _is_active(self) -> bool:
        return self.gripper.is_active()

    def _has_object(self) -> bool:
        if self.gripper.ObjectStatus(2):
            return True
        else:
            return False

    def connect(self):
        self.gripper.connect(self.IP, self.PORT)
        if not self._is_connected():
            self.gripper.connect(self.IP, self.PORT)

    def disconnect(self):
        self.gripper.disconnect()

    def activate(self):
        if not self._is_active():
            self.gripper.activate()

    def open(self):
        self.gripper.move_and_wait_for_pos(0, 255, 255)

    def close(self):
        self.gripper.move_and_wait_for_pos(255, 255, 255)

    def move(self, value: int):  # value between 0-100
        if value < 0 or value > 100:
            raise ValueError("Input value must be between 0 and 100")
        scaled_value = int(value * 255 / 100)
        scaled_value = max(0, min(scaled_value, 255))
        self.gripper.move_and_wait_for_pos(scaled_value, 255, 255)

    def set_force(self, value: int):  # TODO not sure of this function - TEST it.
        if value < 0 or value > 100:
            raise ValueError("Input value must be between 0 and 100")
        scaled_value = int(value * 255 / 100)
        scaled_value = max(0, min(scaled_value, 255))
        self.gripper.FOR = scaled_value

    def set_speed(self, value: int):  # TODO not sure of this function - TEST it.
        if value < 0 or value > 100:
            raise ValueError("Input value must be between 0 and 100")
        scaled_value = int(value * 255 / 100)
        scaled_value = max(0, min(scaled_value, 255))
        self.gripper.SPE = scaled_value



########################################################################################################################

########################################################################################################################


# TODO: Implement ControlX command line interface
class ControlX:
    def __init__(self):
        pass
