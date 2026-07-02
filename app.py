import csv
import os
import uuid
from datetime import datetime
from flask import Flask, flash, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = "pbl_calendar_secret_key"

CSV_FILE = "schedule_data.csv"
JOB_FILE = "job_data.csv"


def init_csv():
    """CSVファイルが存在しない場合、ヘッダーを作成して初期化する"""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "id",
                    "title",
                    "date",
                    "start_time",
                    "end_time",
                    "location",
                    "memo",
                ]
            )

    if not os.path.exists(JOB_FILE):
        with open(JOB_FILE, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "name", "hourly_rate", "location"])


def load_schedules():
    """CSVファイルからすべての予定を読み込む"""
    init_csv()
    schedules = []
    with open(CSV_FILE, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if "id" not in row or not row["id"]:
                row["id"] = str(uuid.uuid4())
            schedules.append(row)
    return schedules


def load_jobs():
    """CSVファイルからすべてのバイト情報を読み込む"""
    init_csv()
    jobs = []
    with open(JOB_FILE, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            jobs.append(row)
    return jobs


def save_schedule(title, date, start_time, end_time, location, memo):
    """新しい予定をCSVに追記する"""
    init_csv()
    new_id = str(uuid.uuid4())
    with open(CSV_FILE, mode="a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([new_id, title, date, start_time, end_time, location, memo])


def save_job(name, hourly_rate, location):
    """新しいバイト情報をCSVに追記する"""
    init_csv()
    new_id = str(uuid.uuid4())
    with open(JOB_FILE, mode="a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([new_id, name, hourly_rate, location])


def update_schedule_file(schedules):
    """予定一覧CSVを上書き保存する（編集・削除用）"""
    with open(CSV_FILE, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["id", "title", "date", "start_time", "end_time", "location", "memo"]
        )
        for s in schedules:
            writer.writerow(
                [
                    s.get("id", "").strip(),
                    s.get("title"),
                    s.get("date"),
                    s.get("start_time"),
                    s.get("end_time"),
                    s.get("location"),
                    s.get("memo"),
                ]
            )


def update_job_file(jobs):
    """バイト情報CSVを上書き保存する（削除用）"""
    with open(JOB_FILE, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "name", "hourly_rate", "location"])
        for j in jobs:
            writer.writerow(
                [
                    j.get("id", "").strip(),
                    j.get("name"),
                    j.get("hourly_rate"),
                    j.get("location"),
                ]
            )


def calculate_salary(schedules, jobs):
    """開始時間と終了時間から実働時間を計算して当月の給料を出す"""
    current_month_str = datetime.now().strftime("%Y-%m")
    total_salary = 0

    for s in schedules:
        if s.get("date", "").startswith(current_month_str):
            for j in jobs:
                if j["name"] in s.get("title", ""):
                    start_str = s.get("start_time", "")
                    end_str = s.get("end_time", "")

                    if start_str and end_str:
                        try:
                            start_t = datetime.strptime(start_str, "%H:%M")
                            end_t = datetime.strptime(end_str, "%H:%M")

                            diff_seconds = (end_t - start_t).total_seconds()
                            actual_hours = diff_seconds / 3600.0

                            if actual_hours > 0:
                                rate = int(j["hourly_rate"])
                                total_salary += int(rate * actual_hours)
                        except ValueError:
                            pass
                    break
    return total_salary


# --- ルート定義 ---


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        date = request.form.get("date", "").strip()
        start_time = request.form.get("start_time", "").strip()
        end_time = request.form.get("end_time", "").strip()
        location = request.form.get("location", "").strip()
        memo = request.form.get("memo", "").strip()

        jobs = load_jobs()
        if not location:
            for j in jobs:
                if j["name"] in title:
                    location = j["location"]
                    break

        if not title or not date:
            flash("エラー：予定名と日付は必須入力です。", "error")
            return redirect(url_for("index"))

        # 時間の前後関係バリデーション
        if start_time and end_time:
            if start_time >= end_time:
                flash(
                    "エラー：終了時間は開始時間より後の時間を設定してください。",
                    "error",
                )
                return redirect(url_for("index"))

        try:
            save_schedule(title, date, start_time, end_time, location, memo)
            flash("予定を正常に登録しました！", "success")
        except Exception as e:
            flash(f"登録に失敗しました: {e}", "error")

        return redirect(url_for("index"))

    raw_schedules = load_schedules()
    jobs = load_jobs()
    total_salary = calculate_salary(raw_schedules, jobs)

    display_schedules = sorted(
        raw_schedules,
        key=lambda x: (x.get("date", ""), x.get("start_time", "") or ""),
    )
    return render_template(
        "index.html",
        schedules=display_schedules,
        total_salary=total_salary,
        current_month=datetime.now().strftime("%Y年%m月"),
    )


@app.route("/edit/<string:id>", methods=["GET", "POST"])
def edit(id):
    """予定の編集画面・更新処理"""
    schedules = load_schedules()
    target_schedule = next((s for s in schedules if s["id"] == id), None)

    if not target_schedule:
        flash("エラー：指定された予定が見つかりません。", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        user_input = {
            "id": id,
            "title": request.form.get("title", "").strip(),
            "date": request.form.get("date", "").strip(),
            "start_time": request.form.get("start_time", "").strip(),
            "end_time": request.form.get("end_time", "").strip(),
            "location": request.form.get("location", "").strip(),
            "memo": request.form.get("memo", "").strip(),
        }

        if not user_input["title"] or not user_input["date"]:
            flash("エラー：予定名と日付は必須入力です。", "error")
            return render_template("edit.html", schedule=user_input)

        if user_input["start_time"] and user_input["end_time"]:
            if user_input["start_time"] >= user_input["end_time"]:
                flash(
                    "エラー：終了時間は開始時間より後の時間を設定してください。",
                    "error",
                )
                return render_template("edit.html", schedule=user_input)

        target_schedule.update(user_input)
        try:
            update_schedule_file(schedules)
            flash("予定を更新しました！", "success")
            return redirect(url_for("index"))
        except Exception as e:
            flash(f"更新に失敗しました: {e}", "error")

    return render_template("edit.html", schedule=target_schedule)


@app.route("/delete/<string:id>", methods=["POST"])
def delete(id):
    """予定の削除処理"""
    schedules = load_schedules()
    filtered_schedules = [s for s in schedules if s["id"] != id]
    try:
        update_schedule_file(filtered_schedules)
        flash("予定を削除しました。", "success")
    except Exception as e:
        flash(f"削除に失敗しました: {e}", "error")
    return redirect(url_for("index"))


@app.route("/jobs", methods=["GET", "POST"])
def jobs_management():
    """バイト情報の登録・一覧表示画面"""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        hourly_rate = request.form.get("hourly_rate", "").strip()
        location = request.form.get("location", "").strip()

        if not name or not hourly_rate:
            flash("エラー：バイト名と時給は必須入力です。", "error")
            return redirect(url_for("jobs_management"))

        if not hourly_rate.isdigit():
            flash("エラー：時給は半角数字で入力してください。", "error")
            return redirect(url_for("jobs_management"))

        try:
            save_job(name, hourly_rate, location)
            flash("バイト情報を登録しました！", "success")
        except Exception as e:
            flash(f"登録に失敗しました: {e}", "error")

        return redirect(url_for("jobs_management"))

    jobs = load_jobs()
    return render_template("jobs.html", jobs=jobs)


@app.route("/jobs/delete/<string:id>", methods=["POST"])
def delete_job(id):
    """バイト情報の削除処理"""
    jobs = load_jobs()
    filtered_jobs = [j for j in jobs if j["id"] != id.strip()]
    try:
        update_job_file(filtered_jobs)
        flash("バイト情報を削除しました。", "success")
    except Exception as e:
        flash(f"削除に失敗しました: {e}", "error")
    return redirect(url_for("jobs_management"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)