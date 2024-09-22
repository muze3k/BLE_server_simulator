import tkinter
import customtkinter

import random
import ctypes
import struct

import codecs  # for datatype conversion

import logging
import asyncio
import threading
from rich.traceback import install
install()


from typing import Any

from bless import (  # type: ignore
        BlessServer,
        BlessGATTCharacteristic,
        GATTCharacteristicProperties,
        GATTAttributePermissions
        )

#logging.basicConfig(level=logging.DEBUG)
#logger = logging.getLogger(name=__name__)
trigger: threading.Event = threading.Event()

customtkinter.set_appearance_mode("System")  
customtkinter.set_default_color_theme("blue")  

app = customtkinter.CTk()  
app.geometry("400x440")
app.title("BLE simulator - Sparkleo ltd.")

try:
    loop = asyncio.get_event_loop()
except RuntimeError as e:
    if str(e).startswith('There is no current event loop in thread'):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    else:
        raise

print(".\n.\n.\nApplication has started, to begin testing press Start server button")

def long_running_task():
    loop.run_until_complete(run(loop))

def startsimulatorthread():
    #print('simulator started')
    button.configure(state="disabled")
    thread = threading.Thread(target=long_running_task)
    thread.start()

    #loop = asyncio.get_event_loop()     # event loop started
    #thread = threading.Thread(target=loop.run_until_complete(run(loop)))
    #loop.run_until_complete(run(loop))
    #thread.start()

def stopsimulatorthread():
    try:
        server.get_characteristic('0000ffd9-0000-1000-8000-00805f9b34fb').value = b'stop'
    except:
        print('Please Start server before closing ')



frame_1 = customtkinter.CTkFrame(master=app)
frame_1.pack(pady=20, padx=20, fill="both", expand=True)


# Use CTkButton instead of tkinter Button
button = customtkinter.CTkButton(master=frame_1, text="Start server", command=startsimulatorthread)
button.pack(pady=10, padx=10)


buttonStop = customtkinter.CTkButton(master=frame_1, text="Stop server", command=stopsimulatorthread)
buttonStop.pack(pady=10, padx=10)



def optionmenu_callback(choice):
    print("optionmenu dropdown clicked:", choice)
    '''
    if choice == 'option 1':
        entry.configure(state="normal")
    if choice == 'option 2':
        entry.configure(state="disabled")
    '''


optionmenu = customtkinter.CTkOptionMenu(master=frame_1, values=["Single value Random uint16 little endian", 
                                                                "Single value user defined uint16 little endian",
                                                                "Array of Random int16 little endian",
                                                                "Array of Random int16 big endian",
                                                                "User defined String"
                                                                ],
                                         command=optionmenu_callback)
optionmenu.pack(pady=10, padx=10)
optionmenu.set("Single value Random uint16 little endian")
#optionmenu.get()   # to get the value of variable

optionmenu2 = customtkinter.CTkOptionMenu(master=frame_1, values=["Read", "Notify"], command=optionmenu_callback)
optionmenu2.pack(pady=10, padx=10)


entry = customtkinter.CTkEntry(frame_1, placeholder_text="Enter your value")
entry.pack(pady=10, padx=10)
entry.configure(state="normal")


freq = customtkinter.CTkEntry(frame_1, placeholder_text="Enter Frequency")  # text field for entering frequency
freq.pack(pady=10, padx=10)
freq.configure(state="normal")


arrsize = customtkinter.CTkEntry(frame_1, placeholder_text="Array size(default 7)")
arrsize.pack(pady=10, padx=10)
arrsize.configure(state="normal")


def read_request(
        characteristic: BlessGATTCharacteristic,
        **kwargs
        ) -> bytearray:
    #logger.debug(f"Reading {characteristic.value}")
    return characteristic.value


def write_request(
        characteristic: BlessGATTCharacteristic,
        value: Any,
        **kwargs
        ):
    characteristic.value = value
    print(value)
    # implement decoding using following link
    # https://stackoverflow.com/questions/27657570/how-to-convert-bytearray-with-non-ascii-bytes-to-string-in-python

    #logger.debug(f"Char value set to {characteristic.value}")
    '''
    if characteristic.value == b'\x0f':
        logger.debug("NICE")
        trigger.set()
    '''

globalArraySize = 7
globalFrequency = 1

