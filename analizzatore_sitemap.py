#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gzip
import re
import requests
import csv
import os
import yaml
from collections import defaultdict
from xml.etree import ElementTree as ET
from urllib.parse import urlparse

def carica_configurazione(file_config='config.yaml'):
    """Carica la configurazione dal file YAML."""
    try:
        with open(file_config, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config
    except FileNotFoundError:
        print(f"Errore: File di configurazione '{file_config}' non trovato.")
        print("Assicurati che il file config.yaml sia presente nella directory.")
        exit(1)
    except yaml.YAMLError as e:
        print(f"Errore nel parsing del file di configurazione: {e}")
        exit(1)

def scarica_sitemap(url):
    """Scarica la sitemap e restituisce il contenuto XML."""
    print(f"Scaricamento della sitemap da {url}...")
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Errore nel download della sitemap: {response.status_code}")
    
    # Verifica se il file è compresso in formato gzip
    try:
        # Prova a decomprimere il contenuto
        contenuto_xml = gzip.decompress(response.content)
        print("File compresso in formato gzip decompresso con successo.")
    except:
        # Se non è compresso, usa il contenuto così com'è
        contenuto_xml = response.content
        print("File non compresso in formato gzip, utilizzo diretto del contenuto XML.")
    
    return contenuto_xml

def analizza_sitemap(contenuto_xml):
    """Analizza il contenuto XML della sitemap e restituisce una lista di URL."""
    print("Analisi della sitemap...")
    
    # Namespace per la sitemap XML
    ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    
    try:
        # Parsing del contenuto XML
        root = ET.fromstring(contenuto_xml)
        
        # Estrazione degli URL
        urls = []
        for url_element in root.findall('.//sm:url', ns):
            loc_element = url_element.find('sm:loc', ns)
            if loc_element is not None and loc_element.text:
                urls.append(loc_element.text)
        
        # Se non troviamo URL con il namespace, proviamo senza
        if not urls:
            for url_element in root.findall('.//url'):
                loc_element = url_element.find('loc')
                if loc_element is not None and loc_element.text:
                    urls.append(loc_element.text)
        
        return urls
    except ET.ParseError as e:
        print(f"Errore nel parsing XML: {e}")
        # Prova a stampare l'inizio del contenuto XML per debug
        print("Inizio del contenuto XML ricevuto:")
        print(contenuto_xml[:200])
        raise

def classifica_urls(urls, config):
    """Classifica gli URL in categorie, prodotti e altre pagine."""
    print("Classificazione degli URL...")
    
    # Pattern regex dalla configurazione
    pattern_categoria = config['pattern_categoria']
    pattern_prodotto = config['pattern_prodotto']
    
    categorie = []
    prodotti = []
    altre_pagine = []
    
    for url in urls:
        if re.search(pattern_categoria, url):
            categorie.append(url)
        elif re.search(pattern_prodotto, url):
            prodotti.append(url)
        else:
            altre_pagine.append(url)
    
    return {
        'categorie': categorie,
        'prodotti': prodotti,
        'altre_pagine': altre_pagine
    }

def estrai_nome_categoria(url, config):
    """Estrae il nome della categoria dall'URL."""
    pattern = config['pattern_estrai_categoria']
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None

def estrai_produttore(url, config):
    """Estrae il nome del produttore dall'URL del prodotto."""
    pattern = config['pattern_estrai_produttore']
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None

def genera_statistiche(urls_classificati, config):
    """Genera statistiche sugli URL classificati."""
    print("Generazione delle statistiche...")
    
    categorie = urls_classificati['categorie']
    prodotti = urls_classificati['prodotti']
    altre_pagine = urls_classificati['altre_pagine']
    
    # Conteggio totale
    totale_urls = len(categorie) + len(prodotti) + len(altre_pagine)
    
    # Estrazione dei nomi delle categorie
    nomi_categorie = [estrai_nome_categoria(url, config) for url in categorie]
    nomi_categorie = [nome for nome in nomi_categorie if nome]  # Rimuove i None
    
    # Conteggio dei prodotti per produttore (non più per categoria)
    prodotti_per_produttore = defaultdict(int)
    for url in prodotti:
        produttore = estrai_produttore(url, config)
        if produttore:
            prodotti_per_produttore[produttore] += 1
    
    # Numero di produttori unici
    num_produttori = len(prodotti_per_produttore)
    
    return {
        'totale_urls': totale_urls,
        'num_categorie': len(categorie),
        'num_prodotti': len(prodotti),
        'num_altre_pagine': len(altre_pagine),
        'num_produttori': num_produttori,
        'nomi_categorie': sorted(set(nomi_categorie)),
        'prodotti_per_produttore': dict(prodotti_per_produttore)
    }

def stampa_statistiche(statistiche):
    """Stampa le statistiche in un formato leggibile."""
    print("\n=== STATISTICHE SITEMAP ===")
    print(f"Totale URL: {statistiche['totale_urls']}")
    print(f"Numero di categorie: {statistiche['num_categorie']}")
    print(f"Numero di prodotti: {statistiche['num_prodotti']}")
    print(f"Numero di produttori: {statistiche['num_produttori']}")
    print(f"Numero di altre pagine: {statistiche['num_altre_pagine']}")
    
    print("\n=== CATEGORIE ===")
    for nome in statistiche['nomi_categorie']:
        print(f"- {nome}")
    
    print("\n=== PRODOTTI PER PRODUTTORE ===")
    for produttore, num_prodotti in sorted(statistiche['prodotti_per_produttore'].items()):
        print(f"- {produttore}: {num_prodotti} prodotti")

def salva_risultati_txt(statistiche, directory_output='output'):
    """Salva i risultati in un file di testo."""
    print(f"\nSalvataggio dei risultati in {directory_output}/risultati_sitemap.txt...")
    
    # Crea la directory di output se non esiste
    if not os.path.exists(directory_output):
        os.makedirs(directory_output)
    
    nome_file = os.path.join(directory_output, 'risultati_sitemap.txt')
    
    with open(nome_file, 'w', encoding='utf-8') as f:
        f.write(f"Totale URL: {statistiche['totale_urls']}\n")
        f.write(f"Numero di categorie: {statistiche['num_categorie']}\n")
        f.write(f"Numero di prodotti: {statistiche['num_prodotti']}\n")
        f.write(f"Numero di produttori: {statistiche['num_produttori']}\n")
        f.write(f"Numero di altre pagine: {statistiche['num_altre_pagine']}\n\n")
        
        f.write("=== CATEGORIE ===\n")
        for nome in statistiche['nomi_categorie']:
            f.write(f"- {nome}\n")
        
        f.write("\n=== PRODOTTI PER PRODUTTORE ===\n")
        for produttore, num_prodotti in sorted(statistiche['prodotti_per_produttore'].items()):
            f.write(f"- {produttore}: {num_prodotti} prodotti\n")
    
    print(f"I risultati sono stati salvati nel file '{nome_file}'")

def salva_risultati_csv(statistiche, directory_output='output'):
    """Salva i risultati in file CSV."""
    print(f"\nSalvataggio dei risultati in formato CSV nella directory '{directory_output}'...")
    
    # Crea la directory di output se non esiste
    if not os.path.exists(directory_output):
        os.makedirs(directory_output)
    
    # Salva le categorie in un file CSV
    categorie_file = os.path.join(directory_output, 'categorie.csv')
    with open(categorie_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Nome Categoria'])
        for nome in statistiche['nomi_categorie']:
            writer.writerow([nome])
    
    # Salva i prodotti per produttore in un file CSV
    prodotti_file = os.path.join(directory_output, 'prodotti_per_produttore.csv')
    with open(prodotti_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Produttore', 'Numero Prodotti'])
        for produttore, num_prodotti in sorted(statistiche['prodotti_per_produttore'].items()):
            writer.writerow([produttore, num_prodotti])
    
    # Salva un riepilogo in un file CSV
    riepilogo_file = os.path.join(directory_output, 'riepilogo.csv')
    with open(riepilogo_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Metrica', 'Valore'])
        writer.writerow(['Totale URL', statistiche['totale_urls']])
        writer.writerow(['Numero di categorie', statistiche['num_categorie']])
        writer.writerow(['Numero di prodotti', statistiche['num_prodotti']])
        writer.writerow(['Numero di produttori', statistiche['num_produttori']])
        writer.writerow(['Numero di altre pagine', statistiche['num_altre_pagine']])
    
    print(f"I file CSV sono stati salvati nella directory '{directory_output}'")

def genera_grafico(statistiche, directory_output='output'):
    """Genera un grafico dei produttori principali."""
    try:
        import matplotlib.pyplot as plt
        
        print("\nGenerazione del grafico dei produttori principali...")
        
        # Crea la directory di output se non esiste
        if not os.path.exists(directory_output):
            os.makedirs(directory_output)
        
        # Ordina i produttori per numero di prodotti e prendi i primi 20
        top_produttori = sorted(statistiche['prodotti_per_produttore'].items(), 
                              key=lambda x: x[1], reverse=True)[:20]
        
        produttori = [item[0] for item in top_produttori]
        num_prodotti = [item[1] for item in top_produttori]
        
        # Crea il grafico
        plt.figure(figsize=(12, 8))
        plt.bar(produttori, num_prodotti)
        plt.xticks(rotation=90)
        plt.xlabel('Produttore')
        plt.ylabel('Numero di Prodotti')
        plt.title('Top 20 Produttori per Numero di Prodotti')
        plt.tight_layout()
        
        # Salva il grafico
        grafico_file = os.path.join(directory_output, 'top_produttori.png')
        plt.savefig(grafico_file)
        
        print(f"Il grafico è stato salvato come '{grafico_file}'")
    except ImportError:
        print("\nImpossibile generare il grafico: matplotlib non è installato.")
        print("Per installare matplotlib, esegui: pip install matplotlib")

def main():
    try:
        # Carica la configurazione
        config = carica_configurazione()
        
        # Scarica la sitemap
        contenuto_xml = scarica_sitemap(config['sitemap_url'])
        
        # Analizza la sitemap
        urls = analizza_sitemap(contenuto_xml)
        
        # Classifica gli URL
        urls_classificati = classifica_urls(urls, config)
        
        # Genera statistiche
        statistiche = genera_statistiche(urls_classificati, config)
        
        # Stampa le statistiche
        stampa_statistiche(statistiche)
        
        # Salva i risultati in un file di testo
        salva_risultati_txt(statistiche)
        
        # Salva i risultati in file CSV
        salva_risultati_csv(statistiche)
        
        # Genera un grafico (se matplotlib è installato)
        genera_grafico(statistiche)
        
    except Exception as e:
        print(f"Si è verificato un errore: {e}")

if __name__ == "__main__":
    main() 