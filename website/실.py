
class Temp:
    def __init__(self, _time, _date):
        self.time = _time
        self.date = _date

    def __str__(self):
        return time + ":00 " + date + "요일"


time_list = ["09", "10", "11", "12", "13"]
date_list = ['월', '화', '수', '목', '금', '토', '일']

time_table = []
for time in time_list:
    second = []
    for date in date_list:
        a = Temp(time, date)
        second.append(a)
    time_table.append(second)

print(time_table[0][0])


n = 3
m = 4
a = [[0] * m for i in range(n)]
print(a)
