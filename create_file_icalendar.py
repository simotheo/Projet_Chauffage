from datetime import datetime, timedelta

def create_icalendar_file(salle, horaires, summaries=None):
    # Remplacez les caractères invalides dans le nom de la salle
    salle_cleaned = salle.replace('/', '').replace('*', '').replace(' ', '_')
    
    icalendar_content = """BEGIN:VCALENDAR
METHOD:PUBLISH
PRODID:-//ADE/version 6.0
VERSION:2.0
CALSCALE:GREGORIAN\n"""

    summaries = summaries or ["Occupation"] * len(horaires)  # Utilise "Occupation" si aucune liste de summaries n'est fournie

        # Vérification si horaires est une liste de tuples de datetime
    if not all(isinstance(horaire, tuple) and len(horaire) == 2 and all(isinstance(dt, datetime) for dt in horaire) for horaire in horaires):
        raise ValueError("horaires should be a list of tuples of datetime objects.")

    for horaire, summary in zip(horaires, summaries):
        dtstart = horaire[0]
        dtend = horaire[1]
        
        icalendar_content += f"""BEGIN:VEVENT
DTSTAMP:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}
DTSTART:{dtstart.strftime('%Y%m%dT%H%M%SZ')}
DTEND:{dtend.strftime('%Y%m%dT%H%M%SZ')}
SUMMARY:{summary}
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

# Exemple d'utilisation avec des summaries personnalisés pour chaque horaire
salle = "8C-030 CHR*  (32pl./32 écrans sans PC)VP TB"
horaires = [
    (datetime(2024, 2, 13, 8, 0), datetime(2024, 2, 13, 10, 0)),
    (datetime(2024, 2, 13, 10, 40), datetime(2024, 2, 13, 11, 0)),
    (datetime(2024, 2, 14, 10, 0), datetime(2024, 2, 14, 12, 0)),
]

summaries = ["Occupation Salle 1", "Reunion", "Maintenance"]

create_icalendar_file(salle, horaires, summaries)
