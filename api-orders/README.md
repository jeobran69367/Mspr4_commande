# Service Commandes - PayeTonKawa

Service de gestion des commandes avec Saga Pattern pour l'importateur de café PayeTonKawa.

## 🎯 Fonctionnalités

- Gestion complète des commandes (création, suivi, annulation)
- Gestion des paniers (panier → validation → livraison)
- Pattern Saga pour les transactions distribuées
- Validation des stocks et disponibilité clients
- Intégration RabbitMQ pour la communication entre services
- Gestion des paiements (simulation Stripe/PayPal)
- Suivi des livraisons
- API REST complète avec FastAPI

## 🏗️ Architecture

### Stack Technique
- **Python**: 3.11
- **Framework**: FastAPI
- **Base de données**: PostgreSQL (port 5435)
- **Message Broker**: RabbitMQ (instance partagée)
- **ORM**: SQLAlchemy (async)
- **Migrations**: Alembic
- **Tests**: Pytest
- **Conteneurisation**: Docker

### Ports
- **API**: 8003
- **Database**: 5435

## 🚀 Installation et Démarrage

### Prérequis
- Python 3.11+
- Docker et Docker Compose
- PostgreSQL 15+
- RabbitMQ 3+

### Installation Locale

1. **Cloner le repository**
```bash
git clone <repository-url>
cd Mspr4_commande/api-orders
```

2. **Créer un environnement virtuel**
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

3. **Installer les dépendances**
```bash
make install-dev
# ou
pip install -r requirements-dev.txt
```

4. **Configurer les variables d'environnement**
```bash
cp .env.template .env
# Éditer .env avec vos configurations
```

5. **Démarrer RabbitMQ (si nécessaire)**

⚠️ **Important**: Ce service utilise une instance **partagée** de RabbitMQ.

**Option A**: Si vous avez déjà RabbitMQ sur votre machine (port 5672 occupé):
- Utilisez votre instance existante
- Assurez-vous que les credentials correspondent à ceux dans `.env`
- Passez à l'étape 6

**Option B**: Si vous n'avez pas RabbitMQ:
```bash
# Démarrer RabbitMQ séparément
docker-compose -f docker-compose.rabbitmq.yml up -d
```

6. **Démarrer la base de données et l'API**
```bash
make docker-up
# ou
docker-compose up -d
```

7. **Initialiser la base de données**
```bash
make init-db
# ou
python scripts/init_db.py
```

8. **Lancer le service**
```bash
make run
# ou
uvicorn app.main:app --reload --host 0.0.0.0 --port 8003
```

### Avec Docker Compose

⚠️ **Note sur RabbitMQ**: Le docker-compose.yml utilise une instance **partagée** de RabbitMQ. Si vous avez déjà RabbitMQ en cours d'exécution sur le port 5672, le service se connectera automatiquement via `host.docker.internal:5672`.

Si vous n'avez pas RabbitMQ, démarrez-le d'abord:
```bash
# Démarrer RabbitMQ séparément (si nécessaire)
docker-compose -f docker-compose.rabbitmq.yml up -d
```

Ensuite, démarrer les services:
```bash
# Démarrer la base de données et l'API
docker-compose up -d

# Voir les logs
docker-compose logs -f orders-api

# Arrêter les services
docker-compose down
```

## 📚 Documentation API

Une fois le service démarré, accédez à :
- **Swagger UI**: http://localhost:8003/docs
- **ReDoc**: http://localhost:8003/redoc

### Endpoints Principaux

#### Orders
- `POST /api/v1/orders` - Créer une commande
- `GET /api/v1/orders/{order_id}` - Obtenir une commande
- `GET /api/v1/orders/numero/{numero}` - Obtenir une commande par numéro
- `GET /api/v1/orders` - Lister les commandes
- `PUT /api/v1/orders/{order_id}` - Mettre à jour une commande
- `PATCH /api/v1/orders/{order_id}/status` - Changer le statut
- `POST /api/v1/orders/{order_id}/cancel` - Annuler une commande

#### Carts
- `GET /api/v1/carts/{customer_id}` - Obtenir le panier
- `POST /api/v1/carts/{customer_id}/items` - Ajouter un article
- `PUT /api/v1/carts/{customer_id}/items/{item_id}` - Modifier un article
- `DELETE /api/v1/carts/{customer_id}/items/{item_id}` - Supprimer un article
- `DELETE /api/v1/carts/{customer_id}` - Vider le panier
- `GET /api/v1/carts/{customer_id}/summary` - Résumé du panier

## 🔄 Saga Pattern

Le service utilise le Saga Pattern pour gérer les transactions distribuées :

