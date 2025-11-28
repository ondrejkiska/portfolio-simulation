# konfigurace.py

import csv

def nacti_konfiguraci(soubor='konfigurace.csv'):
    """Načte parametry simulace z konfiguračního souboru ve formátu CSV."""
    konfigurace = {}
    try:
        with open(soubor, newline='', encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                klic = row['parametr'].strip()
                hodnota = row['hodnota'].strip()

                # Pokus o převod na číslo
                if hodnota.lower() in ["true", "false"]:
                    konfigurace[klic] = hodnota.lower() == "true"
                else:
                    try:
                        konfigurace[klic] = float(hodnota)
                    except ValueError:
                        konfigurace[klic] = hodnota  # necháme jako text

        return konfigurace
    except FileNotFoundError:
        print(f"Soubor '{soubor}' nebyl nalezen.")
        return {}
    except KeyError as e:
        print(f"Chyba v konfiguračním souboru: chybí sloupec {e}")
        return {}



# Mapa parametrů podle typu aktiva
PARAMETRY_TYPU_AKTIVA = {
    'akcie': {'ocekavany_vynos': 0.08, 'volatilita': 0.15},
    'dluhopis': {'ocekavany_vynos': 0.03, 'volatilita': 0.06},
    'zlato': {'ocekavany_vynos': 0.035, 'volatilita': 0.08},
    'hotovost': {'ocekavany_vynos': 0.01, 'volatilita': 0.0}
}

def preved_na_denni(rocni_vynos, rocni_volatilita):
    denni_vynos = (1 + rocni_vynos) ** (1 / 252) - 1
    denni_volatilita = rocni_volatilita / (252 ** 0.5)
    return denni_vynos, denni_volatilita
