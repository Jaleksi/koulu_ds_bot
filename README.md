# KouluBot

## Komennot
prefix/etuliite = `!`
|Komento|Argumentit|Selitys|Esimerkki|
|--|--|--|--|
|ping|Ei argumentteja|Lähinnä testaukseen, botti vastaa komentoon "pong".|`!ping`|
|uusikurssi|Kurssin tunniste (+ kanava johon liitetään)|Hakee kurssin tiedot ja liittää sen halutulle kanavalle. Jos kanavaa ei määritellä valitsee kanavan jolta käsky annettiin.|`!uusikurssi 902150Y englanti_kanava`|
|poistakurssi|Poistettavan kurssin tunniste|Poistaa kurssin tiedot databasesta ja katkaisee yhteyden sen kanavaan|`!poistakurssi 902150Y`|
|kurssit|Ei argumentteja|Listaa tallennetut kurssit|`!kurssit`|
|deadline|Päivämäärä + viesti|Yhdistää siihen kurssiin deadlinen, millä kanavalla komento suoritetaan.|`!deadline 12.5.21 essee`|
|deadlinet|Ei argumentteja|Listaa kaikki tallennetut deadlinet|`!deadlinet`|
|tori|Ei argumentteja|Hakee Oulun kaupungin nettisivuilla päivittyvän livekuvan torilta ja lähettää sen kanavalle.|`!tori`|

## Database schemat
### Kurssitaulukko (courses)
||id (integer)|peppi_id (text)|title (text)|channel_id (integer)|
|--|--|--|--|--|
|__Selitys__|Kurssin juokseva tunniste taulukossa|Kurssin tunniste pepissä|Kurssin lyhyt selite|Kanavan id, jolle yhdistetty|
|__Esimerkki__|`3`|`902150Y`|`Professional English for Tecnology, ETT (1. vsk) ja ETT (2. vsk) KEVÄT`|`809348914829459496`|

### Deadlinetaulukko (deadlines)
||id (integer)|course_id (integer)|timestamp (text)|message (text)|
|--|--|--|--|--|
|__Selitys__|Deadlinen juokseva tunniste taulukossa|Kurssin id, jota deadline koskee|Deadlinen päivämäärä epoch-muodossa|Deadlinen kuvaus|
|__Esimerkki__|`2`|`1`|`1613133521`|`Esseen palautus`|

### Luentoajat -taulukko (lectures)
||id (integer)|course_id (integer)|start_timestamp (text)|end_timestamp (text)|location (text)|
|--|--|--|--|--|--|
|__Selitys__|Luentoajan juokseva tunniste|Kurssin id, jonka luento on kyseessä|Luennon alkamisajan kohta epoch-muodossa|Luennon loppumisajankohta epoch-muodossa|Luennon sijainti|
|__Esimerkki__|`5`|`4`|`1613133761`|`1613138365`|`Zoom`|
