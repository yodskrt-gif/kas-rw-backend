from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import date
import mysql.connector
import os
from dotenv import load_dotenv

# =========================
# Load ENV
# =========================
load_dotenv()

# =========================
# FastAPI
# =========================
app = FastAPI(
    title="Kas RW API"
)

# =========================
# CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# Koneksi Database
# =========================
def get_db():

    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(
            os.getenv("DB_PORT", 3306)
        ),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )

# =========================
# Model Data
# =========================
class TransaksiBase(BaseModel):

    tanggal: date
    keterangan: str
    jenis: str
    jumlah: float


class TransaksiUpdate(BaseModel):

    tanggal: Optional[date] = None
    keterangan: Optional[str] = None
    jenis: Optional[str] = None
    jumlah: Optional[float] = None

# =========================
# Root
# =========================
@app.get("/")
def root():

    return {
        "message":
        "Kas RW API berjalan"
    }

# =========================
# GET Semua Transaksi
# =========================
@app.get("/transaksi")
def get_all():

    db = get_db()

    cursor = db.cursor(
        dictionary=True
    )

    cursor.execute(
        """
        SELECT *
        FROM transaksi
        ORDER BY tanggal DESC
        """
    )

    rows = cursor.fetchall()

    cursor.close()
    db.close()

    return rows

# =========================
# GET Transaksi by ID
# =========================
@app.get("/transaksi/{id}")
def get_one(id: int):

    db = get_db()

    cursor = db.cursor(
        dictionary=True
    )

    cursor.execute(
        """
        SELECT *
        FROM transaksi
        WHERE id = %s
        """,
        (id,)
    )

    row = cursor.fetchone()

    cursor.close()
    db.close()

    if not row:

        raise HTTPException(
            status_code=404,
            detail=
            "Transaksi tidak ditemukan"
        )

    return row

# =========================
# POST Tambah Transaksi
# =========================
@app.post(
    "/transaksi",
    status_code=201
)
def create(data: TransaksiBase):

    db = get_db()

    cursor = db.cursor()

    cursor.execute(
        """
        INSERT INTO transaksi (
            tanggal,
            keterangan,
            jenis,
            jumlah
        )
        VALUES (%s, %s, %s, %s)
        """,
        (
            data.tanggal,
            data.keterangan,
            data.jenis,
            data.jumlah,
        ),
    )

    db.commit()

    new_id = cursor.lastrowid

    cursor.close()
    db.close()

    return {
        "id": new_id,
        "message":
        "Transaksi berhasil ditambahkan"
    }

# =========================
# PUT Update Transaksi
# =========================
@app.put("/transaksi/{id}")
def update(
    id: int,
    data: TransaksiUpdate
):

    db = get_db()

    cursor = db.cursor(
        dictionary=True
    )

    # cek data lama
    cursor.execute(
        """
        SELECT *
        FROM transaksi
        WHERE id = %s
        """,
        (id,)
    )

    row = cursor.fetchone()

    if not row:

        cursor.close()
        db.close()

        raise HTTPException(
            status_code=404,
            detail=
            "Transaksi tidak ditemukan"
        )

    # update hanya field yg diisi
    updated = {
        **row,
        **{
            k: v
            for k, v
            in data.dict().items()
            if v is not None
        }
    }

    cursor.execute(
        """
        UPDATE transaksi
        SET
            tanggal = %s,
            keterangan = %s,
            jenis = %s,
            jumlah = %s
        WHERE id = %s
        """,
        (
            updated["tanggal"],
            updated["keterangan"],
            updated["jenis"],
            updated["jumlah"],
            id,
        ),
    )

    db.commit()

    cursor.close()
    db.close()

    return {
        "message":
        "Transaksi berhasil diperbarui"
    }

# =========================
# DELETE Transaksi
# =========================
@app.delete("/transaksi/{id}")
def delete(id: int):

    db = get_db()

    cursor = db.cursor()

    cursor.execute(
        """
        DELETE FROM transaksi
        WHERE id = %s
        """,
        (id,)
    )

    db.commit()

    affected = cursor.rowcount

    cursor.close()
    db.close()

    if affected == 0:

        raise HTTPException(
            status_code=404,
            detail=
            "Transaksi tidak ditemukan"
        )

    return {
        "message":
        "Transaksi berhasil dihapus"
    }