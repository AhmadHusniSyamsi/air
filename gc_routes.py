from datetime import datetime

from flask import Blueprint, redirect, render_template, request, url_for

from extensions import db
from models import GroundCheck, GroundCheckRow

groundcheck_bp = Blueprint("groundcheck", __name__)

# ============================
# Helper
# ============================
def to_float(val):
    """Convert string ke float atau None kalau kosong."""
    if val is None or val.strip() == "":
        return None
    try:
        return float(val)
    except ValueError:
        return None

# ============================
# Input Ground Check
# ============================
@groundcheck_bp.route("/llz/ground_check", methods=["GET", "POST"])
def ground_check():
    if request.method == "POST":
        lokasi = request.form.get("lokasi")
        tanggal = datetime.strptime(request.form.get("tanggal"), "%Y-%m-%d")
        teknisi = ", ".join(request.form.getlist("teknisi[]"))
        paraf = ", ".join(request.form.getlist("paraf[]"))
        catatan = request.form.get("catatan")

        gc = GroundCheck(
            lokasi=lokasi,
            tanggal=tanggal,
            teknisi=teknisi,
            paraf=paraf,
            catatan=catatan
        )
        db.session.add(gc)
        db.session.flush()  # supaya dapat ID sebelum commit

        # =====================
        # Simpan Data Tabel
        # =====================
        freq_list = ["90 Hz"]*8 + ["Center"] + ["150 Hz"]*8
        jarak_list = [
            "210.1","173.2","139.9","109.2","80.4","52.9","26.2","9.7",
            "0",
            "9.7","26.2","52.9","80.4","109.2","139.9","173.2","210.1"
        ]
        degree_list = [
            "35°","30°","25°","20°","15°","10°","5°","1.85°",
            "0°",
            "1.85°","5°","10°","15°","20°","25°","30°","35°"
        ]

        for idx, (freq, jarak, degree) in enumerate(zip(freq_list, jarak_list, degree_list)):
            if freq == "90 Hz":
                prefix = f"hz90_{idx}_"
            elif freq == "150 Hz":
                prefix = f"hz150_{idx - 9}_"
            else:  # Center
                prefix = f"center_0_"

            # Ambil semua 12 kolom, kosong = None
            tx_values = [to_float(request.form.get(prefix + str(i))) for i in range(12)]

            row = GroundCheckRow(
                groundcheck_id=gc.id,
                freq=freq,
                jarak=jarak,
                degree=degree,  # simpan string langsung, jangan konversi ke float
                tx1_ddm_persen=tx_values[0],
                tx1_ddm_ua=tx_values[1],
                tx1_sum=tx_values[2],
                tx1_mod90=tx_values[3],
                tx1_mod150=tx_values[4],
                tx1_rf=tx_values[5],
                tx2_ddm_persen=tx_values[6],
                tx2_ddm_ua=tx_values[7],
                tx2_sum=tx_values[8],
                tx2_mod90=tx_values[9],
                tx2_mod150=tx_values[10],
                tx2_rf=tx_values[11]
            )
            db.session.add(row)

        db.session.commit()
        return redirect(url_for("groundcheck.detail_data", id=gc.id))

    return render_template("llz/ground_check.html")

# ============================
# Lihat Semua Data
# ============================
@groundcheck_bp.route("/llz/lihat_data")
def lihat_data():
    data = GroundCheck.query.all()
    return render_template("llz/lihat_data.html", ground_check=data)

# ============================
# Edit Ground Check
# ============================
@groundcheck_bp.route("/llz/edit/<int:id>", methods=["GET", "POST"])
def edit_ground_check(id):
    gc = GroundCheck.query.get_or_404(id)

    if request.method == "POST":
        gc.lokasi = request.form.get("lokasi")
        gc.tanggal = datetime.strptime(request.form.get("tanggal"), "%Y-%m-%d")
        gc.teknisi = ", ".join(request.form.getlist("teknisi[]"))
        gc.paraf = ", ".join(request.form.getlist("paraf[]"))
        gc.catatan = request.form.get("catatan")

        # Hapus semua row lama
        GroundCheckRow.query.filter_by(groundcheck_id=gc.id).delete()

        freq_list = ["90 Hz"]*8 + ["Center"] + ["150 Hz"]*8
        jarak_list = [
            "210.1","173.2","139.9","109.2","80.4","52.9","26.2","9.7",
            "0",
            "9.7","26.2","52.9","80.4","109.2","139.9","173.2","210.1"
        ]
        degree_list = [
            "35°","30°","25°","20°","15°","10°","5°","1.85°",
            "0°",
            "1.85°","5°","10°","15°","20°","25°","30°","35°"
        ]

        for idx, (freq, jarak, degree) in enumerate(zip(freq_list, jarak_list, degree_list)):
            if freq == "90 Hz":
                prefix = f"hz90_{idx}_"
            elif freq == "150 Hz":
                prefix = f"hz150_{idx - 9}_"
            else:
                prefix = f"center_0_"

            tx_values = [to_float(request.form.get(prefix + str(i))) for i in range(12)]

            row = GroundCheckRow(
                groundcheck_id=gc.id,
                freq=freq,
                jarak=jarak,
                degree=degree,
                tx1_ddm_persen=tx_values[0],
                tx1_ddm_ua=tx_values[1],
                tx1_sum=tx_values[2],
                tx1_mod90=tx_values[3],
                tx1_mod150=tx_values[4],
                tx1_rf=tx_values[5],
                tx2_ddm_persen=tx_values[6],
                tx2_ddm_ua=tx_values[7],
                tx2_sum=tx_values[8],
                tx2_mod90=tx_values[9],
                tx2_mod150=tx_values[10],
                tx2_rf=tx_values[11]
            )
            db.session.add(row)

        db.session.commit()
        return redirect(url_for("groundcheck.lihat_data"))

    return render_template("llz/edit_ground_check.html", gc=gc)

# ============================
# Delete Ground Check
# ============================
@groundcheck_bp.route("/llz/delete/<int:id>")
def delete_ground_check(id):
    gc = GroundCheck.query.get_or_404(id)
    db.session.delete(gc)
    db.session.commit()
    return redirect(url_for("groundcheck.lihat_data"))

# ============================
# Detail Ground Check
# ============================
@groundcheck_bp.route("/llz/detail/<int:id>")
def detail_data(id):
    record = GroundCheck.query.get_or_404(id)
    rows = GroundCheckRow.query.filter_by(groundcheck_id=id).all()
    return render_template("llz/detail_data.html", record=record, rows=rows)
