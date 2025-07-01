## **Lancer l'API IA**

```bash
python -m venv venv
venv\Scripts\activate  # Sur Windows
source venv/bin/activate # Sur Linux
```
```bash
pip install -r requirements.txt
uvicorn app:app --reload
```

L’API sera dispo sur :

```
http://127.0.0.1:8000/predict?country=France&virus=covid&date=2025-07-01
```

Il faut ensuite démarrer Apollo Server et il appellera l'API pour la query predictPandemic dont voici un exemple :

```js
query ExampleQuery($country: String!, $virus: String!, $date: String!) {
  predictPandemic(country: "France", virus: "covid", date: "2025-07-01")
}
```