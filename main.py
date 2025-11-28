# main.py

def main():
    # === Import modulů a funkcí ===
    from portfolio import nacti_portfolio, vypocitej_zakladni_mnozstvi
    from konfigurace import nacti_konfiguraci
    import simulace as sim
    from rebalancovani import uloz_rebalancovani_do_txt
    import statistiky as stat
    import soubory as f
    import grafy as g

    import os

    # === 1. Načtení vstupních souborů ===
    vstupni_soubory = [
        "portfolio_konzervativni.csv",
        "portfolio_rizikove.csv"
    ]

    # === 2. Načtení konfigurace ===
    konfig = nacti_konfiguraci()
    pocatecni_hodnota = int(konfig.get("pocatecni_hodnota", 100000))
    pocet_dni = int(konfig.get("pocet_dni", 1000))
    denni_volatilita = float(konfig.get("denni_volatilita", 0.02))
    transakcni_poplatek = float(konfig.get("transakcni_poplatek", 0.005))
    rebalancovaci_perioda = int(konfig.get("rebalancovaci_perioda", 90))
    zpusob_rebalancovani = konfig.get("zpusob_rebalancovani", "periodicky")
    tolerance_vahy = float(konfig.get("tolerance_vahy", 0.05))
    inflacni_sazba = float(konfig.get("inflacni_sazba", 0.02))
    model = konfig.get("model", "typovy")
    sdilena_simulace = str(konfig.get("sdilena_simulace", "true")).lower() == "true"

    vysledky = {}
    ceny_sdilene = None
    prvni_nazvy = set()

    # === 3. Simulace portfolií ===
    for i, soubor in enumerate(vstupni_soubory):
        print(f"\n=== Simulace portfolia: {soubor} ===")
        portfolio = nacti_portfolio(soubor)
        if not portfolio:
            print(f"Chyba: {soubor} nebylo načteno.")
            continue

        vypocitej_zakladni_mnozstvi(portfolio, pocatecni_hodnota)
        cilove_vahy = {a['nazev']: a['vaha'] for a in portfolio}

        # Generování sdílených cen pouze pro první portfolio
        if sdilena_simulace and ceny_sdilene is None:
            ceny_sdilene = sim.generuj_sdilene_ceny(
                portfolio, pocet_dni, model=model, denni_volatilita=denni_volatilita
            )
            prvni_nazvy = set(ceny_sdilene.keys())

        # Použití sdílené simulace jen pokud portfolia mají stejná aktiva
        aktualni_nazvy = set(a['nazev'] for a in portfolio)
        if sdilena_simulace and ceny_sdilene is not None and aktualni_nazvy == prvni_nazvy:
            vyvoj_portfolia, historie_rebalancovani = sim.simuluj_portfolio_sdilene(
                portfolio, cilove_vahy, ceny_sdilene,
                rebalancovaci_perioda, zpusob_rebalancovani,
                tolerance_vahy, transakcni_poplatek
            )
        else:
            if sdilena_simulace and ceny_sdilene is not None:
                print("Pozor: portfolia mají odlišná aktiva – sdílená simulace nebude použita.")
            vyvoj_portfolia, historie_rebalancovani = sim.simuluj_portfolio(
                portfolio, cilove_vahy, pocet_dni, rebalancovaci_perioda,
                zpusob_rebalancovani, tolerance_vahy, transakcni_poplatek,
                model=model, denni_volatilita=denni_volatilita
            )

        # Uložení výsledků
        nazev = os.path.splitext(os.path.basename(soubor))[0]
        vysledky[nazev] = vyvoj_portfolia

        # Statistiky
        stat.vypis_statistiku(vyvoj_portfolia)
        celkove_poplatky = sum(z['poplatky_celkem'] for z in historie_rebalancovani)
        print(f"\n$$$ Celkové transakční poplatky: {celkove_poplatky:.2f} Kč")

        # Exporty
        f.uloz_transakce_do_csv(historie_rebalancovani, prefix=nazev)
        f.uloz_vyvoj_portfolia_do_csv(vyvoj_portfolia, prefix=nazev)
        f.uloz_ceny_aktiv_do_csv(portfolio, prefix=nazev)
        f.uloz_statistiky_do_csv(vyvoj_portfolia, prefix=nazev)
        uloz_rebalancovani_do_txt(historie_rebalancovani, prefix=nazev)

        # Grafy
        g.vykresli_ceny_aktiv(portfolio, prefix=nazev)
        g.vykresli_vyvoj_portfolia(vyvoj_portfolia, prefix=nazev)
        g.vykresli_vyvoj_vah(portfolio, prefix=nazev)
        g.vykresli_drawdown(vyvoj_portfolia, prefix=nazev)
        g.vykresli_histogram_vynosu(vyvoj_portfolia, prefix=nazev)
        g.vykresli_heatmapu_korelaci(portfolio, prefix=nazev)
        g.vykresli_realnou_hodnotu_portfolia(vyvoj_portfolia, inflacni_sazba, prefix=nazev)
        g.vykresli_rolling_volatilitu(vyvoj_portfolia, okno=63, prefix=nazev)

    # === 4. Porovnání všech portfolií ===
    g.vykresli_vyvoj_vice_portfolii(vysledky)
    g.vykresli_vyvoj_vice_portfolii_interaktivne(vysledky)


if __name__ == "__main__":
    main()