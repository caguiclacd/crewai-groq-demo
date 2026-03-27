# CrewAI + Groq Streamlit Demo

This app is ready for deployment on **Streamlit Community Cloud**.

## Local run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Community Cloud (Free)

1. Create a GitHub repository.
2. Push this project to GitHub.
3. Go to https://share.streamlit.io and sign in with GitHub.
4. Click **Create app** and select:
   - Repository: your repo
   - Branch: `main`
   - Main file path: `app.py`
5. In the app settings, open **Secrets** and add:

```toml
GROQ_API_KEY = "your_groq_api_key_here"
```

6. Click **Deploy**.

## Notes

- `.env` is ignored by git and should not be committed.
- `runtime.txt` pins Python for Streamlit Cloud compatibility.
- If deployment fails due to package versioning, adjust `requirements.txt` and redeploy.
