from flask import Flask, render_template, request, jsonify, redirect
import mysql.connector
import atexit

app = Flask(__name__)

# Kết nối MySQL
db = mysql.connector.connect(
    host="dpg-d0bjrhhr0fns73dhngg0-a",
    port=5432,
    user="learning_8ayz_user",
    password="5Tf4wiqbQbQRmfG0umgU5vM3pDs4jJ2x",
    database="learning_8ayz"
)
cursor = db.cursor()

# Đóng kết nối MySQL khi ứng dụng dừng
def close_db():
    cursor.close()
    db.close()
atexit.register(close_db)

# Trang chủ - Thêm từ tiếng Anh + tiếng Pháp và hiển thị danh sách
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        english_word = request.form.get("english_word", "").strip()
        vietnamese_meaning = request.form.get("vietnamese_meaning", "").strip()
        french_word = request.form.get("french_word", "").strip()
        
        if english_word and vietnamese_meaning:
            cursor.execute("INSERT INTO learning (english_word, vietnamese_meaning) VALUES (%s, %s)",
                           (english_word, vietnamese_meaning))
            db.commit()

        if french_word and vietnamese_meaning:
            cursor.execute("INSERT INTO french_learning (french_word, vietnamese_meaning) VALUES (%s, %s)",
                           (french_word, vietnamese_meaning))
            db.commit()

    cursor.execute("SELECT id, english_word, vietnamese_meaning FROM learning ORDER BY id ASC")
    english_words = cursor.fetchall()

    cursor.execute("SELECT id, french_word, vietnamese_meaning FROM french_learning ORDER BY id ASC")
    french_words = cursor.fetchall()

    return render_template("home.html", english_words=english_words, french_words=french_words)

# Xóa từ tiếng Anh
@app.route("/delete/<int:word_id>")
def delete_word(word_id):
    cursor.execute("DELETE FROM learning WHERE id = %s", (word_id,))
    db.commit()
    return redirect("/")

# Xóa từ tiếng Pháp
@app.route("/delete-fr/<int:word_id>")
def delete_french_word(word_id):
    cursor.execute("DELETE FROM french_learning WHERE id = %s", (word_id,))
    db.commit()
    return redirect("/")

# Sửa từ (dùng chung cho cả tiếng Anh và tiếng Pháp)
@app.route("/edit/<table>/<int:word_id>", methods=["GET", "POST"])
def edit_word(table, word_id):
    if table == "english":
        table_name = "learning"
        word_field = "english_word"
    elif table == "french":
        table_name = "french_learning"
        word_field = "french_word"
    else:
        return "Invalid table", 400

    if request.method == "POST":
        word = request.form[word_field].strip()
        vietnamese_meaning = request.form["vietnamese_meaning"].strip()
        cursor.execute(f"UPDATE {table_name} SET {word_field} = %s, vietnamese_meaning = %s WHERE id = %s",
                       (word, vietnamese_meaning, word_id))
        db.commit()
        return redirect("/")

    cursor.execute(f"SELECT id, {word_field}, vietnamese_meaning FROM {table_name} WHERE id = %s", (word_id,))
    word = cursor.fetchone()
    return render_template("edit_word.html", word=word, table=table)

# API lấy từ tiếp theo (tiếng Anh)
@app.route("/next-word/<int:last_id>")
def next_word(last_id):
    cursor.execute("SELECT id, english_word, vietnamese_meaning FROM learning WHERE id > %s ORDER BY id ASC LIMIT 1", (last_id,))
    word = cursor.fetchone()
    return jsonify({"id": word[0], "english_word": word[1], "vietnamese_meaning": word[2]}) if word else jsonify({"error": "No more words"})

# API lấy từ tiếp theo (tiếng Pháp)
@app.route("/next-word-fr/<int:last_id>")
def next_french_word(last_id):
    cursor.execute("SELECT id, french_word, vietnamese_meaning FROM french_learning WHERE id > %s ORDER BY id ASC LIMIT 1", (last_id,))
    word = cursor.fetchone()
    return jsonify({"id": word[0], "french_word": word[1], "vietnamese_meaning": word[2]}) if word else jsonify({"error": "No more words"})

@app.route("/viet-to-eng")
def viet_to_eng():
    return render_template("viet_to_eng.html")

@app.route("/eng-to-viet")
def eng_to_viet():
    return render_template("eng_to_viet.html")

@app.route("/viet-to-fr")
def viet_to_fr():
    return render_template("viet_to_fr.html")

@app.route("/fr-to-viet")
def fr_to_viet():
    return render_template("fr_to_viet.html")

if __name__ == "__main__":
    app.run(debug=True)