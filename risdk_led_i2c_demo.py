import sys
from ctypes import *
import platform
import traceback

def err_msg(errTextC):
    return(errTextC.raw.decode())

def init(i2c, pwm):
    
    errTextC = create_string_buffer(1000)
    platform_os = platform.system()
    try:
        if platform_os == "Windows":
            lib = cdll.LoadLibrary("C:\Windows\system32\librisdk.dll")
        if platform_os == "Linux":
            lib = cdll.LoadLibrary("/usr/local/robointellect_sdk/ri_sdk/librisdk.so")
    except OSError as e:
        raise Exception("Failed to load: " + str(e))

    lib.RI_SDK_InitSDK.argtypes = [c_int, c_char_p]
    lib.RI_SDK_CreateModelComponent.argtypes = [c_char_p, c_char_p, c_char_p, POINTER(c_int), c_char_p]
    lib.RI_SDK_LinkPWMToController.argtypes = [c_int, c_int, c_uint8, c_char_p]
    lib.RI_SDK_connector_i2c_SetBus.argtypes = [c_int, c_int, POINTER(c_int), POINTER(c_int), c_char_p]

    errTextC = create_string_buffer(1000)
    errCode = lib.RI_SDK_InitSDK(3, errTextC)
    if errCode != 0:
        raise Exception(f"RI_SDK_InitSDK failed with error code {errCode}: {err_msg(errTextC)}")        

    errCode = lib.RI_SDK_CreateModelComponent("connector".encode(), "i2c_adapter".encode(), "ch341".encode(), i2c, errTextC)
    if errCode != 0:
        raise Exception(f"RI_SDK_CreateModelComponent failed with error code {errCode}: {err_msg(errTextC)}")        

    errCode = lib.RI_SDK_CreateModelComponent("connector".encode(), "pwm".encode(), "pca9685".encode(), pwm, errTextC)
    if errCode != 0:
        raise Exception(f"RI_SDK_CreateModelComponent failed with error code {errCode}: {err_msg(errTextC)}")        


    nextBus = c_int() # Установеленный номер шины.
    prevBus = c_int() # Предыдущий номер шины.
    errCode = lib.RI_SDK_connector_i2c_SetBus(i2c, 1, nextBus, prevBus, errTextC)
                
    if errCode != 0:
        raise Exception(f"init failed with error code {errCode}: {err_msg(errTextC)}")        
#    print("Задан номер шины: ", nextBus, "Предыдущий номер шины: ", prevBus)            

    errCode = lib.RI_SDK_LinkPWMToController(pwm, i2c, 0x40, errTextC)
    if errCode != 0:
        raise Exception(f"RI_SDK_LinkPWMToController failed with error code {errCode}: {err_msg(errTextC)}")        

    return lib
    
def add_led(lib, led, pwm, r, g, b):
    lib.RI_SDK_CreateModelComponent.argtypes = [c_char_p, c_char_p, c_char_p, POINTER(c_int), c_char_p]
    lib.RI_SDK_LinkLedToController.argtypes = [c_int, c_int, c_int, c_int, c_int, c_char_p]

    errTextC = create_string_buffer(1000)
    errCode = lib.RI_SDK_CreateModelComponent("executor".encode(), "led".encode(), "ky016".encode(), led, errTextC)
    if errCode != 0:
        raise Exception(f"RI_SDK_CreateModelComponent failed with error code {errCode}: {err_msg(errTextC)}")        

    errCode = lib.RI_SDK_LinkLedToController(led, pwm, r, g, b, errTextC)
    if errCode != 0:
        raise Exception(f"RI_SDK_LinkLedToController failed with error code {errCode}: {err_msg(errTextC)}")        

def cleanup(lib):
    lib.RI_SDK_DestroySDK.argtypes = [c_bool, c_char_p]

    errTextC = create_string_buffer(1000)
    errCode = lib.RI_SDK_DestroySDK(True, errTextC)
    if errCode != 0:
        raise Exception(f"RI_SDK_DestroySDK failed with error code {errCode}: {err_msg(errTextC)}")        

