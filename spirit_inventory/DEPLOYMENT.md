# Deployment Guide — AWS Lightsail + PostgreSQL + Nginx + Gunicorn

## 1. Lightsail Instance

Create a new instance:
- Blueprint: Ubuntu 22.04 LTS
- Plan: (2GB RAM, 1 vCPU, 60GB SSD)
- Enable automatic snapshots: 

Open ports in Lightsail firewall:
- 22 (SSH)
- 80 (HTTP)
- 443 (HTTPS)

---

## 2. Initial Server Setup

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv nginx postgresql postgresql-contrib certbot python3-certbot-nginx git
```

---

## 3. PostgreSQL Setup

```bash
sudo -u postgres psql

CREATE DATABASE spirit_inventory;
CREATE USER inventory_user WITH PASSWORD 'your-strong-password';
ALTER ROLE inventory_user SET client_encoding TO 'utf8';
ALTER ROLE inventory_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE inventory_user SET timezone TO 'America/New_York';
GRANT ALL PRIVILEGES ON DATABASE spirit_inventory TO inventory_user;
\q
```

---

## 4. Application Setup

```bash
# Create app user
sudo useradd -m -s /bin/bash spiritapp
sudo su - spiritapp

# Clone your repo
git clone https://github.com/yourrepo/spirit_inventory.git
cd spirit_inventory

# Virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements/production.txt

# Environment variables
cp .env.example .env
nano .env   # Fill in all values

# Collect static files
python manage.py collectstatic --settings=config.settings.production --no-input

# Run migrations
python manage.py migrate --settings=spirit_inventory.settings.production

# Create superuser
python manage.py createsuperuser --settings=spirit_inventory.settings.production
```

---

## 5. Gunicorn Setup (via Supervisor)

```bash
sudo apt install -y supervisor

sudo nano /etc/supervisor/conf.d/spirit_inventory.conf
```

```ini
[program:spirit_inventory]
command=/home/spiritapp/spirit_inventory/venv/bin/gunicorn config.wsgi:application --workers 3 --bind unix:/run/spirit_inventory.sock
directory=/home/spiritapp/spirit_inventory
user=spiritapp
autostart=true
autorestart=true
stderr_logfile=/var/log/spirit_inventory/gunicorn.err.log
stdout_logfile=/var/log/spirit_inventory/gunicorn.out.log
environment=DJANGO_SETTINGS_MODULE="spirit_inventory.settings.production"
```

```bash
sudo mkdir -p /var/log/spirit_inventory
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start spirit_inventory
```

---

## 6. Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/spirit_inventory
```

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    client_max_body_size 10M;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        root /home/spiritapp/spirit_inventory;
    }

    location /media/ {
        root /home/spiritapp/spirit_inventory;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/spirit_inventory.sock;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/spirit_inventory /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 7. SSL with Let's Encrypt

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
# Auto-renewal is set up by certbot automatically
```

---

## 8. Deployment Updates (after code changes)

```bash
sudo su - spiritapp
cd spirit_inventory
source venv/bin/activate
git pull
pip install -r requirements/production.txt
python manage.py migrate --settings=spirit_inventory.settings.production
python manage.py collectstatic --settings=spirit_inventory.settings.production --no-input
sudo supervisorctl restart spirit_inventory
```

---

## 9. Backups

### Automatic: Lightsail snapshots
Enable in Lightsail console → Instances → your instance → Snapshots
Cost: ~$2/month for daily snapshots (7-day retention)

### Manual PostgreSQL backup from app (on-demand)
```bash
pg_dump -U spirit_user spirit_inventory > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Restore
```bash
psql -U spirit_user spirit_inventory < backup_file.sql
```

---

## 10. Cost Summary

| Service                  | Monthly Cost |
|--------------------------|-------------|
| Lightsail instance (2GB) | $10.00      |
| Lightsail snapshots      | ~$2.00      |
| Domain (annual / 12)     | ~$1.17      |
| **Total**                | **~$13/month** |