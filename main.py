from wnd import Wnd
from klasa_gml import egb_dzialka, egb_uzytki_grunt

if __name__ == '__main__':
    window = Wnd("Projekt 2", egb_dzialka, egb_uzytki_grunt)
    window.mainloop()
