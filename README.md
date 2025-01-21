# ha-techem
Dette er en integrasjon for å overvåke forbruket av varmtvann og energi i home assistant.

Eksempel på oppsett med målere:
![techem](https://github.com/user-attachments/assets/7996c413-66d1-4f89-a137-abc06f195706)

Koden er oversatt og utviklet med utgangspunkt i [@khaffner](https://github.com/khaffner) sitt shell-script. ([github](https://github.com/khaffner/homeserver/blob/master/home-assistant/config/scripts/techem.sh))

## Installasjon

### Python
1. Last ned python scriptet og plasser dette i ```/config/scripts/python/```

### Terminal
1. Kjør kommandoen ```docker exec -ti homeassistant bash```
2. Kjør kommanden ```python3 -m pip install requests```
3. Bruk ```Ctrl+P + Ctrl+Q``` for å forlate docker containeren

### YAML
1. Opprett ```.yaml``` filer dersom du mangler noen av disse
2. Kopier og lim inn konfigurasjonene fra ```.yaml``` filene

### TenancyID
1. Logg inn på [TechemAdmin](https://beboer.techemadmin.no/)
2. Åpne utviklerverktøyet i nettleseren din (F12)
3. Trykk på 'Network' i menyen
4. Refresh nettsiden (F5)
5. Finn en ```graphql``` request i listen
6. Finn ```objectId``` under 'Payload' i requesten

### Secrets.yaml
1. Oppdater mailadressen i ```secrets.yaml```  (techem_email) til [TechemAdmin](https://beboer.techemadmin.no/) mailadressen din
2. Oppdater passordet i ```secrets.yaml``` (techem_password) til [TechemAdmin](https://beboer.techemadmin.no/) passordet ditt
3. Oppdater ID i ```secrets.yaml``` (techem_objectId) til det 7-sifrede tallet du fant i forrige del

**Til slutt:** Restart HA og verifiser at begge hovedsensorene og de seks utledede templatesensorene finnes i (Innstillinger -> Enheter og tjenester -> Entiteter):
- ```sensor.techem_yearly```
- ```sensor.techem_weekly```
- ```sensor.energi_i_ar```
- ```sensor.energi_sammenlignet_med_i_fjor```
- ```sensor.varmtvann_i_ar```
- ```sensor.varmtvann_sammenlignet_med_i_fjor```
- ```sensor.energi_daglig_snitt_siste_syv_dager```
- ```sensor.energi_sammenlignet_med_forrige_syv_dagers_periode```
- ```sensor.varmtvann_daglig_snitt_siste_syv_dager```
- ```sensor.varmtvann_sammenlignet_med_forrige_syv_dagers_periode```

## Konfigurasjon
### Home Assistant kort
Eksempel på oppsett av et kort fra bildet over:
![techem1](https://github.com/user-attachments/assets/13dbe176-f038-4039-8456-9564575fbbf8)

### Python
Python koden kan konfigureres til å hente data fra ulike perioder. Per nå ligger det to funksjoner inne for å konstruere korrekt datoformat:
- ```get_date_as_string(n: int)``` returnerer datoen ```n``` dager tilbake i tid.
- ```get_first_date_as_string()``` returnerer datoen til den første dagen i året.

Koden er nå satt opp til å både hente ut forbruk så langt dette året, og fra for 8 dager siden til for 1 dager siden (for å hindre manglende ny data), og regne om dette til et daglig gjennomsnitt.
