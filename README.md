# Employee-Scheduler

This Code can generate shift schedules automatically using the CP-Solver from Google [OR-Tools](https://developers.google.com/optimization).  

![scheduler](data/scheduler.gif)

# Implemented rules 
Every employee is in a team.  
Employees in a team are not allowed to work with employees from other teams, this creates a shift change.  
For example, one team works in the early shift, 
for the late shift there will be a team switch so another Team works in late shift.  
The associated teams are in the first column.  
The second column contains the names of the employees, who are numbered here.  
The third column shows the skills that each employee can take on  
The remaining columns show the shift and task assignments. The shift that needs to be taken on is always listed first and then   
the task below.

# Configure your needs

### Input Data

You have to change the input_data_creator.py in the src/model.

The input data is saved in two variables weeks as a list of week objects and teams as a list of team objects.
* __Weeks__ describe the business needs and contain which skill you need on a specific day 
  * If you want to generate 4 Week make sure the weeks list contain 4 Week objects
    * Each Week contain a list of Day objects. You should add 7 days to this list. If you dont want to generate a full Week this list can be smaller than 7.
      * Each Day object contain a list of shifts. We used 3 shifts with early-, late and nightshift. 
        * Each shift object contain a list of skills that have to be done in this shift.
        * Make sure the skill names are the same as in the teams list
  * You have to configure how many days you actually want to generate in the main function in src/main.py
* __Teams__ describe your resources and contain all employees their skills and availability
  * If you don't have separate teams this list has only one entry.
    * Each team object contain a list of employees.
      * Make sure each employee have a unique name 
      * An Employee can be a shift manager or not
      * The variable fixed_skills is used to analyse the business needs and specify a not real employee with a default value of true
      * Each Employee contain a list of skills. Make sure the same skill names are used as in the weeks list.

![model structure](data/model_structure.png)

Make sure that each object has its own unique name.
This is needed to uniquely address the variables of employees, skills and working hours.
Choosing non-unique names can cause incorrect output or errors.

### Rules

Currently, the rules calls have to be manually commented and uncommented whether you want to use the rule or not.
This can be done in the main file in src/main.py.
look up what each rule do and how it works in the src/rule_builder.py file.
The Soft-Constraints need a cost value. to set this value you need a bit of experience, 
you should use the console output to optimize this values see [Understanding Outputs](#understanding-outputs).

# Understanding Outputs

![Scheduler result](data/example_scheduler_result.png)


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

