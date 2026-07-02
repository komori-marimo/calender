import csv
import os
import uuid  # ID生成用に追加
from datetime import datetime
from flask import Flask, flash, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = "pbl_calendar_secret_key"

CSV_FILE = "schedule_data.csv"


def init_csv():
    """CSVファイルが存在しない場合、ヘッダーを作成して初期化する"""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            # 編集・削除のために「id」を先頭に追加
            writer.writerow(["id", "title", "date", "time", "location", "memo"])


def load_schedules():
    """CSVファイルからすべての予定を読み込む"""
    init_csv()
    schedules = []
    with open(CSV_FILE, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 既存のCSVデータにidがない場合の互換性ケア
            if "id" not in row or not row["id"]:
                row["id"] = str(uuid.uuid4())
            schedules.append(row)

    try:
        schedules.sort(key=lambda x: (x["date"], x["time"]))
    except Exception:
        pass
    return schedules


def save_schedule(title, date, time, location, memo):
    """CSVファイルに新しい予定を追記する（新規登録）"""
    init_csv()
    new_id = str(uuid.uuid4())  # 一意のIDを生成
    with open(CSV_FILE, mode="a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([new_id, title, date, time, location, memo])


def update_schedule_file(schedules):
    """全予定リストを受け取り、CSVファイルを上書き保存する（ヘルパー関数）"""
    with open(CSV_FILE, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "title", "date", "time", "location", "memo"])
        for s in schedules:
            writer.writerow(
                [
                    s["id"],
                    s["title"],
                    s["date"],
                    s["time"],
                    s["location"],
                    s["memo"],
                ]
            )


# --- ルート定義 ---


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        date = request.form.get("date", "").strip()
        time = request.form.get("time", "").strip()
        location = request.form.get("location", "").strip()
        memo = request.form.get("memo", "").strip()

        # バリデーション
        if not title or not date:
            flash("エラー：予定名と日付は必須入力です。", "error")
            return redirect(url_for("index"))

        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            flash("エラー：日付の形式が不正です。", "error")
            return redirect(url_for("index"))

        try:
            save_schedule(title, date, time, location, memo)
            flash("予定を正常に登録しました！", "success")
        except Exception as e:
            flash(f"登録に失敗しました（システムエラー: {e}）", "error")

        return redirect(url_for("index"))

    schedules = load_schedules()
    return render_template("index.html", schedules=schedules)


@app.route("/edit/<string:id>", methods=["GET", "POST"])
def edit(id):
    """予定の編集画面・更新処理"""
    schedules = load_schedules()
    # 該当する予定を検索
    target_schedule = next((s for s in schedules if s["id"] == id), None)

    if not target_schedule:
        flash("エラー：指定された予定が見つかりません。", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        date = request.form.get("date", "").strip()
        time = request.form.get("time", "").strip()
        location = request.form.get("location", "").strip()
        memo = request.form.get("memo", "").strip()

        # バリデーション（新規登録と同じ基準）
        if not title or not date:
            flash("エラー：予定名と日付は必須入力です。", "error")
            return render_template("edit.html", schedule=target_schedule)

        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            flash("エラー：日付の形式が不正です。", "error")
            return render_template("edit.html", schedule=target_schedule)

        # データの更新
        target_schedule["title"] = title
        target_schedule["date"] = date
        target_schedule["time"] = time
        target_schedule["location"] = location
        target_schedule["memo"] = memo

        try:
            update_schedule_file(schedules)
            flash("予定を更新しました！", "success")
            return redirect(url_for("index"))
        except Exception as e:
            flash(f"更新に失敗しました（システムエラー: {e}）", "error")

    # GET時は編集画面を表示
    return render_template("edit.html", schedule=target_schedule)


@app.route("/delete/<string:id>", methods=["POST"])
def delete(id):
    """予定の削除処理（安全のためPOSTリクエストのみ受付）"""
    schedules = load_schedules()
    # 該当するIDを除外した新しいリストを作成
    filtered_schedules = [s for s in schedules if s["id"] != id]

    if len(schedules) == len(filtered_schedules):
        flash("エラー：削除対象の予定が見つかりませんでした。", "error")
        return redirect(url_for("index"))

    try:
        update_schedule_file(filtered_schedules)
        flash("予定を削除しました。", "success")
    except Exception as e:
        flash(f"削除に失敗しました（システムエラー: {e}）", "error")

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)