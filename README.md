# ⚛️ Quantum Security & Behavior Visualization Lab

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python\&logoColor=white)
![Qiskit](https://img.shields.io/badge/Qiskit-1.x-6929C4?logo=ibm\&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B?logo=streamlit\&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-5.x-3F4F75?logo=plotly\&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-22C55E)

An interactive quantum computing simulation platform built using **Qiskit**, **Python**, and **Streamlit**.
The project demonstrates practical quantum concepts through authentication simulation, multi-qubit circuit experimentation, randomness analysis, superposition visualization, and quantum noise modeling.

---

# 🌐 Live Demo

https://quantum-security-lab-fu2wicxi3axnf8yqpjwwvx.streamlit.app/

---

# 📂 GitHub Repository

https://github.com/kajal-student/quantum-security-lab

---

# 🚀 Features

## 🔐 Quantum Authentication Lab

* Quantum-generated session token simulation
* Shannon entropy visualization
* Token distribution analysis
* Session validity monitoring

## ⚡ Quantum Circuit Playground

* Multi-qubit circuit experimentation
* Supports H, X, Y, Z, and CNOT gates
* Probability distribution analysis
* Interactive measurement visualization

## 🎲 Classical vs Quantum Randomness Analyzer

* Quantum vs pseudo-random comparison
* Entropy-based randomness analysis
* Distribution visualization using Plotly
* Statistical randomness insights

## 🌀 Superposition Visualizer

* Hadamard gate simulation
* Quantum state transformation visualization
* Probability and measurement analysis
* Interactive state exploration

## 🔧 Quantum Noise Simulator

* Depolarizing, bit-flip, and phase-flip noise simulation
* Clean vs noisy circuit comparison
* Measurement instability analysis
* Quantum noise visualization

## 📊 Experiment Dashboard

* Session-based experiment logging
* Experiment history tracking
* JSON and CSV export support
* Unified analytics dashboard

---

# 🛠 Tech Stack

## Languages

* Python
* JavaScript

## Quantum Framework

* Qiskit
* Qiskit Aer

## Frontend / Visualization

* Streamlit
* Plotly
* Matplotlib

## Supporting Libraries

* NumPy
* Pandas

---

# 📁 Project Structure

```bash
quantum_lab/
│
├── app.py
├── requirements.txt
├── README.md
│
├── .streamlit/
│   └── config.toml
│
├── assets/
│   └── styles.css
│
├── auth/
│   └── quantum_auth.py
│
├── modules/
│   ├── home.py
│   ├── auth_lab.py
│   ├── circuit_playground.py
│   ├── randomness_analyzer.py
│   ├── superposition_viz.py
│   ├── noise_simulator.py
│   └── experiment_dashboard.py
│
├── visualizations/
│   └── charts.py
│
└── utils/
    └── helpers.py
```

---

# ⚙️ Installation

## Clone Repository

```bash
git clone https://github.com/kajal-student/quantum-security-lab.git
cd quantum-security-lab
```

---

## Create Virtual Environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# ▶️ Run Locally

```bash
streamlit run app.py
```

Application runs at:

```bash
http://localhost:8501
```

---

# ☁️ Deployment

This project is fully deployable on **Streamlit Cloud**.

## Deployment Steps

1. Push repository to GitHub
2. Open Streamlit Cloud
3. Connect GitHub repository
4. Set main file path:

```bash
app.py
```

5. Deploy application

---

# ✨ Technical Highlights

* Local quantum simulation using Qiskit Aer
* Multi-qubit circuit experimentation
* Quantum noise modeling
* Shannon entropy analysis
* Session-based experiment logging
* Interactive Plotly visualizations
* Modular Streamlit architecture
* Cloud-deployable application structure

---

# 🧠 Quantum Concepts Covered

| Concept                   | Implementation                             |
| ------------------------- | ------------------------------------------ |
| Hadamard Superposition    | Quantum Auth Lab, Superposition Visualizer |
| Quantum Randomness        | Randomness Analyzer                        |
| Shannon Entropy           | Auth Lab, Randomness Analyzer              |
| Multi-Qubit Circuits      | Circuit Playground                         |
| Bell / GHZ States         | Noise Simulator                            |
| Quantum Noise Models      | Noise Simulator                            |
| Probability Measurement   | Circuit Playground                         |
| Bloch-State Visualization | Superposition Visualizer                   |

---

# 📄 Resume Description

Built an interactive quantum computing simulation platform integrating quantum authentication, circuit experimentation, randomness analysis, and noise modeling using Qiskit and Streamlit. Developed multi-qubit simulation workflows, entropy-based randomness analytics, probability visualization dashboards, and modular cloud-deployable architecture for practical quantum behavior experimentation.

---

# 🔮 Future Improvements

* Real quantum hardware integration
* Persistent experiment storage
* Quantum machine learning modules
* Advanced quantum state visualization
* Multi-user authentication system

---

# 👩‍💻 Author

**Kajal Kumari**
B.Tech — Electronics and Communication Engineering
NSUT

### GitHub

https://github.com/student-kajal

### LinkedIn

https://www.linkedin.com/in/kajal-kumari-98b871263

---

# 📜 License

MIT License
