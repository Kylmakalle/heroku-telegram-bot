import Main_classes
import threading
import utils
import telebot
import config


types = telebot.types
bot = telebot.TeleBot(config.token)

# Инициировать игру в чате
def start_game(gametype, cid):

    game = Main_classes.Game(cid)
    Main_classes.existing_games[cid] = game
    game.gamestate = game.gamestates[0]
    game.gametype = game.gametypes[gametype]
    game.waitingtimer = threading.Timer(300, cancel_game, [game])
    game.waitingtimer.start()


# Удалить игру в чате
def cancel_game(game):
    utils.delete_game(game)
    bot.send_message(game.cid, "Игра отменена.")


# Закончить набор игроков и начать сражение
def start_fight(cid):
    game = Main_classes.existing_games[cid]
    game.waitingtimer.cancel()
    game.gamestate = game.gamestates[1]
    game.waitingtimer.cancel()
    t = threading.Thread(target=utils.prepare_fight, args=[game])
    t.daemon = True
    t.start()