import csv
import os
from datetime import datetime
from flask import Flask, flash, redirect, render_template, request, url_for

app = Flask(__name__)
# flashメッセージ（エラー表示など）を利用するためにシークレットキーを設定
app.secret_key = "pbl_calendar_secret_key"

# データベース（CSVファイル）のパス定義
CSV_FILE = "schedule_data.csv"


def init_csv():
    """CSVファイルが存在しない場合、ヘッダーを作成して初期化する（モデル層の初期化）"""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            # ヘッダー行を定義
            writer.writerow(["title", "date", "time", "location", "memo"])


def load_schedules():
    """CSVファイルからすべての予定を読み込む（モデル層のRead）"""
    init_csv()
    schedules = []
    with open(CSV_FILE, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            schedules.append(row)

    # 日付と時間順に並び替えておくと一覧が見やすくなります
    try:
        schedules.sort(key=lambda x: (x["date"], x["time"]))
    except Exception:
        pass
    return schedules


def save_schedule(title, date, time, location, memo):
    """CSVファイルに新しい予定を追記する（モデル層のCreate）"""
    init_csv()
    with open(CSV_FILE, mode="a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([title, date, time, location, memo])


@app.route("/", methods=["GET", "POST"])
def index():
    # --- [シーケンス図 2, 3] コントローラがリクエストを受け取る ---
    if request.method == "POST":
        # フォームデータの取得
        title = request.form.get("title", "").strip()
        date = request.form.get("date", "").strip()
        time = request.form.get("time", "").strip()
        location = request.form.get("location", "").strip()
        memo = request.form.get("memo", "").strip()

        # --- 方針4: ユーザ入力の検証（バリデーション） ---
        # 設計図の「入力エラー等による保存失敗」のルート
        if not title or not date:
            # 必須入力チェック
            flash("エラー：予定名と日付は必須入力です。", "error")
            # 設計図 8, 9: エラーメッセージを返却して再描画
            return redirect(url_for("index"))

        # 日付フォーマットの簡易検証
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            flash("エラー：日付の形式が不正です。", "error")
            return redirect(url_for("index"))

        # --- [シーケンス図 3, 4, 5] データの保存と成功レスポンス ---
        try:
            save_schedule(title, date, time, location, memo)
            flash("予定を正常に登録しました！", "success")
        except Exception as e:
            # 万が一のファイル書き込み失敗時
            flash(f"登録に失敗しました（システムエラー: {e}）", "error")

        return redirect(url_for("index"))

    # GETリクエスト時は一覧データを取得して画面を描画
    schedules = load_schedules()
    return render_template("index.html", schedules=schedules)


if __name__ == "__main__":
    # アプリケーションの起動
    app.run(debug=True, port=5000)