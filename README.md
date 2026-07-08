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

## 設計図一覧

### 1. ユースケース図
アクター（利用者）と、アプリの主要な機能（ユースケース）の関係性を表した図です。

```mermaid
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
---
```mermaid
classDiagram
    class SystemUser {
        +userType
        +viewCalendar()
    }
    class Schedule {
        -id
        -title
        -date
        -time
        -location
        -memo
        +create()
        +read()
        +update()
        +delete()
    }
    class Notification {
        -notificationId
        -alertTime
        +sendReminder()
    }

    SystemUser "1" --> "*" Schedule : 予定を管理する
    Schedule "1" --> "0..1" Notification : 通知を設定する
---

```mermaid
sequenceDiagram
    autonumber
    actor User as 利用者
    participant UI as 画面 (カレンダーUI)
    participant Ctrl as コントローラ (処理)
    participant DB as モデル (データベース)

    User->>UI: 予定情報を入力して「登録」ボタンをクリック
    Note over User,UI: 入力: 予定名, 日付, 時間, 場所, メモ
    UI->>Ctrl: 予定登録リクエスト送信
    Ctrl->>DB: 予定データを保存 (Create)
    
    alt 保存成功
        DB-->>Ctrl: 成功レスポンス
        Ctrl-->>UI: 登録完了通知 ＆ 画面再描画
        UI-->>User: カレンダーに予定が表示される
    else 入力エラー等による保存失敗
        DB-->>Ctrl: 失敗レスポンス
        Ctrl-->>UI: エラーメッセージ返却
        UI-->>User: 「登録に失敗しました」と表示
    endstateDiagram-v2
---
```mermaid
    [*] --> 未登録 : 予定の計画

    未登録 --> 登録済み : 予定を登録する (Create)
    
    状態: 登録済み
    登録済み --> 登録済み : 予定を編集する (Update)
    
    %% 当日・リマインダー通知のトリガー
    登録済み --> 通知済み : 予定の時刻になる / リマインダー発生
    通知済み --> 登録済み : 通知を確認する
    
    登録済み --> [*] : 予定を削除する (Delete)
    通知済み --> [*] : 予定を削除する (Delete)
    登録済み --> [*] : 予定を削除する (Delete)
    通知済み --> [*] : 予定を削除する (Delete)
---
