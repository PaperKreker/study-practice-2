FROM python:3.14

WORKDIR backend/
ENV PYTHONPATH=/backend

COPY ./requirements.txt /backend/requirements.txt
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r /backend/requirements.txt

COPY . /backend

EXPOSE 8000

CMD ["fastapi", "dev", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]
