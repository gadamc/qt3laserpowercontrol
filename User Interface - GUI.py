from tkinter import *
import tkinter.font as font

import matplotlib.animation as animation
import matplotlib.pyplot as plt

import datetime as dt
import time
import serial

ser = serial.Serial()
ser.port = 'COM7'
ser.baudrate = 115200
ser.open()

window = Tk()

window.title('Microscope Power')
window.geometry("600x400+250+150")

# Main Label
lblfont = font.Font(family = 'Helvetica', size = 25, weight = 'bold')
lbl = Label(window, text = "Set/Read Laser Power", fg = 'black', font = lblfont)
lbl.config(anchor = CENTER)
lbl.pack()

output = Label(window, text = '', font = ('Helvetica', 16))
output.place(x = 240, y = 188)
def readPower():
    # single
    if (v0.get() == 1):
        ser.flushInput()
        ser.write('rp\r'.encode())
        # when you send a command, there is an echo, so need to ignore it
        ser.read_until(b'\r')
        # desired power value
        ret = ser.read_until(b'\r')
        ret = ret.decode().strip()
        if (ret.startswith('current power:')):
            processed = ret.split(':')
            ret = float(processed[1])
            output.config(text = str(ret) + ' mW')
            window.update()
    # continuous
    else:
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        xs = []
        ys = []

        def animate(i, xs, ys):
            ser.flushInput()
            power = ser.write('rp\r'.encode())
            # ignores echo and strip white sapce
            ser.read_until(b'\r')
            value = ser.read_until(b'\r')
            value = value.decode().strip()
            #printSomething(value)
            if (value.startswith('current power:')):
                # have to split to get numerical value
                processed = value.split(':')
                value = processed[1]

                xs.append(dt.datetime.now().strftime('%H:%M:%S'))
                # value is a string, need to convert o float
                ys.append(float(value))

                # Limit x and y lists to 20 items
                xs = xs[-20:]
                ys = ys[-20:]

                # Draw x and y lists
                ax.clear()
                ax.plot(xs, ys)

                # Format plot
                plt.xticks(rotation = 45, ha = 'right')
                plt.subplots_adjust(bottom = 0.30)
                plt.title('Microscope Power')
                plt.ylabel('Power (mW)')

        # Set up plot to call animate() function periodically
        ani = animation.FuncAnimation(fig, animate, fargs = (xs, ys), interval = 1000)
        plt.show()

# Read Power Button and Radio Button
btnFont = font.Font(family = 'Helvetica', size = 16, weight = 'normal')
btn = Button(window, text = "read power", font = btnFont, fg = 'black', width = 10, height = 1, activebackground = '#345', relief = 'raised', borderwidth = 3, command = readPower) # can add command attribute to indicate function to be called when clicked
btn.place(x = 50, y = 180)

v0 = IntVar()
v0.set(1)
r1 = Radiobutton(window, text = 'single', font = ('Helvetica', 12), variable = v0, value = 1)
r2 = Radiobutton(window, text = 'continuous', font = ('Helvetica', 12), variable = v0, value = 2)
r1.place(x = 48, y = 240)
r2.place(x = 115, y = 240)

result = Label(window, text = '', font = ('Helvetica', 12))
result.place(x = 430, y = 310)
def setPower():
    desiredPower = txtfld.get()
    ser.write('sp {}\r'.format(desiredPower).encode())
    ser.read_until(b'\r')
    ret = ser.read_until(b'\r')
    ret = ret.decode().strip()
    result.config(text = ret)
    window.update()
    # to clear entry field: txtfld.delete(0, END)

# set power entry box
lbl1 = Label(window, text = 'enter desired power:', fg = 'black', font = ('Helvetica', 14))
lbl1.place(x = 45, y = 307)
lbl2 = Label(window, text = 'mW', fg = 'black', font = ('Helvetica', 14))
lbl2.place(x = 300, y = 307)

txtfld = Entry(window, bd = 5, width = 8)
txtfld.place(x = 240, y = 310)

# set power button
btn1 = Button(window, text = 'set', font = btnFont, fg = 'black', width = 3, height = 1, activebackground = '#345', relief = 'raised', borderwidth = 3, command = setPower)
btn1.place(x = 370, y = 299)

output1 = Label(window, text = 'Min:', font = ('Helvetica', 16))
output1.place(x = 240, y = 83)
output2 = Label(window, text = 'Max:', font = ('Helvetica', 16))
output2.place(x = 240, y = 113)
def getRange():
    ser.write('pr\r'.encode())
    ser.read_until(b'\r') # gets rid of echo
    ret = ser.read_until(b'\r')
    ret = ret.decode().strip()
    processed = ret.split(',') # format of return is [min val], [max val]
    output1.config(text = "Min: " + processed[0] + " mW")
    output2.config(text = "Max: " + processed[1] + " mW")

# power range button (min/max)
btn2 = Button(window, text = 'get range', font = btnFont, fg = 'black', width = 10, height = 1, activebackground = '#345', relief = 'raised', borderwidth = 3, command = getRange)
btn2.place(x = 50, y = 90)

# reset button
def reset():
    txtfld.delete(0, END)
    v0.set(1)
    output.config(text = '')
    result.config(text = '')
    output1.config(text = 'Min:')
    output2.config(text = 'Max:')

btnReset = Button(text = 'reset', font = btnFont, command = reset)
btnReset.place(x = 5, y = 5)

window.mainloop()

#except:
#    ser.close()
