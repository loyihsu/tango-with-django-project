# Startup Script

This is the quick startup script.

```sh
conda create -n rango python=3.7.5
conda activate rango
pip install -r requirements.txt
python manage.py makemigrations rango
python manage.py migrate
python populate_rango.py
python manage.py runserver
```
