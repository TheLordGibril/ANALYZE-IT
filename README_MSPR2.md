## **Lancer l'API IA**

```bash
cd ml_api
python -m venv venv
venv\Scripts\activate  # Sur Windows
source venv/bin/activate # Sur Linux

pip install -r requirements.txt
uvicorn app:app --reload
```

L’API sera dispo sur :

```
http://127.0.0.1:8000/predict?country=France&virus=covid&date_start=2025-03-01&date_end=2025-07-01
```

Il faut ensuite démarrer Apollo Server et il appellera l'API pour la query predictPandemic dont voici un exemple :

```js
query Query($country: String!, $virus: String!, $dateStart: String!, $dateEnd: String!) {
  predictPandemic(virus: "covid", country: "France", date_start: "2025-03-01", date_end: "2025-07-01")
}
```
