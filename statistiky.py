# statistiky.py

import statistics

def vypis_statistiku(vyvoj, bezrizikova_sazba=0.01):
    """Vypíše základní statistické údaje o vývoji portfolia."""

    if not vyvoj or len(vyvoj) < 2:
        print("Nedostatek dat pro statistiku.")
        return
    
    zacatek = vyvoj[0]
    konec = vyvoj[-1]
    pocet_dni = len(vyvoj) - 1
    roky = pocet_dni / 252  # přibližný počet obchodních dní v roce

    celkove_zhodnoceni = (konec - zacatek) / zacatek * 100
    cagr = (konec / zacatek) ** (1 / roky) - 1  # Compound annual growth rate

    # Výpočet denních výnosů
    denni_vynosy = [(vyvoj[i] - vyvoj[i - 1]) / vyvoj[i - 1] for i in range(1, len(vyvoj))]

    # Výpočet volatility
    smerodatna_odchylka_denni = statistics.stdev(denni_vynosy)
    smerodatna_odchylka_rocni = smerodatna_odchylka_denni * (252 ** 0.5)

    # Sharpe ratio
    sharpe_ratio = (cagr - bezrizikova_sazba) / smerodatna_odchylka_rocni if smerodatna_odchylka_rocni != 0 else float('nan')

    # Max drawdown
    max_so_far = vyvoj[0]
    max_drawdown = 0
    for hodnota in vyvoj:
        max_so_far = max(max_so_far, hodnota)
        drawdown = (hodnota - max_so_far) / max_so_far
        max_drawdown = min(max_drawdown, drawdown)

    minimum = min(vyvoj)
    maximum = max(vyvoj)

    # Výpis
    print("\n--- Statistika vývoje portfolia ---")
    print(f"Počáteční hodnota: {zacatek:.2f} Kč")
    print(f"Konečná hodnota:   {konec:.2f} Kč")
    print(f"Celkové zhodnocení: {celkove_zhodnoceni:.2f} %")
    print(f"Průměrné roční zhodnocení (CAGR): {cagr*100:.4f} %")
    print(f"Denní směrodatná odchylka: {smerodatna_odchylka_denni*100:.4f} %")
    print(f"Roční směrodatná odchylka: {smerodatna_odchylka_rocni*100:.4f} %")
    print(f"Sharpe ratio: {sharpe_ratio:.4f}")
    print(f"Maximum hodnoty: {maximum:.2f} Kč")
    print(f"Minimum hodnoty: {minimum:.2f} Kč")
    print(f"Max drawdown: {max_drawdown*100:.2f} %")
