"""Yumuşatma eğrileri ve özellik başına anahtar kare izi (Iz).

Çizgi film hissi için "geri_tepme" (hedefi biraz aşıp geri gelir) ve "elastik" eğrileri vardır.
"""
import math


def sinirla(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def yumusak(u):
    u = sinirla(u)
    return u * u * (3 - 2 * u)


def hizlan(u):
    u = sinirla(u)
    return u * u * u


def yavasla(u):
    u = sinirla(u)
    return 1 - (1 - u) ** 3


def geri_tepme(u, k=1.70158):
    """Hedefi az aşar, geri oturur (pop-in, yakınlaşma vuruşu)."""
    u = sinirla(u) - 1
    return 1 + u * u * ((k + 1) * u + k)


def elastik(u):
    u = sinirla(u)
    if u in (0.0, 1.0):
        return u
    return 2 ** (-10 * u) * math.sin((u * 10 - 0.75) * (2 * math.pi) / 3) + 1


def dogrusal(u):
    return sinirla(u)


EGRILER = {"yumusak": yumusak, "hizlan": hizlan, "yavasla": yavasla, "geri_tepme": geri_tepme,
           "elastik": elastik, "dogrusal": dogrusal}


class Iz:
    """Her özelliğin ayrı anahtar kare listesi vardır; böylece konum, ifade, saydamlık
    birbirinden bağımsız ve üst üste binen zamanlarda canlandırılabilir.

    ekle(t1, {"x": 300}, sure=0.6, egri="geri_tepme"): t1-sure .. t1 arasında önceki değerden yeni değere.
    """

    def __init__(self, baslangic):
        self.izler = {o: [(-1e9, -1e9, float(v), "yumusak")] for o, v in baslangic.items()}

    def ekle(self, t1, degerler, sure=0.5, egri="yumusak"):
        for o, v in degerler.items():
            k = self.izler.setdefault(o, [(-1e9, -1e9, float(v), "yumusak")])
            k.append((t1 - max(sure, 1e-4), t1, float(v), egri))
            k.sort(key=lambda e: e[1])
        return self

    def ayarla(self, t, degerler):
        return self.ekle(t, degerler, sure=1e-4, egri="dogrusal")

    def _tek(self, o, t):
        k = self.izler[o]
        deger = k[0][2]
        for t0, t1, v, egri in k[1:]:
            if t >= t1:
                deger = v
            elif t > t0:
                u = (t - t0) / (t1 - t0)
                deger = deger + (v - deger) * EGRILER[egri](u)
                break
            else:
                break
        return deger

    def deger(self, t):
        return {o: self._tek(o, t) for o in self.izler}

    def __call__(self, o, t):
        return self._tek(o, t)
