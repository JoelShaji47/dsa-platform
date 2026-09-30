"""SQL track seeds (topic-wise ladder, v1).

Each problem runs against an in-memory SQLite database built from the test
case's seed SQL. Test cases keep the standard ``{input, expected_output,
is_hidden}`` shape so the DSA grader can be reused untouched:

- ``input``: seed SQL (``CREATE TABLE`` + ``INSERT`` statements).
- ``expected_output``: result rows serialized by
  ``app.services.sql_grader.serialize_rows`` (``|``-separated columns, one
  row per line, rows sorted — grading is order-insensitive).
- ``reference_solution``: the reference query. Ignored by ``ProblemSeed``
  validation (never reaches the DB); used by scripts/verify_sql_seeds.py.

Rules for v1 seeds: integer-only data (no float formatting edge cases), no
``|`` characters in string data. Grading is order-insensitive by default;
questions whose correctness depends on row order (``ORDER BY``) start their
seed SQL with the ``ORDERED_MARKER`` line from ``app.services.sql_grader``
and are graded in database order.
"""

SQL = "sql"


# Re-exported for seed readability: questions graded in database order start
# their seed SQL with this marker line (a harmless SQL comment).
from app.services.sql_grader import ORDERED_MARKER  # noqa: E402


def starters(sql: str) -> dict:
    return {SQL: sql}


EMPLOYEES_DDL = """CREATE TABLE employees (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  department TEXT NOT NULL,
  salary INTEGER NOT NULL
);"""

EMPLOYEES_VISIBLE = """INSERT INTO employees (id, name, department, salary) VALUES
  (1, 'Aisha', 'Engineering', 90000),
  (2, 'Ben', 'Marketing', 60000),
  (3, 'Cara', 'Engineering', 75000),
  (4, 'Dev', 'Marketing', 65000);"""

DEPARTMENTS_DDL = """CREATE TABLE departments (
  dept TEXT PRIMARY KEY,
  location TEXT NOT NULL
);"""

DEPARTMENTS_VISIBLE = """INSERT INTO departments (dept, location) VALUES
  ('Engineering', 'New York'),
  ('Marketing', 'London');"""

