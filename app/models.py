from datetime import datetime

from app import db, app
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from app import login
import jwt
from time import time


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


set_roles = db.Table('set_roles',
                     db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('access_control_id', db.Integer, db.ForeignKey('access_control.id'))
                     )


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(120), index=True)
    role = db.Column(db.String(1), index=True)  # 'A' for admin, 'E' for employee
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id', ondelete='CASCADE', onupdate='CASCADE'),
                            nullable=False)

    accesses = db.relationship('AccessControl', secondary=set_roles, backref='users', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_access(self, access_control):
        if not self.is_accessing(access_control):
            self.accesses.append(access_control)

    def un_access(self, access_control):
        if self.is_accessing(access_control):
            self.accesses.remove(access_control)

    def is_accessing(self, access_control):
        return self.accesses.filter(set_roles.c.access_control_id == access_control.id).count() > 0

    def get_accesses(self):
        return AccessControl.query.join(set_roles, (set_roles.c.access_control_id == AccessControl.id)) \
            .filter(set_roles.c.user_id == self.id).order_by(AccessControl.id.asc())

    # For admin
    def __init__(self, username, role, hospital_id):
        self.username = username
        self.role = role
        self.hospital_id = hospital_id
        db.session.add(self)
        db.session.commit()
        if self.role == 'A':
            accesses = AccessControl.query.order_by(AccessControl.id.asc()).all()
            for a in accesses:
                self.set_access(a)
        db.session.commit()

    def user_to_dict(self):
        accesses_list = []
        for a in self.get_accesses():
            accesses_list.append(a.name)
        return {'username': self.username, 'accesses': accesses_list}

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode({'reset_password': self.id, 'exp': time() + expires_in},
                          app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


class AccessControl(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), index=True)
    url = db.Column(db.String(500), index=True)

    def __repr__(self):
        return '<AccessControl {}>'.format(self.name)


class Hospital(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), index=True)
    url = db.Column(db.String(64), index=True)
    email = db.Column(db.String(64), index=True)
    users = db.relationship('User', cascade="all,delete", backref='hospital', lazy='dynamic')
    dotthaus = db.relationship('DotThau', cascade="all,delete", backref='hospital', lazy='dynamic')
    importhistorys = db.relationship('ImportHistory', cascade="all,delete", backref='hospital', lazy='dynamic')
    thuocs = db.relationship('Thuoc', cascade="all,delete", backref='hospital', lazy='dynamic')
    hoatchats = db.relationship('HoatChat', cascade="all,delete", backref='hospital', lazy='dynamic')
    hamluongs = db.relationship('HamLuong', cascade="all,delete", backref='hospital', lazy='dynamic')
    duongdungs = db.relationship('DuongDung', cascade="all,delete", backref='hospital', lazy='dynamic')
    dangbaoches = db.relationship('DangBaoChe', cascade="all,delete", backref='hospital', lazy='dynamic')
    quycachdonggois = db.relationship('QuyCachDongGoi', cascade="all,delete", backref='hospital', lazy='dynamic')
    donvitinhs = db.relationship('DonViTinh', cascade="all,delete", backref='hospital', lazy='dynamic')
    cososanxuats = db.relationship('CoSoSanXuat', cascade="all,delete", backref='hospital', lazy='dynamic')
    nuocsanxuats = db.relationship('NuocSanXuat', cascade="all,delete", backref='hospital', lazy='dynamic')
    nhathaus = db.relationship('NhaThau', cascade="all,delete", backref='hospital', lazy='dynamic')
    ketquatrungthaus = db.relationship('KetQuaTrungThau', cascade="all,delete", backref='hospital', lazy='dynamic')
    fileinformations = db.relationship('FileInformation', cascade="all,delete", backref='hospital', lazy='dynamic')
    khochans = db.relationship('KhoChan', cascade="all,delete", backref='hospital', lazy='dynamic')
    kholes = db.relationship('KhoLe', cascade="all,delete", backref='hospital', lazy='dynamic')
    tonghopthaus = db.relationship('TongHopThau', cascade="all,delete", backref='hospital', lazy='dynamic')
    thongkekhos = db.relationship('ThongKeKho', cascade="all,delete", backref='hospital', lazy='dynamic')
    import_history_nxts = db.relationship('ImportHistoryNXT', cascade="all,delete", backref='hospital', lazy='dynamic')
    nxts = db.relationship('NXT', cascade="all,delete", backref='hospital', lazy='dynamic')
    abcvens = db.relationship('SuDungThuocABCVEN', cascade="all,delete", backref='hospital', lazy='dynamic')
    nhomduoclys = db.relationship('NhomDuocLyBV', cascade="all,delete", backref='hospital', lazy='dynamic')
    nhomhoaduocs = db.relationship('NhomHoaDuocBV', cascade="all,delete", backref='hospital', lazy='dynamic')

    def __repr__(self):
        return '<Hospital {}>'.format(self.name)

    def __init__(self, name, url, email):
        self.name = name
        self.url = url
        self.email = email
        db.session.add(self)
        db.session.commit()
        nhom_duoc_ly = NhomDuocLy.query.all()
        for n in nhom_duoc_ly:
            nn = NhomDuocLyBV(name=n.name, hospital_id=self.id)
            db.session.add(nn)

        nhom_hoa_duoc = NhomHoaDuoc.query.all()
        for n in nhom_hoa_duoc:
            nn = NhomHoaDuocBV(name=n.name, hospital_id=self.id)
            db.session.add(nn)
        db.session.commit()


