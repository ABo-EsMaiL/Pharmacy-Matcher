import re

print("كو isolated:", bool(re.search(r'\b(كو|بلس|بلاس|كومب|co|plus|comp)\b', 'كونكور كو 5مجم')))
print("كو in word:", bool(re.search(r'\b(كو|بلس|بلاس|كومب|co|plus|comp)\b', 'كوفرسيل 5مجم')))
