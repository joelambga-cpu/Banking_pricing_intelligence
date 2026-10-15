# Banking Pricing Intelligence — le cinque risposte di business

Snapshot: gennaio 2023–agosto 2026; 5.000 clienti sintetici. Analisi locale completata l'8 ottobre 2026, senza nuova estrazione dei tassi.

## 1. Quanto sono competitivi i tassi sui depositi?

Il portafoglio simulato remunera i depositi a un tasso medio ponderato per saldo del **1,937%**, contro il **2,46%** del benchmark depositi di agosto 2026: uno scarto di **0,523 punti percentuali, circa 52,3 punti base**. Sotto questa specifica metrica, la remunerazione del portafoglio è inferiore al benchmark.

Il DFR BCE è 2,25% e il benchmark mutui 3,55%. Il gap BCE meno benchmark depositi è quindi −0,21 punti percentuali; lo spread benchmark mutui meno benchmark depositi è 1,09 punti percentuali. Questi due indicatori descrivono il contesto di mercato, non lo scarto fra portafoglio clienti e benchmark.

**Limite:** il benchmark depositi riguarda un prodotto con durata specifica; il portafoglio sintetico non ha attributi equivalenti di scadenza/prodotto. Il confronto è illustrativo e non dimostra che ogni cliente riceva un'offerta non competitiva.

**Evidenza:** query 10 per la media ponderata; ultima osservazione in `data/processed/banking_interest_rates_monthly.csv`; calcolo indipendente salvato in `docs/evidence/business_answers.json`. Pagine pertinenti: Executive Overview e Market & Regimes.

## 2. Quali segmenti sono maggiormente esposti ai deflussi?

**Private presenta l'esposizione relativa maggiore; Affluent presenta la proxy di deflusso più elevata in valore assoluto.** La risposta cambia quindi a seconda che si osservi intensità o massa economica.

| Segmento | Clienti totali | Clienti in calo | Quota in calo | Depositi del segmento | Proxy di deflusso | Proxy / depositi |
|---|---:|---:|---:|---:|---:|---:|
| Mass | 3.528 | 1.988 | 56,35% | 56.558.594,06 € | 1.942.135,90 € | 3,43% |
| Affluent | 1.229 | 697 | 56,71% | 101.912.691,21 € | 4.409.053,39 € | 4,33% |
| Private | 243 | 161 | 66,26% | 70.952.287,23 € | 3.463.635,64 € | 4,88% |

Popolazione: tutti i clienti di ciascun segmento, inclusi quelli non eleggibili al repricing. Un cliente è in calo se la variazione dei depositi a 90 giorni è negativa. Proxy individuale = saldo × valore assoluto della variazione negativa / 100; zero per variazioni non negative. La percentuale relativa usa come denominatore tutti i depositi del segmento.

La proxy complessiva è **9.814.824,94 €**. La somma dei valori di segmento esposti è inferiore di un centesimo per arrotondamento: il totale è calcolato prima dell'arrotondamento.

**Limite:** saldi e variazioni sono generati separatamente. La proxy non è un flusso monetario storico osservato e non è una previsione di uscita futura. Le differenze tra segmenti riflettono anche le ipotesi del generatore.

**Evidenza:** query 08 estesa e `data/analytics/segment_pricing_analysis.csv`; ricalcolo indipendente sul CSV clienti. Pagina pertinente: Segment Analysis; i nuovi campi richiedono refresh e integrazione nella presentazione finale.

## 3. Quanto costerebbe aumentare i tassi di 25 punti base?

Il rialzo mirato costa **121.596,82 € annui**, contro **573.558,93 €** per il rialzo a tutti i clienti: un minor costo di **451.962,11 € annui, circa il 78,8%**.

| Strategia | Clienti coinvolti | Depositi coinvolti | Costo incrementale annuo |
|---|---:|---:|---:|
| Generalizzata, +25 bps | 5.000 | 229.423.572,50 € | 573.558,93 € |
| Mirata, +25 bps | 348 | 48.638.727,34 € | 121.596,82 € |

Formula: depositi coinvolti × 0,0025. Un cliente è target se soddisfa insieme saldo ≥50.000 €, variazione a 90 giorni ≤−5% e gap benchmark meno tasso cliente ≥0,25 punti percentuali.

**Interpretazione:** il minor costo deriva dal volume inferiore remunerato con il rialzo. Non dimostra da solo una maggiore efficacia sulla retention. Nello scenario BASE, i depositi trattenuti simulati sono 1.297.184,73 € con intervento mirato e 2.453.706,23 € con intervento generalizzato: maggiore efficienza di costo e maggiore volume assoluto sono obiettivi diversi.