### Create Order Saga
1. **Validate Customer** - Valider l'existence et l'état du client
2. **Reserve Stock** - Réserver le stock des produits
3. **Create Payment** - Créer le paiement
4. **Create Shipment** - Créer la livraison

En cas d'échec à n'importe quelle étape, les compensations sont exécutées dans l'ordre inverse.

### Compensations
- **Reserve Stock** → Release Stock
- **Create Payment** → Refund Payment
- **Create Shipment** → Cancel Shipment

## 🧪 Tests

```bash
# Exécuter tous les tests
make test

# Avec couverture
make test-cov

# Tests spécifiques
pytest tests/test_orders.py
pytest tests/test_sagas.py
```

## 🛠️ Développement

### Commandes Make

```bash
make help           # Afficher l'aide
make install        # Installer les dépendances
make install-dev    # Installer les dépendances de développement
make test           # Exécuter les tests
make lint           # Linter le code
make format         # Formater le code
make run            # Lancer le serveur de développement
make docker-up      # Démarrer les services Docker
make docker-down    # Arrêter les services Docker
make migrate        # Exécuter les migrations
make init-db        # Initialiser la base de données
make seed-db        # Insérer des données de test
make clean          # Nettoyer les fichiers temporaires
```

### Migrations de Base de Données

```bash
# Créer une nouvelle migration
alembic revision --autogenerate -m "Description"

# Appliquer les migrations
alembic upgrade head

# Revenir en arrière
alembic downgrade -1
```

## 🔧 Configuration

Les variables d'environnement principales :

- `DATABASE_URL` - URL de connexion PostgreSQL
- `RABBITMQ_HOST` - Hôte RabbitMQ
- `RABBITMQ_EXCHANGE` - Exchange RabbitMQ (partagé)
- `CUSTOMER_SERVICE_URL` - URL du service Clients
- `PRODUCT_SERVICE_URL` - URL du service Produits
- `PAYMENT_GATEWAY_URL` - URL de la passerelle de paiement

Voir `.env.template` pour la liste complète.

## 📊 Structure du Projet

```
api-orders/
├── app/
│   ├── api/            # Endpoints API
│   ├── events/         # RabbitMQ event handling
│   ├── integrations/   # Clients externes
│   ├── models/         # Modèles SQLAlchemy
│   ├── repositories/   # Repository pattern
│   ├── sagas/          # Saga pattern implementation
│   ├── schemas/        # Schémas Pydantic
│   ├── services/       # Logique métier
│   ├── utils/          # Utilitaires
│   ├── workflows/      # Workflows métier
│   ├── config.py       # Configuration
│   ├── database.py     # Setup DB
│   └── main.py         # Application FastAPI
├── migrations/         # Migrations Alembic
├── scripts/            # Scripts utilitaires
├── tests/              # Tests
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## 🤝 Contribution

1. Créer une branche feature
2. Implémenter les changements
3. Ajouter des tests
4. Soumettre une Pull Request

## 🔧 Dépannage

### Erreur: "port is already allocated" (RabbitMQ)

Si vous obtenez l'erreur `Bind for 0.0.0.0:5672 failed: port is already allocated`:

**Cause**: Vous avez déjà une instance RabbitMQ en cours d'exécution (ce qui est attendu pour un environnement partagé).

**Solution**:
1. Le service utilise automatiquement votre instance RabbitMQ existante
2. Assurez-vous que les credentials dans `.env` correspondent à votre instance:
   ```
   RABBITMQ_HOST=localhost
   RABBITMQ_USER=payetonkawa
   RABBITMQ_PASSWORD=payetonkawa123
   ```
3. Lancez juste les services sans RabbitMQ:
   ```bash
   docker-compose up -d
   ```

### Erreur: Connection refused (RabbitMQ)

Si l'API ne peut pas se connecter à RabbitMQ:

1. Vérifiez que RabbitMQ est en cours d'exécution:
   ```bash
   docker ps | grep rabbitmq
   # ou si installé localement
   sudo systemctl status rabbitmq-server
   ```

2. Testez la connexion:
   ```bash
   telnet localhost 5672
   ```

3. Si vous utilisez Docker Desktop sur Mac/Windows, assurez-vous que `host.docker.internal` fonctionne

### Vérifier les connexions

```bash
# Vérifier les logs de l'API
docker-compose logs -f orders-api

# Vérifier la santé des services
docker-compose ps

# Interface RabbitMQ Management
open http://localhost:15672
# Login: payetonkawa / payetonkawa123
```

## 📝 Licence

Copyright (c) 2024 PayeTonKawa
