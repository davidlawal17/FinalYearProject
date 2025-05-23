# Investr – Real Estate Investment Assistant

A web application that helps UK property investors make data-driven decisions on buying or selling properties. It combines property search, machine learning-based recommendations, and investment simulations to simplify the investment process.

## Description

Investr is a full-stack platform built with Flask (Python) and React (JavaScript). It enables users to register/login, search for UK-based properties, receive tailored investment recommendations based on ROI, rental yield, and appreciation trends, and simulate investment outcomes. Authentication is handled using Firebase, while property/user data is stored in a PostgreSQL database.

## Getting Started

### Dependencies

* Python 3.10+
* Node.js 18+
* PostgreSQL
* Firebase project credentials

#### Backend Python Packages:

* Flask, Flask-Cors, Flask-SQLAlchemy
* psycopg2-binary, python-dotenv, firebase-admin
* scikit-learn, pandas, numpy

#### Frontend JavaScript Libraries:

* React, React Router, Context API

### Installing

* Clone the repository:

```bashx
git clone https://github.com/davidlawal17/investr.git
cd investr
```

* Set up the backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

* Create a `.env` file in the `backend/` directory using the format below, or copy from `.env.example`:

```env
DATABASE_URL=postgres://your_username:your_password@your_host:your_port/your_database
JWT_SECRET_KEY=your_secret_key_here

REACT_APP_FIREBASE_API_KEY=your_firebase_api_key
REACT_APP_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
REACT_APP_FIREBASE_DATABASE_URL=https://your_project.firebaseio.com
REACT_APP_FIREBASE_PROJECT_ID=your_project_id
REACT_APP_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
REACT_APP_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
REACT_APP_FIREBASE_APP_ID=your_app_id
REACT_APP_FIREBASE_MEASUREMENT_ID=your_measurement_id
```

> Note: A `.env.example` file is included in this repository with placeholder values. Do not commit your actual `.env` file to version control.

* Set up the frontend:

```bash
cd ../frontend
npm install
```

### Executing program

* To run the backend server:

```bash
cd backend
flask run
```

* To run the frontend app:

```bash
cd frontend
npm start
```

The frontend will run at `http://localhost:3000`, and it will communicate with the backend API at `http://localhost:5000`.

## Help

Common issues may include missing or misconfigured `.env` files. Make sure your environment variables are correctly set.

To verify your installed packages:

```bash
pip check
```

## Authors

David Lawal
[LinkedIn](https://www.linkedin.com/in/david-lawal-72a893273)

## Version History

* 1.0

  * Completed full-stack integration
  * Added property search, ML recommendations, and investment simulation
* 0.1

  * Initial backend and frontend setup

## License

This project is provided for academic and personal use only. No license is associated for commercial use.

## Acknowledgments

Inspiration, libraries, and resources:

* Flask, React, Firebase, Scikit-learn
* [DomPizzie](https://gist.github.com/DomPizzie/7a5ff55ffa9081f2de27c315f5018afc)