class DotThau(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(64), index=True)
    name = db.Column(db.String(500), index=True)
    phase = db.Column(db.String(64), index=True)
    formality = db.Column(db.String(64), index=True)
    soQD = db.Column(db.String(64), index=True)
    ngayQD = db.Column(db.Date, index=True)
    ngayHH = db.Column(db.Date, index=True)
    note = db.Column(db.String(500), index=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id', ondelete='CASCADE', onupdate='CASCADE'),
                            nullable=False)

    ketquatrungthaus = db.relationship('KetQuaTrungThau', cascade="all,delete", backref='dot_thau', lazy='dynamic')
    importhistory = db.relationship('ImportHistory', cascade="all,delete", backref='dot_thau', lazy='dynamic')
    nxts = db.relationship('NXT', cascade="all,delete", backref='dot_thau', lazy='dynamic')

    def __repr__(self):
        return '<DotThau {}>'.format(self.name)

    def dot_thau_to_dict(self):
        return {'id': self.id, 'code': self.code, 'name': self.name, 'phase': self.phase, 'formality': self.formality,
                'soQD': self.soQD, 'ngayQD': self.ngayQD, 'ngayHH': self.ngayHH, 'note': self.note}


class ImportHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dot_thau_id = db.Column(db.Integer, db.ForeignKey('dot_thau.id', ondelete='CASCADE', onupdate='CASCADE'))
    time = db.Column(db.DateTime, default=datetime.utcnow)
    import_historys = db.relationship('KetQuaTrungThau', cascade="all,delete", backref='import_history', lazy='dynamic')
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id', ondelete='CASCADE', onupdate='CASCADE'),
                            nullable=False)

    def __repr__(self):
        return '<ImportHistory {}>'.format(self.dot_thau.code)

    def import_history_to_dict(self):
        return {'code': self.dot_thau.code, 'time': self.time, 'id': self.id}


class Thuoc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), index=True)
    codeBV = db.Column(db.String(10), index=True)
    name = db.Column(db.String(500), index=True)
    cch = db.Column(db.String(1000))  # Chưa chuẩn hoá
    sdk = db.Column(db.String(500), index=True)
    ven = db.Column(db.String(1), index=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id', ondelete='CASCADE', onupdate='CASCADE'),
                            nullable=False)

    ketquatrungthaus = db.relationship('KetQuaTrungThau', cascade="all,delete", backref='thuoc', lazy='dynamic')
    khochans = db.relationship('KhoChan', cascade="all,delete", backref='thuoc', lazy='dynamic')
    kholes = db.relationship('KhoLe', cascade="all,delete", backref='thuoc', lazy='dynamic')
    tonghopthaus = db.relationship('TongHopThau', cascade="all,delete", backref='thuoc', lazy='dynamic')
    thongkekhos = db.relationship('ThongKeKho', cascade="all,delete", backref='thuoc', lazy='dynamic')
    nxts = db.relationship('NXT', cascade="all,delete", backref='thuoc', lazy='dynamic')

    def __repr__(self):
        return '<Thuoc {}>'.format(self.name)

    def danh_muc_to_dict(self):
        return {'id': self.id, 'code': self.code, 'codeBV': self.codeBV, 'name': self.name, 'sdk': self.sdk}


