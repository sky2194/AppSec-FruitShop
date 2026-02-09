# Create venv
python -m venv venv

## Activate
source. venv/bin/activate



pip install -r requirements.txt
python app.py


http://localhost:5000


Admin: admin / admin123
User: user / password


## SAST

## SonarQube
docker run -d -p 9000:9000 --name sonarqube sonarqube:9.9-community

sonar-scanner -Dsonar.host.url=http://localhost:9000 -Dsonar.login=<your_token>

## SCA - pip-audit
pip install pip-audit

## DAST
OWSAP-ZAP
docker run --rm \                           # Run container, remove after done
  -v "$(pwd):/zap/wrk" \                    # Mount current folder to /zap/wrk
  -t ghcr.io/zaproxy/zaproxy:stable \       # Use ZAP Docker image
  zap-baseline.py \                          # Run ZAP baseline scan
  -t http://host.docker.internal:5000 \     # Target: your Flask app
  -r zap-report.html                         # Output report filename
