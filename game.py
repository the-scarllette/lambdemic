from graphics import *
from city import City
from player import Player
from outbreak_tracker import OutbreakTracker
from citycard import CityCard

class Game:

    def __init__(self, window):
        self.__window = window
        self.__outbreak_tracker = OutbreakTracker(self.__window)
        self.__game_running = False

        atlanta = City("Atlanta", "blue", [], self.__window, 150, 200, self)
        san_francisco = City("San Francisco", "blue", [], self.__window, 50, 150, self)
        chicago = City("Chicago", "blue", [], self.__window, 150, 150, self)
        montreal = City("montreal", "blue", [], self.__window, 250, 150, self)
        washington = City("Washington", "blue", [], self.__window, 250, 200, self)
        new_york = City("New Work", "blue", [], self.__window, 300, 170, self)
        london = City("london", "blue", [], self.__window, 400, 150, self)
        essen = City("Essen", "blue", [], self.__window, 450, 150, self)
        st_petersburg = City("St Petersburg", "blue", [], self.__window, 500, 100, self)
        paris = City("Paris", "blue", [], self.__window, 400, 200, self)
        madrid = City("Madrid", "blue", [], self.__window, 330, 250, self)
        milan = City("Milan", "blue", [], self.__window, 450, 200, self)

        los_angeles = City("Los Angeles", "yellow", [], self.__window, 50, 200, self)
        mexico_city = City("Mexico City", "yellow", [], self.__window, 100, 250, self)
        miami = City("Miami", "yellow", [], self.__window, 260, 250, self)
        lima = City("Lima", "yellow", [], self.__window, 100, 300, self)
        bogota = City("Bogota", "yellow", [], self.__window, 200, 300, self)
        santiago = City("Santiago", "yellow", [], self.__window, 50, 350, self)
        buenos_aries = City("Buenos Aries", "yellow", [], self.__window, 150, 350, self)
        sao_paulo = City("Sao Paulo", "yellow", [], self.__window, 250, 350, self)
        lagos = City("Lagos", "yellow", [], self.__window, 400, 320, self)
        kinshasa = City("Kinsasha", "yellow", [], self.__window, 450, 350, self)
        johannesburg = City("Johannesburg", "yellow", [], self.__window, 480, 400, self)
        khartoum = City("Khartoum", "yellow", [], self.__window, 480, 310, self)

        algiers = City("Algiers", "black", [], self.__window, 410, 270, self)
        cairo = City("Cairo", "black", [], self.__window, 480, 270, self)
        istanbul = City("Istanbul", "black", [], self.__window, 480, 230, self)
        moscow = City("Moscow", "black", [], self.__window, 530, 180, self)
        baghdad = City("Baghdad", "black", [], self.__window, 550, 240, self)
        riyadh = City("Riyadh", "black", [], self.__window, 550, 290, self)
        tehran = City("Terhan", "black", [], self.__window, 590, 200, self)
        karachi = City("Karachi", "black", [], self.__window, 610, 260, self)
        mumbai = City("Mumbai", "black", [], self.__window, 620, 300, self)
        delhi = City("Delhi", "black", [], self.__window, 640, 220, self)
        chennai = City("Chennai", "black", [], self.__window, 670, 320, self)
        kolkata = City("Kolkata", "black", [], self.__window, 680, 250, self)

        beijing = City("Beijing", "red", [], self.__window, 730, 120, self)
        shanghai = City("Shanghai", "red", [], self.__window, 730, 170, self)
        hong_kong = City("Hong Kong", "red", [], self.__window, 740, 210, self)
        bangkok = City("Bangkok", "red", [], self.__window, 740, 270, self)
        jakarta = City("Kakarta", "red", [], self.__window, 730, 340, self)
        ho_chi_min = City("Ho Chi\nMin City", "red", [], self.__window, 800, 300, self)
        sydney = City("Sydney", "red", [], self.__window, 850, 400, self)
        manila = City("Manila", "red",[], self.__window, 850, 270, self)
        taipei = City("Taipei", "red", [], self.__window, 800, 200, self)
        osaka = City("Osaka", "red", [], self.__window, 850, 170, self)
        tokyo = City("Tokyo", "red", [], self.__window, 850, 130, self)
        seoul = City("Seoul", "red", [], self.__window, 800, 110, self)

        san_francisco.set_left_city(True)
        los_angeles.set_left_city(True)
        tokyo.set_right_city(True)
        manila.set_right_city(True)
        sydney.set_right_city(True)


        san_francisco.set_connected_cities([los_angeles, chicago, tokyo, manila])
        chicago.set_connected_cities([montreal, atlanta, mexico_city, los_angeles])
        montreal.set_connected_cities([new_york, washington, chicago])
        atlanta.set_connected_cities([chicago, washington, miami])
        washington.set_connected_cities([montreal, new_york, miami, atlanta])
        new_york.set_connected_cities([london, madrid, washington, montreal])
        london.set_connected_cities([essen, paris, madrid, new_york])
        essen.set_connected_cities([st_petersburg, milan, london])
        st_petersburg.set_connected_cities([moscow, istanbul, essen])
        paris.set_connected_cities([essen, milan, algiers, madrid, london])
        madrid.set_connected_cities([london, paris, sao_paulo, new_york])
        milan.set_connected_cities([istanbul, paris, essen])

        los_angeles.set_connected_cities([san_francisco, chicago, mexico_city, sydney])
        mexico_city.set_connected_cities([chicago, miami, bogota, lima, los_angeles])
        miami.set_connected_cities([washington, bogota, mexico_city, atlanta])
        lima.set_connected_cities([mexico_city, bogota, santiago])
        bogota.set_connected_cities([miami, sao_paulo, buenos_aries, lima, mexico_city])
        santiago.set_connected_cities([lima])
        buenos_aries.set_connected_cities([bogota, sao_paulo])
        sao_paulo.set_connected_cities([bogota, madrid, lagos, buenos_aries])
        lagos.set_connected_cities([khartoum, kinshasa, sao_paulo])
        kinshasa.set_connected_cities([lagos, khartoum, johannesburg])
        johannesburg.set_connected_cities([kinshasa, khartoum])
        khartoum.set_connected_cities([cairo, johannesburg, kinshasa, lagos])

        algiers.set_connected_cities([paris, istanbul, cairo, madrid])
        cairo.set_connected_cities([istanbul, baghdad, riyadh, khartoum, algiers])
        istanbul.set_connected_cities([st_petersburg, moscow, baghdad, cairo, algiers, milan])
        moscow.set_connected_cities([tehran, istanbul, st_petersburg])
        baghdad.set_connected_cities([tehran, karachi, riyadh, cairo, istanbul])
        riyadh.set_connected_cities([baghdad, karachi, cairo])
        tehran.set_connected_cities([moscow, delhi, karachi, baghdad])
        karachi.set_connected_cities([delhi, mumbai, riyadh, baghdad, tehran])
        mumbai.set_connected_cities([delhi, chennai, karachi])
        delhi.set_connected_cities([kolkata, chennai, mumbai, karachi, tehran])
        chennai.set_connected_cities([delhi, kolkata, bangkok, jakarta, mumbai])
        kolkata.set_connected_cities([hong_kong, bangkok, chennai, delhi])

        beijing.set_connected_cities([seoul, shanghai])
        shanghai.set_connected_cities([beijing, seoul, tokyo, taipei, hong_kong])
        hong_kong.set_connected_cities([shanghai, taipei, manila, ho_chi_min, bangkok, kolkata])
        bangkok.set_connected_cities([hong_kong, ho_chi_min, jakarta, chennai, kolkata])
        jakarta.set_connected_cities([bangkok, ho_chi_min, sydney, chennai])
        ho_chi_min.set_connected_cities([hong_kong, manila, jakarta, bangkok])
        sydney.set_connected_cities([manila, los_angeles])
        manila.set_connected_cities([taipei, san_francisco, sydney, ho_chi_min, hong_kong])
        osaka.set_connected_cities([tokyo, taipei])
        tokyo.set_connected_cities([san_francisco, osaka, shanghai, seoul])
        seoul.set_connected_cities([tokyo, shanghai, beijing])

        atlanta.set_has_res_station(True)


        self.__cities = [san_francisco,
                         chicago,
                         montreal,
                         atlanta,
                         washington,
                         new_york,
                         london,
                         essen,
                         st_petersburg,
                         paris,
                         madrid,
                         milan,
                         los_angeles,
                         mexico_city,
                         miami,
                         lima,
                         bogota,
                         santiago,
                         buenos_aries,
                         sao_paulo,
                         lagos,
                         kinshasa,
                         johannesburg,
                         khartoum,
                         algiers,
                         cairo,
                         istanbul,
                         moscow,
                         baghdad,
                         riyadh,
                         tehran,
                         karachi,
                         mumbai,
                         delhi,
                         chennai,
                         kolkata,
                         beijing,
                         shanghai,
                         hong_kong,
                         bangkok,
                         jakarta,
                         ho_chi_min,
                         sydney,
                         manila,
                         taipei,
                         osaka,
                         tokyo,
                         seoul]

        self.__player_1 = Player("player 1", self.__window, atlanta, "orange", 0)
        self.__player_2 = Player("player 2", self.__window, atlanta, "green", 5)
        self.__players = [self.__player_1, self.__player_2]

        self.__deck = []
        for city in self.__cities:
            self.__deck.append(CityCard(city))
        return

    def get_cities(self):
        return self.__cities

    def add_card_to_player(self, player):
        card_name = input("Enter the card to add to the hand of " + player.get_name() + ":\n")
        for card in self.__deck:
            if card.has_name(card_name):
                self.__deck.remove(card)
                player.add_to_hand(card)
                player.draw()
                return

        print("No matching card found in deck")

    def discard_card_from_player(self, player):
        card_name = input("Enter the card to discard from the hand of " + player.get_name() + ":\n")
        result = player.discard_card_by_name(card_name)
        if result:
            player.draw()
            return

        print("No matching card found in the hand of " + player.get_name())

    def draw_game(self):
        for city in self.__cities:
            city.draw_paths()
        for city in self.__cities:
            city.draw_city()
        for city in self.__cities:
            city.draw_cubes()

        for player in self.__players:
            player.draw()

        self.__outbreak_tracker.draw()
        return

    def edit_player_hand(self, player):
        choice = input("Add cards or discard cards from player hand:\n1/Add\n2:Discard\n")

        if choice == "1":
            self.add_card_to_player(player)
        elif choice == "2":
            self.discard_card_from_player(player)
        else:
            print("Invalid choice")

    def end_game(self):
        print("GAME OVER")
        self.__game_running = False

    def move_player(self, player_name, move_to):
        for player in self.__players:
            if player.has_name(player_name):
                player.set_city(move_to)
                break

    def run_game(self):
        self.__game_running = True

        while self.__game_running:
            try:
                click = self.__window.getMouse()
            except GraphicsError:
                break
            x = click.getX()
            y = click.getY()
            for city in self.__cities:
                if city.is_clicked(x, y):
                    city.click()
                    self.reset_outbreaks()
            for player in self.__players:
                if player.is_clicked(x, y):
                    self.edit_player_hand(player)

    def inc_outbreaks(self):
        self.__outbreak_tracker.inc_outbreaks()
        if self.__outbreak_tracker.get_outbreaks() >= 8:
            self.end_game()

    def reset_outbreaks(self):
        for city in self.__cities:
            city.set_has_outbreaked(False)