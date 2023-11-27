"# celerytask" 
CELERY RUN

in windows:

celery -A ecomproject.celery worker --pool=solo  -l info

celery -A ecomproject.celery worker  -l info


celery -A ecomproject.celery worker -l info
celery -A ecomproject beat -l info
