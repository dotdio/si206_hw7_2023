# Your name: David Diokno
# Your student id: 381518141
# Your email: dadiokno
# List who you have worked with on this project: Andrei Mircea (amircea), Chris Lin (cwlinn), Matt Kish (mattkish)

import unittest
import sqlite3
import json
import os

def read_data(filename):
    full_path = os.path.join(os.path.dirname(__file__), filename)
    f = open(full_path)
    file_data = f.read()
    f.close()
    json_data = json.loads(file_data)
    return json_data

def open_database(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def make_positions_table(data, cur, conn):
    positions = []
    for player in data['squad']:
        position = player['position']
        if position not in positions:
            positions.append(position)
    cur.execute("CREATE TABLE IF NOT EXISTS Positions (id INTEGER PRIMARY KEY, position TEXT UNIQUE)")
    for i in range(len(positions)):
        cur.execute("INSERT OR IGNORE INTO Positions (id, position) VALUES (?,?)",(i, positions[i]))
    conn.commit()

## [TASK 1]: 25 points
# Finish the function make_players_table

#     This function takes 3 arguments: JSON data,
#         the database cursor, and the database connection object

#     It iterates through the JSON data to get a list of players in the squad
#     and loads them into a database table called 'Players'
#     with the following columns:
#         id ((datatype: int; Primary key) - note this comes from the JSON
#         name (datatype: text)
#         position_id (datatype: integer)
#         birthyear (datatype: int)
#         nationality (datatype: text)
#     To find the position_id for each player, you will have to look up 
#     the position in the Positions table we 
#     created for you -- see make_positions_table above for details.

def make_players_table(data, cur, conn):
    cur.execute("""DROP TABLE IF EXISTS Players""")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Players(
        id INTEGER PRIMARY KEY,
        name TEXT,
        position_id INTEGER,
        birthyear INTEGER,
        nationality TEXT,
        FOREIGN KEY (position_id) REFERENCES Positions (id)
    )
    """)
    conn.commit()

    for player in data['squad']:
        player_id = player['id']
        name = player['name']
        position = player['position']
        birthyear = int(player['dateOfBirth'][:4])
        nationality = player['nationality']

        cur.execute ("SELECT id FROM Positions WHERE position = ?", (position,))
        position_id = cur.fetchone()[0]

        cur.execute("""
            INSERT OR IGNORE INTO Players (id, name, position_id, birthyear, nationality) VALUES (?, ?, ?, ?, ?)
        """, (player_id, name, position_id, birthyear, nationality)
        )
    conn.commit()

## [TASK 2]: 10 points
# Finish the function nationality_search

    # This function takes 3 arguments as input: a list of countries,
    # the database cursor, and database connection object. 
 
    # It selects all the players from any of the countries in the list
    # and returns a list of tuples. Each tuple contains:
        # the player's name, their position_id, and their nationality.

def nationality_search(countries, cur, conn):
    placeholders = ','.join(['?' for _ in countries])

    cur.execute(f"""
        SELECT name, position_id, nationality
        FROM Players
        WHERE nationality IN ({placeholders})
    """, tuple(countries)
    )

    result = cur.fetchall()
    return result

## [TASK 3]: 10 points
# finish the function birthyear_nationality_search

#     This function takes 4 arguments as input: 
#     an age in years (int), 
#     a country (string), the database cursor, 
#     and the database connection object.

#     It selects all the players from the country passed to the function 
#     that were born BEFORE (2023 minus the year passed)
#     for example: if we pass 19 for the year, it should return 
#     players with birthdates BEFORE 2004
#     This function returns a list of tuples each containing 
#     the player’s name, nationality, and birth year. 


def birthyear_nationality_search(age, country, cur, conn):
    birthyear_threshold = 2023-age

    cur.execute("""
        SELECT name, nationality, birthyear
        FROM Players
        WHERE nationality = ? AND birthyear < ?
    """, (country, birthyear_threshold)
    )

    result = cur.fetchall()
    return result

## [TASK 4]: 15 points
# finish the function position_birth_search

    # This function takes 4 arguments as input: 
    # a position (string), 
    # age (int), the database cursor,
    # and the database connection object. 

    # It selects all the players who play the position
    #  passed to the function and
    # that were born AFTER (2023 minus the year passed)
    # for example: if we pass 19 for the year, it should return 
    # players with birth years AFTER 2004
    # This function returns a list of tuples each containing 
    # the player’s name, position, and birth year. 
    # HINT: You'll have to use JOIN for this task.

def position_birth_search(position, age, cur, conn):
       birthyear_threshold = 2023 - age

       cur.execute("""
       SELECT Players.name, Positions.position, Players.birthyear
       FROM Players
       JOIN Positions ON Players.position_id = Positions.id
       WHERE Positions.position = ? AND Players.birthyear > ?
       """, (position, birthyear_threshold)
       )

       result = cur.fetchall()
       return result



# [EXTRA CREDIT]
# You’ll make 3 new functions, make_winners_table(), make_seasons_table(),
# and winners_since_search(), 
# and then write at least 2 meaningful test cases for each of them. 

#     The first function takes 3 arguments: JSON data, 
#     the database cursor, and the database connection object.
#     It makes a table with 2 columns:
#         id (datatype: int; Primary key) -- note this comes from the JSON
#         name (datatype: text) -- note: use the full, not short, name
#     hint: look at how we made the Positions table above for an example

#     The second function takes the same 3 arguments: JSON data, 
#     the database cursor, and the database connection object. 
#     It iterates through the JSON data to get info 
#     about previous Premier League seasons (don't include the current one)
#     and loads all of the seasons into a database table 
#     called ‘Seasons' with the following columns:
#         id (datatype: int; Primary key) - note this comes from the JSON
#         winner_id (datatype: text)
#         end_year (datatype: int)
#     NOTE: Skip seasons with no winner!

#     To find the winner_id for each season, you will have to 
#     look up the winner's name in the Winners table
#     see make_winners_table above for details
    
#     The third function takes in a year (string), the database cursor, 
#     and the database connection object. It returns a dictionary of how many 
#     times each team has won the Premier League since the passed year.
#     In the dict, each winning team's (full) name is a key,
#     and the value associated with each team is the number of times
#     they have won since the year passed, including the season that ended
#     the passed year. 

def make_winners_table(data, cur, conn):
    cur.execute("""DROP TABLE IF EXISTS Winners""")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Winners(
        id INTEGER PRIMARY KEY,
        name TEXT
    )
    """)
    for  val in data['seasons']:
        if val['winner']:
            cur.execute("""
                INSERT OR IGNORE INTO Winners (id, name)
                VALUES (?,?)
            """, (val['winner']['id'], val['winner']['name']))
    conn.commit()
    
