# Project Manager
For the Frameworks assignment I have created a website called ‘Project Manager’ using Django. Project manager is a website that companies can use to track their projects. Once registered, users can update their profile (add a profile picture and set their role). They can create projects (set a name, description choose the team members, set the start and end dates, and the status of the project). They can then create tasks for the project and assign to relevant team members. Chat feature of projects allows users to communicate about projects. Users can track time against their projects and the home page gives users an overview on their progress (progress bar showing tasks completed and total count of time tracked for current week). 

## Render Link: https://project-management-u2rr.onrender.com

### To run locally:
- Clone the repository: https://github.com/jodi-curtis/project-management.git
- Create a virtual environment
- Activate the virtual environment
- Install dependencies listed in requirements.txt

### To host PostgreSQL database on render I followed the below steps:
- Visit render.com
- Click ‘Get Started for Free’
- Sign in with GitHub
- On dashboard click New -> PostgreSQL
- Select Free Instance Type
- Click Create Database

### To host my website on Render I followed the below steps:
- On dashboard click New -> Web Service
- Select Public Git Repository
- Paste in https://github.com/jodi-curtis/project-management.git
- Set Build Commands as ‘pip install -r requirements.txt ; python manage.py migrate ; python manage.py collectstatic ; python manage.py ensure_adminuser’
- Set Start Command as ‘gunicorn project_management.wsgi:application’
- Select Free Instance Type
- Enter Environment Variables
- Click Deploy Web Service
