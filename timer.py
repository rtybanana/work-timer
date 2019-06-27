from ctypes import Structure, windll, c_uint, sizeof, byref
from tkinter import Tk, Label, Button
from win10toast import ToastNotifier
import datetime


TIMEOUT_TIME = 120
NOTIFY_TIME = TIMEOUT_TIME - 10
IDLE_TIME = 300


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


class Timer:
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
        self.warning = False
        self.idle = False

        self.lbl_timer = Label(text="", font=("Courier", 40))
        self.lbl_timer.pack()
        self.update_clock()

        self.btn_pause = Button(text="Pause", width=6, command=lambda: self.pause())
        self.btn_pause.pack()

        self.root.mainloop()

    def update_clock(self):
        now = datetime.datetime.now() - self.start_time - self.paused_time
        hours, remainder = divmod(now.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        text = '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))
        self.lbl_timer.configure(text=text)

        # clock operating as normal
        if not self.paused and get_idle_duration() < NOTIFY_TIME:
            if self.warning:                            # reset warning toast flag if the user cancelled the auto pause
                self.warning = False
            self.root.after(1, self.update_clock)       # call self after one millisecond

        # warning toast that the timer is going to auto pause soon, user can activate an input to cancel auto pause
        elif NOTIFY_TIME <= get_idle_duration() < TIMEOUT_TIME:
            if not self.warning:
                toaster = ToastNotifier()
                toaster.show_toast("Are you still there?",
                                   "Wiggle your mouse to continue timing",
                                   icon_path=r'WorkTimer.ico',
                                   duration=5,
                                   threaded=True)
                self.warning = True
            self.root.after(1, self.update_clock)

        # timer auto pause and update_idle() called
        elif get_idle_duration() >= TIMEOUT_TIME:
            self.idle = True
            self.pause()
            self.update_idle()

    # function to monitor mouse and keyboard input to remind the user to restart the timer after a period of inactivity
    def update_idle(self):
        if get_idle_duration() < TIMEOUT_TIME and self.idle:
            toaster = ToastNotifier()
            toaster.show_toast("Welcome back",
                               "Remember to unpause the timer if you're restarting work",
                               icon_path=r'WorkTimer.ico',
                               duration=5,
                               threaded=True)
            self.idle = False
        elif get_idle_duration() > IDLE_TIME and not self.idle:
            self.idle = True

        self.root.after(1, self.update_idle)            # call self after one millisecond

    # pause function for hard coded function calls and also the pause button callback
    def pause(self):
        self.paused = not self.paused
        if self.paused is False:
            self.paused_time += datetime.datetime.now() - self.pause_timestamp
            self.btn_pause.config(text="Pause")
            self.update_clock()
        else:
            self.pause_timestamp = datetime.datetime.now()
            self.btn_pause.config(text="Start")
            self.update_idle()


app = Timer()
