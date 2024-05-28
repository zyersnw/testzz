from django.shortcuts import render
from django.conf import settings
import requests
from urllib.parse import quote

API_KEY = settings.RIOT_API_KEY

def get_summoner_id(api_key, summoner_name):
    summoner_name_encoded = quote(summoner_name)
    url = f'https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name_encoded}'
    response = requests.get(url, headers={'X-Riot-Token': api_key})
    response.raise_for_status()
    return response.json().get('id')

def get_recent_matchlist(api_key, summoner_id):
    url = f'https://kr.api.riotgames.com/lol/match/v4/matchlists/by-account/{summoner_id}'
    response = requests.get(url, headers={'X-Riot-Token': api_key})
    response.raise_for_status()
    return response.json().get('matches', [])

def get_match_details(api_key, match_id):
    url = f'https://kr.api.riotgames.com/lol/match/v4/matches/{match_id}'
    response = requests.get(url, headers={'X-Riot-Token': api_key})
    response.raise_for_status()
    return response.json()

def calculate_troll_score(participant_stats, team_stats, match_details):
    kda = (participant_stats['kills'] + participant_stats['assists']) / (participant_stats['deaths'] or 1)
    cs = participant_stats['totalMinionsKilled'] + participant_stats.get('neutralMinionsKilled', 0)
    gold = participant_stats['goldEarned']
    damage = participant_stats['totalDamageDealtToChampions']
    vision_score = participant_stats.get('visionScore', 0)
    objective_score = participant_stats.get('dragonKills', 0) + participant_stats.get('baronKills', 0) + participant_stats.get('towerKills', 0)
    
    inappropriate_items = 0
    for item in range(0, 7):
        item_id = participant_stats.get(f'item{item}', 0)
        # 아이템 적합성 평가 로직 추가 필요

    avg_kda = sum([(p['kills'] + p['assists']) / (p['deaths'] or 1) for p in team_stats]) / len(team_stats)
    avg_cs = sum([p['totalMinionsKilled'] + p.get('neutralMinionsKilled', 0) for p in team_stats]) / len(team_stats)
    avg_gold = sum([p['goldEarned'] for p in team_stats]) / len(team_stats)
    avg_damage = sum([p['totalDamageDealtToChampions'] for p in team_stats]) / len(team_stats)
    avg_vision = sum([p.get('visionScore', 0) for p in team_stats]) / len(team_stats)
    avg_objectives = sum([p.get('dragonKills', 0) + p.get('baronKills', 0) + p.get('towerKills', 0) for p in team_stats]) / len(team_stats)

    score = 0
    if kda < avg_kda * 0.5:
        score += 15
    if cs < avg_cs * 0.5:
        score += 10
    if gold < avg_gold * 0.5:
        score += 15
    if damage < avg_damage * 0.5:
        score += 20
    if vision_score < avg_vision * 0.5:
        score += 10
    if objective_score < avg_objectives * 0.5:
        score += 20
    if inappropriate_items > 2:
        score += 20
    
    if participant_stats.get('timeSpentDead', 0) / match_details['gameDuration'] > 0.3:
        score += 20

    return score

def troll_identifier(request):
    if request.method == 'POST':
        summoner_name = request.POST.get('summoner_name')
        try:
            summoner_id = get_summoner_id(API_KEY, summoner_name)
            matchlist = get_recent_matchlist(API_KEY, summoner_id)
            if not matchlist:
                message = "매치 리스트를 가져올 수 없습니다."
                return render(request, 'troll_result.html', {'message': message})
            recent_match_id = matchlist[0]['gameId']
            match_details = get_match_details(API_KEY, recent_match_id)
            participant_id = next(p['participantId'] for p in match_details['participantIdentities'] if p['player']['summonerId'] == summoner_id)
            participant_stats = next(p['stats'] for p in match_details['participants'] if p['participantId'] == participant_id)
            team_stats = [p['stats'] for p in match_details['participants'] if p['teamId'] == participant_stats['teamId']]
            troll_score = calculate_troll_score(participant_stats, team_stats, match_details)
            if troll_score >= 50:
                result_message = f"{summoner_name} 님은 트롤일 가능성이 높습니다."
            else:
                result_message = f"{summoner_name} 님은 트롤이 아닙니다."
            return render(request, 'troll_result.html', {'result_message': result_message})
        except requests.exceptions.RequestException as e:
            error_message = f"API 요청 중 오류 발생: {e}"
            return render(request, 'troll_result.html', {'error_message': error_message})
        except KeyError as e:
            error_message = f"응답 데이터에 필요한 키가 없습니다: {e}"
            return render(request, 'troll_result.html', {'error_message': error_message})
    else:
        return render(request, 'troll_identifier_form.html')
