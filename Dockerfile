# parent image
FROM python:3-onbuild

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# run the command
CMD ["python", "./app.py"]
