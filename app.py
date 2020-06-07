from riotwatcher import LolWatcher, ApiError
import pandas as pd

print("Sistema de busca de partidas Ranqueadas. \nApenas para jogadores para o server Brasil")
chave = input("Entre com a chave de desenvolvedor: ")
nome_de_invocador = input("Entre com o nome de de Invocador: ")


api_key = chave
watcher = LolWatcher(api_key)
my_region = 'br1'

# check league's latest version
latest = watcher.data_dragon.versions_for_region(my_region)['n']['champion']

# Lets get some champions static information
static_champ_list = watcher.data_dragon.champions(latest, False, 'pt_BR')
static_spell_list = watcher.data_dragon.summoner_spells(latest, 'pt_BR')
static_item_list = watcher.data_dragon.items(latest, 'pt_BR')

# Criando um dicionario com o ID de cada item, champ, spell e seu nome em Portugues
# champ static list data to dict for looking up
champ_dict = {}
for key in static_champ_list['data']:
    row = static_champ_list['data'][key]
    champ_dict[row['key']] = row['name']

spell_dict = {}
for key in static_spell_list['data']:
    row = static_spell_list['data'][key]
    spell_dict[row['key']] = row['name']

item_dict = {}
for key in static_item_list['data']:
    row = static_item_list['data'][key]
    item_dict[row['image']['full'].split(".")[0]] = row['name']

# Pegando dados do usuario e de seus scores em ranked
me = watcher.summoner.by_name(my_region,nome_de_invocador)#"Judec")
my_ranked_stats = watcher.league.by_summoner(my_region,me['id'])
#print(me['accountId'])

choice = input("Entre com '1' para buscar as statisticas da última partida;\n 2 para buscar as statisticas da partida atual \n 3 para escolher outro nome de invocador \n 4 para sair do programa:  ")

while choice != '4':
    if choice == '3':
        nome_de_invocador = input("Entre com o nome de de Invocador: ")
        me = watcher.summoner.by_name(my_region, nome_de_invocador)  # "Judec")
        my_ranked_stats = watcher.league.by_summoner(my_region, me['id'])
    elif choice == '2':
        try:
            my_spectator = watcher.spectator.by_summoner(my_region, me['id'])

            participants_live = []
            for row in my_spectator['participants']:
                participants_row = {}
                participants_row['teamId'] = row['teamId']
                if row['teamId'] == 100:
                    participants_row['team'] = 'blue'
                else:
                    participants_row['team'] = 'red'

                participants_row['champion'] = row['championId']
                participants_row['spell1'] = row['spell1Id']
                participants_row['spell2'] = row['spell2Id']
                participants_live.append(participants_row)

            for row in participants_live:
                # Transformando o "Numero" do champ no nome dele em PT_BR
                row['champion'] = champ_dict[str(row['champion'])]
                row['spell1'] = spell_dict[str(row['spell1'])]
                row['spell2'] = spell_dict[str(row['spell2'])]
            df = pd.DataFrame(participants_live)
            pd.set_option("display.max_rows", None, "display.max_columns", None)
            print(df)
        except Exception:
          print("Esse Invocador não está em uma partida Ao Vivo no momento")

    elif choice == '1':
        # Historico de partidas desse usuario
        my_matches = watcher.match.matchlist_by_account(my_region,me['accountId'])

        # Pegando a Partida mais recente
        last_match = my_matches['matches'][0]
        match_detail = watcher.match.by_id(my_region, last_match['gameId'])

        participants_name = []
        participants  = []

        # Pegando informação do nome dos participantes e dos itens e spells usados na partida
        for row in match_detail['participantIdentities']:
            identities_row = {}
            identities_row['participantId'] = row['participantId']
            identities_row['summonerName'] = row['player']['summonerName']
            participants_name.append(identities_row)

        for row in match_detail['participants']:
            participants_row = {}
            participants_row['participantId'] = row['participantId']
            participants_row['teamId'] = row['teamId']
            if row['teamId'] == 100:
                participants_row['team'] = 'blue'
            else:
                participants_row['team'] = 'red'

            participants_row['champion'] = row['championId']
            participants_row['spell1'] = row['spell1Id']
            participants_row['spell2'] = row['spell2Id']
            participants_row['win'] = row['stats']['win']
            participants_row['kills'] = row['stats']['kills']
            participants_row['deaths'] = row['stats']['deaths']
            participants_row['assists'] = row['stats']['assists']
            participants_row['totalDamageDealt'] = row['stats']['totalDamageDealt']
            participants_row['goldEarned'] = row['stats']['goldEarned']
            participants_row['champLevel'] = row['stats']['champLevel']
            participants_row['totalMinionsKilled'] = row['stats']['totalMinionsKilled']
            participants_row['item0'] = row['stats']['item0']
            participants_row['item1'] = row['stats']['item1']
            participants_row['item2'] = row['stats']['item2']
            participants_row['item3'] = row['stats']['item3']
            participants_row['item4'] = row['stats']['item4']
            participants_row['item5'] = row['stats']['item5']
            participants.append(participants_row)

        for row in participants:
            for row_aux in participants_name:
                if row['participantId'] == row_aux['participantId']:
                    row['participantName'] = row_aux['summonerName']

        for row in participants:
            # Transformando o "Numero" do champ no nome dele em PT_BR
            row['champion'] = champ_dict[str(row['champion'])]
            row['spell1'] = spell_dict[str(row['spell1'])]
            row['spell2'] = spell_dict[str(row['spell2'])]
            if str(row['item0']) != '0':
                row['item0'] = item_dict[str(row['item0'])]
            if str(row['item1']) != '0':
                row['item1'] = item_dict[str(row['item1'])]
            if str(row['item2']) != '0':
                row['item2'] = item_dict[str(row['item2'])]
            if str(row['item3']) != '0':
                row['item3'] = item_dict[str(row['item3'])]
            if str(row['item4']) != '0':
                row['item4'] = item_dict[str(row['item4'])]
            if str(row['item5']) != '0':
                row['item5'] = item_dict[str(row['item5'])]

        #print(participants)
        df = pd.DataFrame(participants)
        pd.set_option("display.max_rows", None, "display.max_columns", None)
        print(df)

    choice = input("\nEntre com '1' para buscar as statisticas da última partida;\n 2 para buscar as statisticas da partida atual \n 3 para escolher outro nome de invocador \n 4 para sair do programa:  ")