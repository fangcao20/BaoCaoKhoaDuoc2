from datetime import datetime

from sqlalchemy import func

from app import db, app
from app.models import HoatChatTT20, HoatChatSYT, BietDuocGocSYT, SoYTe, ThongTu20, NhomDuocLy, NhomHoaDuoc, \
    NhomDuocLyBV, NhomHoaDuocBV, DotThau, Thuoc, HoatChat, DuongDung, DangBaoChe, HamLuong, QuyCachDongGoi, DonViTinh, \
    CoSoSanXuat, NuocSanXuat, NhomThau, NhaThau, ImportHistory, KetQuaTrungThau, FileInformation, ImportHistoryNXT, NXT
import pandas as pd

with app.app_context():
    # df = pd.read_excel("C:/Users/phuon/OneDrive/Desktop/Book1.xlsx")
    # for i in range(0, df.shape[0]):
    #     row = df.iloc[i].tolist()
    #     stt = row[0]
    #     hoat_chat = row[1]
    #     ndl = row[2].split('.')[1].strip().lower()
    #     ndl_id = NhomDuocLy.query.filter(func.lower(NhomDuocLy.name) == ndl).first().id
    #     nhd = row[5].strip().lower()
    #
    #     nhd_id = NhomHoaDuoc.query.filter(func.lower(NhomHoaDuoc.name) == nhd).first().id
    #     duong_dung = row[7]
    #     h = HoatChatTT20.query.filter_by(name=hoat_chat).first()
    #     if not h:
    #         h = HoatChatTT20(name=hoat_chat)
    #         db.session.add(h)
    #         db.session.flush()
    #     tt = ThongTu20(stt=stt, hoat_chat_tt20_id=h.id, nhom_duoc_ly_id=ndl_id, nhom_hoa_duoc_id=nhd_id, duong_dung=duong_dung)
    #     db.session.add(tt)
    # db.session.commit()

    # df = pd.read_excel("C:/Users/phuon/Downloads/Gói thầu thuốc dược liệu, thuốc cổ truyền năm 2021-2022 [BVQPN-2021-2022-DLCT-03].xlsx")
    # for i in range(1, df.shape[0]):
    #     row = df.iloc[i].tolist()
    #     hoat_chat = row[3]
    #     h = HoatChatSYT.query.filter_by(name=hoat_chat).first()
    #     if not h:
    #         h = HoatChatSYT(name=hoat_chat)
    #         db.session.add(h)
    #         db.session.flush()
    #     ma_he_thong = row[1]
    #     ma_thuoc = str(row[2])
    #     ham_luong = str(row[4]) if str(row[4]) != 'nan' else ''
    #     dang_bao_che = str(row[5]) if str(row[4]) != 'nan' else ''
    #     duong_dung = str(row[7]) if str(row[4]) != 'nan' else ''
    #     don_vi_tinh = str(row[8]) if str(row[4]) != 'nan' else ''
    #     nhom_thau = str(row[9]).capitalize()
    #     s = SoYTe(ma_he_thong=ma_he_thong, ma_thuoc=ma_thuoc, hoat_chat_syt_id=h.id,
    #               ham_luong=ham_luong, dang_bao_che=dang_bao_che, duong_dung=duong_dung, don_vi_tinh=don_vi_tinh,
    #               nhom_thau=nhom_thau)
    #     db.session.add(s)
    # db.session.commit()
    # dl = NhomDuocLy.query.all()
    # for d in dl:
    #     bv = NhomDuocLyBV(name=d.name)
    #     db.session.add(bv)

    # hd = NhomHoaDuoc.query.all()
    # for h in hd:
    #     bv = NhomHoaDuocBV(name=h.name)
    #     db.session.add(bv)
    # db.session.commit()
    #
    #
    # df = pd.read_excel("C:/Users/phuon/Downloads/Sl trúng thầu các gói thầu từ 4.2022-5.2023.xlsx")
    # for i in range(0, df.shape[0]):
    #     row = df.iloc[i].tolist()
    #     ngayQD = datetime.strptime(row[5], '%d/%m/%Y')
    #     ngayHH = datetime.strptime(row[6], '%d/%m/%Y')
    #     d = DotThau(code=row[0], name=row[1], phase=row[2], formality=row[3], soQD=row[4], ngayQD=ngayQD, ngayHH=ngayHH,
    #                 hospital_id=1)
    #     db.session.add(d)
    # db.session.commit()

    DM = ['thuoc', 'hoat_chat', 'ham_luong', 'duong_dung', 'dang_bao_che', 'quy_cach_dong_goi', 'don_vi_tinh',
          'co_so_san_xuat', 'nuoc_san_xuat', 'nha_thau', 'nhom_thau', 'nhom_duoc_ly', 'nhom_hoa_duoc']
    IDS = ['thuoc_id', 'hoat_chat_id', 'ham_luong_id', 'duong_dung_id', 'dang_bao_che_id', 'quy_cach_dong_goi_id',
           'don_vi_tinh_id', 'co_so_san_xuat_id', 'nuoc_san_xuat_id', 'nha_thau_id', 'nhom_thau_id']
    MODELS = [Thuoc, HoatChat, HamLuong, DuongDung, DangBaoChe, QuyCachDongGoi, DonViTinh, CoSoSanXuat, NuocSanXuat,
              NhaThau, NhomThau, NhomDuocLyBV, NhomHoaDuocBV]
    COLUMNS = ['Tên thuốc', 'Hoạt chất', 'Hàm lượng', 'Đường dùng', 'Dạng bào chế', 'Quy cách đóng gói', 'Đơn vị tính',
               'Cơ sở sản xuất', 'Nước sản xuất', 'Nhà thầu', 'Nhóm thầu', 'Nhóm dược lý', 'Nhóm hoá dược']

    hospital_id = 1
    df = pd.read_excel("C:/Users/phuon/OneDrive/Desktop/Thẻ kho/KQTT.xlsx")
    for k in range(0, 882):
        try:
            thau = df.loc[k, 'Thầu'].strip()
        except Exception as e:
            print(e)
            print(k)
        dot_thau_id = DotThau.query.filter_by(code=thau).first().id
        ih = ImportHistory.query.filter_by(dot_thau_id=dot_thau_id).first()
        if ih:
            import_history_id = ih.id
        else:
            ih = ImportHistory(dot_thau_id=dot_thau_id, hospital_id=hospital_id)
            db.session.add(ih)
            db.session.flush()
            import_history_id = ih.id
        kq = KetQuaTrungThau(hospital_id=hospital_id, dot_thau_id=dot_thau_id, import_history_id=import_history_id)
        for i in range(len(MODELS) - 3):
            if COLUMNS[i] == "Tên thuốc":
                thuoc = df.loc[k, "Mã thuốc BV"].strip() if str(df.loc[k, "Mã thuốc BV"]) != 'nan' else ''
                if thuoc != '':
                    thuoc_db = Thuoc.query.filter(Thuoc.codeBV == thuoc, Thuoc.hospital_id == hospital_id).first()
                else:
                    thuoc_db = None
                if not thuoc_db:
                    try:
                        t = Thuoc(name=df.loc[k, "Tên thuốc"].strip(), cch=f';{df.loc[k, "Tên thuốc"].strip()};',
                                  sdk=df.loc[k, "SĐK"].strip() if str(df.loc[k, "SĐK"]) != 'nan' else '',
                                  codeBV=df.loc[k, 'Mã thuốc BV'],
                                  ven=df.loc[k, 'VEN'],
                                  hospital_id=hospital_id)
                    except Exception as e:
                        print(e)
                        print(k)

                    db.session.add(t)
                    db.session.flush()
                    t.code = f'TH{t.id:05}'
                    thuoc_id = t.id
                else:
                    thuoc_id = thuoc_db.id
                kq.thuoc_id = thuoc_id
            elif COLUMNS[i] == "Hoạt chất":
                hoatchat = df.loc[k, "Hoạt chất"].strip()
                hoatchat_db = HoatChat.query.filter(HoatChat.cch.ilike(f';{hoatchat};'),
                                                    HoatChat.hospital_id == hospital_id).first()
                if not hoatchat_db:
                    h = HoatChat(name=hoatchat, cch=f';{hoatchat};', hospital_id=hospital_id)
                    hcsyt = HoatChatSYT.query.filter(func.lower(HoatChatSYT.name) == hoatchat.lower()).first()
                    if hcsyt:
                        h.hoat_chat_syt_id = hcsyt.id
                    hctt20 = HoatChatTT20.query.filter(func.lower(HoatChatTT20.name) == hoatchat.lower()).first()
                    if hctt20:
                        h.hoat_chat_tt20_id = hctt20.id
                        h.nhom_duoc_ly_bv_id = NhomDuocLyBV.query.filter_by(
                            name=hctt20.tt20[0].nhom_duoc_ly.name).first().id
                        h.nhom_hoa_duoc_bv_id = NhomHoaDuocBV.query.filter_by(
                            name=hctt20.tt20[0].nhom_hoa_duoc.name).first().id
                    db.session.add(h)
                    db.session.flush()
                    h.code = f'HC{h.id:05}'
                    hoat_chat_id = h.id
                else:
                    hoat_chat_id = hoatchat_db.id
                kq.hoat_chat_id = hoat_chat_id
            elif COLUMNS[i] == "Nước sản xuất":
                nuocsanxuat = df.loc[k, 'Nước sản xuất'].strip()
                nuocsanxuat_db = NuocSanXuat.query.filter(NuocSanXuat.cch.ilike(f';{nuocsanxuat};'),
                                                          NuocSanXuat.hospital_id == hospital_id).first()
                if not nuocsanxuat_db:
                    n = NuocSanXuat(name=nuocsanxuat, cch=f';{nuocsanxuat};', hospital_id=hospital_id)
                    if nuocsanxuat.lower() in ['việt nam', 'vn']:
                        n.place = 'Nội'
                    else:
                        n.place = 'Ngoại'
                    db.session.add(n)
                    db.session.flush()
                    nuoc_san_xuat_id = n.id
                else:
                    nuoc_san_xuat_id = nuocsanxuat_db.id
                kq.nuoc_san_xuat_id = nuoc_san_xuat_id
            else:
                id_name = IDS[i]
                obj = str(df.loc[k, COLUMNS[i]]).strip() if str(df.loc[k, COLUMNS[i]]) != 'nan' else ''
                if obj != '':
                    obj_db = MODELS[i].query.filter(MODELS[i].cch.ilike(f';{obj};'),
                                                    MODELS[i].hospital_id == hospital_id).first()
                else:
                    obj_db = None
                if not obj_db:
                    ob = MODELS[i](name=obj, cch=f';{obj};', hospital_id=hospital_id)
                    db.session.add(ob)
                    db.session.flush()
                    setattr(kq, id_name, ob.id)
                else:
                    setattr(kq, id_name, obj_db.id)

        if str(df.loc[k, 'Nhóm thầu']) == 'nan':
            nhom_thau_id = 7
        else:
            nhom_thau_id = NhomThau.query.filter(
                func.lower(NhomThau.name).ilike(func.lower(df.loc[k, 'Nhóm thầu'].strip()))).first().id
        so_luong = int(df.loc[k, 'Số lượng']) if str(df.loc[k, 'Số lượng']) != 'nan' else 0
        don_gia = float(df.loc[k, 'Đơn giá']) if str(df.loc[k, 'Đơn giá']) != 'nan' else 0
        thanh_tien = int(df.loc[k, 'Thành tiền']) if str(df.loc[k, 'Thành tiền']) != 'nan' else 0

        kq.nhom_thau_id = nhom_thau_id
        kq.so_luong = so_luong
        kq.thanh_tien = thanh_tien
        kq.don_gia = don_gia
        db.session.add(kq)
    db.session.commit()

    #
    # results = Thuoc.query.all()
    # list_name = []
    # list_thuoc = []
    # for t in results:
    #     name = t.name
    #     if name not in list_name:
    #         list_name.append(name)
    #         list_thuoc.append(t)
    #     else:
    #         index = list_name.index(name)
    #         thuoc = list_thuoc[index]
    #         t.code = thuoc.code
    # db.session.commit()

    # df = pd.read_excel("C:/Users/phuon/OneDrive/Desktop/Book1.xlsx")
    # for i in range(0, df.shape[0]):
    #     row = df.iloc[i].tolist()
    #     hoat_chat_id = row[0]
    #     stt_tt20 = int(row[1])
    #     ndl = int(row[2])
    #
    #     hc = HoatChat.query.get(int(hoat_chat_id))
    #     tt20 = ThongTu20.query.filter_by(stt=stt_tt20).first()
    #     hc_tt20_id = tt20.hoat_chat_tt20_id
    #     nhd_id = tt20.nhom_hoa_duoc_id
    #
    #     nhomhoaduoc = NhomHoaDuoc.query.get(nhd_id)
    #     nhd_name = nhomhoaduoc.name
    #     nhd_bv = NhomHoaDuocBV.query.filter_by(name=nhd_name, hospital_id=1).first()
    #     if hc:
    #         hc.hoat_chat_tt20_id = hc_tt20_id
    #         hc.nhom_duoc_ly_bv_id = ndl
    #         hc.nhom_hoa_duoc_bv_id = nhd_bv.id
    # db.session.commit()

    # df = pd.read_excel("C:/Users/phuon/Downloads/TT20 đã thêm phân nhóm Hóa Dược.xlsx")
    # for i in range(0, df.shape[0]):
    #     row = df.iloc[i].tolist()
    #     stt = row[0]
    #     nhd_name = row[-1]
    #     print(stt, nhd_name)
    #     tt20 = ThongTu20.query.filter_by(stt=stt).first()
    #     nhd = NhomHoaDuoc.query.filter_by(name=nhd_name).first()
    #
    #     tt20.nhom_hoa_duoc_id = nhd.id
    # db.session.commit()

    # hc = HoatChat.query.all()
    # for h in hc:
    #     if h.hoat_chat_tt20_id is not None:
    #         tt20 = ThongTu20.query.filter_by(hoat_chat_tt20_id=h.hoat_chat_tt20_id).first()
    #         h.nhom_hoa_duoc_bv_id = tt20.nhom_hoa_duoc_id
    # db.session.commit()

