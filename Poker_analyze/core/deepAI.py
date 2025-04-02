import time


class Bot:
    def __init__(self):
        self.cards = ''  # 儲存機器人擁有的兩張手牌
        self.score = 0  # 儲存手牌評分（勝率）
        self.hand = ''  # 儲存手牌的描述


def probability_win(own_cards, n_players, common_cards=None):
    """
    計算擁有指定手牌的機器人在德州撲克中獲勝的機率。
    :param own_cards: 自己手中的兩張牌，例如['AS', 'KH']
    :param n_players: 總共參與遊戲的玩家數量
    :param common_cards: （可選）桌面上已經揭示的公共牌
    :return: 獲勝的機率以及平局的機率
    """
    import random  # 將random模組導入，用於隨機選取牌
    from game.poker_score import players_score  # 導入評分函數，計算玩家的手牌評分

    number_games = 1000  # 模擬遊戲的次數，用於估算獲勝機率
    n_win = 0  # 計算機器人贏得遊戲的次數
    n_tie = 0  # 計算機器人與其他玩家平局的次數
    ai = Bot()  # 創建機器人玩家
    ai.cards = own_cards  # 設置機器人的兩張手牌

    # 建立一副撲克牌（52張）
    deck = ['2C', '3C', '4C', '5C', '6C', '7C', '8C', '9C', 'TC', 'JC', 'QC', 'KC', 'AC',
            '2S', '3S', '4S', '5S', '6S', '7S', '8S', '9S', 'TS', 'JS', 'QS', 'KS', 'AS',
            '2H', '3H', '4H', '5H', '6H', '7H', '8H', '9H', 'TH', 'JH', 'QH', 'KH', 'AH',
            '2D', '3D', '4D', '5D', '6D', '7D', '8D', '9D', 'TD', 'JD', 'QD', 'KD', 'AD']

    # 從撲克牌中移除機器人手中的兩張牌
    [deck.remove(card) for card in ai.cards]

    # 如果桌面上已有公共牌，則也從撲克牌中移除這些牌
    if common_cards is not None:
        [deck.remove(card) for card in common_cards]

    # 創建與對手玩家數量相符的機器人
    list_bots = []
    for nbot in range(n_players - 1):
        list_bots.append(Bot())

    # 開始模擬遊戲
    for i in range(number_games):
        bot_deck = deck.copy()  # 每場遊戲重新洗牌，使用未被移除的牌

        # 隨機分配兩張手牌給每位對手玩家
        for bot in list_bots:
            bot.cards = random.sample(bot_deck, 2)  # 從剩下的牌中抽取兩張牌作為手牌
            [bot_deck.remove(bot.cards[i]) for i in range(2)]  # 將抽取的牌從牌堆中移除

        # 決定桌面上的公共牌，如果公共牌已經有部分揭示，則只抽取剩下的部分
        if common_cards is None:
            table = random.sample(bot_deck, 5)  # 沒有公共牌，隨機抽取五張作為公共牌
        else:
            table = common_cards + random.sample(bot_deck, 5 - len(common_cards))  # 補足五張公共牌

        # 計算每個玩家的手牌評分
        players_score(list_bots, table)  # 對所有對手計算手牌評分
        players_score([ai], table)  # 計算機器人玩家的手牌評分

        # 收集每個對手玩家的評分
        list_score = []
        for bot in list_bots:
            list_score.append(bot.score)

        # 比較機器人的評分與其他對手的評分
        if ai.score > max(list_score):  # 如果機器人的評分高於所有對手
            n_win += 1
        elif ai.score == max(list_score):  # 如果機器人的評分與最高的對手相同
            n_tie += 1

    # 返回機器人獲勝和平局的機率
    return n_win / number_games, n_tie / number_games
