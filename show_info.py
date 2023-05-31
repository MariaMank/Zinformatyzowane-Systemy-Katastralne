import customtkinter as ctk

EGB_statusBudynku = {'1': 'wybudowany', '2': 'w budowie', '3': 'budynek do rozbiórki', '4': 'projektowany'}
EGB_rodzajWgKST = {'101': 'budynek przemyslowy',
                   '102': 'budynek transportu i łącznosci',
                   '103': 'budynek handlowo - usługowy',
                   '104': 'zbiornik, silos i budynek magazynowy',
                   '105': 'budynek biurowy',
                   '106': 'budynek szpitala i innej opieki zdrowotnej',
                   '107': 'budynek oświaty, nauki i kultury oraz sportu ',
                   '108': ' budynek produkcyjny, usługowy i gospodarczy',
                   '109': 'pozostały budynek niemieszkalny',
                   '110': 'budynek mieszkalny'}
EGB_glownaFunkcjaBudynku = {'1110.Dj': 'budynek jednorodzinny',  # wzielam tylko te co wystepuja bo tego jest milion
                            '1242.Gr': 'garaż jednopoziomowy',
                            '1274.In': 'budynek nie określony innym atrybutem FSB',
                            'template': ''}
EGB_klasaWgPKOB = {'1110': 'budynki mieszkalne jednorodzinne',
                   # tutaj tak samo, ale nie dlateg ze duzo, tylko mi sie nie chcialo xd
                   '1274': 'pozostałe bydynki niemieszkalne',
                   '1242': 'budynki garaży'}

EGB_materialScian = {'1': 'mur',
                     '2': 'drewno',
                     '3': 'inny'}
EGB_zrodloDaty = {'1': 'dokument',
                  '2': 'żródło niepotwierdzone',
                  '3': 'szacowana'}

nowe_standard_dokl = {}
nowy_sposob_pozyskania = {}

for i in range(1, 10):
    if i in (1, 3, 5, 6, 9):
        nowy_sposob_pozyskania[str(i)] = 'ustalony'
    else:
        nowy_sposob_pozyskania[str(i)] = 'nie ustalony'

for i in range(1, 7):
    if i > 2:
        nowe_standard_dokl[str(i)] = 'nie spełnia'
    else:
        nowe_standard_dokl[str(i)] = 'spełnia'

style = {'width': 350,
         'height': 20,
         'fg_color': ('#0B0B0B', '#373A4A'),
         'corner_radius': 5,
         'anchor': 'w',
         'justify': 'left'}

wlasciciel_style = {'width': 350,
                    'height': 30,
                    'fg_color': ('#0B0B0B', '#2b2d42'),
                    'corner_radius': 5,
                    'anchor': 'center',
                    'justify': 'center'}


