<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a id="readme-top"></a>

<!-- PROJECT SHIELDS -->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![LinkedIn][linkedin-shield]][linkedin-url]



<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/helen1806/SOFTWARE-AGING-MONITOR">
    
  </a>

<h3 align="center">Software Aging Monitor</h3>

  <p align="center">
    A web-based monitoring dashboard to track website availability, response time, and software aging symptoms in real time.
    <br />
    <a href="https://github.com/helen1806/SOFTWARE-AGING-MONITOR">View Demo</a>
    &middot;
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

[![Dashboard Screenshot][product-screenshot]](https://example.com)

The **Software Aging Monitor** is a Flask-based web application designed to detect and track software aging symptoms across websites and services. It continuously monitors response times, uptime, and performance degradation patterns — helping developers and teams identify issues before they escalate into failures.



<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

**Languages**

* ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
* ![HTML](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
* ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
* ![CSS](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)

**Framework & Libraries**

* ![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
* ![Bootstrap](https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white)
* [![Chart.js][Chartjs]][Chartjs-url]
* Flask-SQLAlchemy · APScheduler · Jinja2 · Bootstrap Icons

**Database**

* ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)

**Tools**

* psycopg2 · Python venv

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

This section explains how to run the **Software Aging Monitor** locally. The application was developed and tested locally on a personal system. Follow the steps below to set up the project on your machine.

### Prerequisites

Ensure the following are installed before proceeding:

* Python 3.9+
* PostgreSQL
* Git
* pip (Python package manager)

Verify your installations:

```bash
python --version
pip --version
psql --version
```

### Installation

1. Clone the repository
   ```bash
   git clone https://github.com/helen1806/SOFTWARE-AGING-MONITOR.git
   cd SOFTWARE-AGING-MONITOR
   ```

2. Create and activate a virtual environment

   **Windows:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

   **Mac/Linux:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. Install project dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the PostgreSQL database
   ```sql
   CREATE DATABASE Software aging;
   ```

5. Update the database connection string in `app.py`
   ```
   postgresql://username:password@localhost:5432/database_name
   ```

6. Start the Flask server
   ```bash
   python app.py
   ```

7. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

The **Software Aging Monitor** helps track website availability, response time, and potential software aging symptoms through a dashboard interface.

---

### Step 1 — Add a Website

1. Open the dashboard
2. Click **Add Website**
3. Enter the website name, URL, monitoring interval, and response time threshold

The monitoring engine will begin tracking automatically.

---

### Step 2 — Configure Monitoring Interval

The monitoring interval controls how often the system checks a website:
- **1 minute** → aggressive monitoring
- **5 minutes** → moderate monitoring

Shorter intervals provide more granular data but increase server load.

---

### Step 3 — Set Response Threshold

Define the maximum acceptable response time for a website:
```
5000 ms = 5 seconds
```
If the response time exceeds this value, the system flags it as a performance incident.

---

### Step 4 — Analyze Dashboard Metrics

The dashboard provides key monitoring indicators:
- Uptime percentage
- Average response time
- Active incidents
- Total incidents
- Historical response time chart

[![Dashboard Overview][dashboard-screenshot]](https://example.com)

---

### Step 5 — Monitor Subpages

Add critical subpages (e.g. `/login`, `/checkout`, `/api/status`) to monitor specific performance independently from the main URL.

---

### Step 6 — Trigger Manual Checks

Trigger a monitoring check at any time to instantly verify service status — useful for suspected outages

---

### System Architecture

```
User
 ↓
Flask Server
 ↓
Monitoring Engine (APScheduler)
 ↓
PostgreSQL Database
 ↓
Dashboard Analytics (Chart.js)
```

---


> **Note:** A future version of this project will integrate system-level observability tools to diagnose the underlying causes of website failures and performance degradation.

Currently, the system monitors **application-level symptoms** such as:
- Uptime status
- Response time
- HTTP status codes
- Incident frequency

However, these symptoms alone may not reveal the true root cause of failures. Future versions will expand monitoring across three layers:

---

### Infrastructure Metrics

| Tool | Purpose |
|------|---------|
| **Prometheus** | Time-series metrics collection |
| **Node Exporter** | System metrics (CPU, memory, disk, network) |
| **cAdvisor** | Container resource monitoring |
| **Grafana** | Visualization dashboards for metrics |

These tools will enable monitoring of:
- CPU utilization
- Memory consumption
- Process load
- Container health
- System I/O metrics

---

###  Performance and Resource Profiling

To diagnose software aging issues such as memory leaks or resource exhaustion:

| Tool | Purpose |
|------|---------|
| **PySpy / PyInstrument** | Python runtime profiling |
| **Memory Profiler** | Python memory usage analysis |
| **GC Logs** | Memory allocation tracking |
| **p95 / p99 Latency** | Latency monitoring via Prometheus |

These tools will help detect:
- Memory leaks
- Abnormal garbage collection behavior

---

###  Error Tracking and Reliability Monitoring

To detect deterministic bugs introduced during deployments:

| Tool | Purpose |
|------|---------|
| **Sentry** | Runtime error tracking |
| **Python Logging** | Structured application logging |
| **CI/CD Checks** | Validation checks on deployment |

This enables early detection of:
- Application crashes
- Logic errors in deployments
- Failed service dependencies

---

<p align="right">(<a href="#readme-top">back to top</a>)</p>





<!-- ROADMAP -->
## Roadmap

- [ ] **Feature 1 — Prometheus Metrics Integration**
    - [ ] CPU usage monitoring
    - [ ] Memory utilization tracking
    - [ ] System resource dashboards

- [ ] **Feature 2 — Advanced Incident Detection**
    - [ ] Anomaly detection algorithms
    - [ ] Performance degradation alerts
    - [ ] Pattern recognition for software aging

- [ ] **Feature 3 — Containerized Deployment**
    - [ ] Docker support
    - [ ] Cloud deployment readiness
    - [ ] Observability integrations 



<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also open an issue with the tag "enhancement". Don't forget to give the project a star!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/Feature`)
3. Commit your Changes (`git commit -m 'Add some Feature'`)
4. Push to the Branch (`git push origin feature/Feature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>





<!-- CONTACT -->
## Contact

Your Name -  helenmarys1023@gmail.com

Project Link: [https://github.com/helen1806/SOFTWARE-AGING-MONITOR](https://github.com/helen1806/SOFTWARE-AGING-MONITOR)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->

[forks-shield]: https://img.shields.io/github/forks/github_username/repo_name.svg?style=for-the-badge
[forks-url]: https://github.com/github_username/repo_name/network/members
[stars-shield]: https://img.shields.io/github/stars/github_username/repo_name.svg?style=for-the-badge
[stars-url]: https://github.com/github_username/repo_name/stargazers

[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/in/helen-sebastian
[product-screenshot]: images/screenshot.png
[dashboard-screenshot]: images/dashboard.png
[Chartjs]: https://img.shields.io/badge/Chart.js-FF6384?style=for-the-badge&logo=chartdotjs&logoColor=white
[Chartjs-url]: https://www.chartjs.org/
