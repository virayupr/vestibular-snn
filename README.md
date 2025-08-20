# Vestibular-SNN: Bio-Inspired Spiking Neural Network for Vertigo Modeling

This repository contains the implementation of the paper:

**"Bio-Inspired Spiking Neural Network Model for Simulating and Optimizing Vertigo Treatment"**

---

## 📖 Overview
This project simulates vestibular dysfunction and adaptive recovery using a biologically inspired spiking neural network implemented in [Brian2](https://brian2.readthedocs.io/).  
The model captures three layers:
- **Hair Cells (Input Layer)**
- **Afferent Neurons (Intermediate Layer)**
- **Cerebellar Neurons (Output Layer)**

The code also includes experiments for:
- **Baseline healthy vestibular function**
- **Hypofunction (reduced input)**
- **Afferent silencing**
- **Synaptic blockade**

---

## ⚙️ Installation
Clone the repository and install requirements:

```bash
git clone https://github.com/virayupr/vestibular-snn.git
cd vestibular-snn
pip install -r requirements.txt
