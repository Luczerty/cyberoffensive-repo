# 📖 Guide d’installation et d’utilisation – Projet Phishing Demo

## 🚀 Présentation

Ce projet est une application **Flask** qui simule une **campagne de phishing**.  
Il permet :  
- d’envoyer des emails piégés (faux Slack par défaut) 📧  
- de collecter les événements (mails ouverts, liens cliqués, pièces jointes téléchargées) 📊  
- de capter les identifiants saisis dans une fausse page de connexion 🔐  
- de visualiser tous les résultats dans une interface simple  

⚠️ **Ce projet est uniquement destiné à un usage pédagogique ou dans un cadre légal (tests de sécurité, sensibilisation).**

---

## 🛠️ Installation

### 1. Prérequis

- **Python 3.10+**  
- **pip** (gestionnaire de packages Python)  
- Un compte email SMTP valide (par défaut Gmail)  

---

### 2. Récupération du projet

```bash
git clone https://github.com/toncompte/phisingproject.git
cd phisingproject
```

---

### 3. Création de l’environnement virtuel

```bash
python3 -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
```

---

### 4. Installation des dépendances

```bash
pip install -r requirements.txt
```

---

### 5. Configuration des variables d’environnement

Créer un fichier `.env` à la racine :  

```env
# SMTP
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
PHISHING_FROM_EMAIL=ton.email@gmail.com
PHISHING_FROM_PASSWORD=motdepasse_app

# Flask
FLASK_SECRET_KEY=change-me

# Options
OPEN_CREDENTIALS=false
```

⚠️ Pour Gmail : active un **mot de passe d’application**.

---

### 6. Lancer l’application

```bash
python app.py
```

Puis ouvrir 👉 [http://localhost:3000](http://localhost:3000)

---

## 📷 Interface utilisateur

### Accueil (`/`)
Résumé des campagnes, des événements et des credentials capturés.  
![Accueil](images/home.png)

---

### Création d’une campagne (`/campaigns`)
Définir un nom, une description et une liste d’adresses email.  
![Campagnes](images/campaigns.png)

---

### Exemple d’email reçu
![Email Slack](images/email.png)

---

### Page de connexion factice
Saisie email + mot de passe → enregistrés dans `data/credentials.csv`.  
![Landing](images/landing.png)

---

### Visualisation (`/visualize`)
Affichage des événements et credentials capturés.  
![Visualisation](images/visualize.png)

---

## 📂 Structure du projet

```
phisingproject/
│── app.py                 # Application Flask
│── templates/             # Templates HTML
│── static/                # CSS / logos
│── data/                  # Logs (events, credentials, campaigns)
│── slack.ps1              # Fausse pièce jointe
│── requirements.txt       # Dépendances Python
```

---

## 📑 Fichiers de données

- `data/events.csv` → événements (mail ouvert, lien cliqué, etc.)  
- `data/credentials.csv` → identifiants capturés  
- `data/campaigns.json` → configuration des campagnes  
- `data/hash_mapping.json` → correspondances hash/email  

---

## ⚠️ Sécurité & Avertissement

- À utiliser **uniquement** dans un cadre autorisé (tests, formation, sensibilisation).  
- Ne jamais cibler de vraies personnes sans leur consentement.  