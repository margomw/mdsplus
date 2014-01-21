#!/usr/bin/env python

from MDSplus import *
import serial
from serial import SerialException, SerialTimeoutException
import struct
import time

from pymodbus.client.sync import ModbusTcpClient
from pymodbus.exceptions import *

import logging



class SerialReadTimeoutException(SerialException):
    """Read tmeout give an exception"""
    
class SerialBadMessageException(SerialException):
    """Received bad message give an exception"""









class MILL3(Device):
    parts=[
        {'path':':COMMENT', 'type':'text'},
        {'path':':IP', 'type':'text'},
        {'path':':MOXA_COM1', 'type':'text'},
        {'path':':MOXA_COM2', 'type':'text'},
        {'path':':MOXA_COM3', 'type':'text'},
        {'path':':MOXA_COM4', 'type':'text'},
        {'path':':SHORT_TRN_SP', 'type':'numeric'},
        {'path':':LONG_TRN_SP', 'type':'numeric'},
        {'path':':ROTATION_SP', 'type':'numeric'},
        {'path':':SHORT_TRN', 'type':'numeric'},
        {'path':':LONG_TRN', 'type':'numeric'},
        {'path':':ROTATION', 'type':'numeric'},
        {'path':':PRESSURE', 'type':'numeric'}]

    parts.append({'path':':INIT_ACTION','type':'action',
        'valueExpr':"Action(Dispatch('CPCI_SERVER','INIT',50,None),Method(None,'INIT',head))",
        'options':('no_write_shot',)})

    ser=None


    def sendCmd(self, cmd):
        self.ser.write(cmd)
        time.sleep(0.2)
    
        remaining = 14
    
        msg = bytearray()
    
        while remaining > 0:
            chunk = self.ser.read(remaining)
            if 0 == len(chunk): raise SerialReadTimeoutException        
            msg.extend(chunk)
            remaining -= len(chunk)
    
        if ":" != chr(msg[6]): raise SerialBadMessageException
    
        s1 = cmd[2:6]
        s2 = msg[2:6]
        
    #    print(s1==s2)
    
        data = struct.unpack_from('>i', buffer(msg), 7)
    
        return data[0]




    def INIT(self, arg):
        LONG_TRANSLATION_SET_POINT_MAX_VALUE = 1540
        SHORT_TRANSLATION_SET_POINT_MAX_VALUE = 200

        print 'START INIT'


        try:
            ip = str(self.ip.data())
            ip = ip.strip()
            print ' IP: ' + ip
        except:
            Data.execute('DevLogErr($1, $2)', self.nid, 'Invalid IP')
            return 0

        try:
            longTranslationSetPoint = self.long_trn_sp.data()
            print ' LONG_TRN_SP: ' + str(longTranslationSetPoint)
            if longTranslationSetPoint < 0 or longTranslationSetPoint > LONG_TRANSLATION_SET_POINT_MAX_VALUE:
                Data.execute('DevLogErr($1, $2)', self.nid, 'Invalid LONG_TRN_SP')
                return 0
        except:
            Data.execute('DevLogErr($1, $2)', self.nid, 'Invalid LONG_TRN_SP')
            return 0

        try:
            shortTranslationSetPoint = self.short_trn_sp.data()
            print ' SHORT_TRN_SP: ' + str(shortTranslationSetPoint)
            if shortTranslationSetPoint < 0 or shortTranslationSetPoint > SHORT_TRANSLATION_SET_POINT_MAX_VALUE:
                Data.execute('DevLogErr($1, $2)', self.nid, 'Invalid SHORT_TRN_SP')
                return 0
        except:
            Data.execute('DevLogErr($1, $2)', self.nid, 'Invalid SHORT_TRN_SP')
            return 0
        
        try:
            moxaCom1 = str(self.moxa_com1.data())
            moxaCom1 = moxaCom1.strip()
            print ' MOXA_COM1: ' + moxaCom1
        except:
            Data.execute('DevLogErr($1, $2)', self.nid, 'Invalid MOXA_COM1')
            return 0
        
        try:
            moxaCom2 = str(self.moxa_com2.data())
            moxaCom2 = moxaCom2.strip()
            print ' MOXA_COM2: ' + moxaCom2
        except:
            Data.execute('DevLogErr($1, $2)', self.nid, 'Invalid MOXA_COM2')
            return 0        

        try:
            moxaCom3 = str(self.moxa_com3.data())
            moxaCom3 = moxaCom3.strip()
            print ' MOXA_COM3: ' + moxaCom3
        except:
            Data.execute('DevLogErr($1, $2)', self.nid, 'Invalid MOXA_COM3')
            return 0
        
        try:
            moxaCom4 = str(self.moxa_com4.data())
            moxaCom4 = moxaCom4.strip()
            print ' MOXA_COM4: ' + moxaCom4
        except:
            Data.execute('DevLogErr($1, $2)', self.nid, 'Invalid MOXA_COM4')
            return 0
        
                
        try:
            crouzet=ip
            port=moxaCom1
            
            self.ser=None
            serTimeout=5

                    
            c=ModbusTcpClient(crouzet)
            conn=c.connect()
            if not conn: raise ModbusException("cannot connect to " + crouzet)
                    
            c.write_register(12,1)
            time.sleep(0.5)
            
            self.ser = serial.Serial(
            port = port,
            baudrate = 9600,
            parity = serial.PARITY_NONE,
            stopbits = serial.STOPBITS_ONE,
            bytesize = serial.EIGHTBITS,
            xonxoff = False,
            rtscts = False,
            dsrdtr = False,
            timeout = serTimeout
            )
           
            
            position = self.sendCmd("\x7C\x00\x54\x50\x4F\x53\x00\x00\x00\x00\x00\x01\xC2\x04")
            decimals = self.sendCmd("\x7C\x00\x54\x44\x45\x43\x00\x00\x00\x00\x00\x01\x9C\x04")
            preset = self.sendCmd("\x7C\x00\x54\x52\x45\x46\x00\x00\x00\x00\x00\x01\xAD\x04")
            offset = self.sendCmd("\x7C\x00\x54\x45\x49\x4E\x00\x00\x00\x00\x00\x01\xAC\x04")
            print("raw position: " + str(position))
            print("decimals: " + str(decimals))
            print("preset: " + str(preset))
            print("offset: " + str(offset))
            longPosition=position / (10.0 ** decimals)
            print("long position: " + str(longPosition))
            setattr(self,'long_trn',longPosition)
                   
            port=moxaCom2
            self.ser=None
            serTimeout=5
        
            self.ser = serial.Serial(
            port = port,
            baudrate = 9600,
            parity = serial.PARITY_NONE,
            stopbits = serial.STOPBITS_ONE,
            bytesize = serial.EIGHTBITS,
            xonxoff = False,
            rtscts = False,
            dsrdtr = False,
            timeout = serTimeout
            )
        
            position = self.sendCmd("\x7C\x00\x54\x50\x4F\x53\x00\x00\x00\x00\x00\x01\xC2\x04")
            decimals = self.sendCmd("\x7C\x00\x54\x44\x45\x43\x00\x00\x00\x00\x00\x01\x9C\x04")
            preset = self.sendCmd("\x7C\x00\x54\x52\x45\x46\x00\x00\x00\x00\x00\x01\xAD\x04")
            offset = self.sendCmd("\x7C\x00\x54\x45\x49\x4E\x00\x00\x00\x00\x00\x01\xAC\x04")
            print("raw position: " + str(position))
            print("decimals: " + str(decimals))
            print("preset: " + str(preset))
            print("offset: " + str(offset))
            shortPosition=position / (10.0 ** decimals)
            print("short position: " + str(shortPosition))
            setattr(self,'short_trn',shortPosition)            

        
        
            port=moxaCom3
            self.ser=None
            serTimeout=5
        
            self.ser = serial.Serial(
            port = port,
            baudrate = 9600,
            parity = serial.PARITY_NONE,
            stopbits = serial.STOPBITS_ONE,
            bytesize = serial.EIGHTBITS,
            xonxoff = False,
            rtscts = False,
            dsrdtr = False,
            timeout = serTimeout
            )
        
            position = self.sendCmd("\x7C\x00\x54\x50\x4F\x53\x00\x00\x00\x00\x00\x01\xC2\x04")
            decimals = self.sendCmd("\x7C\x00\x54\x44\x45\x43\x00\x00\x00\x00\x00\x01\x9C\x04")
            preset = self.sendCmd("\x7C\x00\x54\x52\x45\x46\x00\x00\x00\x00\x00\x01\xAD\x04")
            offset = self.sendCmd("\x7C\x00\x54\x45\x49\x4E\x00\x00\x00\x00\x00\x01\xAC\x04")
            print("raw position: " + str(position))
            print("decimals: " + str(decimals))
            print("preset: " + str(preset))
            print("offset: " + str(offset))
            rotation=position / (10.0 ** decimals)
            print("rotation: " + str(rotation))
            setattr(self,'rotation',rotation)            

        
        
            port=moxaCom4
            self.ser=None
            serTimeout=5
        
            self.ser = serial.Serial(
            port = port,
            baudrate = 9600,
            parity = serial.PARITY_NONE,
            stopbits = serial.STOPBITS_ONE,
            bytesize = serial.EIGHTBITS,
            xonxoff = False,
            rtscts = False,
            dsrdtr = False,
            timeout = 10
            )
        
            self.ser.write("\x50\x52\x31\x0D")    
            time.sleep(0.2)
            ack = self.ser.read(3)
            print(ack.encode("hex"))
            self.ser.write("\x05")    
            time.sleep(0.2)
        
            data = self.ser.readline()
            print(data.encode("hex"))    
            if data[0] != '\x30': raise SerialBadMessageException
            data=data[2:13]
            data=data.strip()
            print("pressure: " + data)
            setattr(self,'pressure',float(data))             
        except ModbusException as e:
            print e
        except SerialTimeoutException:   
            print "Timeout on write operation"
        except SerialReadTimeoutException:   
            print "Timeout on read operation"
        except SerialBadMessageException:
            print "Bad message"    
        except SerialException:
            print "Could not open port " + port
        finally:
            if self.ser is not None: self.ser.close()
            if conn: c.write_register(12,2)
            return 1
                