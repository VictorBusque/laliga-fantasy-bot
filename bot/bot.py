import telebot
from telebot.types import Message
from telebot import types
from dotenv import load_dotenv
from os import getenv
from bot.user import User
from fantasy_api.database import FantasyDatabase
from fantasy_api.models.player_model import FantasyPlayer, position_id_to_name
from fantasy_api.models.lineup_model import pos_to_acronym
from fantasy_api.laliga_api import LaLigaFantasyAPI
from random import choice
import logging
from markdownTable import markdownTable

load_dotenv()
BOT_TOKEN = getenv("TELEGRAM_TOKEN")
logging.info(f"Using Telegram Token: {BOT_TOKEN}")
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['random'])
def send_random_player(message: Message):
	players = LaLigaFantasyAPI().get_all_players()
	ids = list(players.keys())
	random_player_id = choice(ids)
	player = players.get(random_player_id)
	response = f"Tu jugador aleatorio es:\n{player.__describe__()}"
	bot.reply_to(message, response, parse_mode="Markdown")

@bot.message_handler(commands=['top_player'])
def send_top_player(message: Message):
	players = LaLigaFantasyAPI().get_all_players()
	players_list = list(players.values())
	players_list.sort(key=lambda p: p.points, reverse=True)
	player = players_list[0]
	response = f"El jugador TOP del campeonato es:\n{player.__describe__()}"
	bot.reply_to(message, response, parse_mode="Markdown")

@bot.message_handler(commands=['top_players'])
def send_top_players(message: Message):
	if len(message.text.split()) == 2 and message.text.split()[1].isdigit():
		top_n = int(message.text.split()[1])
	else:
		top_n = 10
	players = LaLigaFantasyAPI().get_all_players()
	players_list = list(players.values())
	players_list.sort(key=lambda p: p.points, reverse=True)
	players = players_list[:top_n]
	player_info = [{
			"Jugador": player.nickname,
			"Pos": pos_to_acronym.get(position_id_to_name.get(player.positionId).title()),
			"Equipo": player.team.get_shortname(),
			"Puntos": player.points,
   			"Link": f"/p{player.id}"
		} for player in players]
	player_info.sort(key = lambda p: p.get("Puntos"), reverse=True)
	response = markdownTable(player_info).setParams(row_sep = 'always', padding_width = 2, padding_weight = 'centerright').getMarkdown()
	bot.reply_to(message, response, parse_mode="Markdown")

@bot.message_handler(commands=['login'])
def handle_login(message: Message):
	# Expecting message like "/login {team_id} {league_id} {bearer_token}"
	n_args = len(message.text.split())
	if n_args == 4:
		user_team_id = message.text.split()[1]
		user_league_id = message.text.split()[2]
		bearer_token = message.text.split()[3]
		telegram_user_id = message.from_user.id
		user = User(telegram_user_id=telegram_user_id,
					team_id=user_team_id,
					league_id=user_league_id,
					bearer_token=bearer_token)
		lineup = LaLigaFantasyAPI().get_week_results(user)
		user.live_updates_active=True
		user.last_update=lineup
		user.last_update_week=LaLigaFantasyAPI().get_curr_week()
		user.save_or_update()
		bot.reply_to(message, "Perfecto, te he dado de alta en el bot. Puedes usar comandos personalizados para tu equipo.", parse_mode="Markdown")
	else:
		bot.reply_to(message, "Ha habido un error. Esperaba un mensaje siguiendo el formato:\n '/login <team_id> <league_id> <bearer_token>")
  
@bot.message_handler(commands=['week'])
def handle_week(message: Message):
	telegram_user_id = message.from_user.id
	if len(message.text.split()) == 2 and message.text.split()[1].isdigit():
		week_num = int(message.text.split()[1])
	else:
		week_num = None
	try:
		user = User.from_telegram_id(telegram_user_id)
	except:
		bot.reply_to(message, "No est??s identificado. Usa /login para identificarte.")
		return
	week_results = LaLigaFantasyAPI().get_week_results(user, week_num)
	responses = week_results.describe_points()
	for response in responses:
		bot.reply_to(message, response, parse_mode="Markdown")
  
@bot.message_handler(commands=['search'])
def send_search_player(message: Message):
	n_args = len(message.text.split())
	if n_args == 1:
		pass
	if n_args >= 2:
		player_name = ' '.join(message.text.split()[1:]).split(",")[0].strip()
		try:
			team_name = ' '.join(message.text.split()[1:]).split(",")[1].strip()
		except:
			team_name = None
	player_data = LaLigaFantasyAPI().get_all_players()
	players = FantasyDatabase(player_data).get_closest_players(player_name, team_name, 5)
	player_info = [{
			"Jugador": player.nickname,
			"Pos": pos_to_acronym.get(position_id_to_name.get(player.positionId).title()),
			"Equipo": player.team.get_shortname(),
			"Puntos": player.points,
   			"Link": f"/p{player.id}"
		} for player in players]
	if player_info:
		response = markdownTable(player_info).setParams(row_sep = 'always', padding_width = 2, padding_weight = 'centerright').getMarkdown()
	else:
		response = "No he encontrado jugadores que coincidan."
	bot.reply_to(message, response, parse_mode="Markdown")
	
@bot.message_handler(commands=['team'])
def send_team_lineup(message: Message):
	n_args = len(message.text.split())
	if n_args == 1:
		pass
	if n_args >= 2:
		team_name = ' '.join(message.text.split()[1:]).strip()

	player_data = LaLigaFantasyAPI().get_all_players()
	fdb = FantasyDatabase(player_data)
	team_ids = fdb.get_closest_teams(team_name)
	if team_ids:
		players = fdb.get_players_from_team(team_ids[0].id)
		player_info = [{
				"Jugador": player.nickname,
				"Pos": pos_to_acronym.get(position_id_to_name.get(player.positionId).title()),
				"Puntos": player.points
			} for player in players]
		player_info.sort(key = lambda p: p.get("Puntos"), reverse=True)
		if player_info:
			response = markdownTable(player_info).setParams(row_sep = 'always', padding_width = 2, padding_weight = 'centerright').getMarkdown()
	else:
		response = "No he encontrado el equipo que mencionas."
	bot.reply_to(message, response, parse_mode="Markdown")

@bot.message_handler(regexp="/p[0-9]+")
def send_custom_player(message: Message):
	player_id = message.text[2:]
	player: FantasyPlayer = LaLigaFantasyAPI().get_all_players().get(player_id)
	if not player:
		response = "No existe el jugador indicado."
	else:
		response = player.__describe__()
	bot.reply_to(message, response, parse_mode="Markdown")
 
 
@bot.message_handler(commands=['updates'])
def activate_deactivate_updates(message: Message):
	user = User.from_telegram_id(message.from_user.id)
	if len(message.text.split()) < 2:
		adj = "activadas" if user.live_updates_active else "desactivadas"
		response = f"Las actualizaciones en directo est??n {adj}."
	else:
		state = message.text.split()[1].lower()
		if state == "on":
			if user.live_updates_active:
				response = "Ya ten??as las actualizaciones en directo activadas."
			else:
				user.live_updates_active = True
				user.save_or_update()
				response = "Acabas de activar las actualizaciones en directo."
		elif state == "off":
			if not user.live_updates_active:
				response = "Ya ten??as las actualizaciones en directo desactivadas."
			else:
				user.live_updates_active = False
				user.save_or_update()
				response = "Acabas de desactivar las actualizaciones en directo."
	bot.reply_to(message, response, parse_mode="Markdown")