class HoatChat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), index=True)
    name = db.Column(db.String(500), index=True)
    cch = db.Column(db.String(1000))  # Chưa chuẩn hoá
    nhom_duoc_ly_bv_id = db.Column(db.Integer, db.ForeignKey('nhom_duoc_ly_bv.id'))
    nhom_hoa_duoc_bv_id = db.Column(db.Integer, db.ForeignKey('nhom_hoa_duoc_bv.id'))
    hoat_chat_syt_id = db.Column(db.Integer, db.ForeignKey('hoat_chat_syt.id'))
    hoat_chat_tt20_id = db.Column(db.Integer, db.ForeignKey('hoat_chat_tt20.id'))
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id', ondelete='CASCADE', onupdate='CASCADE'),
                            nullable=False)

    ketquatrungthaus = db.relationship('KetQuaTrungThau', cascade="all,delete", backref='hoat_chat', lazy='dynamic')

    def __repr__(self):
        return '<HoatChat {}>'.format(self.name)

    def danh_muc_to_dict(self):
        return {'id': self.id, 'code': self.code, 'name': self.name,
                'nhom_duoc_ly': self.nhom_duoc_ly_bv.name if self.nhom_duoc_ly_bv else '',
                'nhom_hoa_duoc': self.nhom_hoa_duoc_bv.name if self.nhom_hoa_duoc_bv else '',
                'hoat_chat_syt': self.hoat_chat_syt.name if self.hoat_chat_syt else '',
                'hoat_chat_tt20': self.hoat_chat_tt20.name if self.hoat_chat_tt20 else ''}


class HoatChatSYT(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), index=True)
    bietduocgoc = db.relationship('BietDuocGocSYT', backref='hoat_chat', lazy='dynamic')
    soyte = db.relationship('SoYTe', backref='hoat_chat', lazy='dynamic')
    hoat_chat_bv = db.relationship('HoatChat', backref='hoat_chat_syt', lazy='dynamic')

    def __repr__(self):
        return '<HoatChatSYT {}>'.format(self.name)

    def danh_muc_to_dict(self):
        return {'id': self.id, 'name': self.name}


class BietDuocGocSYT(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), index=True)
    hoat_chat_syt_id = db.Column(db.Integer, db.ForeignKey('hoat_chat_syt.id'))
    soyte = db.relationship('SoYTe', backref='biet_duoc_goc', lazy='dynamic')

    def __repr__(self):
        return '<BietDuocGocSYT {}>'.format(self.name)


class SoYTe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ma_he_thong = db.Column(db.String(64), index=True)
    ma_thuoc = db.Column(db.String(64), index=True)
    hoat_chat_syt_id = db.Column(db.Integer, db.ForeignKey('hoat_chat_syt.id'))
    biet_duoc_goc_syt_id = db.Column(db.Integer, db.ForeignKey('biet_duoc_goc_syt.id'))
    ham_luong = db.Column(db.String(500), index=True)
    dang_bao_che = db.Column(db.String(255), index=True)
    duong_dung = db.Column(db.String(64), index=True)
    don_vi_tinh = db.Column(db.String(64), index=True)
    nhom_thau = db.Column(db.String(64), index=True)

    def __repr__(self):
        return '<SoYTe {}>'.format(self.hoat_chat.name)


