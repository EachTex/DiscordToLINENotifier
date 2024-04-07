# DiscordToLINENotifier
DiscordからLINE Notifyにリマインドを送信するプログラムです。

# Notes:
現行の開発/実装環境は最新のバージョンではないものを使用しています。  
これらのコードを使用することは問題ありませんが、  
各人のプログラムに組み込む際は、最新のバージョンに合わせてコードを変更してください。
### Requirements.txt
```py
discord.py==2.0.1
py-cord==2.5.0
```

# Usage:
[ソースコード](https://github.com/EachTex/DiscordToLINENotifier/blob/main/main.py)をCogsフォルダに追加し、  
コード内の "channel_id" を通知先Discordチャンネル(※)のIDに指定してください。
また、カレントディレクトリ内に  
- "remind_line.json" (\*LINE Notifyのトークンを保存するファイル) と  
- "remind.json" (\*リマインドの内容を保存するファイル)  
を作成してください。  
  
※: LINE Notifyを使用しない場合に使用します。
