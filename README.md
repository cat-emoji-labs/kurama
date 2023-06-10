# Python Service

## Prerequisites

- [Poetry](https://python-poetry.org/) should be installed on your system.

- Ensure the database is running in a Docker container:
  ```
  make postgres
  ```

- Ensure you have these environment variables in a .env:
  ```
  OPENAI_API_KEY=<OPEN_AI_KEY>
  DB_URL=postgresql://user:pass@localhost:5433/test
  PORT=5000
  HOST=0.0.0.0
  ```

## Installation

- Install the project dependencies using Poetry. Open a terminal or command prompt and navigate to the project directory.

  ```bash
  poetry install
  ```

## Usage

- Activate the virtual environment created by Poetry.

  ```bash
  poetry shell
  ```

- Start the server

  ```bash
  make server
  ```

# Built with

<img src="images/openai.png" alt="kurama" width="20%" height="20%">
<br/>