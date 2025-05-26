# Eskoz

**Eskoz** is a Django-based project designed to help you quickly and easily create a multilingual blog, with a straightforward deployment process.

## Requirements

Make sure you have the following installed on your system:
- Docker
- Docker Compose

## Installation

### 1. Clone the repository:
```sh
git clone git@github.com:DonAsako/eskoz.git
cd eskoz
```

### 2. Copy the example environment variables file:
```sh
cp .env.example .env
```

### 3. Edit the .env file to configure your environment variables.

### 4. Build and start the Docker containers in detached mode:
```sh
docker compose up --build -d
```

### 5. Creating the first admin user
To create the first Django superuser, run :
```sh
docker compose exec web python manage.py createsuperuser
```

## Key Features
- Ready-to-use multilingual blog
- Easy deployment with Docker
- Built-in Django admin interface

## License
This project is licensed under the GNU General Public License v3.0.
See the [LICENSE](LICENSE) file for more details.