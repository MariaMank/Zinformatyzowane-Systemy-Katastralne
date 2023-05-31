import shapely.geometry
from bs4 import BeautifulSoup
from shapely.ops import unary_union

OZNACZENIE = ('OFU', 'OZU', 'OZK')
with open('poprawiony.gml', 'r', encoding='UTF-8') as file:
    content = file.read()
    gml = BeautifulSoup(content, features='xml')


class Dzialka:
    def __init__(self, info):
        """info: atrybuty jako dict"""
        self.id = info['idDzialki']
        self.geom = info['geom']
        self.info = info
        self.JRG = egb_jednostka_rej[info['JRG2']]['idJednostkiRejestrowej']
        # self.podmiot_in = self.podmiot()

    def budynek(self):
        return egb_budynek.get(self.id)

    def punkty_graniczne(self):
        return [egb_pktgraniczny[i] for i in self.info['punktGranicyDzialki']]

    def podmiot(self):
        """
        podmiot: lista osób (dict)
        podmiot_adres: dict (key = lokalnyId podmiotu) do listy adresów (może być więcej niż 1, np. adresDoKoresOsobyFiz)
        """
        udzial_wl = egb_udzial[self.info['JRG2']]
        link = udzial_wl['EGB_Podmiot']
        podmiot = egb_podmiot[link]
        podmiot_adres = {}
        for i in podmiot:
            adres = [[key, i[key]] for key in i.keys() if key.startswith('adres')]
            podmiot_adres[i['lokalnyId']] = get_adres(adres)
        self.udzial = {
            'licznikUlamkaOkreslajacegoWartoscUdzialu': udzial_wl['licznikUlamkaOkreslajacegoWartoscUdzialu'],
            'mianownikUlamkaOkreslajacegoWartoscUdzialu': udzial_wl['mianownikUlamkaOkreslajacegoWartoscUdzialu'],
            'waznoscOd': udzial_wl['waznoscOd']}

        return podmiot, podmiot_adres

    def klasouzytek(self):
        link = self.info['klasouzytekWGranicachDzialki']
        uzytki = [egb_klasouzytek[i] for i in link] if isinstance(link, list) else [egb_klasouzytek[link]]
        result = []
        for uzytek in uzytki:
            ozn = ''
            for n in OZNACZENIE:
                value = uzytek.get(n)
                if value:
                    ozn += value
                else:
                    break
            result.append(f'{ozn}: {uzytek["powierzchniaEwidencyjnaKlasouzytku"]}')
        assert len(result) == len(uzytki)
        return '\n'.join(result)

    def adres(self):
        link = self.info.get('adresDzialki')
        if not link:
            return None
        adres = egb_adres[link]
        result = []
        for i in ['miejscowosc', 'terytMiejscowosci', 'ulica', 'terytUlicy', 'numerPorzadkowy']:
            result.append(f'{i}: {adres[i]}')
        return "\n".join(result)


class Budynek:
    def __init__(self, info):
        """info: atrybuty jako dict"""
        self.id = info['idBudynku']
        self.geom = info['geom']
        self.info = info

    def blok(self):
        return egb_blok.get(self.info['lokalnyId'])

    def adres(self):
        link = self.info.get('adresBudynku')
        if not link:
            return None
        adres = egb_adres[link]
        result = []
        for i in ['miejscowosc', 'terytMiejscowosci', 'ulica', 'terytUlicy', 'numerPorzadkowy']:
            result.append(f'{i}: {adres[i]}')
        result_2 = [result[2], result[4], result[0]]
        return ("\n".join(result), "\n".join(result_2))


def get_geom(info):
    geom_info = {i.name: i.contents for i in info.find_all()}
    if 'Polygon' in geom_info:
        geom_pts = geom_info['posList'][0].split(' ')
        pts = [[float(geom_pts[i + 1]), float(geom_pts[i])] for i in range(0, len(geom_pts), 2)]
        return shapely.geometry.Polygon(pts)
    elif 'Point' in geom_info:
        return geom_info['pos'][0]
    else:
        return None


def get_info(tag, key='lokalnyId'):
    info = gml.find_all(tag)
    values = {}
    for i in info:
        tag = tag_info(i.children)
        add_to_dict(values, tag[key], tag)
    return values


def append_info(tag, key='lokalnyId'):
    info = gml.find_all(tag)
    values = {}
    for i in info:
        tag = tag_info(i.children)
        values.setdefault(tag[key], []).append(tag)
    return values


