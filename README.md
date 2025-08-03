# Discord Bot

Hier findest du den Source Code zu meinem Discord Bot. Für diese Tutorialreihe benutze ich [Pycord](https://github.com/Pycord-Development/pycord).  
Das ist eine Python-Bibliothek, die auf [discord.py](https://github.com/Rapptz/discord.py) basiert und mit der wir auf die Discord API zugreifen.
Wenn es euch gefaellt, gib ein Star :O

## Projektbeschreibung
Dies ist ein selbstentwickelter Discord-Bot, programmiert in Python mit dem **py-cord** Framework. Der Bot bietet simple Error Handler sowie ein durchdachtes Verifizerungs System.

## Funktionen
- Error Handler
- Verifizierung System mit Sql3 Datenbank
- Ticket System statt Channel erstellt es private threads
- more coming...

## Technische Details
- Programmiersprache: Python 3.9+  
- Framework: **py-cord**  
- Versionskontrolle: Git / GitHub ([Link zum Repo](https://github.com/InvalidDavid/DiscordBot))  

### Hosting-Varianten
- **Raspberry Pi:** Hosting auf Raspberry Pi mit Raspbian OS (Debian-basiert) inkl. Autostart über systemd  
- **Online-Hosting:** Deployment auf Cloud-Plattformen (z.B. Heroku, Replit) mit Plattform-spezifischem Monitoring und Neustart  

## Installation & Nutzung

### Voraussetzungen
- Python 3.9 oder höher installiert  
- Discord Bot Token (Discord Developer Portal)  
- Raspberry Pi / Linux-System oder Cloud-Plattform (für Hosting)  

### Setup
1. Repository klonen:  
   `git clone https://github.com/InvalidDavid/DiscordBot.git`  
2. Verzeichnis wechseln:  
   `cd DiscordBot`  
3. Abhängigkeiten installieren:  
   `pip install -r requirements.txt` (enthält py-cord)  
4. Bot Token in `config.py` oder Umgebungsvariable eintragen  
5. Bot starten:  
   `python main.py`  

### Autostart (Raspberry Pi)
- systemd-Service-Datei erstellen, um den Bot automatisch beim Systemstart zu starten  

### Autostart / Monitoring (Online-Hosting)
- Plattform-spezifische Tools nutzen, z.B. Heroku Dyno Restart, Replit Always-On



## Wichtige Hinweise
- Ihr braucht eine Kategorie names "Data" wo eure datenbanken erstellt werden
- Die Codes nicht als eure ausgeben.  
- Lizenz beachten.  
- Es kommen regelmäßig neue Codes und Updates.  

## Kontakt
Bei Fragen oder Feedback gerne Issues eröffnen oder mich direkt kontaktieren.
Auf Discord -> InvalidDavid (809739434537910283)
