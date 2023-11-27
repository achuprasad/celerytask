"# celerytask" 
CELERY RUN

in windows:

celery -A ecomproject.celery worker --pool=solo  -l info

celery -A ecomproject.celery worker  -l info


celery -A ecomproject.celery worker -l info
celery -A ecomproject beat -l info



redis-server     
redis-cli     
celery -A xtract.celery worker --pool=threads  -l info

celery -A xtract.celery worker  -l info

celery -A xtract.celery worker --concurrency=5  -l info 

celery -A xtract beat -l INFO

celery -A xtract.celery worker --pool=solo  -l info 
