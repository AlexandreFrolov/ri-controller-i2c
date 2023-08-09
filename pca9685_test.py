import time
import smbus
import math

# Адрес контроллера PCA9685 (введите свой адрес, если он был изменен).
PCA9685_ADDRESS = 0x40

# Регистры PCA9685.
PCA9685_MODE1 = 0x00
PCA9685_MODE2 = 0x01

PCA9685_LED0_ON_L = 0x06
PCA9685_LED0_ON_H = 0x07
PCA9685_LED0_OFF_L = 0x08
PCA9685_LED0_OFF_H = 0x09

PCA9685_ALL_LED_ON_L  = 0xFA
PCA9685_ALL_LED_ON_H  = 0xFB
PCA9685_ALL_LED_OFF_L = 0xFC
PCA9685_ALL_LED_OFF_H = 0xFD
PCA9685_PRESCALE      = 0xFE

ALLCALL            = 0x01
OUTDRV             = 0x04
SLEEP              = 0x10
RESTART            = 0x80

CHANNEL00          = 0x00
CHANNEL01          = 0x01
CHANNEL02          = 0x02
CHANNEL03          = 0x03
CHANNEL04          = 0x04
CHANNEL05          = 0x05
CHANNEL06          = 0x06
CHANNEL07          = 0x07
CHANNEL08          = 0x08
CHANNEL09          = 0x09
CHANNEL10          = 0x0A
CHANNEL11          = 0x0B
CHANNEL12          = 0x0C
CHANNEL13          = 0x0D
CHANNEL14          = 0x0E
CHANNEL15          = 0x0F

bus = smbus.SMBus(1)


def set_all_pwm(on, off):
    bus.write_byte_data(PCA9685_ADDRESS, PCA9685_ALL_LED_ON_L, on & 0xFF)
    bus.write_byte_data(PCA9685_ADDRESS, PCA9685_ALL_LED_ON_H, on >> 8)
    bus.write_byte_data(PCA9685_ADDRESS, PCA9685_ALL_LED_OFF_L, off & 0xFF)
    bus.write_byte_data(PCA9685_ADDRESS, PCA9685_ALL_LED_OFF_H, off >> 8)

def set_pwm(channel, on, off):
    bus.write_byte_data(PCA9685_ADDRESS, PCA9685_LED0_ON_L + 4 * channel, on & 0xFF)
    bus.write_byte_data(PCA9685_ADDRESS, PCA9685_LED0_ON_H + 4 * channel, on >> 8)
    bus.write_byte_data(PCA9685_ADDRESS, PCA9685_LED0_OFF_L + 4 * channel, off & 0xFF)
    bus.write_byte_data(PCA9685_ADDRESS, PCA9685_LED0_OFF_H + 4 * channel, off >> 8)


def pulse_to_pwm(pulse, frequency):
    # Длительность одного периода, мкС
    period_duration = (1 / frequency) * 1000000
    
    # Относительное значение длительности импульса (в единицах периода)
    relative_pulse_duration = pulse / period_duration
    
    # Пересчёт относительных значений в диапазон [0, 4096]
    return(int(relative_pulse_duration * 4096))

def set_servo_angle(channel, angle):
    if angle < 0:
        angle = 0
    elif angle > 180:
        angle = 180
        
    sg90_servo_min_pulse = 500      # минимальная длина импульса для sg90 в мкс
    sg90_servo_maxn_pulse = 2400    # максимальная длина импульса для sg90 в мкс
    servo_min = pulse_to_pwm(500, 50)
    servo_max = pulse_to_pwm(2400, 50)

    pulse_width = int(angle * (servo_max - servo_min) / 180 + servo_min)

    print("pulse_width: " + str(pulse_width))
    set_pwm(channel, 0, pulse_width)

def initialize_pca9685():
    set_all_pwm(0, 0)
    time.sleep(2)

    bus.write_byte_data(PCA9685_ADDRESS, PCA9685_MODE2, OUTDRV)
    bus.write_byte_data(PCA9685_ADDRESS, PCA9685_MODE1, ALLCALL)
    time.sleep(0.005)
    

    mode1 = bus.read_byte_data(PCA9685_ADDRESS, PCA9685_MODE1)
    mode1 = mode1 & ~SLEEP                                    # wake up (reset sleep)
    bus.write_byte_data(PCA9685_ADDRESS, PCA9685_MODE1, mode1)
    time.sleep(0.005)                                         # wait for oscillator


def reset():
    bus.write_byte_data(PCA9685_ADDRESS, PCA9685_MODE1, RESTART)
    time.sleep(0.01)


def set_pwm_freq(freq_hz):
    prescaleval = 25000000.0                                  # 25MHz
    prescaleval /= 4096.0                                     # 12-bit
    prescaleval /= float(freq_hz)
    prescaleval -= 1.0
    prescale = int(math.floor(prescaleval + 0.5))
    oldmode = bus.read_byte_data(PCA9685_ADDRESS, PCA9685_MODE1)
    newmode = (oldmode & 0x7F) | 0x10                         # sleep
    bus.write_byte_data(PCA9685_ADDRESS, PCA9685_MODE1, newmode) # go to sleep
    bus.write_byte_data(PCA9685_ADDRESS, PCA9685_PRESCALE, prescale)
    bus.write_byte_data(PCA9685_ADDRESS, PCA9685_MODE1, oldmode)
    time.sleep(0.005)
    bus.write_byte_data(PCA9685_ADDRESS, PCA9685_MODE1, oldmode | 0x80)

try:
    initialize_pca9685()
    set_pwm_freq(50)
    
    
    while True:
        set_servo_angle(CHANNEL00, 0) # 600 мс
        time.sleep(2)

        input("Введите что-нибудь для продолжения:")
        
        set_servo_angle(CHANNEL00, 90) # 1460 мс
        time.sleep(2)

        input("Введите что-нибудь для продолжения:")

        set_servo_angle(CHANNEL00, 180) # 2340 мс
        time.sleep(2)
        input("Введите что-нибудь для продолжения:")

#        set_servo_angle(CHANNEL03, 0)
#        time.sleep(2)

#        set_servo_angle(CHANNEL03, 90)
#        time.sleep(2)

#        set_servo_angle(CHANNEL03, 180)
#        time.sleep(2)


except KeyboardInterrupt:
    pass
finally:
    set_all_pwm(0, 0)
    time.sleep(0.05)
    reset()
