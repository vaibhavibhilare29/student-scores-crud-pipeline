# Student Scores CRUD Pipeline

A simple data pipeline that moves student scores from a CSV file into a MySQL database and performs full CRUD operations using Python.

## Objectives

1. Read `student_scores.csv` using **Pandas**
2. Create the table and insert the data into **MySQL** using **SQLAlchemy**
3. Read the data back from MySQL using **Pandas**
4. Update a record using raw SQL via **mysql-connector-python**
5. Delete a record from the table

## Tech Stack

- Python 3
- Pandas
- SQLAlchemy
- mysql-connector-python
- MySQL

## Pipeline Flow

```
CSV  ->  Pandas  ->  SQLAlchemy  ->  MySQL  ->  Pandas (read)  ->  mysql.connector (update / delete)
```

## Dataset

`student_scores.csv`

| Column | Type |
|---|---|
| id | INT (primary key) |
| name | VARCHAR(100) |
| math_score | INT |
| english_score | INT |
| science_score | INT |

Example:

```csv
id,name,math_score,english_score,science_score
1,Alice,78,85,88
2,Bob,82,79,91
3,Charlie,69,72,75
```

## Project Structure

```
student_project/
├── pipeline.py
├── student_scores.csv
├── pipeline.log        (created when the script runs)
└── README.md
```

## Setup

1. Install the libraries:
   ```bash
   pip install pandas sqlalchemy mysql-connector-python
   ```
2. Create the database in MySQL:
   ```sql
   CREATE DATABASE school;
   ```
3. Open `pipeline.py` and set your MySQL password in `DB_CONFIG` (or set the `DB_PASSWORD` environment variable).
4. Place `student_scores.csv` in the same folder as `pipeline.py`.

## Run

```bash
python pipeline.py
```

## What the script does

| Step | Operation | Tool |
|---|---|---|
| 1 | Read and validate CSV | Pandas |
| 2 | Create table and insert rows | SQLAlchemy |
| 3 | Query data back | Pandas `read_sql` |
| 4 | Update Bob's `math_score` to 90 (id = 2) | mysql.connector |
| 5 | Delete Charlie (id = 3) | mysql.connector |
| 6 | Print the final table | Pandas |

Update and delete use parameterized queries (`%s` placeholders) to prevent SQL injection. All steps are logged to the console and to `pipeline.log`.

## Expected Output

```
Inserted 3 rows into student_scores
Updated 1 row(s) (id=2, math_score=90)
Deleted 1 row(s) (id=3)

Final data:
   id   name  math_score  english_score  science_score
0   1  Alice          78             85             88
1   2    Bob          90             79             91
```

## Verify in MySQL

```sql
USE school;
SELECT * FROM student_scores;
```

## Notes

- The script drops and recreates the `student_scores` table on every run, so it can be re-run safely. Do not point it at a table you want to keep.
- To change which records are updated or deleted, edit `UPDATE_ID`, `NEW_MATH_SCORE` and `DELETE_ID` at the top of `pipeline.py`.

## Troubleshooting

| Error | Fix |
|---|---|
| Access denied for user | Check the password in `DB_CONFIG` |
| Unknown database 'school' | Run `CREATE DATABASE school;` |
| Can't connect to MySQL server | Start the MySQL service |
| CSV file not found | Keep the CSV in the same folder as `pipeline.py` |