def udzial_info(tag):
    info = gml.find_all(tag)
    values = {}
    for i in info:
        jrg = get_link(i.find('egb:JRG'))
        podmiot_link = list(i.find('egb:EGB_Podmiot').children)[1]
        podmiot_link = get_link(podmiot_link)
        jrg_info = tag_info(i)
        jrg_info['EGB_Podmiot'] = podmiot_link
        values[jrg] = jrg_info
    return values


def malz_info(tag):
    """dwie osoby fizyczne"""
    info = gml.find_all(tag)
    values = {}
    for i in info:
        link = i.find('bt:lokalnyId').contents[0]
        malz = []
        for j in list(i.children)[-4::2]:
            o_id = get_link(j)
            malz.extend(egb_podmiot[o_id])
        values[link] = malz
    return values


def tag_info(children):
    info = {}
    for i in list(children)[1::2]:
        if len(i.find_all()) == 0:
            value = i.contents[0] if i.contents else None
            attrs = list(i.attrs.items())
            if attrs:
                value = get_attr(value, *attrs[0])
            add_to_dict(info, i.name, value)
        elif i.name == 'idIIP':
            info['lokalnyId'] = i.find('bt:lokalnyId').contents[0]
        elif i.name == 'geometria':
            info['geom'] = get_geom(i)
        elif i.name == 'oznaczenieKlasouzytku':
            ozn_uzytku(info, i)
    return info


def get_attr(value, attr_key, attr_value):
    """
    uom - jednostka powierzchni
    xlink:href - link do innych obiektów
    nilReason:
        INAPPLICABLE - There is no value.
        MISSING - The correct value is not readily available to the sender of this data.
        OTHER - Other reason without explanation.
        TEMPLATE - The value will be available later.
        UNKNOWN - The correct value is not known to, and not computable by, the sender of this data.
        WITHHELD - The value is not divulged.
    """
    if attr_key == 'nilReason':
        value = attr_value
    elif attr_key == 'xlink:href':
        value = get_link(attr_value, False)
    elif attr_key == 'uom':
        value = f'{value} {attr_value}'
    return value


def ozn_uzytku(dictionary, info):
    for i in OZNACZENIE:
        ozn = info.find(f'egb:{i}')
        if ozn:
            dictionary[i] = ozn.contents[0]


def add_to_dict(dictionary, key, value):
    if key in dictionary:
        if not isinstance(dictionary[key], list):
            dictionary[key] = [dictionary[key]]
        dictionary[key].append(value)
    else:
        dictionary[key] = value


def get_link(link, find=True):
    if find:
        link = link['xlink:href']
    return link.partition('EGiB:')[2]


def get_adres(links):
    result = {}
    for i in links:
        result[i[0]] = (egb_adres[i[1]])
    return result


# UDZIAL WLASNOSCI
egb_udzial = udzial_info('egb:EGB_UdzialWlasnosci')

# PODMIOTY
egb_podmiot = append_info('egb:EGB_OsobaFizyczna')
egb_podmiot.update(append_info('egb:EGB_Instytucja'))
egb_podmiot.update(malz_info('egb:EGB_Malzenstwo'))

# ADRESY
egb_adres = get_info('egb:EGB_Adres')

# KLASOUZYTKI
egb_klasouzytek = get_info('egb:EGB_Klasouzytek')

# PUNKTY GRANICZNE
egb_pktgraniczny = get_info('egb:EGB_PunktGraniczny')

# BLOK BUDYNKU
egb_blok = append_info('egb:EGB_BlokBudynku', 'budynekZWyodrebnionymBlokiemBudynku')

# JEDNOSTKA REJESTROWA
egb_jednostka_rej = get_info('egb:EGB_JednostkaRejestrowaGruntow')

# BUDYNKI
egb_budynek = {}
for b in gml.find_all('egb:EGB_Budynek'):
    bud_info = tag_info(b)
    nr_dzialki = '.'.join(bud_info['idBudynku'].split('.')[0:-1])
    egb_budynek[nr_dzialki] = Budynek(bud_info)

# DZIALKI
egb_dzialka = {}
polygons = []
for dzialka in gml.find_all('egb:EGB_DzialkaEwidencyjna'):
    dz_info = tag_info(dzialka)
    egb_dzialka[dz_info['idDzialki']] = Dzialka(dz_info)
    polygons.append(dz_info['geom'])

dzialki_poly = unary_union(polygons)

# UZYTEK GRUNTOWY
egb_uzytki_grunt = []
for u in gml.find_all('egb:EGB_KonturUzytkuGruntowego'):
    u_poly = get_geom(u)
    if u_poly.representative_point().within(dzialki_poly):
        ofu = u.find('OFU').contents[0]
        egb_uzytki_grunt.append({'ofu': ofu, 'geom': u_poly})
