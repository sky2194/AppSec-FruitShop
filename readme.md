# Fruit Shop Application

A secure web application built with Flask, demonstrating security best practices from SAST (Static Application Security Testing) to DAST (Dynamic Application Security Testing).This application is for educational purposes only. The vulnerabilities are intentional and should never be replicated in production applications. Always follow secure coding practices in real-world applications.

## Overview

This Fruit Shop application was developed following security-first development practices, integrating multiple security testing methodologies throughout the development lifecycle.

## Learning Resources

This project was built based on knowledge gained from YouTube tutorials covering security testing methodologies. While the foundational concepts for SAST, SCA, and DAST testing were learned from video tutorials, the actual implementation, application development, and security testing pipeline were independently developed and applied.

**Key concepts learned from tutorials:**
- SAST (Static Application Security Testing) principles
- SCA (Software Composition Analysis) practices  
- DAST (Dynamic Application Security Testing) workflows
- Security testing integration in development lifecycle

## Application Features

- **User Authentication**: Secure login system with role-based access
- **Admin Dashboard**: Administrative interface for product management
- **Shopping Experience**: Browse and manage fruit inventory
- **Security Testing**: Comprehensive security validation pipeline

## Security Development Approach (SAST to DAST)

This application was developed using a security-first methodology:

### SAST (Static Application Security Testing)
- **Code Analysis**: Regular static code analysis during development
- **SonarQube Integration**: Continuous code quality and security scanning
- **Dependency Scanning**: Automated vulnerability scanning for dependencies
- **SCA (Software Composition Analysis)**: Using pip-audit for Python packages

### DAST (Dynamic Application Security Testing)
- **OWASP ZAP Integration**: Automated dynamic security testing
- **Runtime Analysis**: Security testing against running application
- **Vulnerability Assessment**: Comprehensive security scanning

## Setup Instructions

### Prerequisites
- Python 3.8+
- Docker (for security tools)
- Git

### Installation

1. **Create virtual environment**
   ```bash
   python -m venv venv
   ```

2. **Activate virtual environment**
   ```bash
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   - URL: http://localhost:5000

### Default Credentials
- **Admin Account**: `admin` / `admin123`
- **User Account**: `user` / `password`

## Security Testing

### SAST Tools

#### SonarQube Setup
```bash
docker run -d -p 9000:9000 --name sonarqube sonarqube:9.9-community
```

#### Run SonarQube Analysis
```bash
sonar-scanner -Dsonar.host.url=http://localhost:9000 -Dsonar.login=<your_token>
```

#### Software Composition Analysis (SCA)
```bash
pip install pip-audit
pip-audit
```

### DAST Tools

#### OWASP ZAP Baseline Scan
```bash
docker run --rm \
  -v "$(pwd):/zap/wrk" \
  -t ghcr.io/zaproxy/zaproxy:stable \
  zap-baseline.py \
  -t http://host.docker.internal:5000 \
  -r zap-report.html
```

## Project Structure

```
Fruit-shop/
├── app.py                 # Main Flask application
├── fruits.db             # SQLite database
├── requirements.txt      # Python dependencies
├── sonar-project.properties  # SonarQube configuration
├── zap-report.html       # OWASP ZAP security report
├── zap.yaml             # ZAP configuration
├── .git/                # Git repository
├── .venv/               # Virtual environment
└── venv/               # Python virtual environment
```

## Contributing

This project is developed for educational and demonstration purposes. Feel free to:

1. Fork the repository
2. Create a feature branch
3. Submit pull requests
4. Report issues

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This application is for educational purposes only. The vulnerabilities are intentional and should never be replicated in production applications. Always follow secure coding practices in real-world applications.

## Security Note

This project demonstrates the implementation of security testing from SAST to DAST. The application includes intentionally simple authentication for demonstration purposes. In real-world applications, proper security measures like HTTPS, secure password hashing, and comprehensive authentication should be implemented.

## Acknowledgments

- **YouTube Tutorial**: The SAST, SCA, and DAST testing concepts were learned from educational YouTube videos covering application security testing methodologies
- Open-source security tools (SonarQube, OWASP ZAP, pip-audit)
- The security community for promoting secure development practices