class HoatChatTT20(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), index=True)
    tt20 = db.relationship('ThongTu20', backref='hoat_chat', lazy='dynamic')
    hoat_chat_bv = db.relationship('HoatChat', backref='hoat_chat_tt20', lazy='dynamic')

    def __repr__(self):
        return '<HoatChatTT20 {}>'.format(self.name)

    def danh_muc_to_dict(self):
        return {'id': self.id, 'name': self.name}


class ThongTu20(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stt = db.Column(db.Integer, index=True)
    hoat_chat_tt20_id = db.Column(db.Integer, db.ForeignKey('hoat_chat_tt20.id'))
    nhom_duoc_ly_id = db.Column(db.Integer, db.ForeignKey('nhom_duoc_ly.id'))
    nhom_hoa_duoc_id = db.Column(db.Integer, db.ForeignKey('nhom_hoa_duoc.id'))
    duong_dung = db.Column(db.String(64), index=True)

    def __repr__(self):
        return '<ThongTu20 {}>'.format(self.hoat_chat.name)

    def to_dict(self):
        return {'nhom_duoc_ly': self.nhom_duoc_ly.name, 'nhom_hoa_duoc': self.nhom_hoa_duoc.name}


class HamLuong(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), index=True)
    cch = db.Column(db.String(1000))  # Chưa chuẩn hoá
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id', ondelete='CASCADE', onupdate='CASCADE'),
                            nullable=False)

    ketquatrungthaus = db.relationship('KetQuaTrungThau', cascade="all,delete", backref='ham_luong', lazy='dynamic')

    def __repr__(self):
        return '<HamLuong {}>'.format(self.name)

    def danh_muc_to_dict(self):
        return {'id': self.id, 'name': self.name}


class DuongDung(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), index=True)
    cch = db.Column(db.String(1000))  # Chưa chuẩn hoá
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id', ondelete='CASCADE', onupdate='CASCADE'),
                            nullable=False)

    ketquatrungthaus = db.relationship('KetQuaTrungThau', cascade="all,delete", backref='duong_dung', lazy='dynamic')

    def __repr__(self):
        return '<DuongDung {}>'.format(self.name)

    def danh_muc_to_dict(self):
        return {'id': self.id, 'name': self.name}


class DangBaoChe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), index=True)
    cch = db.Column(db.String(1000))  # Chưa chuẩn hoá
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id', ondelete='CASCADE', onupdate='CASCADE'),
                            nullable=False)

    ketquatrungthaus = db.relationship('KetQuaTrungThau', cascade="all,delete", backref='dang_bao_che', lazy='dynamic')

    def __repr__(self):
        return '<DangBaoChe {}>'.format(self.name)

    def danh_muc_to_dict(self):
        return {'id': self.id, 'name': self.name}


class QuyCachDongGoi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), index=True)
    cch = db.Column(db.String(1000))  # Chưa chuẩn hoá
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id', ondelete='CASCADE', onupdate='CASCADE'),
                            nullable=False)

    ketquatrungthaus = db.relationship('KetQuaTrungThau', cascade="all,delete", backref='quy_cach_dong_goi',
                                       lazy='dynamic')

    def __repr__(self):
        return '<QuyCachDongGoi {}>'.format(self.name)

    def danh_muc_to_dict(self):
        return {'id': self.id, 'name': self.name}


class DonViTinh(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), index=True)
    cch = db.Column(db.String(1000))  # Chưa chuẩn hoá
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id', ondelete='CASCADE', onupdate='CASCADE'),
                            nullable=False)

    ketquatrungthaus = db.relationship('KetQuaTrungThau', cascade="all,delete", backref='don_vi_tinh', lazy='dynamic')

    def __repr__(self):
        return '<DonViTinh {}>'.format(self.name)

    def danh_muc_to_dict(self):
        return {'id': self.id, 'name': self.name}


class CoSoSanXuat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), index=True)
    cch = db.Column(db.String(1000))  # Chưa chuẩn hoá
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id', ondelete='CASCADE', onupdate='CASCADE'),
                            nullable=False)

    ketquatrungthaus = db.relationship('KetQuaTrungThau', cascade="all,delete", backref='co_so_san_xuat',
                                       lazy='dynamic')

    def __repr__(self):
        return '<CoSoSanXuat {}>'.format(self.name)

    def danh_muc_to_dict(self):
        return {'id': self.id, 'name': self.name}


