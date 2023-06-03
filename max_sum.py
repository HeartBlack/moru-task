data =  [3, -1, 2, -1,3,-4, 2]

max_value = data[0]
temp = 0
for i in data:
    if temp < 0:
        temp = 0            
    temp += i
    print("i",i)
    print("temp",temp)

    max_value = max(max_value, temp)
    print("max_val",max_value)
        
print(max_value)