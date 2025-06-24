from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from openai import OpenAI
import os
import json

app = Flask(__name__, static_folder="static")
CORS(app)

# Fungsi padanan fail ikut julat ayat
def fail_padanan(ayat_num):
    if 1 <= ayat_num <= 1000:
        return "1-1000"
    elif 1001 <= ayat_num <= 2000:
        return "1001-2000"
    elif 2001 <= ayat_num <= 3000:
        return "2001-3000"
    elif 3001 <= ayat_num <= 4000:
        return "3001-4000"
    elif 4001 <= ayat_num <= 5000:
        return "4001-5000"
    elif 5001 <= ayat_num <= 6000:
        return "5001-6000"
    elif 6001 <= ayat_num <= 6236:
        return "6001-6236"
    return "1-1000"

# Kiraan nombor ayat keseluruhan
def kira_nombor_ayat(surah, ayat):
    total_ayat_per_surah = [
        7, 286, 200, 176, 120, 165, 206, 75, 129, 109, 123, 111, 43, 52,
        99, 128, 111, 110, 98, 135, 112, 78, 118, 64, 77, 227, 93, 88,
        69, 60, 34, 30, 73, 54, 45, 83, 182, 88, 75, 85, 54, 53, 89, 59,
        37, 35, 38, 29, 18, 45, 60, 49, 62, 55, 78, 96, 29, 22, 24, 13,
        14, 11, 11, 18, 12, 12, 30, 52, 52, 44, 28, 28, 20, 56, 40, 31,
        50, 40, 46, 42, 29, 19, 36, 25, 22, 17, 19, 26, 30, 20, 15, 21,
        11, 8, 8, 19, 5, 8, 8, 11, 11, 8, 3, 9, 5, 4, 7, 3, 6, 3, 5, 4,
        5, 6
    ]
    total = 0
    for i in range(surah - 1):
        total += total_ayat_per_surah[i]
    return total + ayat

# Halaman utama
@app.route("/")
def home():
    return send_from_directory("static", "index.html")

# Endpoint 1: Carian ikut tema
@app.route("/ayat-bertema", methods=["POST"])
def ayat_bertema():
    tema = request.json.get("tema", "").lower()
    print("📥 Tema diterima:", tema)

    hasil = []
    julat_fail = [
        "1-1000", "1001-2000", "2001-3000", "3001-4000",
        "4001-5000", "5001-6000", "6001-6236"
    ]

    try:
        class StopIteration(Exception): pass

        for fail in julat_fail:
            print(f"🔍 Semak fail: quran_bm_{fail}.json")
            with open(f"static/quran_bm_{fail}.json", encoding="utf-8") as f_bm, \
                 open(f"static/quran_arab_{fail}.json", encoding="utf-8") as f_arab:

                bm_data = json.load(f_bm)
                arab_data = json.load(f_arab)

                for bm, arab in zip(bm_data, arab_data):
                    if tema in bm["terjemahan"].lower():
                        print(f"✅ Jumpa padanan dalam: Surah {bm['surah']} Ayat {bm['ayat']}")
                        hasil.append(f"{bm['surah']} Ayat {bm['ayat']}\nArab: {arab['arab']}\nTerjemahan: {bm['terjemahan']}")

                        if len(hasil) >= 100:
                            print("🔴 Had 100 dicapai, berhenti.")
                            raise StopIteration  # keluar dari semua loop

    except StopIteration:
        pass  # ini dibiarkan supaya tidak dianggap ralat besar
    except Exception as e:
        print("❌ Ralat besar dalam /ayat-bertema:", str(e))
        return jsonify({"error": "❌ Ralat semasa proses carian."}), 500

    # ✅ Return WAJIB di akhir fungsi
    if hasil:
        return jsonify({"hasil": "\n\n".join(hasil)})
    else:
        return jsonify({"hasil": "⚠️ Tiada ayat dijumpai."})


# Endpoint 2: Padan ayat ikut surah + ayat
@app.route("/padan-ayat", methods=["POST"])
def padan_ayat():
    surah = int(request.json.get("surah"))
    ayat = int(request.json.get("ayat"))
    ayat_num = kira_nombor_ayat(surah, ayat)
    fail = fail_padanan(ayat_num)

    try:
        with open(f"static/quran_bm_{fail}.json", encoding="utf-8") as f_bm, \
             open(f"static/quran_arab_{fail}.json", encoding="utf-8") as f_arab:

            bm_data = json.load(f_bm)
            arab_data = json.load(f_arab)

        bm = next((a for a in bm_data if a["surah"] == surah and a["ayat"] == ayat), None)
        arab = next((a for a in arab_data if a["surah"] == surah and a["ayat"] == ayat), None)

        if bm and arab:
            return jsonify({
                "surah": surah,
                "ayat": ayat,
                "arab": arab["arab"],
                "terjemahan": bm["terjemahan"]
            })
        else:
            return jsonify({"error": "Ayat tidak dijumpai."}), 404

    except Exception as e:
        print("❌ Ralat besar dalam /padan-ayat:", str(e))
        return jsonify({"error": "❌ Gagal proses ayat."}), 500


@app.route("/asbab", methods=["POST"])
def asbab_al_nuzul():
    try:
        data = request.get_json()
        surah = int(data.get("surah"))
        ayat = int(data.get("ayat"))

        with open("static/asbab.json", encoding="utf-8") as f:
            asbab_data = json.load(f)

        for item in asbab_data:
            if item["surah"] == surah and item["ayat"] == ayat:
                return jsonify({"asbab": item["asbab"]})

        return jsonify({"asbab": "❌ Tiada sebab penurunan."})

    except Exception as e:
        print("❌ Ralat dalam /asbab:", str(e))
        return jsonify({"asbab": "❌ Ralat semasa memproses asbab."})


if __name__ == "__main__":
    app.run(debug=True)
