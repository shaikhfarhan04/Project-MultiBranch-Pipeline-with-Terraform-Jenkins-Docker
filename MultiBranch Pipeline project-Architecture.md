Yes. Let’s turn this into a **complete hands-on MultiBranch Pipeline project** using your existing AWS, Terraform, Jenkins, Docker, and GitHub practice.

The goal is to build a small Flask application, maintain four Git branches, and configure Jenkins to discover and build each branch automatically.

### Project: MultiBranch Pipeline with Terraform + Jenkins + Docker

**What you will practice**

```text
GitHub Repository
       │
       ├── main
       ├── dev
       ├── staging
       └── prod
       │
       ▼
Jenkins Multibranch Pipeline
       │
       ├── Discover branches
       ├── Checkout code
       ├── Install dependencies
       ├── Run tests
       ├── Build Docker image
       └── Display result in Blue Ocean
```

**Final outcome:** You will have a working repository with a `Jenkinsfile`, four branches, a Dockerized Flask app, and Jenkins automatically discovering and building those branches.


## 1. Project structure

Create this folder on your Windows 11 laptop:

```text
multibranch-pipeline/
│
├── app/
│   ├── app.py
│   ├── requirements.txt
│   └── test_app.py
│
├── Dockerfile
├── Jenkinsfile
├── .gitignore
└── README.md
```

We will use **your own GitHub repository**, so you can practice the complete workflow without depending on someone else's code.

---

## 2. Create the Flask application

Open **VS Code → Terminal → PowerShell**.

```powershell
mkdir multibranch-pipeline
cd multibranch-pipeline

mkdir app
```

Create `app/app.py`:

```python
from flask import Flask

app = Flask(__name__)


@app.route("/")
def home():
    return "MultiBranch Pipeline Application is working!"


@app.route("/health")
def health():
    return "OK"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```

Create `app/requirements.txt`:

```text
Flask==3.1.0
pytest==8.3.4
```

Create `app/test_app.py`:

```python
from app import app


def test_home():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert b"MultiBranch Pipeline Application is working!" in response.data


def test_health():
    client = app.test_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.data == b"OK"
```

---

## 3. Create the Dockerfile

Create `Dockerfile` in the project root:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY app/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

EXPOSE 5000

