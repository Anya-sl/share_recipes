FROM python:3.8-slim
RUN pip3 install --upgrade pip 
WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt --no-cache-dir
COPY . .
CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]
RUN python manage.py collectstatic --no-input
