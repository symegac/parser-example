# Setup

1. Copy the repository:

        git clone https://github.com/symegac/parser-example.git

1. Navigate to directory:

        cd parser-example

1. Create a virtual environment:

        python -m venv .venv

1. Activate the virtual environment in your preferred shell:

        # Bash
        . ./.venv/Scripts/activate

        # Windows Command Prompt
        .\.venv\Script\activate.bat

        # Windows PowerShell
        (Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned) ; (& .\.venv\Scripts\Activate.ps1)

1. To install the package and libraries necessary for tests, run the following command:

        pip install -e .[test]

1. To check test coverage, run the following command (optionally, add a `-v` flag at the end to get verbose output in terminal):

        coverage run -m unittest discover -s tests

1. To generate coverage report, run the following command:

        coverage html

1. Open `htmlcov/index.html` in a browser to view coverage report.

1. Run [`example.py`](/example.py) to see the package in action:

        python example.py
