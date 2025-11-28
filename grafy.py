# grafy.py

import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import plotly.graph_objs as go

def _vytvor_cestu(nazev_souboru, prefix):
    """Pomocná funkce pro vytvoření cesty k souboru a složce."""
    cesta = os.path.join("vystupy", prefix, *nazev_souboru.split("/")) if prefix else nazev_souboru
    os.makedirs(os.path.dirname(cesta), exist_ok=True)
    return cesta

def vykresli_ceny_aktiv(portfolio, nazev_souboru="grafy/vyvoj_ceny_aktiv.png", prefix=''):
    if not portfolio:
        print("Portfolio je prázdné")
        return
    pocet_dni = len(portfolio[0]['ceny'])
    dny = list(range(pocet_dni))
    cesta = _vytvor_cestu(nazev_souboru, prefix)

    plt.figure(figsize=(12, 6))
    for aktivum in portfolio:
        plt.plot(dny, aktivum['ceny'], label=aktivum['nazev'])
    plt.title('Vývoj cen jednotlivých aktiv')
    plt.xlabel('Den')
    plt.ylabel('Cena (Kč)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(cesta, dpi=300)
    plt.close()

def vykresli_vyvoj_portfolia(hodnoty_portfolia, nazev_souboru="grafy/vyvoj_portfolia.png", prefix=''):
    if not hodnoty_portfolia:
        print("Není co vykreslit.")
        return
    dny = list(range(len(hodnoty_portfolia)))
    cesta = _vytvor_cestu(nazev_souboru, prefix)

    plt.figure(figsize=(10, 5))
    plt.plot(dny, hodnoty_portfolia, color='darkgreen', linewidth=2)
    plt.title('Vývoj celkové hodnoty portfolia')
    plt.xlabel('Den')
    plt.ylabel('Hodnota portfolia (Kč)')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(cesta, dpi=300)
    plt.close()
    
def vykresli_vyvoj_vah(portfolio, nazev_souboru="grafy/vyvoj_vah.png", prefix=''):
    """
    Vykreslí vývoj skutečných vah jednotlivých aktiv v portfoliu.
    Používá historická množství po každém dni.

    portfolio -- seznam aktiv, každé aktivum má:
        'nazev', 'ceny' (seznam cen po dnech), 'historie_mnozstvi' (seznam slovníků po dnech)
    """
    if not portfolio or not portfolio[0].get("ceny"):
        print("Portfolio neobsahuje historická data.")
        return

    pocet_dni = len(portfolio[0]['ceny'])
    nazvy_aktiv = [a['nazev'] for a in portfolio]
    vyvoj_vah = {nazev: [] for nazev in nazvy_aktiv}

    # Kontrola existence historie_mnozstvi
    if not portfolio[0].get("historie_mnozstvi"):
        print("Portfolio neobsahuje historii množství. Graf nebude přesný.")
        return

    for den in range(pocet_dni):
        celkova_hodnota = sum(
            aktivum['ceny'][den] * aktivum['historie_mnozstvi'][den]
            for aktivum in portfolio
        )
        for aktivum in portfolio:
            mnozstvi_dne = aktivum['historie_mnozstvi'][den]
            vaha = (aktivum['ceny'][den] * mnozstvi_dne) / celkova_hodnota if celkova_hodnota > 0 else 0
            vyvoj_vah[aktivum['nazev']].append(vaha)

    # Vytvoření cesty k souboru
    cesta = os.path.join("vystupy", prefix, *nazev_souboru.split("/")) if prefix else nazev_souboru
    os.makedirs(os.path.dirname(cesta), exist_ok=True)

    # Vykreslení grafu
    plt.figure(figsize=(12, 6))
    for nazev in nazvy_aktiv:
        plt.plot(vyvoj_vah[nazev], label=nazev)

    plt.title("Vývoj skutečných vah aktiv v portfoliu")
    plt.xlabel("Den")
    plt.ylabel("Váha v portfoliu")
    plt.ylim(0, 1)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(cesta, dpi=300)
    plt.close()

def vykresli_drawdown(vyvoj, nazev_souboru="grafy/drawdown.png", prefix=''):
    if not vyvoj:
        print("Není co vykreslit.")
        return
    max_so_far = vyvoj[0]
    drawdowns = []
    for hodnota in vyvoj:
        max_so_far = max(max_so_far, hodnota)
        drawdowns.append((hodnota - max_so_far) / max_so_far * 100)
    cesta = _vytvor_cestu(nazev_souboru, prefix)
    plt.figure(figsize=(12, 6))
    plt.plot(drawdowns, color='crimson')
    plt.title("Drawdown portfolia")
    plt.xlabel("Den")
    plt.ylabel("Pokles od maxima (%)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(cesta, dpi=300)
    plt.close()

def vykresli_histogram_vynosu(vyvoj, nazev_souboru="grafy/histogram_vynosu.png", prefix=''):
    if len(vyvoj)<2:
        print("Nedostatek dat pro histogram výnosů.")
        return
    denni_vynosy = [(vyvoj[i]-vyvoj[i-1])/vyvoj[i-1]*100 for i in range(1,len(vyvoj))]
    cesta = _vytvor_cestu(nazev_souboru, prefix)
    plt.figure(figsize=(10, 5))
    plt.hist(denni_vynosy, bins=50, color='steelblue', edgecolor='black')
    plt.title("Histogram denních výnosů portfolia")
    plt.xlabel("Denní výnos (%)")
    plt.ylabel("Frekvence")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(cesta, dpi=300)
    plt.close()

def vykresli_heatmapu_korelaci(portfolio, nazev_souboru="grafy/heatmapa_korelaci.png", prefix=''):
    data = {}
    for a in portfolio:
        ceny = a['ceny']
        if len(ceny)<2: continue
        data[a['nazev']] = [(ceny[i]-ceny[i-1])/ceny[i-1] for i in range(1,len(ceny))]
    if not data:
        print("Není co korelovat.")
        return
    df = pd.DataFrame(data)
    korelace = df.corr()
    cesta = _vytvor_cestu(nazev_souboru, prefix)
    plt.figure(figsize=(8, 6))
    sns.heatmap(korelace, annot=True, cmap='coolwarm', fmt='.2f', square=True)
    plt.title("Korelace denních výnosů aktiv")
    plt.tight_layout()
    plt.savefig(cesta, dpi=300)
    plt.close()

def vykresli_realnou_hodnotu_portfolia(vyvoj, inflacni_sazba=0.02, nazev_souboru="grafy/realna_hodnota.png", prefix=''):
    if not vyvoj:
        print("Není co vykreslit.")
        return
    realna_hodnota = [vyvoj[i]/((1+inflacni_sazba)**(i/252)) for i in range(len(vyvoj))]
    cesta = _vytvor_cestu(nazev_souboru, prefix)
    plt.figure(figsize=(10,4))
    plt.plot(realna_hodnota, label="Reálná hodnota portfolia", color="green")
    plt.title("Vývoj reálné hodnoty portfolia (zohledněna inflace)")
    plt.xlabel("Den")
    plt.ylabel("Hodnota (v dnešních Kč)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(cesta, dpi=300)
    plt.close()

def vykresli_rolling_volatilitu(vyvoj, okno=63, nazev_souboru="grafy/rolling_volatilita.png", prefix=''):
    if len(vyvoj)<2:
        print("Není co vykreslit.")
        return
    ser = pd.Series(vyvoj)
    denni_vynosy = ser.pct_change().dropna()
    rolling_vol = denni_vynosy.rolling(window=okno).std()*(252**0.5)
    cesta = _vytvor_cestu(nazev_souboru, prefix)
    plt.figure(figsize=(10,4))
    plt.plot(rolling_vol, label=f"{okno}-denní klouzavá roční volatilita", color="orange")
    plt.title("Rolling volatilita portfolia")
    plt.xlabel("Den")
    plt.ylabel("Volatilita")
    plt.legend()
    plt.tight_layout()
    plt.savefig(cesta, dpi=300)
    plt.close()

def vykresli_vyvoj_vice_portfolii(vysledky, prefix=''):
    if not vysledky:
        print("Není co vykreslit.")
        return
    plt.figure(figsize=(12,6))
    for nazev, hodnoty in vysledky.items():
        plt.plot(range(len(hodnoty)), hodnoty, label=nazev)
    plt.title("Srovnání vývoje více portfolií")
    plt.xlabel("Den")
    plt.ylabel("Hodnota portfolia (Kč)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    cesta = os.path.join("vystupy", "porovnani")
    os.makedirs(cesta, exist_ok=True)
    plt.savefig(os.path.join(cesta, "vyvoj_vice_portfolii.png"), dpi=300)
    plt.close()

def vykresli_vyvoj_vice_portfolii_interaktivne(vysledky, vystup='vystupy/porovnani/vyvoj_portfolii_interaktivne.html'):
    if not vysledky:
        print("Není co vykreslit.")
        return
    fig = go.Figure()
    for nazev, hodnoty in vysledky.items():
        fig.add_trace(go.Scatter(x=list(range(len(hodnoty))), y=hodnoty, mode='lines', name=nazev))
    fig.update_layout(
        title='Vývoj hodnoty více portfolií',
        xaxis_title='Den',
        yaxis_title='Hodnota portfolia (Kč)',
        hovermode='x unified',
        template='plotly_white'
    )
    os.makedirs(os.path.dirname(vystup), exist_ok=True)
    fig.write_html(vystup)
    print(f"Interaktivní graf uložen do '{vystup}'")