def make_seasons_table(data, cur, conn):
    cur.execute("""DROP TABLE IF EXISTS seasons""")
    cur.execute("CREATE TABLE IF NOT EXISTS seasons (id INTEGER PRIMARY KEY, winner_id TEXT, end_year INTEGER)")
    s = []
    ind = 0
    for season in data['seasons']:
        if ind == 0:
            ind += 1
            continue
        id = season['id']
        winner = season['winner']
        if not winner:
            continue
        winner_id = winner['id']
        end_year = season['endDate'][0:4]
        s.append((id, winner_id, end_year))
    for i in range(len(s)):
        cur.execute("INSERT OR IGNORE INTO seasons (id, winner_id, end_year) VALUES (?,?,?)",(s[i][0], s[i][1], s[i][2]))
    conn.commit()

def winners_since_search(year, cur, conn):
    cur.execute("""
        SELECT Seasons.end_year, Winners.name FROM Seasons
        JOIN Winners ON Seasons.winner_id = Winners.id
        WHERE Seasons.end_year >= ?
    """, (year,))

    res = {}
    data = cur.fetchall()

    for val in data:
        res[val[1]] = res.get(val[1], 0) + 1
    conn.commit()
    return res

class TestAllMethods(unittest.TestCase):
    def setUp(self):
        path = os.path.dirname(os.path.abspath(__file__))
        self.conn = sqlite3.connect(path+'/'+'Football.db')
        self.cur = self.conn.cursor()
        self.conn2 = sqlite3.connect(path+'/'+'Football_seasons.db')
        self.cur2 = self.conn2.cursor()

    def test_players_table(self):
        self.cur.execute('SELECT * from Players')
        players_list = self.cur.fetchall()

        self.assertEqual(len(players_list), 30)
        self.assertEqual(len(players_list[0]),5)
        self.assertIs(type(players_list[0][0]), int)
        self.assertIs(type(players_list[0][1]), str)
        self.assertIs(type(players_list[0][2]), int)
        self.assertIs(type(players_list[0][3]), int)
        self.assertIs(type(players_list[0][4]), str)

    def test_nationality_search(self):
        x = sorted(nationality_search(['England'], self.cur, self.conn))
        self.assertEqual(len(x), 11)
        self.assertEqual(len(x[0]), 3)
        self.assertEqual(x[0][0], "Aaron Wan-Bissaka")

        y = sorted(nationality_search(['Brazil'], self.cur, self.conn))
        self.assertEqual(len(y), 3)
        self.assertEqual(y[2],('Fred', 2, 'Brazil'))
        self.assertEqual(y[0][1], 3)

    def test_birthyear_nationality_search(self):

        a = birthyear_nationality_search(24, 'England', self.cur, self.conn)
        self.assertEqual(len(a), 7)
        self.assertEqual(a[0][1], 'England')
        self.assertEqual(a[3][2], 1992)
        self.assertEqual(len(a[1]), 3)

    def test_type_speed_defense_search(self):
        b = sorted(position_birth_search('Goalkeeper', 35, self.cur, self.conn))
        self.assertEqual(len(b), 2)
        self.assertEqual(type(b[0][0]), str)
        self.assertEqual(type(b[1][1]), str)
        self.assertEqual(len(b[1]), 3) 
        self.assertEqual(b[1], ('Jack Butland', 'Goalkeeper', 1993)) 

        c = sorted(position_birth_search("Defence", 23, self.cur, self.conn))
        self.assertEqual(len(c), 1)
        self.assertEqual(c, [('Teden Mengi', 'Defence', 2002)])
    
    # test extra credit
    def test_make_winners_table(self):
        self.cur2.execute('SELECT * from Winners')
        winners_list = self.cur2.fetchall()
        self.assertEqual(len(winners_list), 7)
        self.assertEqual(winners_list[0][1], 'Arsenal FC')

    def test_make_seasons_table(self):
        self.cur2.execute('SELECT * from Seasons')
        seasons_list = self.cur2.fetchall()
        self.assertEqual(len(seasons_list), 28)
        self.assertEqual(seasons_list[0][1], '65')

    def test_winners_since_search(self):
        r = winners_since_search(1990, self.cur2, self.conn2)
        self.assertEqual(len(r),  7)
        self.assertEqual(r['Manchester United FC'], 12)


def main():

    #### FEEL FREE TO USE THIS SPACE TO TEST OUT YOUR FUNCTIONS

    json_data = read_data('football.json')
    cur, conn = open_database('Football.db')
    make_positions_table(json_data, cur, conn)
    make_players_table(json_data, cur, conn)
    conn.close()


    seasons_json_data = read_data('football_PL.json')
    cur2, conn2 = open_database('Football_seasons.db')
    make_winners_table(seasons_json_data, cur2, conn2)
    make_seasons_table(seasons_json_data, cur2, conn2)
    conn2.close()


if __name__ == "__main__":
    main()
    unittest.main(verbosity = 2)
