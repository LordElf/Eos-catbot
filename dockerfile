# Use an official Python runtime as a parent image
FROM python:3.10

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip install  -r requirements.txt

EXPOSE 8081

# Run app.py when the container launches
CMD ["python", "discord_bot.py"]