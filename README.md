# Employee-Scheduler

This Code can create shift schedules automatically.  
An Example of a generated result can be found in the section below.  
Google OR-Tools is used to calculate shift schedules.

# Example shift scheduler result

![scheduler](data/scheduler.gif)

Every employee is in a team.  
Employees in a team are not allowed to work with employees from other teams, this creates a shift change.  
For example, one team works in the early shift, 
for the late shift there will be a team switch so another Team works in late shift.  
The associated teams are in the first column.  
The second column contains the names of the employees, who are numbered here.  
The third column shows the skills that each employee can take on  
The remaining columns show the shift and task assignments. The shift that needs to be taken on is always listed first and then   
the task below.


# Run the Code

Needed Packages:  

* Google OR-Tools
    * pip install ortools
    * needed to use the CP-Solver
* Prettytable
    * pip install prettytable
    * needed to print solutions to the console
* openpyxl: pip install openpyxl
    * pip install openpyxl
    * needed to read and write Excel files

Install with:
```sh
pip install -r requirements.txt
```
Alternatively, you can install the package with:
```sh
pip install ortools prettytable openpyxl
```
You can find the entry point in src/main.py

