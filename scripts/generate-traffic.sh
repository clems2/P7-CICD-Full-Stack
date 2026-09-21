#!/usr/bin/env sh
# Génère du trafic applicatif pour alimenter les tableaux de bord de
# supervision : requêtes valides, erreurs 404 et erreurs de validation.
# Usage : ./scripts/generate-traffic.sh [nombre_de_cycles]

set -eu

FRONT_URL="${FRONT_URL:-http://localhost}"
API_URL="${API_URL:-http://localhost}"
CYCLES="${1:-30}"

echo "Génération de $CYCLES cycles vers $FRONT_URL et $API_URL"

i=1
while [ "$i" -le "$CYCLES" ]; do
  # Trafic nominal
  curl -s -o /dev/null "$FRONT_URL/"
  curl -s -o /dev/null "$API_URL/persons"
  curl -s -o /dev/null "$API_URL/organizations"

  # Une requête sur cinq déclenche une erreur, pour que les
  # visualisations d'erreurs aient de la matière.
  if [ $((i % 5)) -eq 0 ]; then
    curl -s -o /dev/null "$API_URL/persons/999999"
    curl -s -o /dev/null "$API_URL/organizations/999999"
    # 405 : méthode non autorisée
    curl -s -o /dev/null -X DELETE "$API_URL/persons"
  fi

  i=$((i + 1))
done

echo "Terminé. Attendre quelques secondes avant de consulter Kibana."