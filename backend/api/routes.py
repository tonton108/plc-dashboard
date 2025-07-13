# backend/api/routes.py

from flask import request, jsonify
from sqlalchemy import or_
from typing import cast
from backend.db import db
from backend.db.models import Equipment

def register_routes(app):
    @app.route("/api/register", methods=["POST"])
    def api_register():
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        equipment_id = data.get("equipment_id")
        mac_address = data.get("mac_address")

        if not equipment_id or not mac_address:
            return jsonify({"error": "equipment_id and mac_address are required"}), 400

        # 既存レコード検索（mac_address or equipment_id）
        equipment = Equipment.query.filter(
            or_(
                getattr(Equipment, 'mac_address') == mac_address,
                getattr(Equipment, 'equipment_id') == equipment_id
            )
        ).first()

        if equipment:
            # 更新
            equipment.manufacturer = data.get("manufacturer")
            equipment.series = data.get("series")
            equipment.ip = data.get("ip")
            equipment.hostname = data.get("hostname")
            equipment.port = data.get("port")
            equipment.interval = data.get("interval")
            equipment.status = "登録済み"
        else:
            # 新規作成
            equipment = Equipment(
                equipment_id=equipment_id,
                manufacturer=data.get("manufacturer"),
                series=data.get("series"),
                ip=data.get("ip"),
                mac_address=mac_address,
                hostname=data.get("hostname"),
                port=data.get("port"),
                interval=data.get("interval"),
                status="登録済み"
            )
            db.session.add(equipment)

        db.session.commit()
        return jsonify({"message": "登録完了"}), 200


    @app.route("/api/check-equipment", methods=["POST"])
    def check_equipment():
        data = request.get_json()
        mac = data.get("mac_address")
        ip = data.get("ip")

        if not mac or not ip:
            return jsonify({"error": "Missing mac_address or ip"}), 400

        equipment = Equipment.query.filter_by(mac_address=mac, ip=ip).first()
        if equipment:
            return jsonify({
                "found": True,
                "id": equipment.id,
                "equipment_id": equipment.equipment_id,
                "manufacturer": equipment.manufacturer,
                "series": equipment.series,
                "ip": equipment.ip,
                "port": equipment.port,
                "interval": equipment.interval,
                "status": equipment.status,
                "hostname": equipment.hostname
            }), 200
        else:
            return jsonify({"found": False}), 200
