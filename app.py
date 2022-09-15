import pandas as pd
from tkinter import Button, Frame, Tk, Label, messagebox , Toplevel
import matplotlib.dates
from datetime import date
import matplotlib.pyplot as plt

# define global variables and functions
datefmt = matplotlib.dates.DateFormatter("%d-%b-%Y  %H:%M:%S")
datefmt1 = matplotlib.dates.DateFormatter("%d-%b-%Y %H:%M:%S")

endDate = date(2022, 10, 15)
todayDate = date.today()

def handler(fig, ax, event):
    # Verify click is within the axes of interest
    if ax.in_axes(event):
        # Transform the event from display to axes coordinates
        ax_pos = ax.transAxes.inverted().transform((event.x, event.y))
        print(ax_pos)

class NewWindow(Toplevel):
     
    def __init__(self, master):
         
        super().__init__(master = master)
        self.title("New Window")
        self.geometry("200x200")
        label = Label(self, text ="This is a new Window")
        label.pack()


class MG:
    def __init__(self, master):
        self.df = None
        self.master = master
        myFrame = Frame(master)
        myFrame.pack()

        Label(master, text='').pack()

        Label(master, text='Please copy the data from the source you want but\nrespect the order \ndate ==> time ==> pressure ==> temperature\nthen after coping the data press load data button').pack()
        Label(master, text='').pack()

        self.loadBtn = Button(master, text='Load data', padx=10,
                              pady=10, command=self.show).pack()

        # Label(master, text='').pack()
        # Label(master, text='').pack()

        # self.loadOpt = Button(master, text='load options', padx=10,
        #                       pady=10)
        # self.loadOpt.bind("<Button>",
        #  lambda e: NewWindow(master)) 

        # self.loadOpt.pack()

        # Label(master, text='').pack()
        # Label(master, text='').pack()

        Label(master, text='Developed by Amr Gharieb\nEmail:- amr@amrgharieb.com\nMob:- +201003944053').pack()

    def show(self):

        self.df = self.prepareDate()

        # draw pressure temperature chart
        fig1, ax1 = plt.subplots(num=1)
        # fig2, ax2 = plt.subplots(num=2)

        self.drawPressureTemperatureChart(fig1, ax1,"Date","Gauge Temperature",'red',"Gauge Pressure",'navy',self.df)
        # self.drawPressureTemperatureChartDervatives(fig2, ax2,"Date","Gauge Temperature",'red',"Gauge Pressure",'navy',self.df)
        
        # self.saveToPickle()                     

        plt.show()

    def prepareDate(self):

        # data work
        self.df = pd.read_clipboard()
        self.df = self.df.set_axis(['Date', 'Time', 'Pressure',
                                    'Temperature'], axis=1, inplace=False)
        self.df['DateTime'] = pd.to_datetime(
            self.df.Date.astype(str)+' '+self.df.Time.astype(str))
        self.df.Pressure = self.df.Pressure.astype(float)
        self.df.Temperature = self.df.Temperature.astype(float)

        self.df['DateTime'] = pd.to_datetime(self.df['DateTime'])
        self.df['TimeDiffInSec'] = self.df.loc[:,
                                               'DateTime'].diff().dt.total_seconds()
        self.df['DeltaPressure'] = self.df.loc[:, 'Pressure'].diff()
        self.df['DeltaTemperature'] = self.df.loc[:, 'Temperature'].diff()
        self.df['TimeDiffCumInSec'] = self.df['TimeDiffInSec'].cumsum()
        self.df['TimeDiffCumInHrs'] = self.df['TimeDiffCumInSec'] / 3600
        self.df['DeltaPbyDeltaTime'] = self.df['DeltaPressure'] / \
            self.df['TimeDiffCumInHrs']

        return self.df

    def pressureTemperature_make_format(self, current, other):
        # current and other are axes
        def format_coord(x, y):
            # x, y are data coordinates
            # convert to display coords
            display_coord = current.transData.transform((x, y))
            inv = other.transData.inverted()
            # convert back to data coords with respect to ax
            ax_coord = inv.transform(display_coord)
            coords = [ax_coord, (x, y)]

            selectedDate = pd.to_datetime(datefmt1(float(coords[0][0])))
            try:
                fdf = self.df[pd.to_datetime(
                    self.df['DateTime']) >= selectedDate].iloc[0]
            except:
                fdf = None

            # s = f'{datefmt(coords[0][0])}, P = {int(coords[1][1])} , T = {int(coords[0][1])}'
            s = f'{fdf.DateTime}, P = {fdf.Pressure} , T = {fdf.Temperature}'

            return s
        return format_coord

    def pressureTemperatureOnClick(self, event, df):
        # print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
        #       ('double' if event.dblclick else 'single', event.button,
        #        event.x, event.y, event.xdata, event.ydata))
        # print(datefmt1(float(event.xdata)))
        selectedDate = pd.to_datetime(datefmt1(float(event.xdata)))
        fdf = df[pd.to_datetime(df['DateTime']) >= selectedDate].iloc[0]

        print(fdf)

    def drawPressureTemperatureChart(self, fig,ax,xlabel,ylabel,ylabel_color,y1label,y1label_color,df):

        fig.tight_layout()
        # pressure temperature plot
        # options
        ax.set_xlabel(xlabel, fontsize=14)
        ax.set_ylabel(ylabel, color=ylabel_color, fontsize=14)
        ax2 = ax.twinx()
        ax2.set_ylabel(y1label, color=y1label_color, fontsize=14)

        # ploting
        ax.plot(df.DateTime, df.Temperature, color=ylabel_color)
        ax2.plot(df.DateTime, df.Pressure, color=y1label_color)
        ax2.format_coord = self.pressureTemperature_make_format(ax2, ax)
        cid = fig.canvas.mpl_connect(
            'button_press_event', lambda e: self.pressureTemperatureOnClick(e, self.df))
        plt.gcf().canvas.set_window_title('Gauge pressure')

    def drawPressureTemperatureChartDervatives(self, fig,ax,xlabel,ylabel,ylabel_color,y1label,y1label_color,df):

        fig.tight_layout()
        # pressure temperature plot
        # options
        ax.set_xlabel(xlabel, fontsize=14)
        ax.set_ylabel(ylabel, color=ylabel_color, fontsize=14)
        ax2 = ax.twinx()
        ax2.set_ylabel(y1label, color=y1label_color, fontsize=14)

        # ploting
        ax.plot(df.DateTime, df.Temperature, color=ylabel_color)
        ax2.plot(df.DateTime, df.Pressure, color=y1label_color)
        ax2.format_coord = self.pressureTemperature_make_format(ax2, ax)
        cid = fig.canvas.mpl_connect(
            'button_press_event', lambda e: self.pressureTemperatureOnClick(e, self.df))
        plt.gcf().canvas.set_window_title('Gauge pressure')

    def saveToPickle(self):
        self.df.to_pickle('savedFile' + '.pkl', \
                                              compression='gzip')



root = Tk()
root.iconbitmap(r'C:\\Users\\Amr Ghrib\\Desktop\\MG\\line.ico')
root.geometry('300x300')
root.eval('tk::PlaceWindow . center')
root.resizable(False, False)
root.title('Memory Gauge Viewer')

if(todayDate > endDate):
    messagebox.showerror(
        title='Expired', message='the program expired\ncontact the developer\n+201003944053\namr@amrgharieb.com')
    root.destroy()

mg = MG(root)

root.mainloop()


