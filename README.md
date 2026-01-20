[![CI](https://github.com/devp3102/IDS568-MLOps/actions/workflows/CI.yml/badge.svg)](https://github.com/devp3102/IDS568-MLOps/actions/workflows/CI.yml)

IDS568: MLOps Milestone 0
Setup Instructions

Clone the repository: git clone https://github.com/devp3102/IDS568-MLOps.git

Create a virtual environment: python3 -m venv venv

Activate the environment: source venv/bin/activate

Install dependencies: pip install -r requirements.txt 

Run tests: pytest 

Technical Explanation: Reproducibility in MLOps

Environment reproducibility serves as the vital foundation for a reliable machine learning lifecycle. By utilizing exact dependency pinning in requirements.txt (using the == operator), this project ensures that the software environment remains consistent across development, testing, and production stages. This practice directly addresses the "it works on my machine" problem, which frequently causes models to fail during deployment due to version mismatches or hidden dependencies.

Applying software engineering principles—such as automated Continuous Integration (CI) via GitHub Actions—ensures that every code change is validated in a clean, isolated environment. This automation creates a "contract" for the development environment, guaranteeing that any collaborator can recreate the exact setup and achieve identical results. By establishing these relationships between data pipelines and deployment environments early, we build maintainable systems capable of scaling to production-level standards used by industry leaders like Google and Netflix. This rigorous management of artifacts and dependencies is essential for long-term model maintainability and deployment success.