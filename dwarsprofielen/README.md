## Werking

Je kunt het uitvoerpad van de dwarsprofielen instellen via ```shared/settings.py``` en de ```CROSSSECTION_OUTPUT_DIR``` variabele.

Stel op ```main.py``` in welke parameters je wilt gebruiken, bijvoorbeeld;

```python
DTCODE = "V344" # dit is de dijktraject code
HOH = 100       # dit is de gewenste hart op hart afstand
LEFT = 20       # het aantal meters dat het dwarsprofiel richting de boezem moet lopen
RIGHT = 50      # het aantal meters dat het dwarsprofiel richting de polder moet lopen
```

Run het script via ```python main.py```

Je krijgt nu in het uitvoerpad de volgende bestanden / paden;

- DIJKTRAJECTCODE
    - 2d; dit zijn de x,y punten van een 2d representatie van het profiel, geschikt om in DStab te kopieren
    - 3d; dit zijn bestanden met de complete dwarsprofiel informatie, l van referentielijn, x, y, z coordinaten
    - plots; plotjes van de dwarsprofielen
    - een shape bestand met de locatie van de dwarsprofielen voor QGis / ArcGIS