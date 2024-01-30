from datetime import datetime, timedelta

from datetime import datetime, timedelta

def create_icalendar_file(salle, horaires):
    # Remplacez les caractères invalides dans le nom de la salle
    salle_cleaned = salle.replace('/', '').replace('*', '').replace(' ', '_')
    
    icalendar_content = """BEGIN:VCALENDAR
METHOD:PUBLISH
PRODID:-//ADE/version 6.0
VERSION:2.0
CALSCALE:GREGORIAN\n"""

    for horaire in horaires:
        dtstart = horaire[0]
        dtend = horaire[1]
        
        icalendar_content += f"""BEGIN:VEVENT
DTSTAMP:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}
DTSTART:{dtstart.strftime('%Y%m%dT%H%M%SZ')}
DTEND:{dtend.strftime('%Y%m%dT%H%M%SZ')}
SUMMARY:Occupation
LOCATION:{salle}
DESCRIPTION:oui
UID:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}-{dtstart.strftime('%Y%m%dT%H%M%SZ')}-{salle}
CREATED:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}
LAST-MODIFIED:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}
SEQUENCE:0
END:VEVENT\n"""

    icalendar_content += "END:VCALENDAR"

    # Écrivez le contenu dans un fichier
    with open(f"calendrier_{salle_cleaned}.ics", "w") as f:
        f.write(icalendar_content)

# Exemple d'utilisation
salle = "8C-041 CHR*  (32pl./32 écrans sans PC)VP TB"
horaires = [
    (datetime(2024, 2, 1, 8, 0), datetime(2024, 2, 1, 10, 0)),
    (datetime(2024, 2, 1, 14, 0), datetime(2024, 2, 1, 16, 0)),
    (datetime(2024, 2, 2, 10, 0), datetime(2024, 2, 2, 12, 0)),
]

create_icalendar_file(salle, horaires)
