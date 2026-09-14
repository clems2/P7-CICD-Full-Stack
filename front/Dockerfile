# syntax=docker/dockerfile:1

# ---------- Étape de construction ----------
FROM node:20-alpine AS build

WORKDIR /src

# Descripteurs avant les sources : la couche d'installation n'est
# invalidée que si les dépendances changent.
COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# Sur une machine vierge, l'invite d'acceptation des statistiques de la
# CLI Angular peut bloquer le build.
ENV NG_CLI_ANALYTICS=false
RUN npx ng build --configuration production

# ---------- Étape d'exécution ----------
FROM caddy:2-alpine AS runtime

RUN addgroup -S app && adduser -S -G app app

COPY Caddyfile /etc/caddy/Caddyfile
COPY --from=build --chown=app:app /src/dist/microcrm/browser /srv

USER app

# Port supérieur à 1024 : un processus non privilégié ne peut pas
# écouter sur 80. L'orchestration fait la correspondance vers l'hôte.
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -q -O /dev/null http://localhost:8080/ || exit 1

CMD ["caddy", "run", "--config", "/etc/caddy/Caddyfile"]