from app import app, db
from app.models import User, AccessControl, Hospital, DotThau, ImportHistory, NhomThau, KetQuaTrungThau, NhomDuocLy1, \
    HoatChat, NhomHoaDuoc, NhomDuocLy1BV, NhomDuocLy2, NhomDuocLy2BV, ATC, NXT, ImportHistoryNXT, SuDungThuocABCVEN, \
    NhomHoaDuocBV


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")


def make_shell_context():
    return {'db': db, 'User': User, 'AccessControl': AccessControl, 'Hospital': Hospital, 'DotThau': DotThau,
            'ImportHistory': ImportHistory, 'NhomThau': NhomThau, 'KetQuaTrungThau': KetQuaTrungThau,
            'NhomDuocLy1': NhomDuocLy1, 'NhomDuocLy2': NhomDuocLy2, 'HoatChat': HoatChat, 'NhomHoaDuoc': NhomHoaDuoc,
            'NhomDuocLy1BV': NhomDuocLy1BV, 'NhomDuocLy2BV': NhomDuocLy2BV, 'NhomHoaDuocBV': NhomHoaDuocBV, 'ATC': ATC,
            'NXT': NXT, 'ImportHistoryNXT': ImportHistoryNXT,
            'SuDungThuocABCVEN': SuDungThuocABCVEN}