**Limite:** saldi costanti e rialzo applicato per un anno intero. Le risposte di retention sono ipotesi; il confronto fra costo annuo e proxy da variazioni a 90 giorni non misura il ROI.

**Evidenza:** query 07, export strategy_cost_comparison, query 09 per gli scenari. Pagine pertinenti: Executive Overview e Retention Scenarios. Valori già documentati, riconciliati nel controllo di compatibilità della nuova analisi.

## 4. A quali segmenti dare priorità nel repricing?

**Per un intervento orientato alla massa eleggibile, Affluent è il primo segmento da esaminare; Private segue per massa e merita attenzione prioritaria per intensità relativa di esposizione.** Mass presenta un perimetro eleggibile molto più limitato con queste regole.

| Segmento | Clienti target | Quota clienti target | Depositi target | Quota depositi target | Costo annuo +25 bps |
|---|---:|---:|---:|---:|---:|
| Affluent | 252 | 20,50% | 27.013.495,68 € | 26,51% | 67.533,74 € |
| Private | 67 | 27,57% | 19.390.028,29 € | 27,33% | 48.475,07 € |
| Mass | 29 | 0,82% | 2.235.203,37 € | 3,95% | 5.588,01 € |

Le quote hanno come denominatore il totale del rispettivo segmento. Affluent offre la massa target maggiore e la maggiore proxy assoluta di deflusso. Private ha la maggiore quota di clienti in calo e il maggior rapporto proxy/depositi; la sua rilevanza non emerge dal solo numero di clienti.

La selezione resta individuale: dare priorità a un segmento non significa aumentare il tasso a tutti i suoi clienti. La graduatoria è condizionata all'obiettivo e alle soglie adottate; non è una politica ottimale dimostrata. Servirebbero comportamento osservato e un test dell'intervento per stimarne l'effetto reale.

**Evidenza:** query 08, confronto dei risultati Q2 con target, masse e costi. Pagina pertinente: Segment Analysis.

## 5. Qual è l'impatto atteso sulla redditività?

Il progetto quantifica **il costo incrementale della raccolta e uno spread indicativo fra tasso mutui e remunerazione ponderata del portafoglio**. Non permette di stimare il profitto netto della banca.

| Indicatore | Situazione iniziale | Rialzo generalizzato | Rialzo mirato |
|---|---:|---:|---:|
| Tasso ponderato depositi | 1,937% | 2,187% | 1,990% |
| Spread indicativo mutui − tasso ponderato depositi | 1,613 pp | 1,363 pp | 1,560 pp |
| Costo annuo incrementale | — | 573.558,93 € | 121.596,82 € |

Il benchmark mutui resta fisso al 3,55%. Il rialzo generalizzato riduce lo spread proxy di 0,250 punti percentuali; quello mirato di circa 0,053 punti percentuali perché interessa solo parte dei saldi. Questo spread usa la remunerazione del portafoglio; il valore 1,09 pp di Market & Regimes usa invece il benchmark depositi. Le due misure non sono intercambiabili.

**Limite:** mancano portafoglio crediti reale, composizione completa della raccolta, persistenza dei saldi trattenuti, costi operativi, perdite su crediti e commissioni. Il minor costo del targeted non equivale a un incremento dimostrato del profitto.

Formulazione per il portfolio: “Profitability impact is estimated through direct repricing cost and an indicative deposit-to-lending rate spread. It is not intended to represent full bank net interest margin or profitability.” La direzione della differenza è sempre tasso impieghi meno tasso depositi.

**Evidenza:** query 10 e profitability_proxy.csv, riconciliati con calcolo ponderato indipendente; query 07 per i costi. Pagina pertinente: Executive Overview; il dettaglio metodologico resta in questa documentazione.

## Verificabilità e stato

`src/quality/verify_business_answers.py` legge SQLite in sola lettura, esegue le query 07/08/10 e confronta i risultati con calcoli indipendenti a precisione decimale sul CSV clienti. Verifica anche che le nove colonne preesistenti dell'export segmenti mantengano i valori. Scrive evidenze con impronte SHA-256 delle fonti e aggiorna il solo export segmenti dopo il superamento dei controlli.

Esito: controlli superati sui tre segmenti e sulle cinque risposte quantitative. Le evidenze riguardano lo snapshot locale; non costituiscono una nuova verifica delle fonti BCE online. La riconciliazione raw/elaborati, il collaudo completo dell'orchestratore, il refresh e la resa nativa Power BI appartengono alla successiva fase di chiusura. Nessuna pubblicazione eseguita.
