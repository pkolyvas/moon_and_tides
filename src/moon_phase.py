with open('moon_sample.json') as user_file:
    moons = user_file.read()

moon_data = json.loads(moons)

cursor = connection.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS current_moon (phase REAL, timestamp TEXT)")



def set_mask_position(phase):
    steps = 200
    position = phase * steps
    return int(position)

print("Current phase: "+str(moon_data["moon"]["phase"])) 
print("Days until next new moon: "+str(moon_data["moon_phases"]["new_moon"]["next"]["days_ahead"]))
print("Steps to set moon mask: "+str(set_mask_position(float(moon_data["moon"]["phase"]))))