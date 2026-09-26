#!/usr/bin/env sh
# Sauvegarde et restauration de la base de données de MicroCRM.
#
# Usage :
#   ./scripts/backup-database.sh backup              crée une archive horodatée
#   ./scripts/backup-database.sh restore <archive>   restaure l'archive indiquée
#   ./scripts/backup-database.sh list                liste les sauvegardes existantes
#
# Le service back-end est arrêté pendant l'opération. HSQLDB répartit ses
# données sur plusieurs fichiers : une copie effectuée pendant que
# l'application écrit pourrait en capturer un état incohérent. Le service
# est indisponible quelques secondes, ce qui est le prix d'une sauvegarde
# dont on sait qu'elle est restaurable.

set -eu

# Le script s'exécute depuis la racine du dépôt, où se trouve le fichier
# d'orchestration.
cd "$(dirname "$0")/.."

SERVICE="back"
CONTAINER="microcrm-back"
BACKUP_DIR="${BACKUP_DIR:-backups}"
# Image minimale, figée : elle ne sert qu'à lire et écrire une archive.
HELPER_IMAGE="alpine:3.22"

usage() {
  echo "Usage : $0 backup | restore <archive> | list"
  exit 1
}

# Le conteneur doit exister — même arrêté — pour que son volume soit
# accessible sans avoir à en deviner le nom.
require_container() {
  if ! docker container inspect "$CONTAINER" >/dev/null 2>&1; then
    echo "Conteneur $CONTAINER introuvable. Lancer d'abord : docker compose up -d"
    exit 1
  fi
}

case "${1:-}" in

  backup)
    require_container
    mkdir -p "$BACKUP_DIR"
    archive="microcrm-$(date +%Y%m%d-%H%M%S).tar.gz"

    echo "Arrêt du service $SERVICE..."
    docker compose stop "$SERVICE" >/dev/null

    echo "Archivage des données..."
    docker run --rm \
      --volumes-from "$CONTAINER" \
      -v "$(pwd)/$BACKUP_DIR:/backup" \
      "$HELPER_IMAGE" \
      tar czf "/backup/$archive" -C /data .

    echo "Redémarrage du service..."
    docker compose start "$SERVICE" >/dev/null

    echo "Sauvegarde créée : $BACKUP_DIR/$archive"
    ;;

  restore)
    archive="${2:-}"
    [ -n "$archive" ] || usage
    # L'archive est vérifiée avant toute interruption de service.
    [ -f "$BACKUP_DIR/$archive" ] || { echo "Archive introuvable : $BACKUP_DIR/$archive"; exit 1; }
    require_container

    echo "Arrêt du service $SERVICE..."
    docker compose stop "$SERVICE" >/dev/null

    echo "Restauration de $archive..."
    # Le contenu existant est effacé avant extraction : une restauration
    # doit rendre l'état exact de la sauvegarde, sans résidu.
    docker run --rm \
      --volumes-from "$CONTAINER" \
      -v "$(pwd)/$BACKUP_DIR:/backup" \
      -e ARCHIVE="$archive" \
      "$HELPER_IMAGE" \
      sh -c 'rm -rf /data/* /data/.[!.]* 2>/dev/null; tar xzf "/backup/$ARCHIVE" -C /data'

    echo "Redémarrage du service..."
    docker compose start "$SERVICE" >/dev/null

    echo "Restauration terminée. Vérifier : curl -s http://localhost:8080/persons"
    ;;

  list)
    ls -1t "$BACKUP_DIR" 2>/dev/null || echo "Aucune sauvegarde dans $BACKUP_DIR/"
    ;;

  *)
    usage
    ;;
esac