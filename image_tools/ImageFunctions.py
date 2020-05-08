import cv2
from image_tools.QR_Reader import QR_Scanner, QR_Scanner_visualized
from pyueye import ueye
import time
from image_tools.pyueye_example_utils import ImageData, ImageBuffer
import OpenCV_to_RAPID


# TODO: Extend the program with threading, this will allow the camera to always stay active
#  and could give a live feed of what the camera sees while still maintaining control over robot.

def capture_image(cam, gripper_height):
    """Captures a single image through PyuEye functions. Focus is manually adjusted depending on the height
    of the camera above the subject.
    """
    camera_height = gripper_height + 70  # Camera is placed 70mm above gripper
    # TODO: Find a curve that correlates distance from subject and focus value
    """if camera_height > 300:
        nRet = ueye.is_Focus(cam.handle(), ueye.FOC_CMD_SET_MANUAL_FOCUS,
                             config.focus_overview, ueye.sizeof(config.focus_overview))
    else:
        nRet = ueye.is_Focus(cam.handle(), ueye.FOC_CMD_SET_MANUAL_FOCUS,
                             config.focus_closeup, ueye.sizeof(config.focus_closeup))"""

    nRet = ueye.is_Focus(cam.hCam, ueye.FOC_CMD_SET_ENABLE_AUTOFOCUS_ONCE, None, 0)

    """nRet = ueye.INT()
    nValue = ueye.INT()

    while True:
        nRet = ueye.is_Focus(cam.hCam, ueye.FOC_CMD_GET_AUTOFOCUS_STATUS, nValue, ueye.sizeof(nValue))

        if nValue == 2:
            time.sleep(0.5)
            break"""

    time.sleep(2.5)
    array = cam.get_image()
    #cv2.imshow("test", array)
    #cv2.waitKey(0)

    # autofocus_status = ueye.INT(0)
    # ueye.is_Focus(cam.handle(), ueye.FOC_CMD_GET_AUTOFOCUS_STATUS, autofocus_status, ueye.sizeof(autofocus_status))
    #img_buffer = ImageBuffer()  # Create image buffer
    # ueye.is_Focus(cam.handle(), ueye.FOC_CMD_SET_ENABLE_AUTOFOCUS_ONCE, None, 0)
    # cam.freeze_video()  # Freeze video captures a single image

    #nRet = ueye.is_WaitForNextImage(cam.handle(), 1000, img_buffer.mem_ptr, img_buffer.mem_id)
    #img_data = ImageData(cam.handle(), img_buffer)
    #array = img_data.as_1d_image()
    #img_data.unlock()

    return array


def findPucks(cam, robot, robtarget_pucks, cam_comp=False, number_of_images=1):
    """Finds all pucks in the frame of the camera by capturing an image and scanning the image for QR codes.
    After the codes have been pinpointed, a series of transformations happen to finally create robtargets
    which can be sent to RobotWare."""

    trans, rot = robot.get_gripper_position()
    gripper_height = robot.get_gripper_height()

    cam_pos = OpenCV_to_RAPID.get_camera_position(trans=trans, rot=rot)

    time.sleep(0.5)  # Short pause before capturing image to ensure that the camera is still
    for _ in range(number_of_images):
        image = capture_image(cam=cam, gripper_height=gripper_height)
        showVideo(cam)

        # Scan the image_tools and return all QR code positions
        temp_puck_list = QR_Scanner(image)

        # Check if the QR codes that were found have already been located previously.
        # If so, remove them from the temporary list.
        for puck in robtarget_pucks:
            if any(puck == x for x in temp_puck_list):
                temp_puck_list.remove(puck)

        for puck in temp_puck_list:
            puck = OpenCV_to_RAPID.create_robtarget(gripper_height=gripper_height, gripper_rot=rot, cam_pos=cam_pos,
                                                    puck=puck, cam_comp=cam_comp)
            robtarget_pucks.append(puck)

    return robtarget_pucks


"""def showVideo(cam):
    img_buffer = ImageBuffer()
    #img_data = ImageData(cam.handle(), img_buffer)
    while True:
        nRet = ueye.is_WaitForNextImage(cam.handle(), 1000, img_buffer.mem_ptr, img_buffer.mem_id)
        img_data = ImageData(cam.handle(), img_buffer)
        array = img_data.as_1d_image()
        # scanned_img = QR_Scanner_visualized(array)
        """


def showVideo(cam):
    while True:
        array = cam.get_image()
        array = QR_Scanner_visualized(array)
        #cv2.imshow("Continuous video display", array)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()
