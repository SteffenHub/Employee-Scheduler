# Employee-Scheduler

This Code can create shift schedules automatically.  
An Example of a generated result can be found in the section below. 
Google OR-Tools is used to calculate shift schedules.
More Information about the Code structure can be found in the README.md of the src folder.

# Example shift scheduler result

![Example Scheduler Result](data/example_scheduler_result.png)

Every employee is in a team.  
Employees in a team are not allowed to work with employees from other teams, this creates a shift change.  
For example, one team works in the early shift, 
for the late shift there will be a team switch so another Team works in late shift.  
The associated teams are in the first column.  
The second column contains the names of the employees, who are numbered here.  
The third column shows the skills that each employee can take on  
The remaining columns show the shift and task assignments. The shift that needs to be taken on is always listed first and then   
the task below.

# Needed Software

This Code uses some external Software:
* Google OR-Tools: pip install ortools
* Prettytable: pip install prettytable
* openpyxl: pip install openpyxl

