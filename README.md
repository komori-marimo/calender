# calender

①目的
学生や社会人が予定を簡単に登録・管理できるようにし、予定を忘れたりスケジュールの重複を防ぐ。

②利用者
学生
社会人
主婦

利用場面
授業やバイトの予定管理
課題提出日の管理
会議やイベントの日程確認
友達との予定管理

③入力・出力
・入力
予定名
日付
時間
場所
メモ

・出力
カレンダー表示
当日の予定一覧
今後の予定一覧
通知・リマインダー

④主要機能
予定登録（Create）
予定閲覧（Read）
予定編集（Update）
予定削除（Delete）
リマインダー通知
CRUD対象データ
予定情報
タイトル
日時
場所
メモ

⑤非目標（今回は作らない機能）
他ユーザとの予定共有
チャット機能
AIによる予定自動作成
Googleカレンダー連携

⑥受け入れ基準
予定の登録ができる
登録した予定を一覧表示できる
予定の編集ができる
予定の削除ができる
日付ごとの予定を確認できる

ユースケース図
flowchart LR
    %% アクターの定義
    Student((学生))
    Worker((社会人))
    Homemaker((主婦))

    %% ユースケースの定義
    UC1[予定を登録する]
    UC2[予定一覧を表示する]
    UC3[予定を編集する]
    UC4[予定を削除する]
    UC5[日付ごとの予定を確認する]
    UC6[リマインダー通知を受け取る]

    %% 関係性の定義
    Student --> UC1
    Student --> UC2
    Student --> UC3
    Student --> UC4
    Student --> UC5

    Worker --> UC1
    Worker --> UC2
    Worker --> UC3
    Worker --> UC4
    Worker --> UC5
    Worker --> UC6

    Homemaker --> UC1
    Homemaker --> UC2
    Homemaker --> UC3
    Homemaker --> UC4
    Homemaker --> UC5

    クラス図
    classDiagram
    class User {
        +String userType
        +viewCalendar()
    }
    class Schedule {
        -int id
        -String title
        -Date date
        -Time time
        -String location
        -String memo
        +create()
        +read()
        +update()
        +delete()
    }
    class Notification {
        -int notificationId
        -Time alertTime
        +sendReminder()
    }

    User "1" --> "*" Schedule : 予定を管理する
    Schedule "1" --> "0..1" Notification : 通知を設定する
