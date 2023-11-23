# Using official python runtime base image
FROM schoolofdevops/vote:v6

# Set the application directory
WORKDIR /app

# Install our requirements.txt
# RUN pip freeze > requirements.txt
ADD vote/requirements.txt /app/requirements.txt
COPY vote/app.py /app/app.py
COPY vote/templates/index.html /app/templates/index.html
COPY vote/static/stylesheets/* /app/static/stylesheets/
RUN pip install -r requirements.txt

# Copy our code from the current folder to /app inside the container
ADD . /app

# Make port 80 available for links and/or publish
EXPOSE 80

# Define our command to be run when launching the container
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:80", "--log-file", "-", "--access-logfile", "-", "--workers", "4", "--keep-alive", "0"]
