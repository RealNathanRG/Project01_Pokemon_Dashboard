from web_scraping import *
import sqlite3

conn = sqlite3.connect("Pokemon.db")
cur = conn.cursor()

stats = pd.DataFrame(stats_table(6))
print(stats.columns)

# Import stats table
stats.to_sql("stats.gen6", conn, if_exists="replace")
# df = pd.DataFrame({'id': [100, 101, 102, 103], 'name': ['Tom', 'Jerry', 'Sooty', 'Sweep']})
attributes = stats[["id", "Pokémon", "form_name"]]
attributes["mega"] = np.where(attributes["form_name"].str.contains("Mega|Primal"), 1, 0)
attributes["alt_form"] = np.where(attributes["form_name"] == attributes["Pokémon"], 0, 1)
attributes["catch_rate"] = attributes["Pokémon"].apply(get_catch_rate)

print(attributes)
#
# for index, row in attributes.iterrows():
#     if any(word in row["form_name"] for word in["Mega", "Primal"]):
#         mega[index] = 1
#     else:
#         mega[index] = 0




