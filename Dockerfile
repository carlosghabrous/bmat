FROM python:3
ENV PYTHONUNBUFFERED=1

ADD Pipfile /app/Pipfile
ADD Pipfile.lock /app/Pipfile.lock
ENV PIPENV_PIPFILE=/app/Pipfile


ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN python -m venv $VIRTUAL_ENV \
    && pip install --upgrade pip \
    && pip install pipenv \
    && pipenv sync

ADD digital /app/digital
ADD dsrs /app/dsrs
ADD manage.py /app

WORKDIR /app
EXPOSE 8000

CMD ["gunicorn", "--bind", ":8000", "--workers", "3", "digital.wsgi:application"]