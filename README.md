# Trendfy

![Tests](https://github.com/romavini/trendfy/actions/workflows/tests.yml/badge.svg)

This repository is the experimental part of the final paper of the PostGraduation in Artificial Intelligence and Machine Learning

## Run

### Start Database

```bash
(venv) $> make run
```

or

```bash
(venv) $> docker-compose up -d
```

### Collect Data

```bash
(venv) $> python -m trendfy --collect <max_albuns>
```

Where `<max_albuns>` refers to the max albums to be collected by year in search.

### Analyse Data

```bash
(venv) $> python -m trendfy --analyse
```
