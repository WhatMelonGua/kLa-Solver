This python code is abadon
Try to fix your dissolved oxygen electrode's response time on website:
http://onlineferment.site/ClarkCorrect.html
it's more convenient & stable!





# kLa-Solver
  If your dissolved oxygen electrode has a response time that cannot be ignored，try to use this repository to correct your experimental data.And welcome to propose possible problems and improvements of the algorithm!

Folder description：
-Main：
  It includes kLa-Solver's Python file, excel visual verification table and solver configuration TXT file.
  You can change the kLa value of dissolved oxygen electrode, default solution time step, and saturated solution concentration (generally 1, i.e. 100%) in TXT file (set.txt).You only need to change the number between two "<text>" to complete this operation,and this is also valid for exe executables!
  
-TestData:
  If you just want to observe the result of this algorithm, you can use the txt file under this folder, which contains the do data of 10 L liquid filling and 20l/min ventilation at 200, 300, 400 rpm. The default dissolved oxygen electrode is used, and you can get relatively good results without changing the configuration file.
  Open the txt data file, after the python or EXE file is executed, enter 0 to select the line data input, copy the do data and t data of TXT in sequence, enter and press enter in sequence