class NuocSanXuat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), index=True)
    cch = db.Column(db.String(1000))  # Chưa chuẩn hoá
    place = db.Column(db.String(10), index=True)  # Nội or Ngoại
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id', ondelete='CASCADE', onupdate='CASCADE'),
                            nullable=False)

    ketquatrungthaus = db.relationship('KetQuaTrungThau', cascade="all,delete", backref='nuoc_san_xuat', lazy='dynamic')

    def __repr__(self):
        return '<CoSoSanXuat {}>'.format(self.name)

    def danh_muc_to_dict(self):
        return {'id': self.id, 'name': self.name, 'place': self.place}


class NhaThau(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), index=True)
    cch = db.Column(db.String(1000))  # Chưa chuẩn hoá
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id', ondelete='CASCADE', onupdate='CASCADE'),
                            nullable=False)

    ketquatrungthaus = db.relationship('KetQuaTrungThau', cascade="all,delete", backref='nha_thau', lazy='dynamic')

    def __repr__(self):
        return '<NhaThau {}>'.format(self.name)

    def danh_muc_to_dict(self):
        return {'id': self.id, 'name': self.name}


class NhomThau(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), index=True)

    ketquatrungthaus = db.relationship('KetQuaTrungThau', cascade="all,delete", backref='nhom_thau', lazy='dynamic')

    def __repr__(self):
        return '<NhomThau {}>'.format(self.name)

    def danh_muc_to_dict(self):
        return {'id': self.id, 'name': self.name}


class NhomDuocLyBV(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), index=True)
    hoatchats = db.relationship('HoatChat', backref='nhom_duoc_ly_bv', lazy='dynamic')
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id', ondelete='CASCADE', onupdate='CASCADE'),
                            nullable=False)

    def __repr__(self):
        return '<NhomDuocLyBV {}>'.format(self.name)

    def danh_muc_to_dict(self):
        return {'id': self.id, 'name': self.name}


class NhomHoaDuocBV(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), index=True)
    hoatchats = db.relationship('HoatChat', backref='nhom_hoa_duoc_bv', lazy='dynamic')
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id', ondelete='CASCADE', onupdate='CASCADE'),
                            nullable=False)

    def __repr__(self):
        return '<NhomHoaDuocBV {}>'.format(self.name)

    def danh_muc_to_dict(self):
        return {'id': self.id, 'name': self.name}


class NhomDuocLy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), index=True)
    tt20 = db.relationship('ThongTu20', backref='nhom_duoc_ly', lazy='dynamic')

    def __repr__(self):
        return '<NhomDuocLy {}>'.format(self.name)

    def danh_muc_to_dict(self):
        return {'id': self.id, 'name': self.name}


class NhomHoaDuoc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), index=True)
    tt20 = db.relationship('ThongTu20', backref='nhom_hoa_duoc', lazy='dynamic')

    def __repr__(self):
        return '<NhomHoaDuoc {}>'.format(self.name)

    def danh_muc_to_dict(self):
        return {'id': self.id, 'name': self.name}


