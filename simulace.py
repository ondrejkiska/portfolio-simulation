# simulace.py

import random
from konfigurace import PARAMETRY_TYPU_AKTIVA, preved_na_denni
from rebalancovani import rebalancuj_portfolio, je_odchylka_prilis_velka

# ========================
# MODELY VÝVOJE CEN
# ========================

def simuluj_den_nahodny(aktualni_cena, denni_volatilita=0.02):
    """Náhodný model: cena +- uniform(denni_volatilita)."""
    delta = random.uniform(-denni_volatilita, denni_volatilita)
    return aktualni_cena * (1 + delta)

def simuluj_den_typove(aktivum):
    """Typový model: cena podle oček. výnosu a volatility aktiva."""
    typ = aktivum.get("typ", "akcie")
    param = PARAMETRY_TYPU_AKTIVA.get(typ, PARAMETRY_TYPU_AKTIVA["akcie"])
    denni_vynos, denni_vol = preved_na_denni(param["ocekavany_vynos"], param["volatilita"])
    zmena = random.gauss(denni_vynos, denni_vol)
    return aktivum["ceny"][-1] * (1 + zmena)

def simuluj_den_korelacni(aktivum, index_zmena, denni_volatilita=0.02):
    """Korelační model: kombinace změny indexu a náhodné složky."""
    korelace = aktivum.get("korelace", 0.5)
    nahodna_slozka = random.uniform(-denni_volatilita, denni_volatilita)
    zmena = korelace * index_zmena + (1 - korelace) * nahodna_slozka
    return aktivum["ceny"][-1] * (1 + zmena)

# ========================
# GENEROVÁNÍ SDÍLENÝCH CEN
# ========================

def generuj_sdilene_ceny(portfolio, pocet_dni, model="typovy", denni_volatilita=0.02):
    """
    Vygeneruje sdílené ceny pro všechna aktiva dle vybraného modelu.
    Vrací slovník {nazev_aktiva: seznam_cen}.
    """
    ceny_aktiv = {a["nazev"]: [a["cena"]] for a in portfolio}

    index = [100.0]  # jen pro korelační model

    for den in range(1, pocet_dni + 1):
        if model == "nahodny":
            for aktivum in portfolio:
                nazev = aktivum["nazev"]
                posledni_cena = ceny_aktiv[nazev][-1]
                delta = random.uniform(-denni_volatilita, denni_volatilita)
                ceny_aktiv[nazev].append(posledni_cena * (1 + delta))

        elif model == "typovy":
            for aktivum in portfolio:
                nazev = aktivum["nazev"]
                posledni_cena = ceny_aktiv[nazev][-1]
                typ = aktivum.get("typ", "akcie")
                param = PARAMETRY_TYPU_AKTIVA.get(typ, PARAMETRY_TYPU_AKTIVA["akcie"])
                denni_vynos, denni_vol = preved_na_denni(param["ocekavany_vynos"], param["volatilita"])
                zmena = random.gauss(denni_vynos, denni_vol)
                ceny_aktiv[nazev].append(posledni_cena * (1 + zmena))

        elif model == "korelacni":
            zmena_indexu = random.uniform(-denni_volatilita, denni_volatilita)
            nova_index = index[-1] * (1 + zmena_indexu)
            index_zmena = (nova_index - index[-1]) / index[-1]
            index.append(nova_index)
            for aktivum in portfolio:
                nazev = aktivum["nazev"]
                korelace = aktivum.get("korelace", 0.5)
                nahodna_slozka = random.uniform(-denni_volatilita, denni_volatilita)
                zmena = korelace * index_zmena + (1 - korelace) * nahodna_slozka
                posledni_cena = ceny_aktiv[nazev][-1]
                ceny_aktiv[nazev].append(posledni_cena * (1 + zmena))

    return ceny_aktiv


# ========================
# SIMULACE PORTFOLIA
# ========================

def simuluj_portfolio(portfolio, cilove_vahy, pocet_dni, rebalancovaci_perioda,
                      zpusob_rebalancovani, tolerance_vahy, transakcni_poplatek,
                      model="typovy", denni_volatilita=0.02, sdilena_simulace=False):
    """Simuluje vývoj portfolia dle zvoleného modelu."""
    vyvoj = []
    historie = []

    for aktivum in portfolio:
        aktivum["ceny"] = [aktivum["cena"]]

    index = [100.0]

    for den in range(1, pocet_dni + 1):
        if model == "nahodny":
            for aktivum in portfolio:
                aktivum["ceny"].append(simuluj_den_nahodny(aktivum["ceny"][-1], denni_volatilita))
        elif model == "typovy":
            for aktivum in portfolio:
                aktivum["ceny"].append(simuluj_den_typove(aktivum))
        elif model == "korelacni":
            zmena_indexu = random.uniform(-denni_volatilita, denni_volatilita)
            nova_index = index[-1] * (1 + zmena_indexu)
            index_zmena = (nova_index - index[-1]) / index[-1]
            index.append(nova_index)
            for aktivum in portfolio:
                aktivum["ceny"].append(simuluj_den_korelacni(aktivum, index_zmena, denni_volatilita))

        # Rebalancování
        if (
            (zpusob_rebalancovani == "periodicky" and den % rebalancovaci_perioda == 0) or
            (zpusob_rebalancovani == "podle_odchylky" and je_odchylka_prilis_velka(portfolio, cilove_vahy, tolerance_vahy)) or
            (zpusob_rebalancovani == "kombinovane" and (
                den % rebalancovaci_perioda == 0 or je_odchylka_prilis_velka(portfolio, cilove_vahy, tolerance_vahy)
            ))
        ):
            rebalancuj_portfolio(portfolio, den, cilove_vahy, historie, transakcni_poplatek)

        hodnota = sum(aktivum["ceny"][-1] * aktivum["mnozstvi"] for aktivum in portfolio)
        vyvoj.append(hodnota)

    return vyvoj, historie

def simuluj_portfolio_sdilene(portfolio, cilove_vahy, ceny_aktiv, rebalancovaci_perioda,
                              zpusob_rebalancovani, tolerance_vahy, transakcni_poplatek):
    """Simulace portfolia nad již vygenerovanými sdílenými cenami."""
    vyvoj = []
    historie = []

    for aktivum in portfolio:
        aktivum["ceny"] = [aktivum["cena"]]

    pocet_dni = len(next(iter(ceny_aktiv.values()))) - 1

    for den in range(1, pocet_dni + 1):
        for aktivum in portfolio:
            aktivum["ceny"].append(ceny_aktiv[aktivum["nazev"]][den])

        if (
            (zpusob_rebalancovani == "periodicky" and den % rebalancovaci_perioda == 0) or
            (zpusob_rebalancovani == "podle_odchylky" and je_odchylka_prilis_velka(portfolio, cilove_vahy, tolerance_vahy)) or
            (zpusob_rebalancovani == "kombinovane" and (
                den % rebalancovaci_perioda == 0 or je_odchylka_prilis_velka(portfolio, cilove_vahy, tolerance_vahy)
            ))
        ):
            rebalancuj_portfolio(portfolio, den, cilove_vahy, historie, transakcni_poplatek)

        hodnota = sum(aktivum["ceny"][-1] * aktivum["mnozstvi"] for aktivum in portfolio)
        vyvoj.append(hodnota)

    return vyvoj, historie