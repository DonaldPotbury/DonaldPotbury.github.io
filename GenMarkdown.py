#
# This program will generate an html file that is the LifeJournal reading
# plan with links to chapters in Bible
#
import sqlite3

#----------------------------------------------------------
#
#----------------------------------------------------------
class ReadingAssignment():
    def __init__(self, scriptures):
        i=0
        self.assignment = ""
        for scripture in scriptures:
            self.month   = scripture[0]
            self.day     = scripture[1]
            self.abbr    = scripture[2]
            self.book    = scripture[3]
            self.chapter = scripture[4]
    
            base_markdown = "[{} {}](https://www.bible.com/bible/111/{}.{}.NIV)"\
                .format(self.book, self.chapter, self.abbr, self.chapter)

            if i == 0:
                self.assignment += base_markdown
            else:
                self.assignment += ', ' + base_markdown
            i+=1


#----------------------------------------------------------
#
#----------------------------------------------------------
class Month:
    def __init__(self, month_nbr, month_name, days):
        self.nbr = month_nbr
        self.name = month_name
        self.days = days



conn = sqlite3.connect('./LifeJournal.db')
sql = "select month_nbr, month_name, days from MonthsInYear"
month_results = conn.execute(sql)

for month in month_results:
    current_month = Month(month[0], month[1], month[2])
    print(current_month.name)
    with open("./{}.md".format(current_month.name), 'w') as md:
        md.write("# Life Journal\n")
        md.write("## {}\n\n\n".format(current_month.name))
        md.write("| Day | Scriptures |\n")
        md.write("| ---: | :--- |\n")
        
        # The daily stuff goes here
        for current_day in range(1, current_month.days + 1):
            
            # Find the reading assignments for the current month and day
            # This will most likely be multiple records which will need to be concatenated into
            # A comma delimited string
            sql = """
            select a.month     
                , a.day        
                , b.abbr         
                , a.book       
                , a.chapter 
                , a.from_verse || '-' || a.to_verse as 'verses'   
            from Assignments a 
            inner join BookAbbr b on a.book = b.book 
            where month = {}   
            and   day = {}     
            order by id;
            """.format(current_month.nbr,current_day)
            daily_reading = conn.execute(sql)
            #print(daily_reading)
            reading_assignment = ReadingAssignment(daily_reading)
        
            md.write("| {} | {} |\n".format(current_day, reading_assignment.assignment))

        md.write("\n\n[back](./LifeJournal.md)")
        
        

conn.close()
    # That's all folks