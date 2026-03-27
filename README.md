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
5. Click **Advanced settings** and set **Python version** to `3.12` or `3.13`.
6. In app settings, open **Secrets** and add:

```toml
GROQ_API_KEY = "your_groq_api_key_here"
```

7. Click **Deploy**.

## Security notes

- Keep API keys only in Streamlit Secrets (cloud) or `.env` (local).
- Never commit `.env` or credentials to Git.
- User input is sanitized before prompt/file-name use.
- Error messages are generic to avoid exposing internals.

## Troubleshooting

- If build logs show Python `3.14.x` and `No matching distribution found for crewai`, set app Python version to `3.12` or `3.13` in **Manage app -> Settings -> Advanced settings** and reboot.
- `crewai==1.12.2` currently supports Python `<3.14`, so Python `3.14` will fail dependency install.

## Notes

- `.env` is ignored by git and should not be committed.
- `runtime.txt` also pins Python, but app settings can override it.
- If deployment fails due to package versioning, adjust `requirements.txt` and redeploy.
