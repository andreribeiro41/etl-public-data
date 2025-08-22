# ETL • Open‑Meteo Weather 🇧🇷
Pipeline de exemplo para portfólio: coleta dados **horários** de clima da API pública **Open‑Meteo** para cidades brasileiras,
transforma em **agregações diárias** e carrega como **CSV/Parquet** e (opcional) **SQLite/Postgres**.

## ▶️ Rodando
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp configs/.env.example .env
make run
```
