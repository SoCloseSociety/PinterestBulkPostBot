---
name: neo-connector
description: Régénère NEO_CONNECTOR.md (manifeste de connexion pour NeoBot) en auditant ce repo.
---

Tu es en train d'auditer CE repo pour produire un manifeste de connexion machine-lisible
destiné à NeoBot (l'agent Neo de SoClose). NeoBot doit pouvoir appeler TOUTES les
fonctionnalités exposées par ce projet sans deviner. Ne rien inventer : tout doit être
prouvé par le code. Si une info est absente, écris "UNKNOWN -- <fichier où elle devrait être>".

Étapes :
1. Détecte le type de projet (Next.js API routes, FastAPI, Express, etc.) et le framework.
2. Trouve TOUTES les routes/endpoints exposés (HTTP, webhooks, SSE/WebSocket, cron, queues).
   Pour Next.js : src/app/**/route.ts + pages/api/**. Pour FastAPI : @app/@router décorateurs.
   Pour Express : app.get/post/... + routers montés.
3. Pour chaque endpoint, extrait : méthode, chemin complet, auth requise (header/cookie/clé),
   params d'entrée (body/query, types, requis/optionnels), forme de la réponse, codes d'erreur,
   et s'il est long-running (pattern generate -> poll status -> fetch result).
4. Liste les variables d'env nécessaires pour appeler le service (clés API, base URL, secrets)
   -- noms uniquement, JAMAIS les valeurs.
5. Détecte la base URL de prod (depuis README, vercel/config, docker-compose, CLAUDE.md).
6. Note les flux multi-étapes (ex: création job async, polling, callback) en pseudo-séquence.

Écris le résultat dans NEO_CONNECTOR.md à la racine, AVEC EXACTEMENT cette structure :

# NEO_CONNECTOR -- <nom du projet>
- service: <slug>
- base_url_prod: <url ou UNKNOWN>
- auth: <type: x-api-key | Bearer | cookie | none> ; header: <nom> ; env_var: <NOM_VAR>
- env_required: [LISTE_DES_NOMS]
- generated_at: <laisser vide, NeoBot le datera>

## Endpoints
Pour CHAQUE endpoint, un bloc :
### <METHOD> <path>
- auth: <oui/non + comment>
- async: <true/false> (true si generate->poll)
- input: <table param | type | requis | description>
- output: <forme JSON résumée>
- errors: <codes + sens>
- example_curl: <exemple réel d'appel>

## Flows
Séquences multi-étapes (ex: 1. POST /generate -> jobId ; 2. GET /status/{jobId} ; 3. GET /result/{jobId}).

## Gaps
Tout ce qui est UNKNOWN ou ambigu, avec le fichier à vérifier.

Termine par un récap : nombre d'endpoints trouvés, combien sont déjà couverts vs nouveaux.
Si le projet n'expose AUCUNE API HTTP (CLI/scraper/bot pur), dis-le clairement et note
qu'il ne doit PAS être câblé comme outils HTTP Neo.