CMD ["python", "app.py"]
```

### Test Docker locally

```powershell
docker build -t multibranch-app:local .
```

```powershell
docker run -d --name multibranch-app -p 5000:5000 multibranch-app:local
```

Open:

```text
http://localhost:5000
```

Expected:

```text
MultiBranch Pipeline Application is working!
```

Test health:

```text
http://localhost:5000/health
```

Expected:

```text
OK
```

Stop the container:

```powershell
docker stop multibranch-app
docker rm multibranch-app
```

---

# 4. Create the Jenkinsfile

This is the **main file for your MultiBranch Pipeline**.

Create `Jenkinsfile` in the project root:

```groovy
pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Information') {
            steps {
                echo "Building branch: ${env.BRANCH_NAME}"
                echo "Build number: ${env.BUILD_NUMBER}"
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r app/requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    . venv/bin/activate
                    pytest app/test_app.py -v
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build -t multibranch-app:${BUILD_NUMBER} .
                '''
            }
        }
    }

    post {
        success {
            echo "Pipeline completed successfully!"
        }

        failure {
            echo "Pipeline failed. Check the logs."
        }

        always {
            echo "Finished building branch: ${env.BRANCH_NAME}"
        }
    }
}
```

### Important

This Jenkinsfile uses:

```groovy
checkout scm
```

That means Jenkins checks out the **branch it is currently building**.

For example:

```text
dev branch       → Jenkins builds dev
staging branch   → Jenkins builds staging
prod branch      → Jenkins builds prod
main branch      → Jenkins builds main
```

This is the key concept of a **Multibranch Pipeline**.

---

# 5. Create `.gitignore`

Create `.gitignore`:

```text
venv/
__pycache__/
.pytest_cache/
*.pyc
.env
.idea/
.vscode/
```

---

# 6. Create your GitHub repository

Go to GitHub and create a new repository.

Suggested name:

```text
multibranch-pipeline
```

Keep it **Public** for easier Jenkins practice.

Then run:

```powershell
git init
```

```powershell
git add .
```

```powershell
git commit -m "Initial Flask application and Jenkins pipeline"
```

```powershell
git branch -M main
```

```powershell
git remote add origin https://github.com/YOUR_USERNAME/multibranch-pipeline.git
```

Replace `YOUR_USERNAME` with your GitHub username.

```powershell
git push -u origin main
```

---

# 7. Create the four branches

This is your **main practical task**.

### Create `dev`

```powershell
git checkout -b dev
```

Make a small change in `app/app.py`:

```python
@app.route("/environment")
def environment():
    return "Development Environment"
```

Then:

```powershell
git add .
git commit -m "Add development environment endpoint"
git push -u origin dev
```

---

### Create `staging`

```powershell
git checkout main
git checkout -b staging
```

Add:

```python
@app.route("/environment")
def environment():
    return "Staging Environment"
```

Then:

```powershell
git add .
git commit -m "Add staging environment endpoint"
git push -u origin staging
```

---

### Create `prod`

```powershell
git checkout main
git checkout -b prod
```

Add:

```python
@app.route("/environment")
def environment():
    return "Production Environment"
```

Then:

```powershell
git add .
git commit -m "Add production environment endpoint"
git push -u origin prod
```

---

### Verify all branches

```powershell
git branch -a
```

Expected:

```text
* prod
  main
  remotes/origin/main
  remotes/origin/dev
  remotes/origin/staging
  remotes/origin/prod
```

Your repository should now look like:

```text
main
 ├── dev
 ├── staging
 └── prod
```

---

# 8. GitHub Personal Access Token

For Jenkins authentication, create a **GitHub Personal Access Token**.

Go to:

**GitHub → Settings → Developer settings → Personal access tokens**

Create a token with repository access.

For a public repository, Jenkins can often clone without credentials, but you should still practice adding credentials.

**Important:** Never share your token in chat, screenshots, or Git commits.

---

# 9. Jenkins Server Setup

You can use your existing Jenkins EC2 server.

### Required plugins

Install:

```text
Blue Ocean
Docker Pipeline
Docker
Git
Pipeline
```

Also ensure Jenkins has access to Docker.

On Ubuntu:

```bash
sudo usermod -aG docker jenkins
```

Then restart Jenkins:

```bash
sudo systemctl restart jenkins
```

Verify:

```bash
sudo systemctl status jenkins
```

Check Docker:

```bash
sudo -u jenkins docker ps
```

If Docker permission is working, you should not see:

```text
permission denied while trying to connect to the Docker daemon
```

---

# 10. Create Jenkins Multibranch Pipeline

Open Jenkins:

```text
http://YOUR_JENKINS_PUBLIC_IP:8080
```

### Steps

```text
Jenkins Dashboard
       ↓
New Item
       ↓
Multibranch Pipeline
       ↓
Enter name:
multibranch-pipeline
       ↓
Branch Sources
       ↓
Git
```

Repository URL:

```text
https://github.com/YOUR_USERNAME/multibranch-pipeline.git
```

Add your GitHub credentials if required.

Under **Build Configuration**:

```text
Mode: by Jenkinsfile
Script Path: Jenkinsfile
```

Click:

```text
Save
```

Then:

```text
Scan Multibranch Pipeline Now
```

---

# 11. Expected Jenkins result

Jenkins should discover:

```text
multibranch-pipeline
│
├── main
├── dev
├── staging
└── prod
```

Each branch should have its own build.

Example:

```text
main       #1 SUCCESS
dev        #1 SUCCESS
staging    #1 SUCCESS
prod       #1 SUCCESS
```

Click any branch:

```text
dev
 ↓
Build #1
 ↓
Console Output
```

You should see:

```text
Building branch: dev
```

Then:

```text
pytest app/test_app.py -v
```

Expected:

```text
2 passed
```

Then:

```text
docker build -t multibranch-app:1 .
```

Finally:

```text
Pipeline completed successfully!
```

---

# 12. Blue Ocean

Open:

```text
Jenkins → Open Blue Ocean
```

You should see:

```text
Multibranch Pipeline
       ↓
dev
       ↓
Build #1
       ↓
Checkout
       ↓
Build Information
       ↓
Install Dependencies
       ↓
Run Tests
       ↓
Build Docker Image
       ↓
SUCCESS
```

This is exactly what your assignment is asking you to demonstrate.

---

# 13. Your practical assignment

Complete these tasks in order:

### Task 1 — Git

* Create GitHub repository.
* Clone repository.
* Create `main`, `dev`, `staging`, `prod`.
* Push all branches.
* Verify using `git branch -a`.

### Task 2 — Application

* Create Flask app.
* Create `/health` endpoint.
* Create Dockerfile.
* Build and run Docker image locally.

### Task 3 — Jenkins

* Install required plugins.
* Add GitHub credentials.
* Create Multibranch Pipeline.
* Configure repository URL.
* Scan repository.

### Task 4 — Pipeline

* Jenkins discovers all branches.
* Each branch runs its own Jenkinsfile.
* Tests execute.
* Docker image builds.
* Check Blue Ocean.

### Task 5 — Branch Change

Make a change in `dev`:

```python
return "Development Environment - Version 2"
```

Push:

```powershell
git add .
git commit -m "Update development environment"
git push
```

Then scan Jenkins again.

**Expected result:**

```text
dev → Build #2 → SUCCESS
```

Other branches should remain unchanged.

---

## Final architecture

```text
                    GitHub
                      │
       ┌──────────────┼──────────────┐
       │              │              │
      dev          staging          prod
       │              │              │
       └──────────────┼──────────────┘
                      │
                      ▼
              Jenkins Multibranch
                      │
       ┌──────────────┼──────────────┐
       │              │              │
      dev          staging          prod
       │              │              │
       ▼              ▼              ▼
    Jenkinsfile    Jenkinsfile    Jenkinsfile
       │              │              │
       ▼              ▼              ▼
      Test           Test           Test
       │              │              │
       ▼              ▼              ▼
   Docker Build   Docker Build   Docker Build
       │              │              │
       └──────────────┼──────────────┘
                      ▼
                Blue Ocean
```

**This is a very good beginner-to-intermediate DevOps project because it combines Git branching, CI/CD, Docker, Jenkins, and AWS in one workflow.**

If you want, I can next give you **Phase 2: the complete AWS EC2 + Jenkins installation + Docker setup + GitHub credentials configuration**, with every command for your Ubuntu EC2 server.