# this function checks if the uuid passed is valid
def checkUUID():
    pass

async def run(loop, opt = optionmenu, opt1 = optionmenu2): # the loop argument here is provided so that blessserver can be created on this event loop
    print("------------------------ SERVER has started ------------------------")
    
    trigger.clear()
    # Instantiate the server
    my_service_name = "Test Service"
    
    global server
    server = BlessServer(name=my_service_name, loop=loop)  # this is why we require the loop argument above in the function definition
    server.read_request_func = read_request
    server.write_request_func = write_request

    # Add Service
    #OTA_DATA_UUID = '23408888-1F40-4CD8-9B89-CA8D45F8A5B0'
    #OTA_CONTROL_UUID = '7AD671AA-21C0-46A4-B722-270E3AE3D830'
    # serviceOTA = 'd6f1d96d-594c-4c53-b1c6-144a1dfde6d8'
    my_service_uuid = "4fafc201-1fb5-459e-8fcc-c5c9c331914b"#"0000ffd5-0000-1000-8000-00805f9b34fb" #"0000ffd5-0000-1000-8000-00805f9b34fb" #"A07498CA-AD5B-474E-940D-16F1FBE7E8CD"
    await server.add_new_service(my_service_uuid)

#0000ffd9-0000-1000-8000-00805f9b34fb

    # Add a Characteristic to the service
    my_char_uuid = "0000b3a1-0000-1000-8000-00805f9b34fb" #"51FF12BB-3ED8-46E5-B4F9-D64E2FEC021B"
    char_flags = (
            GATTCharacteristicProperties.read |
            GATTCharacteristicProperties.notify |
            GATTCharacteristicProperties.indicate
            )
    permissions = (
            GATTAttributePermissions.readable
            )
    await server.add_new_characteristic(
            my_service_uuid,
            my_char_uuid,
            char_flags,
            None,
            permissions)

    my_char_uuid1 = "beb5483e-36e1-4688-b7f5-ea07361b26a8"
    char_flags1 = (
            GATTCharacteristicProperties.write
            )
    permissions1 = (
            GATTAttributePermissions.writeable
            )
    await server.add_new_characteristic(
            my_service_uuid,
            my_char_uuid1,
            char_flags1,
            None,
            permissions1)
    
 
    await server.start()
    while(server.get_characteristic(my_char_uuid1).value != b'stop'):     # b'\x0f'
        # Execute proper frequency
        try:
            x = int(freq.get())
            if x != 0:
                globalFrequency = x
            else:
                globalFrequency = 1
        except:
            globalFrequency = 1

        # Execute proper size of array
        try:
            x = int(arrsize.get())
            if x != 0:
                globalArraySize = x
            else:
                globalArraySize = 7
        except:
            globalArraySize = 7


        # read random integer 16 little
        if  opt.get() == 'Single value Random uint16 little endian' and opt1.get() == 'Read':
            x = server.get_characteristic(my_char_uuid)
            byte_array = ReadRandomInt16Little()
            x.value = byte_array
        
        # notify random integer 16 little
        if opt.get() == 'Single value Random uint16 little endian' and opt1.get() == 'Notify':
            x = server.get_characteristic(my_char_uuid)
            byte_array = NotifyRandomInt16Little()
            x.value = byte_array
            server.update_value(
                my_service_uuid, my_char_uuid
                )
        
        # read user integer 16 little
        if opt.get() == 'Single value user defined uint16 little endian' and opt1.get() == 'Read':
            x = server.get_characteristic(my_char_uuid)
            byte_array = ReadUserInt16Little()
            x.value = byte_array
        

        # notify user integer 16 little
        if opt.get() == 'Single value user defined uint16 little endian' and opt1.get() == 'Notify':
            x = server.get_characteristic(my_char_uuid)
            byte_array = NotifyUserInt16Little()
            x.value = byte_array
            server.update_value(
                my_service_uuid, my_char_uuid
                )
        

        # read user string
        if opt.get() == 'User defined String' and opt1.get() == 'Read':
            x = server.get_characteristic(my_char_uuid)
            byte_array = ReadUserString()
            x.value = bytearray(byte_array, 'utf-8')


        # notify random integer 16 little array
        
        if opt.get() == 'Array of Random int16 little endian' and opt1.get() == 'Notify':
            x = server.get_characteristic(my_char_uuid)
            byte_array = NotifyRandomArrayInt16Little(globalArraySize)
            x.value = byte_array
            server.update_value(
                my_service_uuid, my_char_uuid
                )
        

        # notify random integer 16 big array
        if opt.get() == 'Array of Random int16 big endian' and opt1.get() == 'Notify':
            x = server.get_characteristic(my_char_uuid)
            byte_array = NotifyRandomArrayInt16Big(globalArraySize)
            x.value = byte_array
            server.update_value(
                my_service_uuid, my_char_uuid
                )
        


        await asyncio.sleep(globalFrequency)
        

    #print('------------------------- outside while loop ------------------------------')

    

    #logger.debug("Advertising")
    #logger.info(f"Write '0xF' to the advertised characteristic: {my_char_uuid}")
    #trigger.wait(timeout=10)
    
    #await asyncio.sleep(40)
    #logger.debug("Updating")
    #server.get_characteristic(my_char_uuid)
    
    #print('--------------------- VALUE UPDATED --------------------------------')
    #x = server.get_characteristic(my_char_uuid)
    #x.value = bytearray('hello there', 'utf-8')
    
    #server.update_value(
    #        my_service_uuid, "51FF12BB-3ED8-46E5-B4F9-D64E2FEC021B"
    #        )
    print('------------- SERVER closed ಥ益ಥ -------------')
    #await asyncio.sleep(25)
    await server.stop()
    button.configure(state="normal")


