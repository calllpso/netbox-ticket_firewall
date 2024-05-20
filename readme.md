Install plugin:
    source /opt/netbox/venv/bin/activate
    pip install -e /path/to/plugin     
Migrations DB:
	python manage.py makemigrations ticket_firewall --dry-run
	python manage.py makemigrations ticket_firewall
	python manage.py migrate
