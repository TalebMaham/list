if (Test-Path ../venv) {
  Remove-Item ../venv -R
}

python -m venv ./venv
./venv/Scripts/Activate.ps1

pip install -r ./requirements.txt

deactivate