class TopLevel(ctk.CTkToplevel):
    """Wyświetlanie danych przedmiotowych i podmiotowych dla dzialki i budynku oraz numeryczny opis granic"""

    def __init__(self, wnd, dzialka, old_verison):
        super().__init__(wnd)
        self.geometry('850x500')
        nie = 'NIE' if old_verison else ''
        self.title(f'{nie}AKTUALNE_{dzialka.id}')
        self.dzialka = dzialka
        self.punkty_tab = []
        self.old_verison = old_verison
        pop_tabs = ctk.CTkTabview(self, width=400, height=100)
        pop_tabs.pack(fill='both', expand=True)
        self.dzialka_tab = pop_tabs.add('Dzialka')
        self.dzialka_info()
        if dzialka.budynek():
            self.budynek = dzialka.budynek()
            self.budynek_tab = pop_tabs.add('Budynek')
            self.budynek_info()
        self.podmiot_tab = pop_tabs.add('Podmiot')
        self.podmiot_info()

    def dzialka_info(self):
        scroll_dzialka = ctk.CTkFrame(self.dzialka_tab, fg_color="#2a2a2a")
        scroll_dzialka.pack(side='left', expand=True, fill="both", ipady=10)
        labels = self.labels_dzialka()
        if self.old_verison:
            idx = [i for i in range(9)]
        else:
            idx = [0, 1, 2, 5, 6, 9, 4]
        self.add_attributes(scroll_dzialka, labels, idx)
        label = ctk.CTkLabel(self.dzialka_tab, text='numeryczny opis granic:', **style)
        label.pack(fill='both', ipady=5, pady=5, expand=False, anchor='n', side='top')
        pkt = ctk.CTkTabview(self.dzialka_tab, width=450)
        for i in range(len(self.dzialka.punkty_graniczne())):
            self.punkty_tab.append(pkt.add(f'{i}'))
        pkt.pack(fill='both', expand=True, anchor='s', side='bottom')
        self.add_border_points()

    def budynek_info(self):
        labels_budynek = self.labels_budynek()
        if self.old_verison:
            idx = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
            idx_2 = [13, 14, 15, 16, 17, 18, 19, 20, 23]
            scroll_budynek = ctk.CTkFrame(self.budynek_tab, fg_color="#2a2a2a")
            scroll_budynek.pack(side='left', expand=True, fill="both", ipady=10)
            self.add_attributes(scroll_budynek, labels_budynek, idx)
            scroll_budynek_2 = ctk.CTkFrame(self.budynek_tab, fg_color="#2a2a2a")
            scroll_budynek_2.pack(side='left', expand=True, fill="both", ipady=10)
            self.add_attributes(scroll_budynek_2, labels_budynek, idx_2)
        else:
            idx = [0, 1, 4, 8, 9, 21, 22]
            scroll_budynek = ctk.CTkFrame(self.budynek_tab, fg_color="#2a2a2a")
            scroll_budynek.pack(side='left', expand=True, fill="both", ipady=10)
            self.add_attributes(scroll_budynek, labels_budynek, idx)

    def podmiot_info(self):
        podmiot_info = self.dzialka.podmiot()
        osoba_info = podmiot_info[0]
        labels_osoba = self.labels_podmiot(podmiot_info)

        scroll_udzial = ctk.CTkFrame(self.podmiot_tab, fg_color="#2a2a2a")
        scroll_udzial.pack(side='bottom', expand=True, fill="both", ipady=10)
        if list(podmiot_info[1][osoba_info[0]['lokalnyId']])[0] == 'adresInstytucji':
            idx = [0, 1, 2, 3]
        else:
            idx = [0, 1, 2, 3, 4, 5, 6, 7, 8]
        for i, labelka in enumerate(labels_osoba):
            if len(labels_osoba) == 1:
                scroll_osoba = ctk.CTkFrame(self.podmiot_tab, fg_color="#2a2a2a")
                scroll_osoba.pack(side='top', expand=True, fill="both", ipady=10)
            else:
                scroll_osoba = ctk.CTkFrame(self.podmiot_tab, fg_color="#2a2a2a")
                scroll_osoba.pack(side='left', expand=True, fill="both", ipady=10)
                label = ctk.CTkLabel(master=scroll_osoba, text='Właściciel' + ' ' + str(i + 1), wraplength=400,
                                     **wlasciciel_style)
                label.pack(padx=5, pady=5, expand=True, fill='both')
            self.add_attributes(scroll_osoba, labelka, idx)

        label_2 = ctk.CTkLabel(master=scroll_udzial,
                               text=f"udział własności: {self.dzialka.udzial['licznikUlamkaOkreslajacegoWartoscUdzialu']}/{self.dzialka.udzial['mianownikUlamkaOkreslajacegoWartoscUdzialu']}",
                               wraplength=400,
                               **{'width': 350,
                                  'height': 20,
                                  'fg_color': ('#0B0B0B', '#373A4A'),
                                  'corner_radius': 5,
                                  'anchor': 'center',
                                  'justify': 'center'})
        label_2.pack(padx=5, pady=5, expand=True, fill='both')
        label_3 = ctk.CTkLabel(master=scroll_udzial, text=f"data uzyskania praw: {self.dzialka.udzial['waznoscOd']}",
                               wraplength=400,
                               **{'width': 350,
                                  'height': 20,
                                  'fg_color': ('#0B0B0B', '#373A4A'),
                                  'corner_radius': 5,
                                  'anchor': 'center',
                                  'justify': 'center'})
        label_3.pack(padx=5, pady=5, expand=True, fill='both')

    def add_border_points(self):
        for i in range(len(self.punkty_tab)):
            dane = self.dzialka.punkty_graniczne()[i]
            wsp = dane.get('geom')
            idik = dane.get('idPunktu')
            sposob_poz = dane.get('zrodloDanychZRD')
            standard = dane.get('bladPolozeniaWzgledemOsnowy')
            stab = dane.get('kodStabilizacji')
            ozn = dane.get('oznWMaterialeZrodlowym')
            operat = dane.get('dodatkoweInformacje')
            if self.old_verison == False:
                standard = nowe_standard_dokl[standard]
                sposob_poz = nowy_sposob_pozyskania[sposob_poz]
            add_label('współrzędne: {}'.format(wsp), self.punkty_tab[i])
            add_label('identyfikator: {}'.format(idik), self.punkty_tab[i])
            add_label('sposób pozyskania danych: {}'.format(sposob_poz), self.punkty_tab[i])
            add_label('spełnienie standardów dokł.: {}'.format(standard), self.punkty_tab[i])
            add_label('rodzaj stabilizacji: {}'.format(stab), self.punkty_tab[i])
            add_label('oznaczenie w materiale źródłowym: {}'.format(ozn), self.punkty_tab[i])
            add_label('{}'.format(operat), self.punkty_tab[i])

    def labels_dzialka(self):
        dod_info = self.dzialka.info.get('dodatkoweInformacje')
        if dod_info:
            dod_info = dod_info.replace(':', ':\n')
            dod_info = dod_info.replace(';', '\n')
        else:
            dod_info = 'inne dokumenty określające prawa:'
        kw = self.dzialka.info.get('numerElektronicznejKW')
        klasy = 'gleboznawczych' if self.old_verison else 'bonitacyjnych'
        return (f'identyfikator działki: {self.dzialka.id}',
                f"pole powierzchni: {self.dzialka.info['powierzchniaEwidencyjna']}",
                f'informacje o konturach użytków i klasach {klasy}:\n{self.dzialka.klasouzytek()}',
                f"wartość i data określenia: {self.dzialka.info['wartoscGruntu']}, {self.dzialka.info['dataWyceny']}",
                f"nr jednostki rejestrowej gruntów: {self.dzialka.JRG}",
                f"oznaczenie księgi wieczystej lub dok. określających własność: {kw if kw else ' '}",
                f"{dod_info}",
                f"nr rejestru zabytków: {self.dzialka.info['nrRejestruZabytkow']}",
                f"id rejonu statystycznego: {self.dzialka.info['idRejonuStatystycznego']}",
                f"adres:\n{self.dzialka.adres()}")

    def labels_budynek(self):
        # kontur = str(self.budynek.info['geom'])[10:-2]
        # print(kontur)
        return (f'identyfikator budynku: {self.budynek.id}',
                f"pole powierzchni zabudowy: {self.budynek.info['powZabudowy']}",
                f"rok zakończenia budowy: {self.budynek.info['rokZakonczeniaBudowy']}",
                f"status budynku: {EGB_statusBudynku[self.budynek.info['statusBudynku']]}",
                f"rodzaj według KST: {EGB_rodzajWgKST[self.budynek.info['rodzajWgKST']]}",
                f"główna funkcja budynku: {EGB_glownaFunkcjaBudynku[self.budynek.info['glownaFunkcjaBudynku']]}",
                f"data wyceny: {self.budynek.info['dataWyceny']}",
                f"klasa według PKOB: {EGB_klasaWgPKOB[self.budynek.info['klasaWgPKOB']]}",
                f"liczba kondygnacji nadziemnych: {self.budynek.info['liczbaKondygnacjiNadziemnych']}",
                f"liczba kondygnacji podziemnych: {self.budynek.info['liczbaKondygnacjiPodziemnych']}",
                f"powierzchnia użytkowa pomieszczeń przynależnych do lokali: {self.budynek.info['powierzchniaUzytkowaPomieszczenPrzynaleznychDoLokali']}",
                f"liczba ujawnionych samodzielnych lokali: {self.budynek.info['liczbaUjawnionychSamodzielnychLokali']}",
                f"materiał ścian zewnętrznych budynku: {EGB_materialScian[self.budynek.info['materialScianZewn']]}",
                f"numer rejestru zabytków: {self.budynek.info['numerRejestruZabytkow']}",
                f"wartość budynku: {self.budynek.info['wartoscBudynku']}",
                f"stopień pewności ustalenia daty budowy: {EGB_zrodloDaty.get(self.budynek.info.get('stopienPewnosciUstaleniaDatyBudowy'))}",
                f"stan użytkowania budynku: {self.budynek.info['stanUzytkowaniaBudynku']}",
                f"data rozbiórki budynku: {self.budynek.info['dataRozbiorkiBudynku']}",
                f"przyczyna rozbiórki budynku: {self.budynek.info['przyczynaRozbiorkiBudynku']}",
                f"czy wiata: {self.budynek.info['czyWiata']}",
                f"adres:\n{self.budynek.adres()[0]}",
                f"adres:\n{self.budynek.adres()[1]}",
                f"id działki na której znajduje się budynek:{self.dzialka.id}",
                f"numeryczny opis konturu budynku:\n{self.budynek.geom}")

    def labels_podmiot(self, podmiot_info):
        osoba_info = podmiot_info[0]
        adres_info = podmiot_info[1]
        wiecej_osob = []
        if list(adres_info[osoba_info[0]['lokalnyId']])[0] == 'adresOsobyFizycznej':
            for i, osoba in enumerate(osoba_info):
                adres = adres_info[osoba['lokalnyId']]
                adres = adres[list(adres.keys())[0]]
                nr = adres['nrLokalu']
                slash = "\\"
                label_adres = f"ul. {adres['ulica']} {adres['numerPorzadkowy']}{slash + nr if nr != 'missing' else ''}" \
                              f"\n{adres['kodPocztowy']} {adres['miejscowosc']}" \
                              f"\npowiat: {adres['powiat']}" \
                              f"\nwojewództwo: {adres['wojewodztwo']}"
                drugi_czlon = osoba['drugiCzlonNazwiska']
                dlugie_nazw = ' - ' + drugi_czlon if drugi_czlon != 'inapplicable' else ''
                plec = 'mężczyzna' if osoba['plec'] == '1' else 'kobieta'
                labels = (f"imię: {osoba['pierwszeImie']}",
                          f"drugie imię: {osoba['drugieImie']}",
                          f"nazwisko: {osoba['pierwszyCzlonNazwiska'] + dlugie_nazw}",
                          f"płeć: {plec}", f"PESEL: {osoba['pesel']}", f"imię matki: {osoba['imieMatki']}",
                          f"imię ojca: {osoba['imieOjca']}",
                          f"nr dokumentu tożsamości: {osoba['oznDokumentuStwierdzajacegoTozsamosc']}",
                          f"adres: {label_adres}")
                wiecej_osob.append(labels)
        else:
            adres = adres_info[osoba_info[0]['lokalnyId']]
            osoba = osoba_info[0]
            adres = adres[list(adres.keys())[0]]
            nr = adres['nrLokalu']
            slash = "\\"
            label_adres = f"ul. {adres['ulica']} {adres['numerPorzadkowy']}{slash + nr if nr != 'missing' else ''}" \
                          f"\n{adres['kodPocztowy']} {adres['miejscowosc']}" \
                          f"\npowiat: {adres['powiat']}" \
                          f"\nwojewództwo: {adres['wojewodztwo']}"
            label = (f"nazwa: {osoba['nazwaPelna']}",
                     f"REGON: {osoba['regon']}",
                     f"NIP: {osoba['nip']}",
                     f"adres: {label_adres}")
            wiecej_osob.append(label)
        return wiecej_osob

    def add_attributes(self, scroll, labels, idx):
        j = 1
        for i in idx:
            if j == 2:
                j += 1
            # add_label(f'{j}. {labelk[i]}', scroll)
            add_label(f'{labels[i]}', scroll)
            j += 1


def add_label(text, tab):
    label = ctk.CTkLabel(master=tab, text=text, wraplength=400, **style)
    label.pack(padx=5, pady=5, expand=True, fill='both')
