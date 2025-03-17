# Port Scanner Linux

Un outil en ligne de commande pour surveiller les ports ouverts et les connexions établies sur les systèmes Linux Ubuntu.

## 📋 Description

Ce script Python permet de visualiser facilement :
- Les ports en écoute (listening) sur votre système
- Les connexions réseau actives/établies
- Les processus associés à chaque port ouvert

L'outil est particulièrement utile pour :
- Diagnostiquer des problèmes réseau
- Surveiller la sécurité de votre système
- Identifier les applications qui utilisent le réseau

## 🔧 Prérequis

- Python 3.6+
- Système Linux (testé sur Ubuntu)
- Commandes `ss` et `lsof` installées (généralement disponibles par défaut)

## 💻 Installation

1. Clonez ce dépôt :
```bash
git clone https://github.com/ahottois/scan-port.git
cd port-scanner
```

2. Rendez le script exécutable :
```bash
chmod +x scan-port.py
```

## 🚀 Utilisation

### Commande de base

```bash
./scan-port.py
```

Par défaut, l'outil affiche tous les ports en écoute et les connexions établies.

### Options disponibles

```
-l, --listening    Affiche uniquement les ports en écoute
-c, --connections  Affiche uniquement les connexions établies
-p, --processes    Inclut les informations sur les processus (nécessite sudo)
-o, --output       Sauvegarde les résultats dans un fichier
```

### Exemples d'utilisation

Afficher tous les ports en écoute avec les processus associés :
```bash
sudo ./scan-port.py -l -p
```

Afficher uniquement les connexions établies et sauvegarder dans un fichier :
```bash
./scan-port.py -c -o resultats.txt
```

## 📊 Exemple de sortie

```
Scan des ports et connexions - 2025-03-17 14:30:45
==================================================

Ports en écoute:
--------------------------------------------------
Protocole  Adresse locale        Port      
--------------------------------------------------
tcp        0.0.0.0               22        
  └─ sshd (PID: 1234, User: root)
tcp        127.0.0.1             3306      
  └─ mysqld (PID: 5678, User: mysql)
tcp        127.0.0.1             8080      
  └─ python3 (PID: 9101, User: utilisateur)

Connexions établies:
--------------------------------------------------------------------------------
Protocole  Adresse locale        Port local Adresse distante     Port distant
--------------------------------------------------------------------------------
tcp        192.168.1.100         22         192.168.1.10        56789     
tcp        192.168.1.100         80         192.168.1.20        34567     
```

## 🛡️ Sécurité

Pour afficher les informations de processus (`-p`), des privilèges administrateur sont nécessaires. Utilisez `sudo` :

```bash
sudo ./scan-port.py -p
```
