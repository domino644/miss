# Opis datasetu

Ten zbiór danych zawiera informacje o wykrytych anomaliach termicznych (punktach pożaru) pobrane z systemu **NASA FIRMS** (sensor VIIRS). Dane służą jako podstawa do walidacji i inicjalizacji automatu komórkowego.

## 📌 Informacje ogólne
* **Źródło:** Satelity NOAA-20 (N20) oraz Suomi NPP (SNPP).
* **Rozdzielczość:** Każdy punkt to piksel o rozmiarze ok. **375m x 375m**.
* **Obszar:** Wyspa Rodos, Grecja.

---

## 📊 Opis kolumn w pliku CSV

| Kolumna | Nazwa | Opis i znaczenie |
| :--- | :--- | :--- |
| `latitude` | Szerokość geogr. | Współrzędna Y punktu zapłonu. |
| `longitude` | Długość geogr. | Współrzędna X punktu zapłonu. |
| `brightness` | Jasność (K) | Temperatura w kanale I4 (podczerwień). Im wyższa, tym intensywniejszy ogień. |
| `acq_date` | Data | Data wykrycia pożaru (YYYY-MM-DD). |
| `acq_time` | Godzina (UTC) | Czas przelotu satelity nad obszarem (HHMM). |
| `confidence` | Pewność | Wiarygodność detekcji: `h` (wysoka), `n` (nominalna), `l` (niska). |
| `frp` | Moc ognia (MW) | *Fire Radiative Power* – energia emitowana przez pożar. Kluczowa dla prędkości rozprzestrzeniania. |
| `bright_t31` | Temp. tła (K) | Temperatura podłoża/chmur w kanale M15. |
| `daynight` | Dzień/Noc | `D` = Day (Dzień), `N` = Night (Noc). |
| `timestamp` | Znacznik czasu | **Kluczowa kolumna dla symulacji.** Połączona data i godzina w formacie chronologicznym. |

---