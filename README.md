## Werking

In deze repo staat de code die bij Waternet gebruikt wordt voor de toetsing van de waterkeringen.

### shared

In de shared folder staan alle objecten en functies die over de verschillende toetsingen worden gedeeld. Deze map moet in je ```PYTHONPATH``` staan of je moet het pad importeren aan het begin van het script.

### data connecties

Voor de connectie naar de data zijn de instellingen in ```shared/settings.py``` nodig. In de ```hoogtetoets/scripts/download_data``` map zijn scripts opgenomen om de AHN2, AHN3 en AHN4 data te downloaden. **Let wel** de AHN2 data staat niet meer online. De downloads zijn enkel voor het beheergebied van Waternet ingesteld.

Voorbeeld settings bestand;

```python 
# locatie van de AHN raster bestanden
AHN2_DATA = "/home/breinbaas/Documents/ahn2"
AHN3_DATA = "/home/breinbaas/Documents/ahn3"
AHN4_DATA = "/home/breinbaas/Documents/ahn4"

AHN2_YEAR = 2009  # see https://www.amsterdam.nl/stelselpedia/ahn-index/inwinnen-ahn/ (actually 2008-2010)
AHN3_YEAR = 2015  # see https://www.amsterdam.nl/stelselpedia/ahn-index/inwinnen-ahn/
AHN4_YEAR = 2020  # see https://www.ahn.nl/kwaliteitsbeschrijving

# locatie van diverse shape bestanden
SHAPE_FILES = "/home/breinbaas/Documents/shapefiles"

# pad naar de dijk info shape
LEVEESECTIONS_SHAPE = "/home/breinbaas/Documents/shapefiles/dijksegmenten.shp"
LEVEES_SHAPE = "/home/breinbaas/Documents/shapefiles/dijktrajecten.shp"

# pad naar uitvoer
# dwarsprofielen uitvoer
CROSSSECTION_OUTPUT_DIR = "/home/breinbaas/Documents/dwarsprofielen"
# hoogtetoets uitvoer
HEIGHT_ASSESSMENT_OUTPUT_DIR = "/home/breinbaas/Documents/hoogtetoets"
```

#### Testen

De belangrijkste functionaliteit wordt in de tests gechecked. Dit wordt uitgevoerd met pytest welke je via VSCode kunt inzien en uitvoeren. Alle testen zijn opgenomen in de map ```tests```, alle uitvoer die in deze tests wordt gemaakt komt in de ```testdata/output``` map. Invoer voor de testen moet in de ```testdata``` map.