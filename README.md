# Ton Action Scanner

Ton Action Scanner is an open-source API designed for fetching transactions' data, aimed to be the fastest and most reliable tool for getting the data from TON-blockchain.

## Documentation:

> Work In Progress

## Development:

### Prerequisites

- Python 3.12
- PostgreSQL 17.2

### Installation

1. **Clone the repository:**

   ```bash
   git clone git@github.com:ruslan-korneev/ton-action-scanner.git
   cd ton-action-scanner
   ```

2. **Create a virtual environment and activate it:**

   ```bash
   python3.12 -m venv .venv
   source .venv/bin/activate
   poetry install
   ```

   if you are using uv:
    ```bash
   uv venv
   uv pip install -r pyproject.toml
    ```

4. **Set up PostgreSQL:**

   - Create a new PostgreSQL database.
   - Update the database credentials in the `.env` file with your database credentials.

5. **Run database migrations:**

   ```bash
   alembic upgrade head
   ```

6. **Start the server:**

   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

   The API will be available at `http://0.0.0.0:8000`.

## Usage

- **API Documentation**: Access interactive API documentation at `http://0.0.0.0:8000/api/v1/docs`.

## Contact

For questions or feedback, please contact [admin@ruslan.beer](mailto:admin@ruslan.beer).