class KetQuaTrungThau(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    thuoc_id = db.Column(db.Integer, db.ForeignKey('thuoc.id'))
    hoat_chat_id = db.Column(db.Integer, db.ForeignKey('hoat_chat.id'))
    ham_luong_id = db.Column(db.Integer, db.ForeignKey('ham_luong.id'))
    duong_dung_id = db.Column(db.Integer, db.ForeignKey('duong_dung.id'))
    dang_bao_che_id = db.Column(db.Integer, db.ForeignKey('dang_bao_che.id'))
    quy_cach_dong_goi_id = db.Column(db.Integer, db.ForeignKey('quy_cach_dong_goi.id'))
    don_vi_tinh_id = db.Column(db.Integer, db.ForeignKey('don_vi_tinh.id'))
    co_so_san_xuat_id = db.Column(db.Integer, db.ForeignKey('co_so_san_xuat.id'))
    nuoc_san_xuat_id = db.Column(db.Integer, db.ForeignKey('nuoc_san_xuat.id'))
    nha_thau_id = db.Column(db.Integer, db.ForeignKey('nha_thau.id'))
    nhom_thau_id = db.Column(db.Integer, db.ForeignKey('nhom_thau.id'))
    so_luong = db.Column(db.Integer)
    don_gia = db.Column(db.Float)
    thanh_tien = db.Column(db.BigInteger)
    dot_thau_id = db.Column(db.Integer, db.ForeignKey('dot_thau.id', ondelete='CASCADE', onupdate='CASCADE'),
                            nullable=False)
    import_history_id = db.Column(db.Integer,
                                  db.ForeignKey('import_history.id', ondelete='CASCADE', onupdate='CASCADE'),
                                  nullable=False)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id', ondelete='CASCADE', onupdate='CASCADE'),
                            nullable=False)

    def __repr__(self):
        return '<KetQuaTrungThau {}>'.format(self.thuoc.name)


class FileInformation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), index=True)
    time = db.Column(db.String(500))
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id', ondelete='CASCADE', onupdate='CASCADE'),
                            nullable=False)

    def __repr__(self):
        return '<FileInformation {}>'.format(self.name)


class KhoChan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Date, index=True)
    thuoc_id = db.Column(db.Integer, db.ForeignKey('thuoc.id'))
    nhap = db.Column(db.Integer)
    xuat = db.Column(db.Integer)
    ton = db.Column(db.Integer)
    file_id = db.Column(db.Integer, db.ForeignKey('file_information.id', ondelete='CASCADE', onupdate='CASCADE'),
                        nullable=False)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id', ondelete='CASCADE', onupdate='CASCADE'),
                            nullable=False)

    def __repr__(self):
        return '<KhoChan {}>'.format(self.time)


class KhoLe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Date, index=True)
    thuoc_id = db.Column(db.Integer, db.ForeignKey('thuoc.id'))
    nhap = db.Column(db.Integer)
    xuat = db.Column(db.Integer)
    ton = db.Column(db.Integer)
    file_id = db.Column(db.Integer, db.ForeignKey('file_information.id', ondelete='CASCADE', onupdate='CASCADE'),
                        nullable=False)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id', ondelete='CASCADE', onupdate='CASCADE'),
                            nullable=False)

    def __repr__(self):
        return '<KhoLe {}>'.format(self.time)


class TongHopThau(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Date, index=True)
    thuoc_id = db.Column(db.Integer, db.ForeignKey('thuoc.id'))
    tong_ke_hoach = db.Column(db.Integer)
    tong_su_dung = db.Column(db.Integer)
    con_lai = db.Column(db.Integer)
    ton_chan = db.Column(db.Integer)
    nhap_le_moi_nhat = db.Column(db.Integer)
    ton_le_moi_nhat = db.Column(db.Integer)
    trung_binh_nhap_chan = db.Column(db.Integer)
    so_lan_du_tru = db.Column(db.Float)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id', ondelete='CASCADE', onupdate='CASCADE'),
                            nullable=False)

    def __repr__(self):
        return '<TongHopThau {}>'.format(self.time)

    def to_dict(self):
        hoat_chat = self.thuoc.ketquatrungthaus[0].hoat_chat
        ham_luong = self.thuoc.ketquatrungthaus[0].ham_luong.name
        duong_dung = self.thuoc.ketquatrungthaus[0].duong_dung.name
        dang_bao_che = self.thuoc.ketquatrungthaus[0].dang_bao_che.name
        nhom_thau = self.thuoc.ketquatrungthaus[0].nhom_thau.name
        nhom_duoc_ly_bv = hoat_chat.nhom_duoc_ly_bv.name if hoat_chat.nhom_duoc_ly_bv else 'Chưa chọn nhóm dược lý'
        nhom_hoa_duoc_bv = hoat_chat.nhom_hoa_duoc_bv.name if hoat_chat.nhom_hoa_duoc_bv else 'Chưa chọn nhóm hoá dược'
        return [self.time, self.tong_ke_hoach, self.tong_su_dung, self.con_lai, self.nhap_le_moi_nhat,
                self.ton_le_moi_nhat, self.trung_binh_nhap_chan, self.so_lan_du_tru, self.thuoc_id, self.thuoc.name,
                hoat_chat.name, nhom_duoc_ly_bv, nhom_hoa_duoc_bv, nhom_thau, self.ton_chan, ham_luong, duong_dung,
                dang_bao_che]


