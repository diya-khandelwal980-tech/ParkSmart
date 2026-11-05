# ParkSmart – Intelligent Parking Optimization System

ParkSmart is a Python-based desktop application developed as a Design and Analysis of Algorithms (DAA) mini project.

It helps manage parking spaces efficiently using different algorithms and an SQLite database.

## Features

- Smart parking allocation using Greedy Algorithm
- Shortest route calculation using Dijkstra's Algorithm
- Parking slot searching using Linear Search
- Parking slot sorting using Selection Sort
- Vehicle entry and exit management
- Parking history and record filtering
- Vehicle search and parking duration
- CSV export functionality
- Interactive dashboard with parking statistics
- SQLite database integration

## Technologies Used

- Python
- Tkinter
- SQLite
- CSV
- Heapq
- DateTime

## Algorithms Implemented

| Algorithm | Application |
|---|---|
| Greedy Algorithm | Nearest parking slot allocation |
| Dijkstra's Algorithm | Shortest route calculation |
| Linear Search | Parking slot searching |
| Selection Sort | Sorting slots by distance |

## How to Run

1. Install Python 3.
2. Download or clone this repository.
3. Open the project folder in VS Code.
4. Run the following command:

```bash
python main.py
```

## Project Structure

```text
ParkSmart/
│
├── main.py
├── algorithms.py
├── database.py
├── README.md
└── .gitignore
```

## Database

ParkSmart uses SQLite to store parking slots and vehicle parking records. The database is initialized automatically when the application runs.

## Project Type

MCA Mini Project – Design and Analysis of Algorithms (DAA)