from adafruit_motorkit import MotorKit
from adafruit_motor import stepper
import board
import analogio
from analogio import AnalogIn
import time

# initialize analog voltage read in
adc = analogio.AnalogIn(board.A0)

# initialize motor control
kit = MotorKit(i2c=board.I2C())
kit.stepper1.release()

# reads in voltage, calculates and returns current power
def analogReadIn():
    # circuitpython metro board has 65535 steps
    RESPONSIVITY = 0.26
    LOAD_RESISTANCE = 33000
    #current_power = 14.232*((adc.value / 65535 * 5) / (RESPONSIVITY * LOAD_RESISTANCE) * 1000)
    current_power = 14.232 * (0.9476 * ((adc.value / 65535 * 5) / (RESPONSIVITY * LOAD_RESISTANCE) * 1000)) - 0.08
    return current_power

def avgPower():
    total = 0.0
    for i in range(80):
        total = total + analogReadIn()
    return total / 80

# measures the min and max power the wheel can attenuate based off the current
def measureMinMax():
    current_p = avgPower()
    abs_min = current_p
    abs_max = current_p
    counter = 0;
    while counter != 420:
        for i in range(10):
            kit.stepper1.onestep(direction=stepper.FORWARD, style=stepper.MICROSTEP)
        current_p = avgPower()
        if current_p > abs_max:
            abs_max = current_p
        if current_p < abs_min:
            abs_min = current_p
        counter = counter + 1
        kit.stepper1.release()
    kit.stepper1.release()
    minmax = [abs_min, abs_max]
    return minmax

# sets power of microscope by using feedback loop between power meter and attenuator
def setPower(desired_power):

    current_power = avgPower()
    counter = 0
    times = 0
    while (times < 3):
        #while round(current_power, 4) != desired_power:
        while (abs(current_power - desired_power) / desired_power) > 0.002:
        #while (abs(current_power - desired_power) / (0.5 * (current_power + desired_power))) > 0.001:
            if (counter > 700):
                kit.stepper1.release()
                return False
            if current_power < desired_power:
                for i in range(5):
                    kit.stepper1.onestep(direction=stepper.FORWARD, style=stepper.MICROSTEP)

            elif current_power > desired_power:
                for i in range(5):
                    kit.stepper1.onestep(direction=stepper.BACKWARD, style=stepper.MICROSTEP)

            time.sleep(0.15)
            counter = counter + 1
            current_power = avgPower()
        times = times + 1
    kit.stepper1.release()
    return True

while(True):
    cmd = input()
    cmdlist = cmd.strip().split(' ')

    #call read power function
    if cmdlist[0] == 'rp':
        val = avgPower()
        print('current power: {}'.format(val))

    # call set power function
    elif cmdlist[0] == 'sp':
        # desired power value saved as second element in list
        val = setPower(float(cmdlist[1]))
        if (val):
            print('done')
        else:
            print('failed, try again')

    # measure min max power
    elif cmdlist[0] == 'pr':
        val = measureMinMax()
        print('{}, {}'.format(val[0], val[1])) # min, max

    else:
        print('wrong cmd {}'.format(cmd))
