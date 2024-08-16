# NPS Product Surveys

This Django application handles the logic for sending product surveys to customers, capturing their feedback, and storing the results for further analysis. The project is designed to manage surveys across multiple product categories, ensuring that customers provide valuable feedback without being overwhelmed with repeated or redundant survey requests.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Running Tests](#running-tests)

## Features

- **Survey Generation Logic**: Automatically generates surveys for customers based on their orders, following specified business rules to avoid over-surveying.
- **Survey Versioning**: Supports multiple versions of surveys (e.g., with or without demographic questions) based on whether the customer has already provided certain information.
- **Exclusion Criteria**: Excludes customers from surveys based on their purchase history, product categories, and previous survey participation.
- **API Integration**: Captures survey responses via a webhook API and stores the data in the database.
- **Database Storage**: Manages survey data across multiple tables, linking orders, customers, and survey responses.

## Installation

### Prerequisites

- Python 3.8+
- Django 4.0+
- PostgreSQL

### Steps

1. **Clone the Repository**

    ```bash
    git clone https://github.com/Upendrasg/NPS-Product-Surveys.git
    cd nps-product-surveys
    ```

2. **Set Up a Virtual Environment**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install Dependencies**

    ```bash
    cd .\product_survey\product_survey\
    pip install -r requirements.txt
    ```

4. **Create App Migrations File**
    ```bash
    python manage.py makemigrations survey 
    ```

5. **Run Migrations**

    ```bash
    python manage.py migrate
    ```

5. **Create a Superuser**

    ```bash
    python manage.py createsuperuser
    ```

6. **Run the Development Server**

    ```bash
    python manage.py runserver
    ```

7. **Access the Application**

    Open your browser and go to `http://127.0.0.1:8000/admin` to access the Django admin panel and manage surveys.

## Usage

### Sending Surveys

- Surveys are generated and sent based on the criteria specified in the business logic.
- Surveys are sent 30 days after the order delivery, with exclusions applied based on the product category and previous survey participation.
- Use the management command or the admin interface to trigger survey generation.

### Receiving Survey Responses

- The application provides an API endpoint to receive survey responses from Typeform (or any other form service).
- Responses are stored in the `nps_survey_primary_response` and `nps_survey_question_response` tables.

## API Endpoints

### `POST /survey/receive-survey-response/`

This endpoint receives survey response data and stores it in the database.

- **Request Body**: JSON containing survey response data, including customer ID, survey ID, and answers to the survey questions.
- **Response**: Status code `200 OK` on successful data storage.

### `GET surveys/receive_survey_response/`

This endpoint generates a CSV file containing the list of customers eligible for surveys, based on the current date and business logic.

- **Response**: CSV file with customer and survey details.

## Running Tests

To run the test suite:

```bash
python manage.py test

