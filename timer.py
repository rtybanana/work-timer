from ctypes import Structure, windll, c_uint, sizeof, byref
from tkinter import Tk, Label, Button
from win10toast import ToastNotifier
import datetime


def get_idle_duration():
    lastInputInfo = LASTINPUTINFO()
    lastInputInfo.cbSize = sizeof(lastInputInfo)
    windll.user32.GetLastInputInfo(byref(lastInputInfo))
    millis = windll.kernel32.GetTickCount() - lastInputInfo.dwTime
    return millis / 1000.0


class LASTINPUTINFO(Structure):
    _fields_ = [
        ('cbSize', c_uint),
        ('dwTime', c_uint),
    ]

NOTIFY_TIME = 110
TIMEOUT_TIME = 120


class App:
    def __init__(self):
        self.root = Tk()
        self.root.title("Work Timer")
        self.root.geometry("300x100")
        self.root.resizable(0, 0)
        self.root.iconbitmap(r'WorkTimer.ico')

        self.start_time = datetime.datetime.now()
        self.pause_timestamp = 0
        self.paused_time = datetime.timedelta(0)
        self.paused = False
        self.idle = False

        self.lbl_timer = Label(text="", font=("Courier", 40))
        self.lbl_timer.pack()
        self.update_clock()

        self.btn_pause = Button(text="Pause", width=6, command=lambda: self.pause())
        self.btn_pause.pack()

        self.root.mainloop()

    def pause(self):
        self.paused = not self.paused
        if self.paused is False:
            self.paused_time += datetime.datetime.now() - self.pause_timestamp
            self.update_clock()
            self.btn_pause.config(text="Pause")
        else:
            self.pause_timestamp = datetime.datetime.now()
            self.btn_pause.config(text="Start")

    def update_clock(self):
        now = datetime.datetime.now() - self.start_time - self.paused_time
        hours, remainder = divmod(now.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        text = '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))
        self.lbl_timer.configure(text=text)

        if not self.paused and get_idle_duration() < TIMEOUT_TIME:
            self.root.after(1, self.update_clock)
        elif get_idle_duration() >= NOTIFY_TIME:
            self.clock_timeout()

        elif get_idle_duration() >= TIMEOUT_TIME:
            self.idle = True
            self.pause()
            self.update_idle()

    def clock_timeout(self):
        notified = False
        if not notified:
            toaster = ToastNotifier()
            toaster.show_toast("Are you still there?",
                               "Wiggle your mouse to continue timing",
                               icon_path=r'WorkTimer.ico',
                               duration=10,
                               threaded=True)
            notified = True
        if get_idle_duration() > 120:
            self.update_idle()

    def update_idle(self):
        toaster = ToastNotifier()
        if get_idle_duration() < 120 and self.idle:
            toaster.show_toast("Welcome back",
                               "Remember to unpause the work timer if you're restarting work",
                               icon_path=r'WorkTimer.ico',
                               threaded=True)
            self.idle = False
        elif get_idle_duration() > 300 and not self.idle:
            self.idle = True

        self.root.after(1, self.update_idle)


app = App()
