# Atlanta Food Finder

## Folder Structure

### `accounts`
- **Description:** Contains all the user authentication backend components

### `static`
- **Description:** Includes static files like stylesheets

### `templates`
- **Description:** Contains all HTML files used in the project

### `Atlanta-Food-Finder`
- **Description:** The main application of the project. This is where the core functionality of the app is implemented

## HTML Pages

### `register.html`
- **Purpose:** Signup page for new users.
- **Required Fields:**
  - **First Name** 
  - **Last Name**
  - **Username** 
  - **Email** 
  - **Password** 
- **Recommended Link:**
  - **Login:** Direct link to `login.html` for users with an existing account.

### `login.html`
- **Purpose:** The login page.
- **Required Fields:**
  - **Username** 
  - **Password** 
- **Included Links:**
  - **Signup:** Direct link to `register.html` for new users.
  - **Forgot Password:** Direct link to `forgot_password.html` for password recovery.

### `forgot_password.html`
- **Purpose:** Displays when the user clicks the "Forgot Password?" link from the login page.
- **Required Fields:** 
  - **Email:** Password reset link will be sent here.
- **Recommended Links:**
  - **Login:** Direct link to `login.html` for users who remember their account.
  - **Register:** Direct link to `register.html` for users who don’t have an account.

### `password_reset_sent.html`
- **Purpose:** Appears after the user clicks the "Reset Password" button on `reset_password.html`.
- **Required Fields:** None.
- **Required Information:**
  - A password reset link has been sent to the user's email.
  - The link will be valid for 24 hours.

### `reset_password.html`
- **Purpose:** Appears after the user clicks the password reset link sent to their email.
- **Required Fields:**
  - **Password:** New password for the user.

### `index.html`
- **Purpose:** The main page shown after a successful login.

## Running Django Locally

Follow these steps to set up and run the Django project locally:

### 1. Clone the Repository

Clone the repository to your local machine:

```bash
git clone https://github.com/estherpark514/Atlanta-Food-Finder.git
cd atlanta-food-finder
```

### 2. Apply Migrations

Create and apply database migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Run the Development Server

Start the Django development server:

```bash
python manage.py runserver
```

The server will be available at `http://127.0.0.1:8000/`.

### 4. Login

Use the following credentials to log in:

```bash
Username: CS2340
Password: Atlanta-Food-Finder
```

### 5. Access the Admin Interface

To access the Django admin interface, visit `http://127.0.0.1:8000/admin/`

---
