## **Lancer l'API IA**

```bash
cd ml_api
python -m venv venv
venv\Scripts\activate  # Sur Windows
source venv/bin/activate # Sur Linux

pip install -r requirements.txt
uvicorn app:app --reload
```

L’API sera disponible sur :

```
http://127.0.0.1:8000/predict?country=France&virus=covid&date_start=2025-03-01&date_end=2025-07-01
```

Il faut ensuite démarrer Apollo Server comme dans le premier README.md puis il appellera l'API IA que l'on vient de lancer avec uvicorn pour effectuer la query predictPandemic dont voici un exemple :

```js
query Query($country: String!, $virus: String!, $dateStart: String!, $dateEnd: String!) {
  predictPandemic(virus: "covid", country: "France", date_start: "2025-03-01", date_end: "2025-07-01")
}
```

Après avoir lancé l'API IA et Apollo Server, il ne reste plus qu'à lancer le frontend :

```bash
cd frontend
npm run dev
```

---

## ***Livrables***

- Une documentation détaillée comprenant le choix de l’algorithme utilisé pour créer l’IA ainsi que les principes d’ergonomie et d’accessibilité mis en place de l’interface utilisateur. Les métriques de performance de votre IA devront être apportée (Précision, score, etc.).
La documentation sur l'ergonomie et l'accessibilité se trouve ici : `documentation_conduite_au_changement.pdf.
Le benchmark des modèles IA se trouve ici : `rapport_benchmark.pdf


- Benchmark des solutions Front-end : `frontend_benchmark.pdf`

- Une application Front-end moderne respectant l’intégralité des points évoqués dans l’expression du besoin en justifiant les technologies utilisées. `/frontend`

- Une API IA développée en Python en justifiant les technologies additionnelles utilisées. `/ml_api`

- Une documentation d’API mise à jour de type OPEN API. `/backend/openapi_MSPR502.yaml`

- Des tests automatisés et rapport de couverture des tests pour l’interface utilisateur. La couverture des tests effectués avec Cypress est de 77,87% et une capture d'écran des résultats est accessible ici : `documentation_conduite_au_changement.pdf`. Les résultats sont également disponibles ici : `/cypress/coverage/lcov-report/index.html`

- Une documentation en lien avec la conduite au changement dans le contexte de l’accessibilité. `documentation_conduite_au_changement.pdf`