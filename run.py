from streamlit.web.cli import main
import sys

sys.argv = [
    "streamlit",
    "run",
    "app.py"
]

main()