def getRandomInteger8():
    # Generate a random uint8_t integer
    uint8_value = random.randint(0, ctypes.c_uint8(-1).value)
    return uint8_value

def getRandomInteger16():
    # Generate a random uint16_t integer
    uint16_value = random.randint(0, ctypes.c_uint16(-1).value)
    return uint16_value

def getUserInteger16():
    # Generate a random uint16_t integer
    #integer = int(input('Enter a uint16 value (0-65535): '))
    try:
        integer = int(entry.get())
        uint16_value = ctypes.c_uint16(integer).value
        return uint16_value
    except:
        print('Wrong integer entered')
        return None

def getRandomInteger32():
    # Generate a random uint32_t integer
    uint32_value = random.randint(0, ctypes.c_uint32(-1).value)
    return uint32_value

def ReadRandomInt16Little():
    value = getRandomInteger16()
    num_bytes = (value.bit_length() + 7) // 8  # Calculate the number of bytes required
    byte_array = value.to_bytes(num_bytes, 'little')  # Convert the integer to a bytearray
    return byte_array

def ReadUserInt16Little():
    value = getUserInteger16()
    
    try:
        if value < 256:
            print('You are writing a value that is not 2 bytes long which wont be read by uint16 option on Bluedash, try value above 256')
        else:
            num_bytes = (value.bit_length() + 7) // 8  # Calculate the number of bytes required
            byte_array = value.to_bytes(num_bytes, 'little')  # Convert the integer to a bytearray
            return byte_array
    except:
        return None

def NotifyRandomInt16Little():
    value = getRandomInteger16()
    num_bytes = (value.bit_length() + 7) // 8  # Calculate the number of bytes required
    byte_array = value.to_bytes(num_bytes, 'little')  # Convert the integer to a bytearray
    return byte_array

def NotifyUserInt16Little():
    value = getUserInteger16()
    try:
        num_bytes = (value.bit_length() + 7) // 8  # Calculate the number of bytes required
        byte_array = value.to_bytes(num_bytes, 'little')  # Convert the integer to a bytearray
        return byte_array
    except:
        return None

def NotifyRandomArrayInt16Little(arraysize):
    arraylist = []
    for i in range(arraysize):
        arraylist.append(getRandomInteger16())

    #value = getRandomInteger16()
    byte_array = struct.pack('<' + 'H' * len(arraylist), *arraylist)
    return byte_array

def NotifyRandomArrayInt16Big(arraysize):
    arraylist = []
    for i in range(arraysize):
        arraylist.append(getRandomInteger16())

    #value = getRandomInteger16()
    byte_array = struct.pack('>' + 'H' * len(arraylist), *arraylist)
    return byte_array

def ReadUserString():
    #value = input('Enter your text: ')
    usrString = entry.get()
    return usrString


#loop = asyncio.get_event_loop()     # event loop started
#loop.run_until_complete(run(loop))
app.mainloop()