# 🚨 Projet PoC de Phishing (interne & pédagogique)

⚠️ **Ce projet est un Proof of Concept (PoC) pédagogique uniquement.**
Il ne doit être utilisé que dans un cadre légal, en environnement contrôlé (tests internes, formation, sensibilisation).

---

## 📌 Pré-requis

- Python 3 installé
- Docker & Docker Compose installés
- Installer les dépendances Python :
  ```bash
  pip install flask
  ```

---

## ⚙️ Installation

1. **Cloner le dépôt :**
   ```bash
   git clone <lien-du-repo>
   cd phising-project
   ```

2. **Lancer le backend Flask :**
   ```bash
   python3 app.py
   ```

3. **Lancer le client MailHog (via Docker) :**
   ```bash
   sudo docker compose up -d
   ```
   (Enlevez `sudo` si votre utilisateur est déjà dans le groupe `docker`.)

---

## 🌐 Accès aux services

- Application Flask (serveur de phishing factice) → [http://localhost:3000](http://localhost:3000)
- Client MailHog (visualisation des mails envoyés) → [http://localhost:8025](http://localhost:8025)

---

## 🔍 Comment ça marche ?

La plateforme repose sur **Flask** et propose désormais un tableau de bord complet avec templates HTML.

### `/` (GET)
- Tableau de bord affichant :
  - Un résumé des campagnes enregistrées et des évènements collectés.
  - Un formulaire d'envoi rapide pour tester un message sur un destinataire unique.
  - Un aperçu des dernières campagnes créées.

### `/campaigns` (GET & POST)
- Interface de gestion des campagnes.
- Permet de définir un nom, une description et une liste de destinataires.
- Un bouton « Lancer » déclenche l'envoi du mail de phishing à l'ensemble des contacts sélectionnés.

### `/phisingpixel` (GET)
- Pixel invisible chargé lors de l'ouverture du mail.
- Enregistre dans le journal l'ouverture du message avec l'adresse e-mail du destinataire.

### `/landing` (GET)
- Page de connexion factice générée à partir d'un template.
- Chaque visite est tracée dans le journal (clic sur le lien de la campagne).

### `/download` (GET)
- Déclenche le téléchargement de l'attachement (nom inversé pour renforcer l'illusion).
- L'action est associée à l'utilisateur ayant cliqué.

### `/login` (POST)
- Récupère `username` et `password` soumis via `/landing`.
- Stocke les informations avec l'identifiant de suivi dans `data/credentials.csv`.

### `/visualize` (GET)
- Tableau de bord des journaux :
  - `data/events.csv` pour les ouvertures, clics et téléchargements.
  - `data/credentials.csv` pour les identifiants soumis.

### `/guide` (GET)
- Page de documentation intégrée décrivant les bonnes pratiques et les étapes de mise en œuvre.

---

## 📂 Fichiers générés

Tous les fichiers sont conservés dans le dossier `data/` :

- `events.csv` → journal des interactions (ouverture, clic, téléchargement, envoi).
- `credentials.csv` → identifiants saisis depuis la page de connexion factice.
- `campaigns.json` → campagnes enregistrées depuis l'interface.
- `hash_mapping.json` → correspondance entre identifiant de suivi, adresse e-mail et campagne.

Un fichier `.gitkeep` est présent pour conserver le dossier vide dans Git, mais les données générées sont ignorées par défaut (`.gitignore`).

---

## 🧠 Conseils d'utilisation

- Personnalisez le contenu des templates dans `templates/` pour coller à vos scénarios internes.
- Utilisez la page « Guide » pour partager les bonnes pratiques auprès des équipes sécurité.
- Après chaque campagne, exportez ou supprimez les données sensibles stockées dans `data/`.
