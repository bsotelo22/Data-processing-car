DATA READING:

In order to properly read the json file first some small changes needs to be made to the format in which we receive the file:
    1. encapsulate between [] the full file
    2. use find and replace to change } for },

For correct execution of the python file, Onedot_task.py the data (supplier_car.json) must be in the same folder as the execution folder.