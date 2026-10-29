# ScatterLab — Relationship Analysis (Task 29)

A distinctive scatter-plot web app for exploring the relationship between two numerical variables. Built with **Python, Flask, Pandas, NumPy, and Matplotlib**. It includes three CSV datasets and supports CSV uploads. **No Jupyter Notebook is required.**

## Included datasets

- `datasets/iris_dataset.csv` — 150 flower records from scikit-learn's bundled Iris dataset, including species and four numerical measurements.
- `datasets/housing_dataset.csv` — 120 generated example house records. This is synthetic practice data, not real property listings.
- `datasets/student_performance_dataset.csv` — 150 generated example student records. This is synthetic practice data, not real student records.

## Run on Windows (VS Code terminal)

1. Extract the ZIP. Open the `Relationship_Analysis_WebApp` folder in VS Code.
2. Open **Terminal → New Terminal**. Make sure the terminal is inside this folder. You should see `app.py`, `requirements.txt`, `datasets`, and `templates` when you run `dir`.
3. Check Python:

   ```powershell
   py --version
   ```

4. Create a local virtual environment (recommended):

   ```powershell
   py -m venv .venv
   ```

5. Install the libraries:

   ```powershell
   .\.venv\Scripts\python.exe -m pip install --upgrade pip
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

   If the virtual environment command fails, use `py -m pip install -r requirements.txt` instead.

6. Start the web application:

   ```powershell
   .\.venv\Scripts\python.exe app.py
   ```

   If you used the fallback install instead, run `py app.py`.

7. Open **http://127.0.0.1:5000** in Chrome. Choose one of the three datasets, select two numeric columns, and click **Generate scatter plot**. You can upload another CSV with at least two numerical columns.
8. To stop the server, return to the terminal and press **Ctrl+C**.

If Windows blocks a command because scripts are disabled, these instructions use the `.venv\Scripts\python.exe` executable directly and do not require activating the environment.

## What the app delivers

- Scatter plot with a fitted trend line
- Pearson correlation value
- Positive, negative, or weak linear-pattern interpretation
- Four data observations, including range and row count
- Upload support for CSV files (maximum 10 MB)
- Correlation caveat: association does not demonstrate causation

## GitHub: create a new repository and push

Account: `PranathiM15`

1. Open this **new repository page**: https://github.com/new
2. Repository name: `relationship-analysis-task29`
3. Description: `A Python web app that visualizes relationships between numerical variables using scatter plots, correlation analysis, and three sample datasets.`
4. Choose **Public** or **Private** as required. Do not tick “Add a README”, `.gitignore`, or license because the project already contains files for these.
5. Click **Create repository**.
6. In VS Code, open Terminal and verify you are in the project folder:

   ```powershell
   dir
   ```

   You should see `app.py`, `README.md`, `requirements.txt`, `datasets`, `static`, and `templates`.

7. Run the following commands in this exact order:

   ```powershell
   git --version
   git init
   git add .
   git commit -m "Add relationship analysis web app"
   git branch -M main
   git remote add origin https://github.com/PranathiM15/relationship-analysis-task29.git
   git push -u origin main
   ```

8. If Git says **`remote origin already exists`**, use this instead of `git remote add origin ...`, then continue with push:

   ```powershell
   git remote set-url origin https://github.com/PranathiM15/relationship-analysis-task29.git
   git push -u origin main
   ```

9. If Git asks you to sign in, complete the browser authentication prompt. GitHub no longer accepts your account password in the terminal for normal HTTPS Git operations; use the browser sign-in / Git Credential Manager flow.
10. After a successful push, open: https://github.com/PranathiM15/relationship-analysis-task29

### If Git is not installed

Install Git for Windows from https://git-scm.com/download/win, finish the installer, close and reopen VS Code, then check `git --version` before repeating the Git commands. Do not run Git commands until that command works.

## Troubleshooting

- **`No module named flask`**: run `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` from the project folder.
- **`can't open file app.py`**: terminal is in the wrong folder. Use `cd` to enter the extracted `Relationship_Analysis_WebApp` folder.
- **Port 5000 is busy**: close the other app using it, then retry.
- **Plot is blank / data error**: choose two different numerical columns and generate again.
- **Push rejected because the remote has a README**: only if you accidentally initialized the GitHub repo with files, run `git pull --rebase origin main` and resolve any prompted conflicts before pushing. The recommended setup is to create an empty repository first.

### Optional shortcut

You can also double-click `run_app.bat` on Windows. It creates the `.venv` folder if needed, installs the requirements, and starts the app. Keep the terminal window open while using the web app.
