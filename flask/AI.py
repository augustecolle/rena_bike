from ABE_ADCPi import ADCPi
from ABE_helpers import ABEHelpers
import time

def i2c(address):
    address = 0x6e
    i2c_helper = ABEHelpers()
    bus = i2c_helper.get_smbus()
    adc = ADCPi(bus, address, rate=18)
    return bus, adc

def getAI(address, channel = 1):
    bus, adc = i2c(address)
    return adc.read_voltage(channel)

def setPGA(address, gain):
    bus, adc = i2c(address)
    adc.set_pga(gain)

