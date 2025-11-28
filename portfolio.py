# portfolio.py

import csv
import os

def nacti_portfolio(soubor='portfolio_input.csv'):
    """Funkce načte vstupní parametry portfolia
    ze strukturovaného textového souboru CSV."""

    # Vždy vzhledem ke složce tohoto souboru
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cesta = os.path.join(base_dir, soubor)
    portfolio = []
    
    try:
        with open(cesta, newline='', encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                aktivum = {
                    'nazev': row['Asset'],
                    'cena': float(row['InitialPrice']),
                    'vaha': float(row['InitialWeight']),
                    'typ': row['AssetType'],
                    'korelace': float(row.get('CorrelationWithIndex', 0.0)) # výchozí hodnota je 0.0
                }
                portfolio.append(aktivum)

        # Oveření, že váhy dávají přibližně 1.0
        soucet_vah = sum(a['vaha'] for a in portfolio)
        if abs(soucet_vah - 1.0) > 0.001:
            raise ValueError(f"Součet vah není 1.0 (aktualně {soucet_vah:.4f})")
        
        return portfolio
    
    except FileNotFoundError:
        print(f"Soubor '{soubor}' nebyl nalezen.")
        return []
    except KeyError as e:
        print(f"Chyba ve struktuře CVS souboru - chybí sloupec: {e}")
        return []
    except ValueError as e:
        print(f"Chyba v datech: {e}")
        return []
    

# Výpočet množství jednotek každého aktiva
def vypocitej_zakladni_mnozstvi(portfolio, pocatecni_hodnota=1000):
    """Funkce na základě počáteční hodnoty portfolia a váhy
    každého aktiva spočítá, kolik jednotek každého aktiva držíme na začátku."""
    suma_vah = sum(aktivum['vaha'] for aktivum in portfolio)
    castky = []
    
    # Normálně rozdělí mezi všechna aktiva kromě posledního
    for aktivum in portfolio[:-1]:
        cilova_castka = (aktivum['vaha'] / suma_vah) * pocatecni_hodnota
        castky.append(cilova_castka)
        aktivum['mnozstvi'] = cilova_castka / aktivum['cena']
        aktivum['historie_mnozstvi'] = [aktivum['mnozstvi']]

    # Poslední aktivum dostane zbytek
    zbytek = pocatecni_hodnota - sum(castky)
    posledni = portfolio[-1]
    posledni['mnozstvi'] = zbytek / posledni['cena']
    posledni['historie_mnozstvi'] = [posledni['mnozstvi']]

# Výpočet hodnoty portfolia v čase

def vypocitej_vyvoj_portfolia(portfolio):
    """Funkce každý den spočítá celkovou hodnotu portfolia."""

    pocet_dni = len(portfolio[0]['ceny'])
    vyvoj = []

    for den in range(pocet_dni):
        hodnota = 0
        for aktivum in portfolio:
            cena = aktivum['ceny'][den]
            mnozstvi = aktivum['mnozstvi']
            hodnota += cena * mnozstvi
        vyvoj.append(hodnota)

    return vyvoj