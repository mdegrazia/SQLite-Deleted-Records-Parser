SQLite-Parser
=============

Script to recover deleted entries in an SQLite database and places the output into either a TSV file or text file (-r)

###Usage for sqlparse.py

    sqlparse.py -f /home/sanforensics/smsmms.db -o report.tsv
    sqlparse.py -f /home/sanforensics/smssms.db -r -o report.txt
	
	Optional switch -p to print out re purposed B-Leaf pages:
	
	sqlparse.py -p -f /home/sanforensics/smsmms.db -o report.tsv
    sqlparse.py -p -f /home/sanforensics/smssms.db -r -o report.txt
	
    
###Usage for sqlparse_CLI.exe

    sqlparse_CLI.exe -f C:\Users\Mari\smsmms.db -o report.tsv
    sqlparse_CLI.exe -f C:\Users\Mari\smsmms.db -t -o report.txt
	
	sqlparse_CLI.exe -p -f C:\Users\Mari\smsmms.db -o report.tsv
    sqlparse_CLI.exe -p -f C:\Users\Mari\smsmms.db -r -o report.txt

###sqlparse_GUI.exe
This file is a GUI interface

###More Information

View the blog post at http://az4n6.blogspot.com/2013/11/python-parser-to-recover-deleted-sqlite.html for more information






Email Mari,  arizona4n6 at gmail dot com for help/questions/bugs
