FROM python:3.9-alpine

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

#inform of the port to be exposed
EXPOSE 56788

#Create a user to run the application NOT as root
RUN adduser --disabled-password --gecos '' --no-create-home  webuser
USER webuser

#Run the application (-u is to avoid buffering)
CMD ["python", "-u", "dictee_tor.py"]