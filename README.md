# Spotify Clone

This project is a **Spotify Clone** built using **Django** as the backend framework, **PostgreSQL** as the database, and **HTML/CSS/JavaScript** with **Tailwind CSS** for the front end. The app replicates some of the key features of Spotify, including music search, playlists, and more, using the **Spotify API** for retrieving music data.

## Features

- **User Authentication:** Sign up, log in, and log out functionality.
- **Music Search:** Search for tracks, artists, or albums using the Spotify API.
- **Playlist Management:** Create, manage, and add tracks to playlists.
- **Spotify API Integration:** The app uses a custom token creation mechanism to access Spotify's API for music data retrieval.
- **Responsive Design:** Fully responsive layout using Tailwind CSS.
- **Dynamic Content:** Real-time updates of playlists, search results, and tracks.
- **PostgreSQL Integration:** For efficient and scalable database management.

## Tech Stack

- **Backend:** Django (Python)
- **Frontend:** HTML, CSS, JavaScript, Tailwind CSS
- **Database:** PostgreSQL
- **API:** Spotify API (OAuth for token creation)
- **Version Control:** Git & GitHub

## Installation

### Prerequisites
Ensure that you have the following installed on your machine:

- Python 3.x
- PostgreSQL
- Django
- Node.js and npm (for managing JavaScript dependencies)

### Steps to Set Up the Project

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Nader-Mamdouh/Django-Spotify-Clone.git
   cd spotify-clone
2. **Setup Virtual Enviroment
  python -m venv env
  source env/bin/activate  # For Linux/macOS
  # For Windows
  # env\Scripts\activate
  pip install -r requirements.txt
  
3. **Configure PostgreSQL:

  -Create a new database and user in PostgreSQL.
  -Update the DATABASES settings in settings.py with your PostgreSQL credentials.
  -Run migrations:
  -python manage.py makemigrations
  -python manage.py migrate
  
4. **Obtain Spotify API credentials:

  Create a Spotify Developer account and get your client ID and client secret.
  Update your settings.py or environment variables with the following:

  -SPOTIFY_CLIENT_ID=<your-client-id>
  -SPOTIFY_CLIENT_SECRET=<your-client-secret>
  
5. **Token Creation for Spotify API:

  The app includes a token creation mechanism to access the Spotify API. It fetches an OAuth token using the client credentials and uses this token to make requests to the Spotify API for search and other features.
6. **Run the server:
  python manage.py runserver
  Open the app: Visit http://localhost:8000 in your browser.

##Usage
-**Register an account or log in using an existing account.
-**Use the search bar to find music by artists, albums, or tracks through the Spotify API.
-**Create and manage playlists.
-**Play music and explore different categories.  
  
   
