# syntax=docker/dockerfile:1

# ---------- Étape de construction ----------
FROM gradle:8.7-jdk21 AS build

WORKDIR /src

# Les descripteurs sont copiés avant les sources : cette couche n'est
# invalidée que si les dépendances changent, pas à chaque modification
# du code. La résolution est donc mise en cache par Docker.
COPY gradle ./gradle
COPY gradlew settings.gradle build.gradle ./
RUN ./gradlew dependencies --no-daemon

COPY src ./src

# bootJar plutôt que build : les tests ont déjà été exécutés par la CI,
# et aucune image n'est publiée sans qu'ils soient passés au vert.
RUN ./gradlew bootJar --no-daemon

# ---------- Étape d'exécution ----------
FROM eclipse-temurin:21-jre-alpine AS runtime

# Utilisateur non privilégié : une compromission de l'application ne
# donne pas les droits root dans le conteneur.
RUN addgroup -S app && adduser -S -G app app

WORKDIR /app

# Le JAR est renommé : son nom d'origine contient le numéro de version,
# qui changera dès la mise en place des releases automatiques.
COPY --from=build --chown=app:app /src/build/libs/*.jar ./app.jar

RUN mkdir -p /data && chown app:app /data
ENV MICROCRM_DB_PATH=/data/microcrm

USER app

# Port réel de l'API. La déclaration précédente indiquait 4200, qui est
# le port du serveur de développement Angular.
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=25s --retries=3 \
  CMD wget -q -O /dev/null http://localhost:8080/ || exit 1

CMD ["java", "-jar", "/app/app.jar"]