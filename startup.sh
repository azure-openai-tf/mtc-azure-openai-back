
apt update
apt install build-essential
python -m pip install -r requirements.txt

python -m uvicorn api:app --host 0.0.0.0 --app-dir source
# python -m uvicorn api:app --host 0.0.0.0 --app-dir source --reload