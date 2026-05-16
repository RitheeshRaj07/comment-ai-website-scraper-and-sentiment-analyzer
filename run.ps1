Write-Host "Starting Comment.AI Hackathon Demo..." -ForegroundColor Cyan
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
