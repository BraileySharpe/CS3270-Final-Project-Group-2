# ♟️ CS3270 Final Project – Chess Engine with AI

### **Authors**

Brailey Sharpe • Colby Daniel • Matthew Shirley

---

## Overview

This project is a custom-built chess engine that features an AI opponent powered by search algorithms and a neural network evaluation model.

The engine combines classical techniques like Minimax/Negamax and Alpha-Beta pruning with modern machine learning to evaluate board states and make strategic decisions.

---

## Preview

### Starting Screen

<img width="255" height="310" alt="starting screen" src="https://github.com/user-attachments/assets/964af799-d45e-41a2-ba97-aec6efb10ced"/>

### In-Game View

<img width="623" height="578" alt="gameplay" src="https://github.com/user-attachments/assets/9a988460-4ce1-4491-995e-54acb861a901"/>

---

## Features

* Fully playable chess game with GUI
*  AI opponent using:

  * Negamax search
  * Alpha-Beta pruning
  * Move ordering optimizations
  * Quiescence search
*  CNN-based board evaluation model
*  Performance comparison with Stockfish
*  Modern UI built with `ttkbootstrap`

---

##  How to Run

###  Terminal

```bash
python -m main
```

###  IDE

Run:

```
main.py
```

from the project root directory.

---

##  Model Comparison

To compare the AI against Stockfish:

```bash
python comparison/Stockfish_comparison.py
```

---

##  Dependencies

Install all required packages with:

```bash
pip install -r requirements.txt
```

Or install manually:

```
chess==1.11.2  
kagglehub==1.0.1  
matplotlib==3.10.9  
numpy==2.4.4  
pandas==3.0.2  
scikit_learn==1.8.0  
torch==2.10.0  
ttkbootstrap==1.20.2  
```

---

##  How It Works (High-Level)

1. The game generates all legal moves for a given board state
2. The AI searches possible future positions using Negamax
3. Alpha-Beta pruning removes unnecessary branches to improve speed
4. The CNN evaluates board positions to assign scores
5. The best move is selected based on search + evaluation

---

If you want, I can take this one step further and tailor it specifically for **GitHub portfolio impact** (like adding badges, performance benchmarks, or recruiter-focused wording).
