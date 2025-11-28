# soubory.py

import csv
import statistics
import os

# ========================
# SPRÁVA SLOŽEK
# ========================

def zajisti_slozku_vystupy(prefix):
    """Zajistí existenci složek: vystupy/{prefix}/statistiky a vystupy/{prefix}/grafy."""
    zaklad = os.path.join("vystupy", prefix)
    os.makedirs(os.path.join(zaklad, "statistiky"), exist_ok=True)
    os.makedirs(os.path.join(zaklad, "grafy"), exist_ok=True)

# ========================
# 1. HISTORIE TRANSAKCÍ
# ========================

def uloz_transakce_do_csv(historie, prefix=''):
    """Uloží historii rebalancování do CSV souboru."""
    if not historie:
        print("Historie transakcí je prázdná.")
        return
    
    zajisti_slozku_vystupy(prefix)
    nazev_souboru = os.path.join("vystupy", prefix, "statistiky", f"{prefix}_transakce.csv")
    
    with open(nazev_souboru, mode='w', newline='', encoding='utf-8') as soubor:
        pole = ['Den', 'Aktivum', 'Původní množství', 'Nové množství', 'Změna', 'Poplatek']
        writer = csv.DictWriter(soubor, fieldnames=pole, delimiter=';')
        writer.writeheader()

        for zaznam in historie:
            den = zaznam['den']
            for t in zaznam['transakce']:
                writer.writerow({
                    'Den': den,
                    'Aktivum': t['aktivum'],
                    'Původní množství': f"{t['puvodni']:.4f}",
                    'Nové množství': f"{t['nove']:.4f}",
                    'Změna': f"{t['rozdil']:+.4f}",
                    'Poplatek': f"{t.get('poplatek', 0):.2f}"
                })

    print(f"Transakce byly uloženy do souboru '{nazev_souboru}'.")

# ========================
# 2. VÝVOJ HODNOTY PORTFOLIA
# ========================

def uloz_vyvoj_portfolia_do_csv(vyvoj, prefix=''):
    """Uloží denní hodnotu portfolia do CSV souboru."""
    if not vyvoj:
        print("Vývoj portfolia je prázdný.")
        return

    zajisti_slozku_vystupy(prefix)
    nazev_souboru = os.path.join("vystupy", prefix, "statistiky", f"{prefix}_vyvoj.csv")

    with open(nazev_souboru, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow(['Den', 'Hodnota portfolia (Kč)'])
        for den, hodnota in enumerate(vyvoj):
            writer.writerow([den, f"{hodnota:.2f}"])

# ========================
# 3. VÝVOJ CEN AKTIV
# ========================

def uloz_ceny_aktiv_do_csv(portfolio, prefix=''):
    """Uloží vývoj ceny jednotlivých aktiv po dnech do CSV."""
    if not portfolio:
        print("Portfolio je prázdné.")
        return
    
    pocet_dni = len(portfolio[0]['ceny'])
    zajisti_slozku_vystupy(prefix)
    nazev_souboru = os.path.join("vystupy", prefix, "statistiky", f"{prefix}_ceny.csv")

    with open(nazev_souboru, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        hlavicka = ['Den'] + [aktivum['nazev'] for aktivum in portfolio]
        writer.writerow(hlavicka)

        for den in range(pocet_dni):
            radek = [den] + [f"{aktivum['ceny'][den]:.4f}" for aktivum in portfolio]
            writer.writerow(radek)

# ========================
# 4. STATISTIKY PORTFOLIA
# ========================

def uloz_statistiky_do_csv(vyvoj, prefix='', bezrizikova_sazba=0.01):
    """Vypočítá a uloží statistiky portfolia do CSV a TXT souboru."""
    if not vyvoj or len(vyvoj) < 2:
        print("Nedostatek dat pro statistiku.")
        return

    zajisti_slozku_vystupy(prefix)
    slozka = os.path.join("vystupy", prefix, "statistiky")

    zacatek = vyvoj[0]
    konec = vyvoj[-1]
    pocet_dni = len(vyvoj) - 1
    roky = pocet_dni / 252  # přibližný počet obchodních dní v roce

    celkove_zhodnoceni = (konec - zacatek) / zacatek * 100
    cagr = (konec / zacatek) ** (1 / roky) - 1

    denni_vynosy = [(vyvoj[i] - vyvoj[i-1])/vyvoj[i-1] for i in range(1, len(vyvoj))]
    smerodatna_odchylka_denni = statistics.stdev(denni_vynosy)
    smerodatna_odchylka_rocni = smerodatna_odchylka_denni * (252 ** 0.5)
    sharpe_ratio = (cagr - bezrizikova_sazba) / smerodatna_odchylka_rocni if smerodatna_odchylka_rocni != 0 else float('nan')

    max_so_far = vyvoj[0]
    max_drawdown = 0
    for hodnota in vyvoj:
        max_so_far = max(max_so_far, hodnota)
        drawdown = (hodnota - max_so_far) / max_so_far
        max_drawdown = min(max_drawdown, drawdown)

    minimum = min(vyvoj)
    maximum = max(vyvoj)

    # CSV
    csv_soubor = os.path.join(slozka, f"{prefix}_statistiky.csv")
    with open(csv_soubor, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(["Statistika", "Hodnota"])
        writer.writerow(["Počáteční hodnota", f"{zacatek:.2f}"])
        writer.writerow(["Konečná hodnota", f"{konec:.2f}"])
        writer.writerow(["Celkové zhodnocení (%)", f"{celkove_zhodnoceni:.2f}"])
        writer.writerow(["Průměrné roční zhodnocení (%)", f"{cagr*100:.4f}"])
        writer.writerow(["Denní směrodatná odchylka (%)", f"{smerodatna_odchylka_denni*100:.4f}"])
        writer.writerow(["Roční směrodatná odchylka (%)", f"{smerodatna_odchylka_rocni*100:.4f}"])
        writer.writerow(["Sharpe ratio", f"{sharpe_ratio:.4f}"])
        writer.writerow(["Maximum", f"{maximum:.2f}"])
        writer.writerow(["Minimum", f"{minimum:.2f}"])
        writer.writerow(["Max drawdown (%)", f"{max_drawdown*100:.2f}"])

    # TXT
    txt_soubor = os.path.join(slozka, f"{prefix}_statistiky.txt")
    with open(txt_soubor, mode="w", encoding="utf-8") as f:
        f.write("Souhrn statistiky portfolia\n")
        f.write("="*35 + "\n")
        f.write(f"Počáteční hodnota: {zacatek:.2f} Kč\n")
        f.write(f"Konečná hodnota:   {konec:.2f} Kč\n")
        f.write(f"Celkové zhodnocení: {celkove_zhodnoceni:.2f} %\n")
        f.write(f"Roční zhodnocení (CAGR): {cagr*100:.4f} %\n")
        f.write(f"Roční volatilita: {smerodatna_odchylka_rocni*100:.4f} %\n")
        f.write(f"Sharpe ratio: {sharpe_ratio:.4f}\n")
        f.write(f"Maximum: {maximum:.2f} Kč\n")
        f.write(f"Minimum: {minimum:.2f} Kč\n")
        f.write(f"Maximální pokles (drawdown): {max_drawdown*100:.2f} %\n")

    print(f"Statistiky byly exportovány do '{csv_soubor}' a '{txt_soubor}'.")
