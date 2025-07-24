# 📊 Analizzatore Sitemap XML

Un tool Python per analizzare sitemap XML di e-commerce e generare statistiche. **⚠️ Attenzione**: questo script è configurato per strutture URL specifiche e richiede adattamento per il tuo caso d'uso.

## ✨ Cosa fa

- Scarica e analizza sitemap XML automaticamente
- Classifica le URL in categorie, prodotti e altre pagine
- Genera statistiche (URL totali, categorie, prodotti, produttori)
- Esporta i risultati in TXT, CSV e grafici

## 🚀 Installazione e Utilizzo

### 1. Installa i requisiti
```bash
pip install requests matplotlib PyYAML
```

### 2. Scarica lo script
```bash
git clone https://github.com/yourusername/analizzatore-sitemap-xml.git
cd analizzatore-sitemap-xml
```

### 3. Configura lo script
```bash
cp config.example.yaml config.yaml
```
Poi modifica `config.yaml` con l'URL della tua sitemap e adatta i pattern regex alla tua struttura URL.

### 4. Lancialo
```bash
python analizzatore_sitemap.py
```

## 📊 Struttura URL Supportata

Lo script è configurato per strutture URL specifiche che potrebbero non corrispondere alla tua:

- **Categorie**: `/it/nome-categoria/123/`
- **Prodotti**: `/it/nome-produttore/nome-categoria/nome-prodotto/id-prodotto/`
- **Altre pagine**: tutto il resto

**⚠️ Importante**: Se la tua struttura URL è diversa, dovrai modificare i pattern regex nel file `config.yaml`.

## 📁 Output

Lo script crea una cartella `output/` con:
- `risultati_sitemap.txt` - Statistiche complete
- `categorie.csv` - Lista categorie
- `prodotti_per_produttore.csv` - Prodotti per produttore
- `riepilogo.csv` - Riepilogo
- `top_produttori.png` - Grafico top 20 produttori

## ⚙️ Personalizzazione

**Questo script richiede personalizzazione per funzionare con la tua struttura URL.**

Modifica il file `config.yaml` per adattarlo al tuo caso:

```yaml
# URL della sitemap
sitemap_url: "https://tuosito.com/sitemap.xml"

# Pattern per identificare pagine categoria
pattern_categoria: "/it/[^/]+/\\d{3}/$"

# Pattern per identificare pagine prodotto
pattern_prodotto: "/it/[^/]+/[^/]+/[^/]+/[^/]+/$"

# Pattern per estrarre nome categoria
pattern_estrai_categoria: "/it/([^/]+)/\\d{3}/$"

# Pattern per estrarre produttore
pattern_estrai_produttore: "/it/([^/]+)/[^/]+/[^/]+/[^/]+/$"
```

### 🔧 Come Adattare i Pattern

1. **Analizza la tua struttura URL** - esamina come sono strutturate le tue URL
2. **Modifica i pattern regex** - adatta i pattern nel `config.yaml`
3. **Testa lo script** - verifica che la classificazione funzioni correttamente

### 📝 Esempi di Pattern

- **Categoria semplice**: `/categoria/123/` → `pattern_categoria: "/[^/]+/\\d+/$"`
- **Prodotto con più livelli**: `/cat1/cat2/prodotto/123/` → `pattern_prodotto: "/[^/]+/[^/]+/[^/]+/\\d+/$"`

## 📝 Licenza

MIT License - vedi [LICENSE](LICENSE)

## 🤝 Contributi

Contributi benvenuti! Apri una issue o una pull request.

## ⚠️ Disclaimer

**Questo script è fornito "così com'è" senza alcuna garanzia. Non è previsto supporto tecnico.**

- Lo script richiede conoscenze di regex e Python per essere adattato
- Usalo solo se sai cosa stai facendo e comprendi i rischi
- L'autore non si assume responsabilità per eventuali danni o problemi
- Testa sempre lo script in un ambiente sicuro prima dell'uso in produzione

---

⭐ Se ti è utile, dai una stella al progetto! 