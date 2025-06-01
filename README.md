# MASTOPIA Integrated Version for Collaboration with Jessica Lee
https://mastopia-spr2025.streamlit.app/

### How to run it on your own machine

1. Install the requirements (Python>=3.9)
 
   ```
   $ pip install -r requirements.txt
   ```
   
2. Add your API keys in ```.streamlit/secrets.toml```

3. Run the app

   ```
   $ streamlit run streamlit_app.py --server.enableCORS false --server.enableXsrfProtection false
   ```