class ThongKeKho(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ngay_nhap_chan = db.Column(db.Date, index=True)
    thuoc_id = db.Column(db.Integer, db.ForeignKey('thuoc.id'))
    nhap_chan = db.Column(db.Integer)
    ton_le_truoc_nhap_chan = db.Column(db.Integer)
    trung_binh_nhap_chan = db.Column(db.Integer)
    du_tru_con_lai = db.Column(db.Integer)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id', ondelete='CASCADE', onupdate='CASCADE'),
                            nullable=False)

    def __repr__(self):
        return '<ThongKeKho {}>'.format(self.ngay_nhap_chan)

    def to_dict(self):
        return [self.id, self.ngay_nhap_chan, self.thuoc_id, self.nhap_chan, self.ton_le_truoc_nhap_chan,
                self.trung_binh_nhap_chan, self.du_tru_con_lai]


class ImportHistoryNXT(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    month = db.Column(db.String(64), index=True)
    time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id', ondelete='CASCADE', onupdate='CASCADE'),
                            nullable=False)
    nxts = db.relationship('NXT', backref='import_history', cascade="all,delete", lazy='dynamic')

    def __repr__(self):
        return '<ImportHistoryNXT {}>'.format(self.name)

    def import_history_to_dict(self):
        return {'name': self.name, 'time': self.time, 'id': self.id, 'month': self.month}


class NXT(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    thuoc_id = db.Column(db.Integer, db.ForeignKey('thuoc.id'))
    nhap = db.Column(db.Integer)
    ton_bv = db.Column(db.Integer)
    xuat = db.Column(db.Integer)
    ton_cuoi_bv = db.Column(db.Integer)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id', ondelete='CASCADE', onupdate='CASCADE'),
                            nullable=False)
    import_history_id = db.Column(db.Integer,
                                  db.ForeignKey('import_history_nxt.id', ondelete='CASCADE', onupdate='CASCADE'),
                                  nullable=False)
    dot_thau_id = db.Column(db.Integer,
                            db.ForeignKey('dot_thau.id', ondelete='CASCADE', onupdate='CASCADE'))

    def __repr__(self):
        return '<NXT {}>'.format(self.thuoc.name)


class SuDungThuocABCVEN(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    thuoc = db.Column(db.String(500), index=True)
    hoat_chat = db.Column(db.String(500), index=True)
    biet_duoc = db.Column(db.String(1), index=True)
    generic = db.Column(db.String(1), index=True)
    ven = db.Column(db.String(1), index=True)
    noi_ngoai = db.Column(db.String(10), index=True)
    nhom_duoc_ly = db.Column(db.String(500), index=True)
    nhom_hoa_duoc = db.Column(db.String(500), index=True)
    nhom_thau = db.Column(db.String(10), index=True)
    don_vi_tinh = db.Column(db.String(100), index=True)
    so_luong = db.Column(db.Integer)
    thanh_tien = db.Column(db.BigInteger)
    phan_tram_tong_tien = db.Column(db.Float)
    xep_hang_abc = db.Column(db.Integer)
    phan_tram_tich_luy_tong_tien = db.Column(db.Float)
    nhom_abc = db.Column(db.String(1), index=True)
    abc_ven_matrix = db.Column(db.String(3), index=True)
    gop_abc_ven = db.Column(db.String(2), index=True)
    phan_tram_so_luong = db.Column(db.Float)
    phan_tram_so_luong_tich_luy = db.Column(db.Float)
    period = db.Column(db.Integer)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id', ondelete='CASCADE', onupdate='CASCADE'),
                            nullable=False)

    def __repr__(self):
        return '<SuDungThuocABCVEN {}>'.format(self.thuoc)
