# 📖 Projet Phishing Demo – Flask

## 🚀 Présentation
Ce projet est une application **Flask** qui simule une campagne de phishing.  
Elle permet :  
- 📧 d’envoyer des emails piégés (faux Slack par défaut)  
- 📊 de collecter les événements (mails ouverts, clics, téléchargements)  
- 🔐 de capter les identifiants saisis dans une fausse page de connexion  
- 🖥️ de visualiser tous les résultats dans une interface simple  

⚠️ **Attention :** Ce projet est uniquement destiné à un usage pédagogique ou dans un cadre légal (tests de sécurité, sensibilisation).

---

## 🛠️ Installation

### 1. Prérequis
- Python **3.10+**
- `pip` (gestionnaire de packages Python)
- Un compte email SMTP valide  
  👉 ou bien utiliser **MailHog** via Docker Compose pour tester en local.

### 2. Récupération du projet
```bash
git clone https://github.com/Luczerty/phisingproject
cd phisingproject
```

### 3. Création de l’environnement virtuel
```bash
python3 -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
```

### 4. Installation des dépendances
```bash
pip install -r requirements.txt
```

### 5. Configuration
Éditer le fichier **`app.py`** et adapter les variables SMTP :
```python
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
FROM_EMAIL = "exemple@gmail.com"
FROM_PASSWORD = "motdepasse-ou-token"
```

### 6. Lancer l’application
```bash
python app.py
```

Puis ouvrir 👉 [http://localhost:3000](http://localhost:3000)

---

## 📷 Interface utilisateur

- **Accueil (`/`)** → résumé des campagnes, événements et identifiants capturés.  
- **Campagnes (`/campaigns`)** → création et gestion de campagnes (liste des destinataires, description).  
- **Visualisation (`/visualize`)** → affichage des événements et identifiants capturés.  
- **Landing (`/landing`)** → page factice de connexion (Slack par défaut).  
- **Login (`/login`)** → capture des identifiants saisis.  

---

## 📂 Structure du projet

### 📑 Fichiers de données
- `data/events.csv` → événements (mails ouverts, clics, téléchargements, etc.)  
- `data/credentials.csv` → identifiants capturés  
- `data/campaigns.json` → configuration des campagnes  
- `data/hash_mapping.json` → correspondance hash ↔ email  

### 📁 Templates
- `templates/landing.html` → landing page par défaut  
- `templates/emails/phishing_email.html` → mail par défaut  

---

## 📖 Personnalisation

### 🔹 Changer la Landing Page
La landing page est la page affichée lorsqu’un utilisateur clique sur le lien.  
Par défaut :
```python
return render_template("landing.html", hash_id=hash_id)
```

Exemple pour utiliser une variante :
```python
return render_template("landing_microsoft.html", hash_id=hash_id)
```

👉 Tu peux créer plusieurs variantes :  
```text
landing_slack.html      → imitation Slack
landing_microsoft.html  → imitation Microsoft
landing_google.html     → imitation Google
```

---

### 🔹 Changer le Mail envoyé
Le contenu du mail est défini dans la fonction `send_phishing_email`.

**Sujet du mail :**
```python
msg["Subject"] = "🔒 Test de sensibilisation interne"
```

➡️ Exemple modifié :
```python
msg["Subject"] = "⚠️ Connexion Microsoft requise"
```

**Template du mail :**
```text
templates/emails/phishing_email.html
```

👉 Variantes possibles :
```text
emails/slack_email.html → mail Slack
emails/ms_email.html    → mail Microsoft
```

---

## ✅ Résumé rapide
- Modifier `templates/landing.html` → pour changer la landing page  
- Modifier `templates/emails/phishing_email.html` → pour changer le mail  
- Modifier `msg["Subject"]` → pour changer l’objet du mail  

---

## ⚠️ Avertissement
Cet outil est exclusivement conçu pour :  
- la sensibilisation à la cybersécurité  
- les tests de sécurité en environnement autorisé  

❌ Toute utilisation malveillante est strictement interdite.