SQL_PROBLEMS = [
    {
        "title": "Select Employee Names",
        "slug": "sql-select-names",
        "difficulty": "EASY",
        "topic": "SQL",
        "description": """# Select Employee Names

## Statement
Return the `name` of every employee in the `employees` table.

## Schema
```sql
CREATE TABLE employees (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  department TEXT NOT NULL,
  salary INTEGER NOT NULL
);
```

## Example

**Table: employees**
```
id | name  | department  | salary
1  | Aisha | Engineering | 90000
2  | Ben   | Marketing   | 60000
3  | Cara  | Engineering | 75000
4  | Dev   | Marketing   | 65000
```

**Output**
```
name
Aisha
Ben
Cara
Dev
```

Explanation: all four employee names are returned.
""",
        "starter_code": starters("-- Return the name of every employee.\nSELECT "),
        "test_cases": [
            {
                "input": EMPLOYEES_DDL + "\n" + EMPLOYEES_VISIBLE + "\n",
                "expected_output": "Aisha\nBen\nCara\nDev",
                "is_hidden": False,
            },
            {
                "input": EMPLOYEES_DDL
                + "\nINSERT INTO employees (id, name, department, salary) VALUES\n"
                + "  (10, 'Eli', 'Sales', 50000),\n"
                + "  (11, 'Fay', 'Sales', 55000),\n"
                + "  (12, 'Gus', 'HR', 52000);\n",
                "expected_output": "Eli\nFay\nGus",
                "is_hidden": True,
            },
            {
                # Edge: empty table returns zero rows.
                "input": EMPLOYEES_DDL + "\n",
                "expected_output": "",
                "is_hidden": True,
            },
        ],
        "reference_solution": "SELECT name FROM employees;",
        "sources": ["sql-topic"],
        "pattern_key": "sql-select",
    },
    {
        "title": "High Earners",
        "slug": "sql-where-high-earners",
        "difficulty": "EASY",
        "topic": "SQL",
        "description": """# High Earners

## Statement
Return the `name` of every employee whose `salary` is greater than 70000.

## Schema
```sql
CREATE TABLE employees (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  department TEXT NOT NULL,
  salary INTEGER NOT NULL
);
```

## Example

**Table: employees**
```
id | name  | department  | salary
1  | Aisha | Engineering | 90000
2  | Ben   | Marketing   | 60000
3  | Cara  | Engineering | 75000
4  | Dev   | Marketing   | 65000
```

**Output**
```
name
Aisha
Cara
```

Explanation: only Aisha (90000) and Cara (75000) earn more than 70000.
""",
        "starter_code": starters(
            "-- Return the names of employees earning more than 70000.\nSELECT "
        ),
        "test_cases": [
            {
                "input": EMPLOYEES_DDL + "\n" + EMPLOYEES_VISIBLE + "\n",
                "expected_output": "Aisha\nCara",
                "is_hidden": False,
            },
            {
                "input": EMPLOYEES_DDL
                + "\nINSERT INTO employees (id, name, department, salary) VALUES\n"
                + "  (5, 'Hana', 'Engineering', 120000),\n"
                + "  (6, 'Ivan', 'Engineering', 80000),\n"
                + "  (7, 'Jill', 'Operations', 80000),\n"
                + "  (8, 'Ken', 'Operations', 40000);\n",
                "expected_output": "Hana\nIvan\nJill",
                "is_hidden": True,
            },
            {
                # Edge: exactly 70000 is not greater than 70000.
                "input": EMPLOYEES_DDL
                + "\nINSERT INTO employees (id, name, department, salary) VALUES\n"
                + "  (1, 'Asha', 'Engineering', 90000),\n"
                + "  (2, 'Rui', 'Marketing', 70000),\n"
                + "  (3, 'Max', 'Operations', 60000);\n",
                "expected_output": "Asha",
                "is_hidden": True,
            },
        ],
        "reference_solution": "SELECT name FROM employees WHERE salary > 70000;",
        "sources": ["sql-topic"],
        "pattern_key": "sql-where",
    },
    {
        "title": "Department Headcount",
        "slug": "sql-group-by-headcount",
        "difficulty": "MEDIUM",
        "topic": "SQL",
        "description": """# Department Headcount

## Statement
For each department, return the department name and the number of employees
in it. Name the count column `headcount`.

## Schema
```sql
CREATE TABLE employees (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  department TEXT NOT NULL,
  salary INTEGER NOT NULL
);
```

## Example

**Table: employees**
```
id | name  | department  | salary
1  | Aisha | Engineering | 90000
2  | Ben   | Marketing   | 60000
3  | Cara  | Engineering | 75000
4  | Dev   | Marketing   | 65000
```

**Output**
```
department  | headcount
Engineering | 2
Marketing   | 2
```

Explanation: each department has two employees.
""",
        "starter_code": starters(
            "-- Return each department and its employee count as `headcount`.\nSELECT "
        ),
        "test_cases": [
            {
                "input": EMPLOYEES_DDL + "\n" + EMPLOYEES_VISIBLE + "\n",
                "expected_output": "Engineering|2\nMarketing|2",
                "is_hidden": False,
            },
            {
                "input": EMPLOYEES_DDL
                + "\nINSERT INTO employees (id, name, department, salary) VALUES\n"
                + "  (1, 'Asha', 'Engineering', 90000),\n"
                + "  (2, 'Ravi', 'Engineering', 80000),\n"
                + "  (3, 'Mira', 'Engineering', 70000),\n"
                + "  (4, 'Tom', 'Sales', 60000);\n",
                "expected_output": "Engineering|3\nSales|1",
                "is_hidden": True,
            },
            {
                # Edge: empty table returns zero groups.
                "input": EMPLOYEES_DDL + "\n",
                "expected_output": "",
                "is_hidden": True,
            },
        ],
        "reference_solution": "SELECT department, COUNT(*) AS headcount FROM employees GROUP BY department;",
        "sources": ["sql-topic"],
        "pattern_key": "sql-group-by",
    },
    {
        "title": "Employee Locations",
        "slug": "sql-join-locations",
        "difficulty": "MEDIUM",
        "topic": "SQL",
        "description": """# Employee Locations

## Statement
Return each employee's `name` together with the `location` of their
department. Join `employees` to `departments` on the department name. Only
employees whose department appears in `departments` should be returned.

## Schema
```sql
CREATE TABLE employees (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  department TEXT NOT NULL,
  salary INTEGER NOT NULL
);
CREATE TABLE departments (
  dept TEXT PRIMARY KEY,
  location TEXT NOT NULL
);
```

## Example

**Table: employees**
```
id | name  | department  | salary
1  | Aisha | Engineering | 90000
2  | Ben   | Marketing   | 60000
3  | Cara  | Engineering | 75000
4  | Dev   | Marketing   | 65000
```

**Table: departments**
```
dept        | location
Engineering | New York
Marketing   | London
```

**Output**
```
name  | location
Aisha | New York
Ben   | London
Cara  | New York
Dev   | London
```

Explanation: each employee is matched to their department's location.
""",
        "starter_code": starters(
            "-- Return each employee name with their department location.\nSELECT "
        ),
        "test_cases": [
            {
                "input": EMPLOYEES_DDL
                + "\n"
                + EMPLOYEES_VISIBLE
                + "\n"
                + DEPARTMENTS_DDL
                + "\n"
                + DEPARTMENTS_VISIBLE
                + "\n",
                "expected_output": "Aisha|New York\nBen|London\nCara|New York\nDev|London",
                "is_hidden": False,
            },
            {
                "input": EMPLOYEES_DDL
                + "\nINSERT INTO employees (id, name, department, salary) VALUES\n"
                + "  (20, 'Eli', 'Sales', 50000),\n"
                + "  (21, 'Fay', 'HR', 55000);\n"
                + DEPARTMENTS_DDL
                + "\nINSERT INTO departments (dept, location) VALUES\n"
                + "  ('Engineering', 'Berlin'),\n"
                + "  ('Sales', 'Paris');\n",
                "expected_output": "Eli|Paris",
                "is_hidden": True,
            },
            {
                # Edge: no department matches, so the join is empty.
                "input": EMPLOYEES_DDL
                + "\nINSERT INTO employees (id, name, department, salary) VALUES\n"
                + "  (20, 'Eli', 'Sales', 50000);\n"
                + DEPARTMENTS_DDL
                + "\n",
                "expected_output": "",
                "is_hidden": True,
            },
        ],
        "reference_solution": "SELECT e.name, d.location FROM employees e JOIN departments d ON e.department = d.dept;",
        "sources": ["sql-topic"],
        "pattern_key": "sql-join",
    },
    {
        "title": "Above Average Salary",
        "slug": "sql-subquery-above-average",
        "difficulty": "MEDIUM",
        "topic": "SQL",
        "description": """# Above Average Salary

## Statement
Return the `name` of every employee whose `salary` is strictly greater than
the average salary across all employees. Use a subquery to compute the
average.

## Schema
```sql
CREATE TABLE employees (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  department TEXT NOT NULL,
  salary INTEGER NOT NULL
);
```

## Example

**Table: employees**
```
id | name  | department  | salary
1  | Aisha | Engineering | 90000
2  | Ben   | Marketing   | 60000
3  | Cara  | Engineering | 75000
4  | Dev   | Marketing   | 65000
```

**Output**
```
name
Aisha
Cara
```

Explanation: the average salary is 72500, so only Aisha (90000) and Cara
(75000) are above it.
""",
        "starter_code": starters(
            "-- Return names of employees earning more than the average salary.\nSELECT "
        ),
        "test_cases": [
            {
                "input": EMPLOYEES_DDL + "\n" + EMPLOYEES_VISIBLE + "\n",
                "expected_output": "Aisha\nCara",
                "is_hidden": False,
            },
            {
                "input": EMPLOYEES_DDL
                + "\nINSERT INTO employees (id, name, department, salary) VALUES\n"
                + "  (30, 'Lia', 'Engineering', 100000),\n"
                + "  (31, 'Max', 'Engineering', 50000),\n"
                + "  (32, 'Nia', 'Engineering', 50000);\n",
                "expected_output": "Lia",
                "is_hidden": True,
            },
            {
                # Edge: everyone earns the average, so nobody is above it.
                "input": EMPLOYEES_DDL
                + "\nINSERT INTO employees (id, name, department, salary) VALUES\n"
                + "  (30, 'Lia', 'Engineering', 50000),\n"
                + "  (31, 'Max', 'Engineering', 50000);\n",
                "expected_output": "",
                "is_hidden": True,
            },
        ],
        "reference_solution": "SELECT name FROM employees WHERE salary > (SELECT AVG(salary) FROM employees);",
        "sources": ["sql-topic"],
        "pattern_key": "sql-subquery",
    },
    {
        "title": "Salary Rank",
        "slug": "sql-window-salary-rank",
        "difficulty": "HARD",
        "topic": "SQL",
        "description": """# Salary Rank

## Statement
Return each employee's `name` together with their salary rank in a column
named `salary_rank`. The highest salary gets rank 1; tied salaries share the
same rank and the next rank is skipped (the `RANK()` window function). Use a
window function — do not hard-code ranks.

## Schema
```sql
CREATE TABLE employees (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  department TEXT NOT NULL,
  salary INTEGER NOT NULL
);
```

## Example

**Table: employees**
```
id | name  | department  | salary
1  | Aisha | Engineering | 90000
2  | Ben   | Marketing   | 60000
3  | Cara  | Engineering | 90000
4  | Dev   | Marketing   | 60000
5  | Eli   | Engineering | 75000
```

**Output**
```
name  | salary_rank
Aisha | 1
Ben   | 4
Cara  | 1
Dev   | 4
Eli   | 3
```

Explanation: Aisha and Cara tie at 90000 (rank 1), Eli is next (rank 3 —
rank 2 is skipped), Ben and Dev tie at 60000 (rank 4).
""",
        "starter_code": starters(
            "-- Return each name with its RANK() over salary descending as `salary_rank`.\nSELECT "
        ),
        "test_cases": [
            {
                "input": EMPLOYEES_DDL
                + "\nINSERT INTO employees (id, name, department, salary) VALUES\n"
                + "  (1, 'Aisha', 'Engineering', 90000),\n"
                + "  (2, 'Ben', 'Marketing', 60000),\n"
                + "  (3, 'Cara', 'Engineering', 90000),\n"
                + "  (4, 'Dev', 'Marketing', 60000),\n"
                + "  (5, 'Eli', 'Engineering', 75000);\n",
                "expected_output": "Aisha|1\nBen|4\nCara|1\nDev|4\nEli|3",
                "is_hidden": False,
            },
            {
                "input": EMPLOYEES_DDL
                + "\nINSERT INTO employees (id, name, department, salary) VALUES\n"
                + "  (10, 'Fay', 'Sales', 100000),\n"
                + "  (11, 'Gus', 'Sales', 200000),\n"
                + "  (12, 'Hal', 'Sales', 200000);\n",
                "expected_output": "Fay|3\nGus|1\nHal|1",
                "is_hidden": True,
            },
            {
                # Edge: a single employee always ranks 1.
                "input": EMPLOYEES_DDL
                + "\nINSERT INTO employees (id, name, department, salary) VALUES\n"
                + "  (10, 'Solo', 'Sales', 42000);\n",
                "expected_output": "Solo|1",
                "is_hidden": True,
            },
        ],
        "reference_solution": "SELECT name, RANK() OVER (ORDER BY salary DESC) AS salary_rank FROM employees;",
        "sources": ["sql-topic"],
        "pattern_key": "sql-window",
    },
    {
        "title": "Count Departments",
        "slug": "sql-count-distinct",
        "difficulty": "EASY",
        "topic": "SQL",
        "description": """# Count Departments

## Statement
Return the number of distinct departments in the `employees` table in a
column named `dept_count`.

## Schema
```sql
CREATE TABLE employees (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  department TEXT NOT NULL,
  salary INTEGER NOT NULL
);
```

## Example

**Table: employees**
```
id | name  | department  | salary
1  | Aisha | Engineering | 90000
2  | Ben   | Marketing   | 60000
3  | Cara  | Engineering | 75000
4  | Dev   | Marketing   | 65000
```

**Output**
```
dept_count
2
```

Explanation: there are two distinct departments, Engineering and Marketing.
""",
        "starter_code": starters(
            "-- Return the distinct department count as `dept_count`.\nSELECT "
        ),
        "test_cases": [
            {
                "input": EMPLOYEES_DDL + "\n" + EMPLOYEES_VISIBLE + "\n",
                "expected_output": "2",
                "is_hidden": False,
            },
            {
                "input": EMPLOYEES_DDL
                + "\nINSERT INTO employees (id, name, department, salary) VALUES\n"
                + "  (1, 'Asha', 'Engineering', 90000),\n"
                + "  (2, 'Ravi', 'Sales', 80000),\n"
                + "  (3, 'Mira', 'HR', 70000);\n",
                "expected_output": "3",
                "is_hidden": True,
            },
            {
                # Edge: no rows means zero departments.
                "input": EMPLOYEES_DDL + "\n",
                "expected_output": "0",
                "is_hidden": True,
            },
        ],
        "reference_solution": "SELECT COUNT(DISTINCT department) AS dept_count FROM employees;",
        "sources": ["sql-topic"],
        "pattern_key": "sql-aggregate",
    },
    {
        "title": "Name Search",
        "slug": "sql-like-search",
        "difficulty": "EASY",
        "topic": "SQL",
        "description": """# Name Search

## Statement
Return the `name` of every employee whose name starts with the letter 'A'.
Use the `LIKE` operator.

## Schema
```sql
CREATE TABLE employees (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  department TEXT NOT NULL,
  salary INTEGER NOT NULL
);
```

## Example

**Table: employees**
```
id | name  | department  | salary
1  | Aisha | Engineering | 90000
2  | Ben   | Marketing   | 60000
3  | Cara  | Engineering | 75000
4  | Dev   | Marketing   | 65000
```

**Output**
```
name
Aisha
```

Explanation: only Aisha's name starts with 'A'.
""",
        "starter_code": starters(
            "-- Return names starting with 'A' using LIKE.\nSELECT "
        ),
        "test_cases": [
            {
                "input": EMPLOYEES_DDL + "\n" + EMPLOYEES_VISIBLE + "\n",
                "expected_output": "Aisha",
                "is_hidden": False,
            },
            {
                "input": EMPLOYEES_DDL
                + "\nINSERT INTO employees (id, name, department, salary) VALUES\n"
                + "  (1, 'Amit', 'Engineering', 90000),\n"
                + "  (2, 'Asha', 'Sales', 80000),\n"
                + "  (3, 'Ben', 'Marketing', 60000);\n",
                "expected_output": "Amit\nAsha",
                "is_hidden": True,
            },
            {
                # Edge: no name matches.
                "input": EMPLOYEES_DDL
                + "\nINSERT INTO employees (id, name, department, salary) VALUES\n"
                + "  (1, 'Ben', 'Marketing', 60000),\n"
                + "  (2, 'Dev', 'Marketing', 65000);\n",
                "expected_output": "",
                "is_hidden": True,
            },
        ],
        "reference_solution": "SELECT name FROM employees WHERE name LIKE 'A%';",
        "sources": ["sql-topic"],
        "pattern_key": "sql-where",
    },
    {
        "title": "Big Departments",
        "slug": "sql-having-big-departments",
        "difficulty": "MEDIUM",
        "topic": "SQL",
        "description": """# Big Departments

## Statement
For each department with more than one employee, return the department name
and its employee count in a column named `headcount`. Filter groups with
`HAVING`, not with `WHERE`.

## Schema
```sql
CREATE TABLE employees (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  department TEXT NOT NULL,
  salary INTEGER NOT NULL
);
```

## Example

**Table: employees**
```
id | name  | department  | salary
1  | Aisha | Engineering | 90000
2  | Ben   | Marketing   | 60000
3  | Cara  | Engineering | 75000
4  | Dev   | Marketing   | 65000
```

**Output**
```
department  | headcount
Engineering | 2
Marketing   | 2
```

Explanation: both departments have two employees, so both qualify.
""",
        "starter_code": starters(
            "-- Return departments with more than one employee (use HAVING).\nSELECT "
        ),
        "test_cases": [
            {
                "input": EMPLOYEES_DDL + "\n" + EMPLOYEES_VISIBLE + "\n",
                "expected_output": "Engineering|2\nMarketing|2",
                "is_hidden": False,
            },
            {
                "input": EMPLOYEES_DDL
                + "\nINSERT INTO employees (id, name, department, salary) VALUES\n"
                + "  (1, 'Asha', 'Engineering', 90000),\n"
                + "  (2, 'Ravi', 'Engineering', 80000),\n"
                + "  (3, 'Mira', 'Engineering', 70000),\n"
                + "  (4, 'Tom', 'Sales', 60000);\n",
                "expected_output": "Engineering|3",
                "is_hidden": True,
            },
            {
                # Edge: every department is a singleton, so nothing qualifies.
                "input": EMPLOYEES_DDL
                + "\nINSERT INTO employees (id, name, department, salary) VALUES\n"
                + "  (1, 'Asha', 'Engineering', 90000),\n"
                + "  (2, 'Tom', 'Sales', 60000);\n",
                "expected_output": "",
                "is_hidden": True,
            },
        ],
        "reference_solution": "SELECT department, COUNT(*) AS headcount FROM employees GROUP BY department HAVING COUNT(*) > 1;",
        "sources": ["sql-topic"],
        "pattern_key": "sql-having",
    },
    {
        "title": "All Employees, With Locations",
        "slug": "sql-left-join-all",
        "difficulty": "MEDIUM",
        "topic": "SQL",
        "description": """# All Employees, With Locations

## Statement
Return every employee's `name` together with the `location` of their
department. Unlike an inner join, employees whose department has no entry in
`departments` must still appear — with a NULL location. Use `LEFT JOIN`.

## Schema
```sql
CREATE TABLE employees (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  department TEXT NOT NULL,
  salary INTEGER NOT NULL
);
CREATE TABLE departments (
  dept TEXT PRIMARY KEY,
  location TEXT NOT NULL
);
```

## Example

**Table: employees**
```
id | name  | department  | salary
1  | Aisha | Engineering | 90000
2  | Ben   | Marketing   | 60000
3  | Cara  | Engineering | 75000
4  | Dev   | Marketing   | 65000
5  | Eli   | HR          | 55000
```

**Table: departments**
```
dept        | location
Engineering | New York
Marketing   | London
```

**Output**
```
name  | location
Aisha | New York
Ben   | London
Cara  | New York
Dev   | London
Eli   | NULL
```

Explanation: Eli works in HR, which has no departments row, so his location
is NULL — but he still appears.
""",
        "starter_code": starters(
            "-- Return every employee name with their department location (use LEFT JOIN).\nSELECT "
        ),
        "test_cases": [
            {
                "input": EMPLOYEES_DDL
                + "\nINSERT INTO employees (id, name, department, salary) VALUES\n"
                + "  (1, 'Aisha', 'Engineering', 90000),\n"
                + "  (2, 'Ben', 'Marketing', 60000),\n"
                + "  (3, 'Cara', 'Engineering', 75000),\n"
                + "  (4, 'Dev', 'Marketing', 65000),\n"
                + "  (5, 'Eli', 'HR', 55000);\n"
                + DEPARTMENTS_DDL
                + "\n"
                + DEPARTMENTS_VISIBLE
                + "\n",
                "expected_output": "Aisha|New York\nBen|London\nCara|New York\nDev|London\nEli|NULL",
                "is_hidden": False,
            },
            {
                "input": EMPLOYEES_DDL
                + "\nINSERT INTO employees (id, name, department, salary) VALUES\n"
                + "  (20, 'Fay', 'HR', 55000),\n"
                + "  (21, 'Gus', 'HR', 52000);\n"
                + DEPARTMENTS_DDL
                + "\nINSERT INTO departments (dept, location) VALUES\n"
                + "  ('Engineering', 'Berlin');\n",
                "expected_output": "Fay|NULL\nGus|NULL",
                "is_hidden": True,
            },
            {
                # Edge: no employees at all.
                "input": EMPLOYEES_DDL + "\n" + DEPARTMENTS_DDL + "\n" + DEPARTMENTS_VISIBLE + "\n",
                "expected_output": "",
                "is_hidden": True,
            },
        ],
        "reference_solution": "SELECT e.name, d.location FROM employees e LEFT JOIN departments d ON e.department = d.dept;",
        "sources": ["sql-topic"],
        "pattern_key": "sql-join",
    },
    {
        "title": "High Paying Departments",
        "slug": "sql-cte-high-paying",
        "difficulty": "MEDIUM",
        "topic": "SQL",
        "description": """# High Paying Departments

## Statement
Using a `WITH` clause (CTE), compute the average salary per department, then
return the names of departments whose average salary is strictly greater
than 70000.

## Schema
```sql
CREATE TABLE employees (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  department TEXT NOT NULL,
  salary INTEGER NOT NULL
);
```

## Example

**Table: employees**
```
id | name  | department  | salary
1  | Aisha | Engineering | 90000
2  | Ben   | Marketing   | 60000
3  | Cara  | Engineering | 75000
4  | Dev   | Marketing   | 65000
```

**Output**
```
department
Engineering
```

Explanation: Engineering averages 82500 (above 70000) while Marketing
averages 62500.
""",
        "starter_code": starters(
            "-- Use a WITH clause, then select departments averaging above 70000.\nWITH "
        ),
        "test_cases": [
            {
                "input": EMPLOYEES_DDL + "\n" + EMPLOYEES_VISIBLE + "\n",
                "expected_output": "Engineering",
                "is_hidden": False,
            },
            {
                "input": EMPLOYEES_DDL
                + "\nINSERT INTO employees (id, name, department, salary) VALUES\n"
                + "  (1, 'Asha', 'Engineering', 100000),\n"
                + "  (2, 'Ravi', 'Marketing', 50000),\n"
                + "  (3, 'Mira', 'Marketing', 90000);\n",
                "expected_output": "Engineering",
                "is_hidden": True,
            },
            {
                # Edge: no department averages above the bar.
                "input": EMPLOYEES_DDL
                + "\nINSERT INTO employees (id, name, department, salary) VALUES\n"
                + "  (1, 'Ben', 'Marketing', 60000),\n"
                + "  (2, 'Dev', 'Marketing', 65000);\n",
                "expected_output": "",
                "is_hidden": True,
            },
        ],
        "reference_solution": "WITH dept_avg AS (SELECT department, AVG(salary) AS avg_sal FROM employees GROUP BY department) SELECT department FROM dept_avg WHERE avg_sal > 70000;",
        "sources": ["sql-topic"],
        "pattern_key": "sql-cte",
    },
    {
        "title": "Top Earners",
        "slug": "sql-order-by-top-earners",
        "difficulty": "MEDIUM",
        "topic": "SQL",
        "description": """# Top Earners

## Statement
Return the `name` of the two highest-paid employees, highest salary first.
Order rows with `ORDER BY` and keep only two with `LIMIT`. Row order matters
for this question — it is graded exactly as returned.

## Schema
```sql
CREATE TABLE employees (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  department TEXT NOT NULL,
  salary INTEGER NOT NULL
);
```

## Example

**Table: employees**
```
id | name  | department  | salary
1  | Aisha | Engineering | 90000
2  | Ben   | Marketing   | 60000
3  | Cara  | Engineering | 75000
4  | Dev   | Marketing   | 65000
5  | Zara  | Sales       | 120000
6  | Mira  | Sales       | 110000
```

**Output**
```
name
Zara
Mira
```

Explanation: Zara (120000) and Mira (110000) are the top two, in that order.
""",
        "starter_code": starters(
            "-- Return the top 2 earners, highest first (ORDER BY + LIMIT).\nSELECT "
        ),
        "test_cases": [
            {
                "input": ORDERED_MARKER
                + "\n"
                + EMPLOYEES_DDL
                + "\nINSERT INTO employees (id, name, department, salary) VALUES\n"
                + "  (1, 'Aisha', 'Engineering', 90000),\n"
                + "  (2, 'Ben', 'Marketing', 60000),\n"
                + "  (3, 'Cara', 'Engineering', 75000),\n"
                + "  (4, 'Dev', 'Marketing', 65000),\n"
                + "  (5, 'Zara', 'Sales', 120000),\n"
                + "  (6, 'Mira', 'Sales', 110000);\n",
                "expected_output": "Zara\nMira",
                "is_hidden": False,
            },
            {
                "input": ORDERED_MARKER
                + "\n"
                + EMPLOYEES_DDL
                + "\nINSERT INTO employees (id, name, department, salary) VALUES\n"
                + "  (10, 'Fay', 'Sales', 50000),\n"
                + "  (11, 'Zed', 'Engineering', 150000),\n"
                + "  (12, 'Amy', 'Marketing', 100000);\n",
                "expected_output": "Zed\nAmy",
                "is_hidden": True,
            },
            {
                # Edge: fewer rows than the limit still returns in order.
                "input": ORDERED_MARKER
                + "\n"
                + EMPLOYEES_DDL
                + "\nINSERT INTO employees (id, name, department, salary) VALUES\n"
                + "  (10, 'Solo', 'Sales', 42000);\n",
                "expected_output": "Solo",
                "is_hidden": True,
            },
        ],
        "reference_solution": "SELECT name FROM employees ORDER BY salary DESC LIMIT 2;",
        "sources": ["sql-topic"],
        "pattern_key": "sql-order-by",
    },
    {
        "title": "Salary Bands",
        "slug": "sql-case-bands",
        "difficulty": "MEDIUM",
        "topic": "SQL",
        "description": """# Salary Bands

## Statement
Return each employee's `name` with a salary band in a column named `band`:
`'senior'` for salary 80000 or above, `'mid'` for 65000 or above, and
`'junior'` otherwise. Use a `CASE` expression.

## Schema
```sql
CREATE TABLE employees (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  department TEXT NOT NULL,
  salary INTEGER NOT NULL
);
```

## Example

**Table: employees**
```
id | name  | department  | salary
1  | Aisha | Engineering | 90000
2  | Ben   | Marketing   | 60000
3  | Cara  | Engineering | 75000
4  | Dev   | Marketing   | 65000
```

**Output**
```
name  | band
Aisha | senior
Ben   | junior
Cara  | mid
Dev   | mid
```

Explanation: Aisha is senior (90000), Ben junior (60000), Cara and Dev mid.
""",
        "starter_code": starters(
            "-- Return each name with its CASE band as `band`.\nSELECT "
        ),
        "test_cases": [
            {
                "input": EMPLOYEES_DDL + "\n" + EMPLOYEES_VISIBLE + "\n",
                "expected_output": "Aisha|senior\nBen|junior\nCara|mid\nDev|mid",
                "is_hidden": False,
            },
            {
                "input": EMPLOYEES_DDL
                + "\nINSERT INTO employees (id, name, department, salary) VALUES\n"
                + "  (1, 'Asha', 'Engineering', 80000),\n"
                + "  (2, 'Ravi', 'Sales', 65000),\n"
                + "  (3, 'Mira', 'HR', 64999);\n",
                "expected_output": "Asha|senior\nMira|junior\nRavi|mid",
                "is_hidden": True,
            },
            {
                # Edge: empty table returns no bands.
                "input": EMPLOYEES_DDL + "\n",
                "expected_output": "",
                "is_hidden": True,
            },
        ],
        "reference_solution": "SELECT name, CASE WHEN salary >= 80000 THEN 'senior' WHEN salary >= 65000 THEN 'mid' ELSE 'junior' END AS band FROM employees;",
        "sources": ["sql-topic"],
        "pattern_key": "sql-case",
    },
]
