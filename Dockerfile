FROM python:3.10

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install -y libgl1

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 7860

CMD ["python", "app.py"]