import io
import pyqrcode
from base64 import b64encode
import eel
from ctypes import *
from dwfconstants import *
import math
import time
import sys
import numpy
import matplotlib.pyplot as plt


eel.init('web')


@eel.expose
def dummy(dummy_param):
    print("I got a parameter: ", dummy_param)
    return "string_value", 1, 1.2, True, [1, 2, 3, 4], {"name": "eel"}


@eel.expose
def generate_qr(data):
    img = pyqrcode.create(data)
    imp_analyser()
    # img = imp_analyser()
    buffers = io.BytesIO()
    img.png(buffers, scale=8)
    encoded = b64encode(buffers.getvalue()).decode("ascii")
    print("QR code generation successful.")
    return "data:image/png;base64, " + encoded

def imp_analyser():
    if sys.platform.startswith("win"):
        dwf = cdll.LoadLibrary("dwf.dll")
    elif sys.platform.startswith("darwin"):
        dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
    else:
        dwf = cdll.LoadLibrary("libdwf.so")

    version = create_string_buffer(16)
    dwf.FDwfGetVersion(version)
    print("DWF Version: "+str(version.value))

    hdwf = c_int()
    szerr = create_string_buffer(512)
    print("Opening first device")
    dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))

    if hdwf.value == hdwfNone.value:
        dwf.FDwfGetLastErrorMsg(szerr)
        print(str(szerr.value))
        print("failed to open device")
        quit()

    # this option will enable dynamic adjustment of analog out settings like: frequency, amplitude...
    dwf.FDwfDeviceAutoConfigureSet(hdwf, c_int(3)) 

    sts = c_byte()
    steps = 100
    start = 1e2
    stop = 1e6
    reference = 1e3

    print("Reference: "+str(reference)+" Ohm  Frequency: "+str(start)+" Hz ... "+str(stop/1e3)+" kHz for nanofarad capacitors")
    dwf.FDwfAnalogImpedanceReset(hdwf)
    dwf.FDwfAnalogImpedanceModeSet(hdwf, c_int(8)) # 0 = W1-C1-DUT-C2-R-GND, 1 = W1-C1-R-C2-DUT-GND, 8 = AD IA adapter
    dwf.FDwfAnalogImpedanceReferenceSet(hdwf, c_double(reference)) # reference resistor value in Ohms
    dwf.FDwfAnalogImpedanceFrequencySet(hdwf, c_double(start)) # frequency in Hertz
    dwf.FDwfAnalogImpedanceAmplitudeSet(hdwf, c_double(1)) # 1V amplitude = 2V peak2peak signal
    dwf.FDwfAnalogImpedanceConfigure(hdwf, c_int(1)) # start
    time.sleep(2)

    rgHz = [0.0]*steps
    rgRs = [0.0]*steps
    rgXs = [0.0]*steps
    for i in range(100):
        hz = stop * pow(10.0, 1.0*(1.0*i/(steps-1)-1)*math.log10(stop/start)) # exponential frequency steps
        rgHz[i] = hz
        dwf.FDwfAnalogImpedanceFrequencySet(hdwf, c_double(hz)) # frequency in Hertz
        time.sleep(0.01) 
        dwf.FDwfAnalogImpedanceStatus(hdwf, None) # ignore last capture since we changed the frequency
        while True:
            if dwf.FDwfAnalogImpedanceStatus(hdwf, byref(sts)) == 0:
                dwf.FDwfGetLastErrorMsg(szerr)
                print(str(szerr.value))
                quit()
            if sts.value == 2:
                break
        resistance = c_double()
        reactance = c_double()
        dwf.FDwfAnalogImpedanceStatusMeasure(hdwf, DwfAnalogImpedanceResistance, byref(resistance))
        dwf.FDwfAnalogImpedanceStatusMeasure(hdwf, DwfAnalogImpedanceReactance, byref(reactance))
        rgRs[i] = abs(resistance.value) # absolute value for logarithmic plot
        rgXs[i] = abs(reactance.value)

    fig = plt.plot(rgHz, rgRs, rgHz, rgXs)
    ax = plt.gca()
    ax.set_xscale('log')
    ax.set_yscale('log')
    plt.show()

    dwf.FDwfAnalogImpedanceConfigure(hdwf, c_int(0)) # stop
    dwf.FDwfDeviceClose(hdwf)

    from Tkinter import Tk
    from tkinter.filedialog import askopenfilename

    Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
    filename = askopenfilename() # show an "Open" dialog box and return the path to the selected file
    print(filename)


eel.start('index.html', size=(1300, 750))
