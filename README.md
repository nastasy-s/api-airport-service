# **Airport API Service**

Airport API Service is a RESTful backend application built with Django and Django REST Framework.
The project provides functionality for managing airports, routes, aircraft, crews, flights, and ticket bookings with JWT-based authentication.

This project demonstrates relational data modeling, nested serialization, custom validation logic, permission management, and API documentation using OpenAPI.

## **Technology Stack**
* Python 3
* Django
* Django REST Framework
* djangorestframework-simplejwt (JWT authentication)
* drf-spectacular (OpenAPI / Swagger)
* SQLite (default database)

## **Core Functionality**

### Airport Management
* Create, retrieve, update, and delete airports
* Each airport stores its name and closest major city

### Route Management
* Define routes between two airports
* Distance tracking between locations

### Aircraft Management
* Manage airplane types
* Manage airplanes with capacity calculation
* Automatic seat capacity property

### Crew Management
* Assign crew members to flights
* Many-to-many relationship between flights and crew

### Flight Management
* Schedule flights with departure and arrival times
* Assign route, airplane, and crew to each flight

### Ticket Booking System
* Authenticated users can create orders
* Each order can include multiple tickets
* Unique seat constraint per flight (flight + row + seat)
* Atomic transaction handling during ticket creation

### Authentication
The API uses JWT authentication.

Obtain Token

Endpoint:
`POST /api/user/token/`

Request body:

`{
  "username": "your_username",
  "password": "your_password"
}`

Response:

`{
  "refresh": "refresh_token",
  "access": "access_token"
}`
Use the access token in the Authorization header:

`Authorization: Bearer <access_token>`
Swagger UI provides an "Authorize" button for convenient authentication.

### Permissions
* Read operations are publicly accessible (where applicable)
* Write operations are restricted to admin users
* Order endpoints only for authenticated users
* Users can access only their own orders

### Installation
Clone the repository
`git clone https://github.com/YOUR_USERNAME/api-airport-service.git
cd api-airport-service`
Create virtual environment
`python3 -m venv venv`
`source venv/bin/activate`
Install dependencies
`pip install -r requirements.txt`
Configure environment variables

Create a `.env` file in the project root:

`DJANGO_SECRET_KEY=your_secret_key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost`
Apply migrations
`python manage.py migrate`
Create superuser
`python manage.py createsuperuser`
Run development server
`python manage.py runserver`
API Documentation

Swagger UI:
http://127.0.0.1:8000/api/docs/

OpenAPI schema:
http://127.0.0.1:8000/api/schema/

### Database Structure Overview
Main entities:
* Airport
* Route (ForeignKey: source, destination)
* AirplaneType
* Airplane (ForeignKey: airplane_type)
* Crew
* Flight (ForeignKey: route, airplane; ManyToMany: crew)
* Order (ForeignKey: user)
* Ticket (ForeignKey: flight, order)

Constraints:
* Unique seat per flight (flight, row, seat)
* Atomic order creation
* Related object optimization using select_related and prefetch_related

### Development Workflow
* Development branch: develop
* Pull request from develop to main
* Feature-based commits with clear naming

### Project Goals
This project demonstrates:
* Proper relational modeling in Django
* Advanced serializer configuration
* Nested object creation
* Transaction management
* JWT-based authentication
* Role-based permission control
* API documentation using OpenAPI

Author
Anastasiia Savchenko