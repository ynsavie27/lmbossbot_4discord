import json
from collections import OrderedDict

# ボスマスタJSONファイルを読み込み
with open('./boss_mst.json', 'r', encoding='utf-8') as f:
    boss_mst = json.load(f, object_pairs_hook=OrderedDict)

### ボスマスタレイアウト
# boss_mst[ボスIDのテキスト]={
#     'intvl_min':分数,
#     'pop_time':時刻'YYMM'のリスト,
#     'duration_min':分数,
#     'pop_rate':数値(0-100%),
#     'pop_place':テキスト,
#     'name':ボス名のリスト,
#     'note':テキスト,
#     'disable_flg':数値(0以外なら無効)
# }

# ボス名からボスID取得用変数を生成
# key:ボス名、値:ボスIDの辞書
# boss_name2id = {}
for bid in boss_mst.keys():
    int_h = int(boss_mst[bid].get('intvl_min') / 60)
    pop_ran = ''
    if boss_mst[bid].get('pop_rate') < 100:
        pop_ran = '(ランダム)'
    bname_list = boss_mst[bid].get('name')
    ptext = ''
    for bname in bname_list:
        ptext += bname + ','
    ptext += ':' + str(int_h) + 'h' + pop_ran
    ptext += ':' + boss_mst[bid].get('pop_place')
    print(ptext)
