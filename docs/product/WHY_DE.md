# Warum dieses Repository existiert

> Englisch ist der Primärtext dieses Repositories. Ein deutscher Klon liegt in `WHY_DE.md`.

## Problem

Viele lokale AI-Builder-Setups sind entweder zu locker oder zu riskant.
Sie schreiben zu leicht in Quellmaterial zurück, vermischen Experiment und echten Projektzustand und setzen voraus, dass Nutzer mit einem terminallastigen Einstieg beginnen wollen.

## Gewählter Ansatz

Dieses Repository nutzt ein lokales GUI-first-Builder-Modell mit drei bewussten Entscheidungen:

1. der Quellpfad bleibt read-only
2. geprüfte Ausgaben gehen nur in eine Sandbox
3. der Ersteinstieg läuft über einen kleinen Setup-Wizard und danach über eine Browser-Oberfläche

## Warum dieser Ansatz

Ich wollte einen Builder-Workflow, der für echte lokale Arbeit nützlich ist, ohne unsichere Direktschreibzugriffe in die Quelle zu normalisieren.
Die read-only-Quellgrenze erzwingt die Trennung zwischen "was schon existiert" und "was gerade ausprobiert wird".
Die Sandbox macht Experimente billig, während das Originalprojekt stabil bleibt.

Ich habe mich außerdem für einen GUI-first-Einstieg entschieden, weil viele lokale Nutzer und kleine Teams zuerst eine sichtbare Arbeitsoberfläche brauchen, bevor sie einen tieferen Operatorpfad brauchen.
Der Wizard reduziert den Reibungsverlust beim ersten Start und macht den Setup-Zustand explizit statt versteckt.

Die Default-Runtime bleibt absichtlich CPU-safe.
Ein tragfähiger portabler Ausgangspunkt ist hier wertvoller, als von Anfang an stärkere Hardware vorauszusetzen.

## Warum nicht die naheliegende Alternative

Ich wollte nicht:

- Direktschreibzugriffe in das gemountete Source-Repo
- einen reinen Terminal-Ersteindruck
- ein hardwarehungriges Default-Setup
- einen Builder-Stack, der sich wie ein Wissenssystem verhält

Diese Entscheidungen hätten den Stack auf den ersten Blick mächtiger wirken lassen, aber weniger diszipliniert und weniger portabel.

## Trade-off

Dieses Design ist langsamer und stärker begrenzt als ein lockerer Aufbau.
Der Nutzer muss eine zusätzliche Grenze und einen zusätzlichen Review-Schritt akzeptieren.
Das ist beabsichtigt.

## Was ich als Nächstes verbessern würde

Wenn ich das weiter ausbaue, würde ich die Designgründe im Repo selbst noch sichtbarer machen:
warum die repo-bridge existiert, warum die Sandbox verpflichtend ist und wo die Builder-Grenze endet.
