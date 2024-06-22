Run the myapp.py file with the following command
      streamlit run myapp.py

After running streamlit run myapp.py in one terminal to start your Streamlit application and ensuring your FastAPI application is running in another terminal using uvicorn main:app --reload

Ensure that both applications are running without conflicts on their respective ports. Streamlit typically runs on port 8501 by default, and FastAPI can run on port 8000 or another port as configured.
Once both applications are running, you can interact with them through your web browser.