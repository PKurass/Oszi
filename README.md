# CAN Oscilloscope

Dieses Projekt stellt ein einfaches Oszilloskop dar, das Spannungswerte von einer CAN-Schnittstelle liest, die Messwerte von 10–500 Hz in 16-Bit-Hexform liefert. Die Werte werden in Dezimal beziehungsweise in Volt umgerechnet und als kontinuierlicher Graph (Spannung gegen Zeit) dargestellt.

## Funktionen
- Kontinuierlicher Plot mit Fensterbreite von einer Sekunde
- "Messung Starten" und "Messung Stoppen/Graph einfrieren"
- Trigger-Funktion auf eine einstellbare Spannung
- Simulation eingebaut, falls keine CAN-Schnittstelle vorhanden ist

## Installation
```
pip install -r requirements.txt
```

## Anwendung
```
python main.py
```

## Erstellen einer Windows-„.exe“
Mit [PyInstaller](https://pyinstaller.org/) kann eine lauffähige Datei erzeugt werden:
```
pyinstaller --onefile --windowed main.py
```
Die erzeugte Datei befindet sich anschließend im `dist/`-Verzeichnis.

## Hinweise
- Die Anwendung setzt `python-can` mit einer konfigurierten `socketcan`-Schnittstelle voraus. Ist keine Schnittstelle verfügbar, arbeitet die App im Simulationsmodus.
- Das Design orientiert sich an modernen dunklen UI-Konzepten.
