from app import app, db
from app.models import User, AccessControl, Hospital, DotThau, ImportHistory, NhomThau, KetQuaTrungThau, NhomDuocLy, \
    HoatChat, NhomHoaDuoc, NhomDuocLyBV, ThongTu20, HoatChatTT20, NXT, ImportHistoryNXT, SuDungThuocABCVEN


if __name__ == "__main__":
    app.run(debug=True)


def make_shell_context():
    return {'db': db, 'User': User, 'AccessControl': AccessControl, 'Hospital': Hospital, 'DotThau': DotThau,
            'ImportHistory': ImportHistory, 'NhomThau': NhomThau, 'KetQuaTrungThau': KetQuaTrungThau,
            'NhomDuocLy': NhomDuocLy, 'HoatChat': HoatChat, 'NhomHoaDuoc': NhomHoaDuoc, 'NhomDuocLyBV': NhomDuocLyBV,
            'ThongTu20': ThongTu20, 'HoatChatTT20': HoatChatTT20, 'NXT': NXT, 'ImportHistoryNXT': ImportHistoryNXT,
            'SuDungThuocABCVEN': SuDungThuocABCVEN}
