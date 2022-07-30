FROM python:3.9.10

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn
COPY . .



# run the app with app server
CMD [ "gunicorn", "-c", "gunicorn.conf", "app:web_app" ]

# Run the following command to see the image:
# docker build -t lims-back-end-python ./
# docker run -d -p 5000:5000 -d lims-back-end-python

#docker ps
