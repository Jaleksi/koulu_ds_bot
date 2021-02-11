# KouluBot

## Komennot
prefix/etuliite = `!`
|Komento|Argumentit|Selitys|Esimerkki|
|--|--|--|--|
|ping|Ei argumentteja|Lähinnä testaukseen, botti vastaa komentoon "pong".|`!ping`|
|uusikurssi|Kurssin tunniste (+ kanava johon liitetään)|Hakee kurssin tiedot ja liittää sen halutulle kanavalle. Jos kanavaa ei määritellä valitsee kanavan jolta käsky annettiin.|`!uusikurssi 902150Y englanti_kanava`|
|poistakurssi|Poistettavan kurssin tunniste|Poistaa kurssin tiedot databasesta ja katkaisee yhteyden sen kanavaan|`!poistakurssi 902150Y`|
|kurssit|Ei argumentteja|Listaa tallennetut kurssit|`!kurssit`|
|tori|Ei argumentteja|Hakee Oulun kaupungin nettisivuilla päivittyvän livekuvan torilta ja lähettää sen kanavalle.|`!tori`|

## Database schemat
### Kurssitaulukko (courses)
||id (text)|title (text)|channel (integer)|
|--|--|--|--|
|Selitys|Kurssin tunniste|Kurssin lyhyt selite|Kanavan id, jolle yhdistetty|
|Esimerkki|`902150Y`|`Professional English for Tecnology, ETT (1. vsk) ja ETT (2. vsk) KEVÄT`|`809348914829459496`|

### Muistutustaulukko (alarms)
### TODO
