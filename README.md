# store-service-api
This is an API developed with FastAPI and Mongo Atlas to manage information for businesses registered in the system.

# Setup and Run Guide
Follow these steps to set up and run the project in your local environment.

# 1. Clone the Repository
If you haven't already, clone the repository to your local machine:

git clone https://github.com/utn-integrador-III/store-service-api.git
cd store-service-api

# 2. Create and Activate Virtual Environment
It is a best practice to work inside a virtual environment to isolate project dependencies.


# Create the virtual environment (you can name it 'venv' or as you prefer)
python -m venv venv
To activate it:

On Windows:

PowerShell
.\venv\Scripts\activate


source venv/bin/activate
You will know it's active because the environment's name (venv) will appear at the beginning of your command prompt.

# 3. Configure Environment Variables
This project uses a .env file to manage sensitive configurations, such as the database connection.

Create a file named .env in the project root and add the following content, adjusting the values if necessary:

# Connection URL to your MongoDB instance
MONGO_URL="mongodb://localhost:27017"

# Name of the database the application will use
MONGO_DB="store_service"

# Port on which the API will run
API_PORT=8000

# 4. Install Dependencies
With the virtual environment activated, install all required libraries by running:

pip install -r requirements.txt

# 5. Run the API
Now, run the API server with Uvicorn. The --reload flag will cause the server to restart automatically every time you make a change to the code.

uvicorn main:app --reload
If everything is correct, you will see a message in the console indicating that the server is running:

INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)

# API Documentation and Usage
FastAPI automatically generates interactive API documentation (Swagger UI), which is very useful for understanding and testing the endpoints.

Accessing the Docs
Once the server is running, open your browser and go to one of the following URLs:

Swagger UI (Recommended): http://127.0.0.1:8000/docs

ReDoc: http://127.0.0.1:8000/redoc

# Testing the Enterprise Endpoint
In the Swagger documentation, you will find the endpoint we've created.

Endpoint: GET /api/v1/EMPRESA_ESPECIFICA/{id}

Description: Allows you to retrieve detailed information for a company via its ID.

To test it from the browser or a tool like Postman, use the full URL, replacing {id} with a real ID from your database.

# Example URL:
http://127.0.0.1:8000/api/v1/EMPRESA_ESPECIFICA/68674b8ef6585d5be64e81c3