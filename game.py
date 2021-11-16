from graphics import *
from city import City
from player import Player
from outbreak_tracker import OutbreakTracker
from citycard import CityCard
from nextturnbutton import NextTurnButton
from curetracker import CureTracker
from random import randint, choice
from deck import Deck


class Game:

    def __init__(self, window, mode, use_graphics, auto_run):
        self.__window = window
        self.__outbreak_tracker = OutbreakTracker(self.__window)
        self.__game_running = False
        self.__mode = mode
        self.__auto_run = auto_run

        self.__epidemics = 4
        self.__infection_rate_track = [2, 2, 2, 3, 3, 4, 4]
        self.__infection_rate_index = 0
        self.__infection_rate = self.__infection_rate_track[self.__infection_rate_index]

        atlanta = City("Atlanta", "blue", [], self.__window, 150, 200, self)
        san_francisco = City("San Francisco", "blue", [], self.__window, 50, 150, self)
        chicago = City("Chicago", "blue", [], self.__window, 150, 150, self)
        montreal = City("montreal", "blue", [], self.__window, 250, 150, self)
        washington = City("Washington", "blue", [], self.__window, 250, 200, self)
        new_york = City("New Work", "blue", [], self.__window, 300, 170, self)
        london = City("London", "blue", [], self.__window, 400, 150, self)
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
        jakarta = City("Jakarta", "red", [], self.__window, 730, 340, self)
        ho_chi_min = City("Ho Chi\nMin City", "red", [], self.__window, 800, 300, self)
        sydney = City("Sydney", "red", [], self.__window, 850, 400, self)
        manila = City("Manila", "red", [], self.__window, 850, 270, self)
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

        atlanta.set_has_res_station(True)
        self.__research_stations = [city for city in self.__cities if city.has_research_station()]

        self.__player_1 = Player("player 1", self.__window, atlanta, "orange", 0)
        self.__player_2 = Player("player 2", self.__window, atlanta, "green", 5)
        self.__players = [self.__player_1, self.__player_2]
        self.__current_turn = 0

        self.__next_turn_button = NextTurnButton(self.__window, 650, 400)

        self.__infection_deck = Deck(self.__window, 900, 10)
        self.__player_deck = Deck(self.__window, 10, 400)
        for city in self.__cities:
            self.__infection_deck.add_card(CityCard(city))
            self.__player_deck.add_card(CityCard(city))
        self.__infection_deck.shuffle()
        self.__player_deck.shuffle()

        self.colours = ["blue", "yellow", "black", "red"]
        self.__cure_trackers = [CureTracker(self.__window, self.colours[i], 20*(i+1), 10) for i in range(4)]

        self.setup_game()
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

    def cure_disease(self, colour):
        for tracker in self.__cure_trackers:
            if tracker.get_colour() == colour:
                tracker.set_cured(True)
                return

    def discard_card_from_player(self, player):
        card_name = input("Enter the card to discard from the hand of " + player.get_name() + ":\n")
        result = player.discard_card_by_name(card_name)
        if result:
            player.draw()
            return

        print("No matching card found in the hand of " + player.get_name())

    def discard_to_hand_limit(self, player):
        if self.__mode == "random":
            cards_in_hand = player.get_hand_size()
            removed_str = ""
            while cards_in_hand > 7:
                to_discard = choice(player.get_hand()).get_name()
                player.discard_card_by_name(to_discard)
                removed_str += (to_discard + " ")
                cards_in_hand -= 1
        print("Removed " + removed_str + "from " + player.get_name() + "'s hand")

    def draw_cures(self):
        for tracker in self.__cure_trackers:
            tracker.draw()
        return

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
        self.__next_turn_button.draw()
        self.draw_cures()
        return

    def edit_player_hand(self, player):
        choice = input("Add cards or discard cards from player hand:\n1/Add\n2:Discard\n")

        if choice == "1":
            self.add_card_to_player(player)
        elif choice == "2":
            self.discard_card_from_player(player)
        else:
            print("Invalid choice")

    def epidemic(self):
        self.__infection_rate_index += 1
        self.__infection_rate = self.__infection_rate_track[self.__infection_rate_index]
        card = self.__infection_deck.draw_bottom_card()
        city = self.find_city_by_name(card.get_name())
        for i in range(3):
            city.inc_cubes(city.get_colour())
        self.__infection_deck.discard_card(card)
        self.__infection_deck.restack_discard_pile()
        print(city.get_name() + " had an epidemic")

    def end_game(self):
        print("GAME OVER")
        self.__game_running = False

    def find_city_by_name(self, search_name):
        for city in self.__cities:
            if city.has_name(search_name):
                return city
        return -1

    def is_cured(self, colour):
        return colour in self.__cured

    def player_draw_cards(self, player):
        for i in range(2):
            card = self.__player_deck.draw_card()
            if card.is_epidemic:
                self.epidemic()
                continue
            player.add_to_hand(card)
            print("Gave " + player.get_name() + " " + card.get_name())
            player.draw()

    def next_turn(self):
        if self.__mode == 'random':
            print("Making random moves")
            for n in range(4):
                '''Chooses random number to determine what move to tak
                0 - Drive/Ferry
                1 - Direct Flight
                2 - Charter Flight
                3 - Shuttle Flight
                4 - Build Research Station
                5 - Treat Disease
                6 - Share Knowledge
                7 - Discover Cure
                if unable to take that action, repeats process until it can take an action'''
                move_made = False
                available_moves = [x for x in range(8)]
                acting_player = self.__players[self.__current_turn]
                cards = acting_player.get_hand()
                current_city = acting_player.get_city()
                while not move_made:
                    move = choice(available_moves)
                    if move == 0: # Drive/Ferry
                        new_city = choice(acting_player.get_connected_cities())
                        acting_player.move_to(new_city)
                        move_made = True
                        print("Moving " + acting_player.get_name() + " to " + new_city.get_name())
                    elif move == 1: # Direct Flight
                        if not cards:
                            available_moves.remove(1)
                            continue
                        card_to_use = choice(cards)
                        acting_player.discard_card_by_name(card_to_use.get_name())
                        acting_player.move_to(self.find_city_by_name(card_to_use.get_name()))
                        print("Direct flight of " + acting_player.get_name() + " to " + card_to_use.get_name())
                        move_made = True
                    elif move == 2: # Charter Flight
                        if not acting_player.is_city_in_hand():
                            available_moves.remove(2)
                            continue
                        acting_player.discard_card_by_name(acting_player.get_city_name())
                        acting_player.move_to(choice(self.__cities))
                        move_made = True
                        print("Charter flight of " + acting_player.get_name() + " to " + acting_player.get_city_name())
                    elif move == 3: # Shuttle Flight
                        if len(self.__research_stations) <= 1 or not current_city.has_research_station():
                            available_moves.remove(3)
                            continue
                        move_to = current_city
                        while move_to.equals(current_city):
                            move_to = choice(self.__research_stations)
                        acting_player.move_to(move_to)
                        move_made = True
                        print("Shuttle flight of " + acting_player.get_name() + " to " + acting_player.get_city_name())
                    elif move == 4: # Build Research Station
                        if current_city.has_research_station() or not acting_player.is_city_in_hand():
                            available_moves.remove(4)
                            continue
                        acting_player.discard_card_by_name(current_city.get_name())
                        current_city.set_has_res_station(True)
                        current_city.draw_city()
                        current_city.draw_cubes()
                        move_made = True
                        print("Research station built by " + acting_player.get_name() + " at " + current_city.get_name())
                    elif move == 5: # Treat Disease
                        colours = ["blue", "yellow", "black", "red"]
                        found_colour = False
                        while colours and not found_colour:
                            to_treat = choice(colours)
                            if current_city.get_cubes(to_treat) > 0:
                                found_colour = True
                            else:
                                colours.remove(to_treat)
                        if not found_colour:
                            available_moves.remove(5)
                            continue
                        current_city.dec_cubes(to_treat)
                        move_made = True
                        print("Treated " + to_treat + " by " + acting_player.get_name() + " at " + current_city.get_name())
                    elif move == 6: # Share Knowledge
                        other_player = self.__players[(self.__current_turn + 1) % len(self.__players)]
                        if current_city.equals(other_player.get_city()):
                            giving_player = -1
                            if acting_player.is_city_in_hand():
                                giving_player = acting_player
                                taking_player = other_player
                            elif other_player.is_city_in_hand():
                                giving_player = other_player
                                taking_player = acting_player
                            if giving_player != -1:
                                giving_player.remove_card_by_name(current_city.get_name())
                                taking_player.add_to_hand(CityCard(current_city))
                                giving_player.draw()
                                taking_player.draw()
                                move_made = True
                                continue
                        available_moves.remove(6)
                    elif move == 7: # Discover Cure
                        if not current_city.has_research_station():
                            available_moves.remove(7)
                            continue
                        colours = {"blue" : 0, "yellow" : 0, "black" : 0, "red" : 0}
                        found_colour = False
                        for card in cards:
                            colour = card.get_colour()
                            colours[colour] += 1
                            if colours[colour] >= 5:
                                if not self.is_cured(colour):
                                    found_colour = True
                                    break

                        if not found_colour:
                            available_moves.remove(7)
                            continue

                        self.cure_disease(colour)
                        self.draw_cures()
                        i = 1
                        while i <= 5:
                            to_discard = choice(cards)
                            if to_discard.get_colour() == colour:
                                acting_player.discard_card_by_name(to_discard.get_name())
                                i += 1
                        acting_player.draw()
                        move_made = True
                        print("Cured " + colour + " by " + acting_player.get_name())



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
            if self.__next_turn_button.is_clicked(x, y):
                for player in self.__players:
                    if player.get_hand_size() > 7:
                        self.discard_to_hand_limit(player)
                self.next_turn()
                self.player_draw_cards(self.__players[self.__current_turn])
                self.infect_cities()
                self.__current_turn = (self.__current_turn + 1) % len(self.__players)

    def inc_outbreaks(self):
        self.__outbreak_tracker.inc_outbreaks()
        if self.__outbreak_tracker.get_outbreaks() >= 8:
            self.end_game()

    def infect_cities(self):
        for i in range(self.__infection_rate):
            city = self.find_city_by_name(self.__infection_deck.draw_and_discard().get_name())
            city.inc_cubes(city.get_colour())
            print(city.get_name() + " infected")

    def is_cured(self, colour):
        for tracker in self.__cure_trackers:
            if tracker.get_colour() == colour:
                return tracker.is_cured()


    def reset_outbreaks(self):
        for city in self.__cities:
            city.set_has_outbreaked(False)

    def setup_game(self):
        #Placing initial cards
        for cubes_to_place in range(1, 4):
            for i in range(3):
                city = self.find_city_by_name(self.__infection_deck.draw_and_discard().get_name())
                for j in range(cubes_to_place):
                    city.inc_cubes(city.get_colour())
                print(city.get_name() + " has " + str(cubes_to_place) + " cubes")

        #Dealing cards to players
        for player in self.__players:
            for i in range(4):
                player.add_to_hand(self.__player_deck.draw_and_discard())

        #Shuffling in Epidemics
        self.__player_deck.add_epidemics(self.__epidemics)
        return
