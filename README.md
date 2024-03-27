# pco-weattherAPI

## Prérequis

- Git
- Python 3.x
- Pip (gestionnaire de paquets Python)
- Node.js
- npm (gestionnaire de paquets Node.js)

## Installation

```
git clone https://github.com/Conisla/pco-weatherAPI.git
```

### API

```
cd back

py -m venv .env

.env\Scripts\activate

pip install -r requirements.txt
```

### Front

```
cd front/wfm-api

npm i
```

## Configurer le projet Django

Création de la base de donnée et d'un profil administrateur

```
python manage.py migrate

python manage.py createsuperuser
```

## Démarrer l'API

dans le répertoire back/weatherAPI

```
python manage.py runserver
```

## Utiliser le front

dans le répertoire front/wfm-api

```
npm run serve
```
