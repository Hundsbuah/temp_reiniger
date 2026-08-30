# PRODUCT — Temp-Reiniger

Einzelnes Desktop-Utility für Windows (Python / CustomTkinter), kompilierbar zu
einer einzigen EXE über PyInstaller.

## Surface & Mode
- **Surface:** eine Fenster-App (Desktop, keine Web-Oberfläche).
- **Mode:** Operate — der Nutzer vollzieht eine Aufgabe (Temp-Ordnerein
  ansehen und leeren). Scanbarkeit, Konsistenz und native Erwartungen schlagen
  Ausdruck.

## Audience / Job / Action
- **Audience:** Person an ihrem eigenen Windows-PC, die Speicherplatz von drei
  Temp-Ordnern befreien will.
- **Job:** sehen, wie „schwer" jeder der drei Temp-Ordner ist und ihn gezielt
  oder im Ganzen leeren.
- **Action:** `Löschen` pro Ordner, `Alle löschen` für alle drei.

## Die drei Ordner (genau so gefordert)
1. `%TEMP%`
2. `%LOCALAPPDATA%\Temp`
3. `%SystemRoot%\Temp`

> Hinweis (Wahrheit über Windows): `%TEMP%` und `%LOCALAPPDATA%\Temp` zeigen
> auf den selben physischen Ordner. Beide werden dennoch als eigene Karten
> dargestellt (wie gefordert); bei „Alle löschen" wird jeder physische Ordner
> nur einmal geleert (Deduplizierung), damit nichts doppelt verarbeitet wird.

## Constraints
- Wurzelmappen selbst dürfen **nie** gelöscht werden — nur deren Inhalt.
- Keine automatischen Löschungen; nur durch expliziten Button-Klick.
- Gesperrte/in-Benutzung befindliche Dateien werden übersprungen, nicht
  abgebrochen. `C:\Windows\Temp` kann ohne Admin-Rechte nur teilweise geleert
  werden (dann wird übersprungen).
- UI muss während Scan/Lösch nicht einfrieren (Worker-Thread).

## Chosen direction & memorable moment
- **Direction:** „The Scale" — drei Instrument-Felder mit relativen
  Füllstand-Leisten und großen Bahnschrift-Ziffern.
- **Memorable moment:** der Füllstand + die Zahl sinken, nachdem geleert wurde
  (das „Leerziehen" der Container).

## Annahmen (aus dem Brief abgeleitet, kein Antwort-Mechanismus vorhanden)
- UI-Sprache Deutsch (Prompt ist deutsch).
- Framework CustomTkinter (modern, single-EXE-freundlich, echtes Design).
- Gesamt = Summe der drei sichtbaren Karten (visuell konsistent); Duplikat-
  Hinweis wird angezeigt, wenn zwei Pfade identisch sind.
- Kein UAC-Elevate-Forcing; Admin bleibt eine Option des Nutzers.