FROM python:3
ENV PYTHONUNBUFFERED=1

ADD Pipfile /app/Pipfile
ADD Pipfile.lock /app/Pipfile.lock
ENV PIPENV_PIPFILE=/app/Pipfile

RUN python -m venv /app/env \
    && /app/env/bin/pip install --upgrade pip \
    && /app/env/bin/pip install pipenv \
    && /app/env/bin/pipenv sync

ADD digital /app/digital
ADD dsrs /app/dsrs
ADD manage.py /app
WORKDIR /app

ENV VIRTUAL_ENV /app/env 
ENV PATH /app/env/bin:$PATH
EXPOSE 8000

CMD ["gunicorn", "--bind", ":8000", "--workers", "3", "digital.wsgi:application"]