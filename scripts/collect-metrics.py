#!/usr/bin/env python3
"""Calcule les métriques DORA et les KPI du pipeline depuis l'historique GitHub Actions.

Le calcul est reproductible : relancer le script sur le même historique
produit les mêmes valeurs. Seule la bibliothèque standard est utilisée.

Usage :
    ./scripts/collect-metrics.py
    GITHUB_TOKEN=... ./scripts/collect-metrics.py   # quota d'API plus élevé

Le jeton est facultatif. Sans lui, l'API publique autorise 60 requêtes par
heure et par adresse IP, ce qui suffit pour ce dépôt. Il ne doit jamais être
écrit dans un fichier ni committé.

Conventions de calcul — voir la documentation technique, section 6 :
  - Déploiement : exécution réussie du workflow sur main comportant le job
    de publication d'images.
  - Lead time : du commit ayant déclenché la première exécution sur une
    branche jusqu'à la fin du pipeline de fusion sur main.
  - Échec de changement : exécution en échec sur main déclenchée par un push.
  - Les pull requests de mise à jour automatique des dépendances sont exclues
    des métriques de livraison : elles mesurent l'obsolescence de la stack,
    non le processus de l'équipe.
"""

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime
from statistics import mean, median

REPOSITORY = os.environ.get("GITHUB_REPOSITORY", "clems2/P7-CICD-Full-Stack")
WORKFLOW_NAME = "CI/CD"
MAIN_BRANCH = "main"
AUTOMATED_ACTOR = "dependabot[bot]"
PUBLISH_JOB_PREFIX = "Publish image"
TEST_STEPS = {
    "back": "Build, test and generate coverage",
    "front": "Test and generate coverage",
}
API = "https://api.github.com"


def fetch(path):
    """Interroge l'API GitHub et renvoie la réponse décodée."""
    request = urllib.request.Request(f"{API}{path}")
    request.add_header("Accept", "application/vnd.github+json")
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        if error.code == 403:
            sys.exit("Quota d'API atteint. Réessayer plus tard ou définir GITHUB_TOKEN.")
        raise


def parse(timestamp):
    return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))


def seconds_between(start, end):
    return (parse(end) - parse(start)).total_seconds()


def fetch_runs():
    """Récupère toutes les exécutions du workflow, page par page."""
    runs, page = [], 1
    while True:
        batch = fetch(f"/repos/{REPOSITORY}/actions/runs?per_page=100&page={page}")
        runs.extend(batch["workflow_runs"])
        if len(runs) >= batch["total_count"] or not batch["workflow_runs"]:
            break
        page += 1
    return [run for run in runs if run["name"] == WORKFLOW_NAME]


def fetch_jobs(run_id):
    return fetch(f"/repos/{REPOSITORY}/actions/runs/{run_id}/jobs")["jobs"]


def summarize(values, unit):
    if not values:
        return "aucune donnée"
    return (f"médiane {median(values):.1f} {unit}, moyenne {mean(values):.1f} {unit} "
            f"(n={len(values)}, min {min(values):.1f}, max {max(values):.1f})")


def merged_branch(run):
    """Extrait la branche fusionnée du message d'un commit de fusion."""
    message = run["head_commit"]["message"].split("\n")[0]
    if "from " not in message:
        return None
    return message.split("from ", 1)[1].split("/", 1)[-1].strip()


def lead_times(runs):
    """Lead time en minutes, pour chaque branche humaine fusionnée sur main."""
    pull_requests = [r for r in runs
                     if r["event"] == "pull_request" and r["actor"]["login"] != AUTOMATED_ACTOR]
    values = []
    for merge in (r for r in runs if r["event"] == "push" and r["head_branch"] == MAIN_BRANCH):
        branch = merged_branch(merge)
        if not branch or branch.startswith("dependabot/"):
            continue
        attempts = [r for r in pull_requests if r["head_branch"] == branch]
        if not attempts:
            continue
        first = min(attempts, key=lambda r: r["created_at"])
        values.append(seconds_between(first["head_commit"]["timestamp"], merge["updated_at"]) / 60)
    return values


def restore_times(main_runs):
    """Durée, en heures, entre un échec sur main et le retour au vert suivant."""
    ordered = sorted(main_runs, key=lambda r: r["created_at"])
    values = []
    for index, run in enumerate(ordered):
        if run["conclusion"] != "failure":
            continue
        recovery = next((r for r in ordered[index + 1:] if r["conclusion"] == "success"), None)
        if recovery:
            values.append(seconds_between(run["created_at"], recovery["updated_at"]) / 3600)
    return values


def main():
    runs = fetch_runs()
    main_runs = [r for r in runs if r["head_branch"] == MAIN_BRANCH]
    pushes = [r for r in main_runs if r["event"] == "push"]

    # Les déploiements sont identifiés par la présence du job de publication.
    deployments, test_durations = [], {name: [] for name in TEST_STEPS}
    for run in (r for r in pushes if r["conclusion"] == "success"):
        jobs = fetch_jobs(run["id"])
        if any(job["name"].startswith(PUBLISH_JOB_PREFIX) for job in jobs):
            deployments.append(run)
        for job in jobs:
            for component, step_name in TEST_STEPS.items():
                for step in job.get("steps", []):
                    if step["name"] == step_name and step.get("completed_at"):
                        test_durations[component].append(
                            seconds_between(step["started_at"], step["completed_at"]))

    pull_requests = [r for r in runs if r["event"] == "pull_request"]
    rejected = [r for r in pull_requests if r["conclusion"] == "failure"]
    failed_pushes = [r for r in pushes if r["conclusion"] == "failure"]

    print(f"Dépôt : {REPOSITORY} — {len(runs)} exécutions du workflow {WORKFLOW_NAME}\n")

    print("## Métriques DORA\n")
    print(f"- Lead time : {summarize(lead_times(runs), 'min')}")
    if deployments:
        first = min(parse(r["created_at"]) for r in deployments)
        last = max(parse(r["created_at"]) for r in deployments)
        days = max((last - first).total_seconds() / 86400, 1)
        print(f"- Deployment frequency : {len(deployments)} publications en "
              f"{days:.1f} jours, soit {len(deployments) / days:.2f} par jour")
    else:
        print("- Deployment frequency : aucune publication")
    rate = 100 * len(failed_pushes) / len(pushes) if pushes else 0
    print(f"- Change failure rate : {rate:.1f} % ({len(failed_pushes)}/{len(pushes)} intégrations)")
    print(f"- MTTR pipeline : {summarize(restore_times(main_runs), 'h')}")
    print("- MTTR application : relevé depuis les logs d'accès, hors du périmètre de ce script\n")

    print("## KPI du pipeline\n")
    for event in ("pull_request", "push", "schedule"):
        durations = [seconds_between(r["run_started_at"], r["updated_at"])
                     for r in runs if r["event"] == event and r["conclusion"] == "success"]
        print(f"- Durée du pipeline ({event}) : {summarize(durations, 's')}")
    for component, durations in test_durations.items():
        print(f"- Durée des tests ({component}) : {summarize(durations, 's')}")
    rejection = 100 * len(rejected) / len(pull_requests) if pull_requests else 0
    automated = [r for r in pull_requests if r["actor"]["login"] == AUTOMATED_ACTOR]
    automated_rejected = [r for r in rejected if r["actor"]["login"] == AUTOMATED_ACTOR]
    print(f"- Taux de rejet par la CI : {rejection:.1f} % ({len(rejected)}/{len(pull_requests)}), "
          f"dont {len(automated_rejected)}/{len(automated)} mises à jour automatiques")


if __name__ == "__main__":
    main()