def led_flicker(lib, led, r, g, b, duration, qty, async_mode):
    lib.RI_SDK_exec_RGB_LED_Flicker.argtypes = [c_int, c_int, c_int, c_int, c_int, c_int, c_bool, c_char_p]

    errTextC = create_string_buffer(1000)
    errCode = lib.RI_SDK_exec_RGB_LED_Flicker(led, r, g, b, duration, qty, async_mode, errTextC)
    if errCode != 0:
        raise Exception(f"RI_SDK_exec_RGB_LED_Flicker failed with error code {errCode}: {err_msg(errTextC)}")        

def led_pulse(lib, led, r, g, b, duration, async_mode):
    lib.RI_SDK_exec_RGB_LED_SinglePulse.argtypes = [c_int, c_int, c_int, c_int, c_int, c_bool, c_char_p]
    errTextC = create_string_buffer(1000)
    errCode = lib.RI_SDK_exec_RGB_LED_SinglePulse(led, r, g, b, duration, async_mode, errTextC)
    if errCode != 0:
        raise Exception(f"RI_SDK_exec_RGB_LED_SinglePulse failed with error code {errCode}: {err_msg(errTextC)}")        

def led_pulse_pause(lib, led, r, g, b, duration, pause, limit, async_mode):
    lib.RI_SDK_exec_RGB_LED_FlashingWithPause.argtypes = [c_int, c_int, c_int, c_int, c_int, c_int, c_int, c_bool, c_char_p]

    errTextC = create_string_buffer(1000)
    errCode = lib.RI_SDK_exec_RGB_LED_FlashingWithPause(led, r, g, b, duration, pause, limit, async_mode, errTextC)
    if errCode != 0:
        raise Exception(f"RI_SDK_exec_RGB_LED_FlashingWithPause failed with error code {errCode}: {err_msg(errTextC)}")        

def led_pulse_frequency(lib, led, r, g, b, frequency, limit, async_mode):
    lib.RI_SDK_exec_RGB_LED_FlashingWithFrequency.argtypes = [c_int, c_int, c_int, c_int, c_int, c_int, c_bool, c_char_p]

    errTextC = create_string_buffer(1000)
    errCode = lib.RI_SDK_exec_RGB_LED_FlashingWithFrequency(led, r, g, b, frequency, limit, async_mode, errTextC)
    if errCode != 0:
        raise Exception(f"RI_SDK_exec_RGB_LED_FlashingWithFrequency failed with error code {errCode}: {err_msg(errTextC)}")        

def led_cleanup(lib, led):
    lib.RI_SDK_DestroyComponent.argtypes = [c_int, c_char_p]

    errTextC = create_string_buffer(1000)
    errCode = lib.RI_SDK_DestroyComponent(led, errTextC)
    if errCode != 0:
        raise Exception(f"RI_SDK_DestroyComponent failed with error code {errCode}: {err_msg(errTextC)}")        


if __name__ == "__main__":
    try:
        i2c = c_int()
        pwm = c_int()
        led = c_int()
        
        lib = init(i2c, pwm)

#        add_led(lib, led, pwm, 15, 14, 13)
        add_led(lib, led, pwm, 14, 15, 13)

        print("Start pulse...")

        led_pulse(lib, led, 255, 0, 0, 1500, False)
        led_pulse(lib, led, 0, 255, 0, 1500, False)
        led_pulse(lib, led, 0, 0, 255, 1500, False)

        print("Start flicker...")

        led_flicker(lib, led, 255, 0, 0, 500, 5, False)
        led_flicker(lib, led, 0, 255, 0, 500, 5, False)
        led_flicker(lib, led, 0, 0, 255, 500, 5, False)

        print("Start pulse_pause...")

        led_pulse_pause(lib, led, 255, 0, 0, 1000, 200, 3, False)
        led_pulse_pause(lib, led, 0, 255, 0, 1000, 200, 3, False)
        led_pulse_pause(lib, led, 0, 0, 255, 1000, 200, 3, False)

        print("Start pulse_frequency...")

        led_pulse_frequency(lib, led, 255, 0, 0, 10, 10, False)
        led_pulse_frequency(lib, led, 0, 255, 0, 20, 10, False)
        led_pulse_frequency(lib, led, 0, 0, 255, 30, 10, False)

        led_cleanup(lib, led)
        cleanup(lib)
    except Exception as e:
        print(traceback.format_exc() + "===> ", str(e))
        sys.exit(2)
 