## Werking

In deze repo staat de code die bij Waternet gebruikt wordt voor de toetsing van de waterkeringen.

### shared

In de shared folder staan alle objecten en functies die over de verschillende toetsingen worden gedeeld. Deze map moet in je ```PYTHONPATH``` staan of je moet het pad importeren aan het begin van het script.

### data connecties

Voor de connectie naar de data zijn de instellingen in ```shared/settings.py``` nodig. In de ```hoogtetoets/scripts/download_data``` map zijn scripts opgenomen om de AHN2, AHN3 en AHN4 data te downloaden. **Let wel** de AHN2 data staat niet meer online. De downloads zijn enkel voor het beheergebied van Waternet ingesteld.

#### Testen

De belangrijkste functionaliteit wordt in de tests gechecked. Dit wordt uitgevoerd met pytest welke je via VSCode kunt inzien en uitvoeren. Alle testen zijn opgenomen in de map ```tests```, alle uitvoer die in deze tests wordt gemaakt komt in de ```testdata/output``` map. Invoer voor de testen moet in de ```testdata``` map.