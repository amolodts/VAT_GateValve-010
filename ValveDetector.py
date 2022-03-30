#!/usr/bin/env python3
from tango import DevState, DispLevel, DeviceProxy, READ
from tango.server import Device, attribute, device_property

class ValveDetector(Device):
    # Properties, set which two ports you need to read out valves data
    Port1 = device_property(
        dtype="str",
        default_value="A0",
    )
    
    Port2 = device_property(
        dtype="str",
        default_value="A1",
    ) 
    
    # Attributes
    valve_pos = attribute(
            label='Position of Valve',
            dtype=str,
            access=READ,
            display_level=DispLevel.OPERATOR,
            doc='Returns position of valve. Possible options: open, closed & moving. Moving means that it is between the position open and closed.'
        )
    
    
    def init_device(self):
        Device.init_device(self)
        self.set_state(DevState.INIT)
        self.set_status('Initialization of valve device.')
        try:
            # connect to a running tango device to consum its data
            self.daq = DeviceProxy('imaging/DAQDevice/typA')
            self.set_status('Connected to tape device: {:s}'.format('imaging/DAQDevice/typA'))
        except:
            self.error_stream('Could not connect to DAQDevice.')
            self.set_status('Could not connect to DAQDevice.')
            self.set_state(DevState.ALARM)
            return

    
    def read_valve_pos(self):
        
        self.set_state(DevState.RUNNING)
        self.set_status('Reading data of valve.')
        
        # read out data of both ports
        val1 = getattr(self.daq, self.Port1)
        val2 = getattr(self.daq, self.Port2)
        
        # interpretation of ports data
        # in this case the PortA Pull-up is enabled, so all pins are high (=1) at default and low (=0) if signal is detected
        if val1 == True and val2 == True:
            return 'moving'
        elif val1 == True and val2 == False:
            return 'closed'
        elif val1 == False and val2 == False:
            return 'open'
        else:
            self.set_status('Check if everything is ok at the valve.')
            self.set_state(DevState.ALARM)
            return 'alarm'
       
if __name__ == '__main__':
    ValveDetector.run_server()
