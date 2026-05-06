# Thesis-Pipeline

Dieses Repository enthält die Evaluationspipeline einer Bachelorarbeit zur Untersuchung der Verständlichkeit von LLM-generiertem Python-Code.

Die Pipeline erzeugt Python-Lösungen für Aufgaben des MBPP-Benchmarks, prüft die funktionale Korrektheit mit automatisierten Testfällen, analysiert funktional korrekte Lösungen mit SonarQube und exportiert die Ergebnisse als strukturierte CSV-Datensätze.

## Unterstützte Modelle und Modi

Aktuell werden folgende Modelle beziehungsweise Ausführungsmodi unterstützt:

- OpenAI (`gpt-5.4`) im Standardmodus
- Anthropic (`claude-sonnet-4-6`) im Standardmodus
- Google Gemini (`gemini-2.5-pro`) im Standardmodus
- Google Gemini (`gemini-2.5-pro`) im Batch-Modus

## Ziel der Pipeline

Für jede Benchmark-Aufgabe durchläuft die Pipeline die folgenden Schritte:

1. Laden einer Aufgabe aus dem MBPP-Datensatz
2. Extraktion der erwarteten Funktionssignatur aus der Referenzlösung
3. Erstellung zweier Promptvarianten:
   - `standard`
   - `readability`
4. Anfrage an das jeweilige LLM
5. Extraktion des generierten Python-Codes aus der Modellantwort
6. Ausführung der MBPP-Testfälle
7. Ausschluss funktional inkorrekter Lösungen von der statischen Analyse
8. Analyse funktional korrekter Lösungen mit SonarQube
9. Speicherung aller Ergebnisse in einer strukturierten CSV-Datei

## Projektstruktur

```text
thesis-pipeline/
├── README.md
├── requirements.txt
├── run_openai.py
├── run_anthropic.py
├── run_gemini.py
├── run_gemini_batch.py
├── data/
│   └── mbpp-modified.jsonl
└── src/
    ├── __init__.py
    ├── config.py
    ├── code_extractor.py
    ├── dataset_writer.py
    ├── mbpp_loader.py
    ├── pipeline_core.py
    ├── prompts.py
    ├── sonar_runner.py
    ├── test_runner.py
    └── providers/
        ├── __init__.py
        ├── openai_provider.py
        ├── anthropic_provider.py
        ├── gemini_provider.py
        └── gemini_batch_provider.py
```

## Datensatz

Die Datei `data/mbpp-modified.jsonl` enthält die in dieser Arbeit verwendete, projektspezifisch angepasste Variante des MBPP-Datensatzes.

Die Datei liegt im JSONL-Format vor und enthält unter anderem Felder wie:

- `text`
- `code`
- `task_id`
- `test_setup_code`
- `test_list`
- `challenge_test_list`

Diese Variante wurde für die konkrete Evaluationspipeline der Bachelorarbeit vorbereitet.

## Voraussetzungen

- Python 3.11 oder neuer empfohlen
- Java Runtime für SonarQube / SonarScanner
- SonarScanner CLI im `PATH`
- optional ein laufender SonarQube-Server für die statische Analyse

## Einrichtung unter Debian / Ubuntu

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip default-jre curl unzip
cd thesis-pipeline
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Anschließend muss eine `.env`-Datei manuell erstellt werden.

## Umgebungsvariablen

Beispiel:

```env
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GEMINI_API_KEY=

ENABLE_SONAR=false
SONAR_HOST_URL=http://localhost:9000
SONAR_TOKEN=
SONAR_POLL_SECONDS=2
SONAR_MAX_POLL_ATTEMPTS=20
```

## SonarQube-Integration

Wenn `ENABLE_SONAR=true` gesetzt ist, werden funktional korrekte Lösungen mit SonarQube analysiert.

Dafür werden benötigt:

- ein laufender SonarQube-Server
- eine gültige `SONAR_HOST_URL`
- ein gültiges `SONAR_TOKEN`
- ein installierter `sonar-scanner` im `PATH`

Nur Lösungen mit `test_status == pass` werden an SonarQube übergeben.

## Ausführung der Pipeline

### OpenAI (Standardmodus)

```bash
source .venv/bin/activate
python run_openai.py --min-task-id 11 --max-task-id 510 --limit 500
```

### Anthropic (Standardmodus)

```bash
source .venv/bin/activate
python run_anthropic.py --min-task-id 11 --max-task-id 510 --limit 500
```

### Gemini (Standardmodus)

```bash
source .venv/bin/activate
python run_gemini.py --min-task-id 11 --max-task-id 510 --limit 500
```

### Gemini (Batch-Modus)

```bash
source .venv/bin/activate
python run_gemini_batch.py --min-task-id 11 --max-task-id 510 --limit 500
```

## Ergebnisdaten

Während der Ausführung werden Laufartefakte im Ordner `outputs/` erzeugt, darunter:

- Ergebnis-CSV-Dateien
- Rohantworten der Modelle
- extrahierter Python-Code
- SonarQube-Projektordner
- Batch-Eingabe- und Batch-Ausgabedateien für Gemini

Diese Laufartefakte sind in der Regel nicht für ein öffentliches Repository gedacht.

## Struktur der Ergebnisdateien

Die CSV-Dateien enthalten unter anderem folgende Felder:

- `run_id`
- `timestamp_utc`
- `provider_latency_seconds`
- `task_id`
- `model_name`
- `provider`
- `prompt_type`
- `test_status`
- `input_tokens`
- `output_tokens`
- `cognitive_complexity`
- `cyclomatic_complexity`
- `lines_of_code`
- `code_smells`


## Sicherheitshinweis

Der generierte Python-Code wird automatisiert in einem Subprozess mit Timeout ausgeführt.

Trotz dieser einfachen Schutzmaßnahmen muss der generierte Code als nicht vertrauenswürdig betrachtet werden. Für größere oder produktionsnahe Experimente ist eine stärker isolierte Ausführungsumgebung empfehlenswert.

