import tkinter as tk
import customtkinter as ctk
import matplotlib.pyplot as plt
import shapely.geometry
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.textpath import TextPath
from matplotlib.patches import PathPatch
from show_info import TopLevel

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")
plt.style.use('dark_background')
dz_color = ['#69b3de', '#8ad5ff']
bud_color = ['#fa8174']
u_color = ['#b1d281', '#a0c170']
checkbox_pady = {'sticky': 'w', 'padx': 15, 'pady': 5}
tog_btn_pady = {'padx': 5, 'ipadx': 10, 'ipady': 10}


class Wnd(ctk.CTk):
    def __init__(self, title, dzialki, uzytki):
        super().__init__()
        self.title(title)
        self.dzialki = dzialki
        self.uzytki = uzytki
        self.geometry('1200x650')
        self.chosen_plot = False
        self.pressed = None
        self.xlim = None
        self.ylim = None
        self._set_window()
        self.plot_info = {}
        self.text_info = {}
        self.bud_info = {}
        self.uzytki_info = []
        self.plot()
        self.default_lim = (self.ax.get_xlim(), self.ax.get_ylim())
        self.ax.set_axis_off()

    def _set_window(self):
        """
        txt_frame - ramka do labels, buttons itd
        plot_frame - wyswietlanie
        ustawienia canvas do rysowania
        """
        txt_frame = ctk.CTkFrame(self)
        txt_frame.pack(side='left', expand=False, padx=15, pady=20, fill='y')
        self.tabs = ctk.CTkTabview(txt_frame, width=400)
        self.tabs.pack(fill='both', expand=True)
        plot_frame = ctk.CTkFrame(self)
        plot_frame.pack(side='right', expand=True, fill='both', padx=10, pady=20)
        self.fig = plt.Figure(figsize=(20, 20))
        self.fig.patch.set_color('#0B0B0B')
        self.fig.canvas.mpl_connect('scroll_event', self.zoom)
        self.fig.canvas.mpl_connect('button_press_event', self.mouse_button)
        self.fig.canvas.mpl_connect('motion_notify_event', self.motion)
        self.fig.canvas.mpl_connect('button_release_event', self.release)
        self.fig.canvas.mpl_connect('key_press_event', self.key_press)
        self.ax = self.fig.add_subplot()
        self.fig.subplots_adjust(top=1, bottom=0.001, left=0, right=0.999)
        self.ax.set_aspect('equal', anchor='SW', adjustable='datalim')
        self.canvas = FigureCanvasTkAgg(self.fig, plot_frame)
        self.canvas.get_tk_widget().pack()

    def plot(self):
        """rysowanie działek, budynków i użytków"""
        dane_len = len(self.dzialki.keys())
        dzialki_tab = self.tabs.add('Dzialki')
        budynki_tab = self.tabs.add('Budynki')
        self.plot_uzytki()
        b_row = 0
        dzialki_frame = ctk.CTkFrame(dzialki_tab, fg_color="#333333")
        dzialki_frame.pack(fill='both', expand=True, anchor='n', pady=10)
        bud_frame = ctk.CTkFrame(budynki_tab, fg_color="#333333")
        bud_frame.pack(expand=True, anchor='n', pady=10)
        for j, key in enumerate(sorted(self.dzialki.keys())):
            c = j // ((dane_len + 1) // 2)
            r = j if c == 0 else j - (dane_len + 1) // 2
            dzialka = self.dzialki[key]
            self.plot_chcekbox(dzialka, dz_color, r, c, dzialki_frame, self.plot_info)
            bud = dzialka.budynek()
            if bud:
                self.plot_chcekbox(bud, bud_color, b_row, 0, bud_frame, self.bud_info, bud=True)
                b_row += 1
        self.toggle_buttons(dzialki_tab, self.plot_info, dane_len)
        self.toggle_buttons(budynki_tab, self.bud_info, dane_len)
        self.canvas.draw()

    def plot_uzytki(self):
        uzytki_tab = self.tabs.add('Użytki gruntowe')
        for u in self.uzytki:
            u_pl, = self.ax.plot(*poly_xy(u['geom']), c=u_color[0])
            self.uzytki_info.append(u_pl)
            point = u['geom'].representative_point()
            self.uzytki_info.append(self.plot_txt(u['ofu'], (point.x, point.y - 1.5), u_color[1], 0.6))
        uzytki_bool = tk.BooleanVar(value=True)
        cb = ctk.CTkCheckBox(uzytki_tab, text=f'UŻYTKI GRUNTOWE', variable=uzytki_bool,
                             command=lambda b=uzytki_bool: self.toggle_uzytki(b))
        cb.pack(anchor='n', pady=10)

    def plot_chcekbox(self, shape, color, row, col, tab, info, bud=False):
        plot = self.ax.plot(*poly_xy(shape.geom), c=color[0])[0]
        if bud:
            plot = self.plot_blok(plot, shape)
        else:
            point = shape.geom.representative_point()
            self.text_info[shape.id] = self.plot_txt(shape.id, (point.x - 8, point.y), color[1], 1, zorder=3)
        bool_var = tk.BooleanVar(value=True)
        info[shape.id] = [plot, bool_var]
        cb = ctk.CTkCheckBox(tab, text=f'{shape.id}', variable=bool_var,
                             command=lambda k=shape.id: self.toggle(info[k][1].get(), [k]))
        cb.grid(row=row, column=col, **checkbox_pady)

    def plot_blok(self, plot, shape):
        plot = [plot]
        bud_blok = shape.blok()
        if bud_blok:
            for blok in bud_blok:
                plot.append(self.ax.plot(*poly_xy(blok['geom']), c=bud_color[0])[0])
        return plot

    def plot_txt(self, text, xy, color, alpha, zorder=1):
        txt = TextPath(xy, text, size=1.5)
        patch = self.ax.add_patch(PathPatch(txt, color=color, alpha=alpha, zorder=zorder))
        return patch

    def toggle_buttons(self, tab, info, row):
        button_frame = ctk.CTkFrame(tab, fg_color="#333333")
        button_frame.pack(side='bottom', expand=False, anchor='s', ipady=5)
        ctk.CTkButton(button_frame, text='Zaznacz wszytskie',
                      command=lambda: self.toggle(True, info.keys())).pack(side='left', anchor='e', **tog_btn_pady)
        ctk.CTkButton(button_frame, text='Odznacz wszytskie',
                      command=lambda: self.toggle(False, info.keys())).pack(side='right', anchor='w', **tog_btn_pady)

    def zoom(self, event):
        """zoomowanie myszką"""
        factor = 0.8 if event.button == 'up' else 1.2
        new_xlim = get_lim(self.ax.get_xlim(), event.xdata, factor)
        new_ylim = get_lim(self.ax.get_ylim(), event.ydata, factor)
        self.ax.set_xlim(new_xlim)
        self.ax.set_ylim(new_ylim)
        self.canvas.draw()

    def key_press(self, event):
        """'Esc': resetuj zoom"""
        if event.key == 'escape':
            self.ax.set_xlim(self.default_lim[0])
            self.ax.set_ylim(self.default_lim[1])
            self.canvas.draw()

    def mouse_button(self, event):
        if event.button == plt.MouseButton.LEFT:
            self.pressed = (event.x, event.y)
            self.xlim = self.ax.get_xlim()
            self.ylim = self.ax.get_ylim()

    def motion(self, event):
        """przesuwanie myszką"""
        try:
            if event.button == plt.MouseButton.LEFT:
                fig_size = self.fig.get_size_inches() * self.fig.dpi
                self.ax.set_xlim(get_dist(self.xlim, fig_size[0], event.x, self.pressed[0]))
                self.ax.set_ylim(get_dist(self.ylim, fig_size[1], event.y, self.pressed[1]))
                self.canvas.draw()
        except TypeError:
            pass

    def release(self, event):
        """wybieranie działki przez kliknięcie"""
        if event.button == plt.MouseButton.LEFT:
            if self.pressed == (event.x, event.y):
                self.pressed = None
                x = event.xdata
                y = event.ydata
                if x and y:
                    if self.chosen_plot:
                        self.toggle(True, self.plot_info.keys())
                        self.chosen_plot = False
                    else:
                        self.show_one(x, y)
                        self.chosen_plot = True

    def show_one(self, x, y):
        point = shapely.geometry.Point((x, y))
        for key in self.dzialki.keys():
            if point.within(self.dzialki[key].geom):
                self.toggle(False, self.plot_info.keys())
                self.toggle(True, [key])
                TopLevel(self, self.dzialki[key], True)
                TopLevel(self, self.dzialki[key], False)
                break

    def toggle(self, value, plots):
        for key in plots:
            if key in self.bud_info:
                self.toggle_budynek(key, value)
            else:
                self.toggle_dzialka(key, value)
                bud = self.dzialki[key].budynek()
                if bud:
                    self.toggle_budynek(bud.id, value)
        self.canvas.draw()

    def toggle_dzialka(self, key, value):
        self.text_info[key].set_alpha(int(value))
        self.plot_info[key][0].set_alpha(int(value))
        self.plot_info[key][1].set(value)

    def toggle_budynek(self, key, value):
        for i in self.bud_info[key][0]:
            i.set_alpha(int(value))
        self.bud_info[key][1].set(int(value))

    def toggle_uzytki(self, param):
        value = param.get()
        for u in self.uzytki_info:
            u.set_alpha(int(value))
        self.canvas.draw()


def get_lim(lim, data, factor):
    l_dist = (data - lim[0]) * factor
    r_dist = (lim[1] - data) * factor
    return data - l_dist, data + r_dist


def get_dist(lim, fig_size, xy, pressed_xy):
    dist = (lim[1] - lim[0]) / fig_size * (xy - pressed_xy)
    return lim[0] - dist, lim[1] - dist


def poly_xy(poly):
    return poly.exterior.xy
