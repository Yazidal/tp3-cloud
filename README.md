# Starter - Cloud Migration Challenge

Lancer le monolithe :

```bash
cp .env.example .env      # une seule fois : identifiants PostgreSQL
docker compose up -d --build
./smoke_test.sh
```

Avant toute modification, observez son comportement lorsque le conteneur est supprimé puis recréé.

Le projet se déroule ensuite en deux temps :

1. rendre l'application **Cloud-ready localement** (état externalisé, replicas, configuration runtime) ;
2. démarrer le **AWS Academy Learner Lab** dès le début du TP pour vérifier l'accès, tout en terminant le refactor local ; le déploiement AWS commence lorsque la base Cloud-ready est stable.

Le starter utilise un petit classifieur Iris pré-entraîné sans scikit-learn au runtime afin que les images Docker restent légères sur les petites VM du laboratoire.

## Stockage objet

Les datasets ne sont plus écrits dans `./uploads` (perdu avec le conteneur) mais
dans un bucket S3. En local, le service `s3` (versitygw) expose l'API S3 sur
`http://localhost:9000` avec un backend persistant (`volume s3data`).

`storage.py` ne fixe `endpoint_url` et les clés **que si** `S3_ENDPOINT_URL` /
`S3_ACCESS_KEY` sont présentes : sur AWS ces variables sont retirées et boto3
utilise automatiquement le rôle d'instance IAM.

