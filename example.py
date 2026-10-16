from datetime import datetime
from pathlib import Path

from parser import *
from parser.util import truncate

section = lambda text: print(f"\n{text:=^80}")

DATA_PATH = Path(__file__).parent / "bilag"

# forcing LF as EOL char, even on Windows
config = ParserConfig(newline='\n')
# using standard settings, apart from EOL
parser = StandardCSVParser(config=config)
# reading CSV file
reader = CSVReader(DATA_PATH / "sogne.dawa.csv", parser=parser)

# custom column types (in addition to simple data types predicted by reader)
coltypes = {
    "ændret": datetime.fromisoformat,
    "geo_ændret": datetime.fromisoformat
}
# loading read data into table
table = Table(reader.header, reader.rows, **coltypes)

# alphabetizing table and taking preview
alphabetized_parishes = table.sort("navn").head()
section("Danish parishes alphabetized")
print(f"{alphabetized_parishes:13}")

# loading new file using same parser and reader settings
reader.reload(new_path=DATA_PATH / "employees.ascii.csv")
table = Table(reader.header, reader.rows)

# sorting table by salary in descending order, taking first 5 entries
salaries = table.sort("salary", reverse=True)
highest_salaries = salaries.head(5)
section("Highest salaries")
print(highest_salaries)

# taking last five entries
lowest_salaries = salaries.tail(5)
section("Lowest salaries")
print(f"{lowest_salaries:18}")

# comparing input and output
section("Raw CSV input")
print(truncate(reader.raw_data, 200))

section("Parsed data")
print(reader.header)
print(truncate(reader.rows, 200))

section("JSON output")
print(truncate(reader.to_json(), 400))
