# rebalancovani.py

import os

# Rebalancování portfolia

def rebalancuj_portfolio(portfolio, den, cilove_vahy, historie, poplatek_sazba=0.005):
    """Funkce rebalancuje portfolio v daný den a změny zaznamenává do seznamu 'historie'."""

    # Spočítá celkovou hodnotu portfolia
    celkova_hodnota = sum(aktivum['ceny'][den] * aktivum['mnozstvi'] for aktivum in portfolio)

    zaznam = {
        'den': den,
        'transakce': [],
        'poplatky_celkem': 0.0,
        'hodnota_portfolia': celkova_hodnota
    }

    # Pro každé aktivum spočítá nové množství
    for aktivum in portfolio:
        nazev = aktivum['nazev']
        cilova_vaha = cilove_vahy[nazev]
        cilova_castka = celkova_hodnota * cilova_vaha
        aktualni_cena = aktivum['ceny'][den]

        puvodni_mnozstvi = aktivum['mnozstvi']
        aktualni_hodnota = puvodni_mnozstvi * aktualni_cena

        # Výpočet rozdílu (nákup/prodej)
        rozdil_castky = cilova_castka - aktualni_hodnota
        poplatek = abs(rozdil_castky) * poplatek_sazba
        zaznam['poplatky_celkem'] += poplatek

        # Částka dostupná pro nákup/prodej po odečtení poplatku
        skutecna_castka = cilova_castka - poplatek if rozdil_castky > 0 else cilova_castka + poplatek
        nove_mnozstvi = skutecna_castka / aktualni_cena

        aktivum['mnozstvi'] = nove_mnozstvi

        # Uložení historie množství
        if "historie_mnozstvi" not in aktivum:
            aktivum["historie_mnozstvi"] = []
        # Doplníme historii až do aktuálního dne (pokud ještě chybí)
        while len(aktivum["historie_mnozstvi"]) < den:
            aktivum["historie_mnozstvi"].append(puvodni_mnozstvi)
        aktivum["historie_mnozstvi"].append(nove_mnozstvi)

        zaznam['transakce'].append({
            'aktivum': nazev,
            'puvodni': puvodni_mnozstvi,
            'nove': nove_mnozstvi,
            'rozdil': nove_mnozstvi - puvodni_mnozstvi,
            'poplatek': poplatek
        })

    historie.append(zaznam)


def je_odchylka_prilis_velka(portfolio, cilove_vahy, tolerance=0.05):
    """Vrátí True, pokud je nějaká váha aktiva mimo toleranci vůči cíli."""
    celkova_hodnota = sum(a['mnozstvi'] * a['ceny'][-1] for a in portfolio)
    for aktivum in portfolio:
        aktualni_vaha = (aktivum['mnozstvi'] * aktivum['ceny'][-1]) / celkova_hodnota
        cilova_vaha = cilove_vahy[aktivum['nazev']]
        if abs(aktualni_vaha - cilova_vaha) > tolerance:
            return True
    return False

def uloz_rebalancovani_do_txt(historie, prefix=""):
    """Uloží historii rebalancování do textového souboru ve výstupy/<prefix>/statistiky/."""
    if not historie:
        return
    
    slozka = os.path.join("vystupy", prefix, "statistiky")
    os.makedirs(slozka, exist_ok=True)

    cesta = os.path.join(slozka, f"{prefix}_rebalancovani.txt")
    with open(cesta, mode="w", encoding="utf-8") as f:
        f.write("Záznamy rebalancování portfolia\n")
        f.write("=" * 45 + "\n")
        for zaznam in historie:
            den = zaznam['den']
            hodnota = zaznam.get("hodnota_portfolia", 0)
            poplatky = zaznam.get("poplatky_celkem", 0)
            f.write(f"Den {den} - Hodnota: {hodnota:.2f} Kč - Poplatky celkem: {poplatky:.2f} Kč\n")
            for transakce in zaznam['transakce']:
                f.write(f" - {transakce['aktivum']}: {transakce['puvodni']:.4f} -> {transakce['nove']:.4f} "
                        f"(změna: {transakce['rozdil']:+.4f}, poplatek: {transakce['poplatek']:.2f} Kč)\n")
            f.write("-" * 45 + "\n")
    
    print(f"Rebalancování bylo uloženo do: {cesta}")