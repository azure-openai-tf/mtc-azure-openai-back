
echo GCC Lib Install Start
apt -y install build-essential gcc
echo GCC Lib Install End

echo PIP Install Start
python -m pip install -r requirements.txt
echo PIP Install END


echo Start Server
python -m uvicorn api:app --host 0.0.0.0 --app-dir source
# python -m uvicorn api:app --host 0.0.0.0 --app-dir source --reload