from datetime import timedelta, datetime
from urllib.parse import urlsplit

import pandas as pd
from flask import render_template, flash, redirect, url_for, request, jsonify, get_flashed_messages
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy import func, case, desc

from app import app, db
from app.email import send_password_reset_email
from app.forms import LoginForms, ChangePasswordForm, ResetPasswordRequestForm, ResetPasswordForm, InputDotThau
from app.models import User, AccessControl, DotThau, ImportHistory, Thuoc, HoatChat, HamLuong, DuongDung, DangBaoChe, \
    QuyCachDongGoi, DonViTinh, CoSoSanXuat, NuocSanXuat, NhaThau, NhomThau, KetQuaTrungThau, NhomDuocLy1, NhomHoaDuoc, \
    FileInformation, KhoChan, KhoLe, ThongKeKho, TongHopThau, HoatChatSYT, NhomDuocLy1BV, \
    NhomHoaDuocBV, ImportHistoryNXT, NXT, SuDungThuocABCVEN, SuDungTheoThang, NhomDuocLy2BV, ATC


@app.route('/dang-nhap', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForms()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Tên đăng nhập hoặc mật khẩu không chính xác.', 'info')
            return redirect(url_for('login'))
        login_user(user)
        next_page = request.args.get(next)
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', form=form)


@app.route('/dang-xuat')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/<username>/doi-mat-khau', methods=['GET', 'POST'])
@login_required
def change_password(username):
    user = User.query.filter_by(username=username).first_or_404()
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if user.check_password(form.old_password.data):
            user.set_password(form.new_password.data)
            db.session.commit()
            flash('Đổi mật khẩu thành công!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Mật khẩu không chính xác!', 'danger')
            # return redirect(url_for('change_password', username=current_user.username))
    return render_template("change_password.html", user=current_user, form=form)


@app.route('/quen-mat-khau', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user:
            flash('Tên đăng nhập không chính xác!', 'danger')
        elif user.role != 'A':
            flash('Chỉ có admin mới được đặt lại mật khẩu. Nhân viên vui lòng liên hệ admin để đặt lại mật khẩu.',
                  'info')
        else:
            email = user.hospital.email
            send_password_reset_email(user, email)
            flash(f'Vui lòng kiểm tra {email} để đặt lại mật khẩu.', 'info')
            return redirect(url_for('login'))
    return render_template('reset_password_request.html', user=current_user, form=form)


@app.route('/dat-lai-mat-khau/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        flash('Liên kết đã hết hạn. Vui lòng thực hiện lại!', 'info')
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Mật khẩu của bạn đã được đặt lại.', 'success')
        return redirect(url_for('login'))
    return render_template('reset_password.html', user=current_user, form=form)


@app.route('/<url>/phan-quyen', methods=['GET', 'POST'])
@login_required
def set_accesses(url):
    hospital = current_user.hospital
    employees = User.query.filter(User.hospital == hospital, User.role == 'E').all()
    return render_template('access_control.html', user=current_user, employees=employees)


@app.route('/add-employee', methods=['POST'])
@login_required
def add_employee():
    username = request.form['username']
    if username == '':
        flash('Vui lòng nhập tên đăng nhập cho nhân viên.', 'danger')
    elif User.query.filter_by(username=username).first():
        flash('Tên đăng nhập đã tồn tại, vui lòng nhập tên đăng nhập khác.', 'danger')
    else:
        accesses = request.form.getlist('accesses[]')
        if len(accesses) < 1:
            flash('Vui lòng chọn ít nhất 1 quyền.', 'danger')
        else:
            u = User(username=username, role='E', hospital_id=current_user.hospital.id)
            u.set_password('123123')
            db.session.add(u)

            for a in accesses:
                u.set_access(AccessControl.query.get(int(a)))
            db.session.commit()
            flash(f'Thêm nhân viên {username} thành công.', 'success')
            flash_messages = [{'category': category, 'message': message} for category, message in
                              get_flashed_messages(with_categories=True)]
            employees = User.query.filter(User.hospital == current_user.hospital, User.role == 'E').all()
            employees_list = []
            for e in employees:
                employees_list.append(e.user_to_dict())
            return jsonify({'flash_messages': flash_messages, 'employees': employees_list})
    flash_messages = [{'category': category, 'message': message} for category, message in
                      get_flashed_messages(with_categories=True)]
    return jsonify({'flash_messages': flash_messages})


@app.route('/delete-employee', methods=['POST'])
@login_required
def delete_employee():
    username = request.form['username']
    if username == '':
        flash('Vui lòng chọn 1 nhân viên trong bảng để xoá.', 'danger')
    elif User.query.filter_by(username=username).first():
        db.session.delete(User.query.filter_by(username=username).first())
        db.session.commit()
        flash(f'Đã xoá {username} thành công.', 'success')
        flash_messages = [{'category': category, 'message': message} for category, message in
                          get_flashed_messages(with_categories=True)]
        employees = User.query.filter(User.hospital == current_user.hospital, User.role == 'E').all()
        employees_list = []
        for e in employees:
            employees_list.append(e.user_to_dict())
        return jsonify({'flash_messages': flash_messages, 'employees': employees_list})
    else:
        flash('Vui lòng chọn 1 nhân viên trong bảng để xoá.', 'danger')
    flash_messages = [{'category': category, 'message': message} for category, message in
                      get_flashed_messages(with_categories=True)]
    return jsonify({'flash_messages': flash_messages})


@app.route('/<url>/nhap-ket-qua-trung-thau', methods=['GET', 'POST'])
@login_required
def nhap_ket_qua_trung_thau(url):
    form = InputDotThau()
    choices = {
        'rr': 'Đấu thầu rộng rãi',
        'hc': 'Đấu thầu hạn chế',
        'cd': 'Chỉ định thầu',
        'ch': 'Chào hàng cạnh tranh',
        'ms': 'Mua sắm trực tiếp',
        'tth': 'Tự thực hiện'
    }
    if form.validate_on_submit():
        if form.submit.data:
            if DotThau.query.filter(DotThau.code == form.code.data,
                                    DotThau.hospital_id == current_user.hospital.id).first():
                flash('Trùng mã đợt thầu, vui lòng đặt lại.', 'danger')
            else:
                dt = DotThau(code=form.code.data, name=form.name.data, phase=form.phase.data,
                             formality=choices.get(form.formality.data, ''),
                             soQD=form.soQD.data, ngayQD=form.ngayQD.data, ngayHH=form.ngayHH.data, note=form.note.data,
                             hospital_id=current_user.hospital.id)
                db.session.add(dt)
                db.session.commit()
                return redirect(url_for('nhap_ket_qua_trung_thau', url=current_user.hospital.url))
        elif form.update.data:
            dt = DotThau.query.filter_by(id=int(form.id.data)).first()
            dt.code = form.code.data
            dt.name = form.name.data
            dt.phase = form.phase.data
            dt.formality = choices.get(form.formality.data, '')
            dt.soQD = form.soQD.data
            dt.ngayQD = form.ngayQD.data
            dt.ngayHH = form.ngayHH.data
            dt.note = form.note.data
            db.session.commit()
            return redirect(url_for('nhap_ket_qua_trung_thau', url=current_user.hospital.url))
        elif form.delete.data:
            dt = DotThau.query.filter_by(id=int(form.id.data)).first()
            db.session.delete(dt)
            db.session.commit()
            return redirect(url_for('nhap_ket_qua_trung_thau', url=current_user.hospital.url))
    dot_thau = DotThau.query.filter_by(hospital=current_user.hospital).all()
    import_history = ImportHistory.query.filter_by(hospital=current_user.hospital).order_by(
        ImportHistory.time.desc()).all()
    return render_template('nhap_ket_qua_trung_thau.html', user=current_user, form=form,
                           dot_thau=dot_thau, import_history=import_history)


@app.route('/nhap-ket-qua-trung-thau-1', methods=['POST', 'GET'])
@login_required
def ket_qua_trung_thau():
    dot_thau = DotThau.query.filter_by(hospital=current_user.hospital).all()
    codes = [(g.id, g.code) for g in dot_thau]
    if 'id' in request.form:
        id = request.form['id']
        dt = DotThau.query.filter_by(id=int(id)).first()

        results = KetQuaTrungThau.query.filter(KetQuaTrungThau.hospital_id == current_user.hospital.id,
                                               KetQuaTrungThau.dot_thau_id == dt.id).all()
        bao_cao_dict = []
        for r in results:
            try:
                tht = TongHopThau.query.filter_by(thuoc_id=r.thuoc_id).first()
                if tht:
                    tong_su_dung = tht.tong_su_dung
                    con_lai = tht.con_lai if tht.con_lai != 0 else '0'
                else:
                    tong_su_dung = '0'
                    con_lai = r.so_luong
                bao_cao_dict.append(
                    {'Mã thuốc BV': r.thuoc.codeBV, 'Tên thuốc': r.thuoc.name, 'Hoạt chất': r.hoat_chat.name,
                     'Hàm lượng': r.ham_luong.name,
                     'SĐK': r.thuoc.sdk, 'Đường dùng': r.duong_dung.name,
                     'Nhóm Dược lý 1': r.hoat_chat.nhom_duoc_ly1_bv.name if r.hoat_chat.nhom_duoc_ly1_bv else '',
                     'Nhóm Dược lý 2': r.hoat_chat.nhom_duoc_ly2_bv.name if r.hoat_chat.nhom_duoc_ly2_bv else '',
                     'Nhóm Hóa dược': r.hoat_chat.nhom_hoa_duoc_bv.name if r.hoat_chat.nhom_hoa_duoc_bv else '',
                     'Dạng bào chế': r.dang_bao_che.name, 'Quy cách đóng gói': r.quy_cach_dong_goi.name,
                     'Đơn vị tính': r.don_vi_tinh.name, 'Cơ sở sản xuất': r.co_so_san_xuat.name,
                     'Nước sản xuất': r.nuoc_san_xuat.name, 'Nội/Ngoại': r.nuoc_san_xuat.place,
                     'Nhà thầu': r.nha_thau.name, 'Nhóm thầu': r.nhom_thau.name,
                     'Kế hoạch': r.so_luong,
                     'Sử dụng': tong_su_dung,
                     'Còn lại': con_lai})
            except Exception as e:
                print(e)
                break
        return jsonify(dot_thau_dict=dt.dot_thau_to_dict(), codes=codes, bao_cao_dict=bao_cao_dict)
    dot_thau_dict = [dt.dot_thau_to_dict() for dt in dot_thau]
    import_history = ImportHistory.query.filter_by(hospital=current_user.hospital).order_by(
        ImportHistory.time.desc()).all()
    import_history_dict = []
    for i in import_history:
        import_history_dict.append(i.import_history_to_dict())
    return jsonify(codes=codes, dot_thau_dict=dot_thau_dict, import_history_dict=import_history_dict)


@app.route('/end-dot-thau', methods=['POST'])
@login_required
def end_dot_thau():
    state = request.form['state']
    dot_thau_id = int(request.form['dot_thau_id'])

    dt = DotThau.query.get(dot_thau_id)
    if state == 'true':
        dt.end = 1
        db.session.commit()
        return jsonify(message=f'Đã kết thúc đợt thầu {dt.code}.')
    else:
        dt.end = None
        db.session.commit()
        return jsonify(message=f'Đợt thầu {dt.code} tiếp tục.')


DM = ['thuoc', 'hoat_chat', 'ham_luong', 'duong_dung', 'dang_bao_che', 'quy_cach_dong_goi', 'don_vi_tinh',
      'co_so_san_xuat', 'nuoc_san_xuat', 'nha_thau', 'nhom_thau', 'nhom_duoc_ly', 'nhom_hoa_duoc']
IDS = ['thuoc_id', 'hoat_chat_id', 'ham_luong_id', 'duong_dung_id', 'dang_bao_che_id', 'quy_cach_dong_goi_id',
       'don_vi_tinh_id', 'co_so_san_xuat_id', 'nuoc_san_xuat_id', 'nha_thau_id', 'nhom_thau_id']
MODELS = [Thuoc, HoatChat, HamLuong, DuongDung, DangBaoChe, QuyCachDongGoi, DonViTinh, CoSoSanXuat, NuocSanXuat,
          NhaThau, NhomThau, NhomDuocLy1BV, NhomHoaDuocBV]
COLUMNS = ['Tên thuốc', 'Hoạt chất', 'Hàm lượng', 'Đường dùng', 'Dạng bào chế', 'Quy cách đóng gói', 'Đơn vị tính',
           'Cơ sở sản xuất', 'Nước sản xuất', 'Nhà thầu', 'Nhóm thầu', 'Nhóm dược lý', 'Nhóm hoá dược']


@app.route('/save-file', methods=['POST'])
@login_required
def save_file():
    try:
        hospital_id = current_user.hospital.id
        data = request.get_json()
        dt = DotThau.query.filter(
            DotThau.id == int(data['maDotThau']), DotThau.hospital_id == current_user.hospital.id).first()
        dot_thau_id = dt.id
        ih = ImportHistory(dot_thau_id=dot_thau_id, hospital_id=hospital_id, time=func.now())
        db.session.add(ih)
        db.session.flush()
        import_history_id = ih.id
        results = data['data']
        for r in results:
            kq = KetQuaTrungThau(hospital_id=hospital_id, dot_thau_id=dot_thau_id, import_history_id=import_history_id)
            for i in range(len(MODELS) - 3):
                if COLUMNS[i] == "Tên thuốc":
                    thuoc = r["Mã thuốc BV"].strip()
                    thuoc_db = Thuoc.query.filter(Thuoc.codeBV == thuoc, Thuoc.hospital_id == hospital_id).first()
                    if not thuoc_db:
                        thuoc_cung_ten = Thuoc.query.filter(func.lower(Thuoc.name) == r["Tên thuốc"].strip().lower(),
                                                            Thuoc.hospital_id == hospital_id).first()
                        t = Thuoc(name=r["Tên thuốc"].strip(), show="1", sdk=r['SĐK'],
                                  codeBV=r['Mã thuốc BV'], ven=r['VEN'], hospital_id=hospital_id)
                        db.session.add(t)
                        db.session.flush()

                        if thuoc_cung_ten:
                            t.code = thuoc_cung_ten.code
                            print(thuoc_cung_ten)
                        else:
                            t.code = f'TH{t.id:05}'
                        thuoc_id = t.id
                    else:
                        thuoc_id = thuoc_db.id
                    kq.thuoc_id = thuoc_id
                elif COLUMNS[i] == "Hoạt chất":
                    hoatchat = r["Hoạt chất"].strip()
                    hoatchat_db = HoatChat.query.filter(func.lower(HoatChat.name == hoatchat.lower()),
                                                        HoatChat.hospital_id == hospital_id).first()
                    if not hoatchat_db:
                        h = HoatChat(name=hoatchat, show="1", hospital_id=hospital_id)
                        hcsyt = HoatChatSYT.query.filter(func.lower(HoatChatSYT.name) == hoatchat.lower()).first()
                        if hcsyt:
                            h.hoat_chat_syt_id = hcsyt.id
                        atc = ATC.query.filter(func.lower(ATC.name) == hoatchat.lower()).first()
                        if atc:
                            h.atc_id = atc.id
                            h.nhom_duoc_ly1_bv_id = NhomDuocLy1BV.query. \
                                filter_by(hospital_id=hospital_id, nhom_duoc_ly1_id=atc.nhom_duoc_ly1_id).first().id
                            h.nhom_duoc_ly2_bv_id = NhomDuocLy2BV.query. \
                                filter_by(hospital_id=hospital_id, nhom_duoc_ly2_id=atc.nhom_duoc_ly2_id).first().id
                            h.nhom_hoa_duoc_bv_id = NhomHoaDuocBV.query. \
                                filter_by(hospital_id=hospital_id, nhom_hoa_duoc_id=atc.nhom_hoa_duoc_id).first().id
                        db.session.add(h)
                        db.session.flush()
                        h.code = f'HC{h.id:05}'
                        hoat_chat_id = h.id
                    else:
                        hoat_chat_id = hoatchat_db.id
                    kq.hoat_chat_id = hoat_chat_id
                elif COLUMNS[i] == "Nước sản xuất":
                    nuocsanxuat = r['Nước sản xuất'].strip()
                    nuocsanxuat_db = NuocSanXuat.query.filter(func.lower(NuocSanXuat.name) == nuocsanxuat.lower(),
                                                              NuocSanXuat.hospital_id == hospital_id).first()
                    if not nuocsanxuat_db:
                        n = NuocSanXuat(name=nuocsanxuat, show="1", hospital_id=hospital_id)
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
                    obj = r[COLUMNS[i]].strip()
                    obj_db = MODELS[i].query.filter(func.lower(MODELS[i].name) == obj.lower(),
                                                    MODELS[i].hospital_id == hospital_id).first()
                    if not obj_db:
                        if obj == "":
                            obj = "N/A"
                        ob = MODELS[i](name=obj, show="1", hospital_id=hospital_id)
                        db.session.add(ob)
                        db.session.flush()
                        setattr(kq, id_name, ob.id)
                    else:
                        setattr(kq, id_name, obj_db.id)
            nhom_thau = NhomThau.query.filter(
                func.lower(NhomThau.name).ilike(func.lower(r['Nhóm thầu'].strip()))).first()
            if nhom_thau:
                nhom_thau_id = nhom_thau.id
            else:
                nhom_thau_id = NhomThau.query.filter_by(name='None').first().id

            so_luong_str = r['Số lượng'].replace(',', '').replace('.', '')
            don_gia_str = r['Đơn giá'].replace(',', '').replace('.', '')
            thanh_tien_str = r['Thành tiền'].replace(',', '').replace('.', '')

            so_luong = int(so_luong_str) if so_luong_str else 0
            don_gia = float(don_gia_str) if don_gia_str else 0.0
            thanh_tien = int(thanh_tien_str) if thanh_tien_str else 0

            kq.nhom_thau_id = nhom_thau_id
            kq.so_luong = so_luong
            kq.thanh_tien = thanh_tien
            kq.don_gia = don_gia
            db.session.add(kq)

        db.session.commit()
        import_history = ImportHistory.query.filter_by(hospital=current_user.hospital).order_by(
            ImportHistory.time.desc()).all()
        import_history_dict = []
        for i in import_history:
            import_history_dict.append(i.import_history_to_dict())
        return jsonify(import_history_dict=import_history_dict)
    except Exception as e:
        print(e)
        return jsonify({'message': 'Đã có lỗi xảy ra, vui lòng thử lại sau.'})


@app.route('/delete-import-history', methods=['POST'])
@login_required
def delete_import_history():
    id = int(request.form['id'])
    ih = ImportHistory.query.get(id)
    db.session.delete(ih)
    db.session.commit()
    import_history = ImportHistory.query.filter_by(hospital=current_user.hospital).order_by(
        ImportHistory.time.desc()).all()
    import_history_dict = []
    for i in import_history:
        import_history_dict.append(i.import_history_to_dict())
    return jsonify(import_history_dict=import_history_dict)


@app.route('/bao-cao-tong-hop', methods=['POST'])
@login_required
def bao_cao():
    results = KetQuaTrungThau.query.filter_by(hospital=current_user.hospital).all()
    bao_cao_dict = []
    for r in results:
        try:
            bao_cao_dict.append(
                {'Tên thuốc': r.thuoc.name, 'Hoạt chất': r.hoat_chat.name, 'Hàm lượng': r.ham_luong.name,
                 'Mã thuốc BV': r.thuoc.codeBV,
                 'SĐK': r.thuoc.sdk, 'Đường dùng': r.duong_dung.name,
                 'Nhóm Dược lý 1': r.hoat_chat.nhom_duoc_ly1_bv.name if r.hoat_chat.nhom_duoc_ly1_bv else '',
                 'Nhóm Dược lý 2': r.hoat_chat.nhom_duoc_ly2_bv.name if r.hoat_chat.nhom_duoc_ly2_bv else '',
                 'Nhóm Hóa dược': r.hoat_chat.nhom_hoa_duoc_bv.name if r.hoat_chat.nhom_hoa_duoc_bv else '',
                 'Dạng bào chế': r.dang_bao_che.name, 'Quy cách đóng gói': r.quy_cach_dong_goi.name,
                 'Đơn vị tính': r.don_vi_tinh.name, 'Cơ sở sản xuất': r.co_so_san_xuat.name,
                 'Nước sản xuất': r.nuoc_san_xuat.name, 'Nội/Ngoại': r.nuoc_san_xuat.place,
                 'Nhà thầu': r.nha_thau.name, 'Nhóm thầu': r.nhom_thau.name,
                 'Số lượng': r.so_luong,
                 'Đơn giá': r.don_gia, 'Thành tiền': r.thanh_tien, 'VEN': r.thuoc.ven,
                 'Đợt thầu': r.dot_thau.code,
                 'Số QĐ': r.dot_thau.soQD,
                 'Ngày QĐ': str(r.dot_thau.ngayQD),
                 'Ngày hết hạn': str(r.dot_thau.ngayHH)})
        except Exception as e:
            print(e)
            break
    return jsonify(bao_cao_dict=bao_cao_dict)


@app.route('/<url>/danh-muc', methods=['POST', 'GET'])
@login_required
def danh_muc(url):
    return render_template('danh_muc.html', user=current_user)


@app.route('/get-danh-muc', methods=['GET'])
def get_danh_muc():
    danh_muc_dict = {}
    tables = [
        (Thuoc, 'thuoc_dict'),
        (HoatChat, 'hoat_chat_dict'),
        (HamLuong, 'ham_luong_dict'),
        (NhomHoaDuocBV, 'nhom_hoa_duoc_dict'),
        (NhomDuocLy1BV, 'nhom_duoc_ly1_dict'),
        (NhomDuocLy2BV, 'nhom_duoc_ly2_dict'),
        (DuongDung, 'duong_dung_dict'),
        (DangBaoChe, 'dang_bao_che_dict'),
        (QuyCachDongGoi, 'quy_cach_dong_goi_dict'),
        (DonViTinh, 'don_vi_tinh_dict'),
        (CoSoSanXuat, 'co_so_san_xuat_dict'),
        (NuocSanXuat, 'nuoc_san_xuat_dict'),
        (NhaThau, 'nha_thau_dict'),
        (NhomThau, 'nhom_thau_dict'),
        (HoatChatSYT, 'hoat_chat_syt_dict'),
        (ATC, 'hoat_chat_bhyt_dict'),
    ]

    for table, variable_name in tables:
        query = table.query
        if hasattr(table, 'hospital'):
            query = query.filter_by(hospital=current_user.hospital, show="1")
        query = query.order_by(table.name.asc())
        result = [t.danh_muc_to_dict() for t in query.all()]
        danh_muc_dict[variable_name] = result
    return jsonify(danh_muc=danh_muc_dict)


@app.route('/get-nhom-dl-hd', methods=['POST'])
def get_nhom_dl_hd():
    atc_id = int(request.form.get('id'))
    atc = ATC.query.get(int(atc_id))
    if atc:
        return jsonify(nhom_dl_hd=atc.nhom_dl_hd())
    else:
        return {'message': 'Đã có lỗi xảy ra, vui lòng thử lại sau.'}


@app.route('/luu-hoat-chat', methods=['POST'])
def luu_hoat_chat():
    hoat_chat_id = request.form.get('hoat_chat_id').strip()
    nhom_duoc_ly1_bv_id = request.form.get('nhom_duoc_ly1_bv_id')
    nhom_duoc_ly2_bv_id = request.form.get('nhom_duoc_ly2_bv_id')
    nhom_hoa_duoc_bv_id = request.form.get('nhom_hoa_duoc_bv_id')
    hoat_chat_bhyt_id = request.form.get('hoat_chat_bhyt_id')
    hoat_chat_syt_id = request.form.get('hoat_chat_syt_id')
    hc = HoatChat.query.filter_by(id=int(hoat_chat_id)).first()
    if nhom_duoc_ly1_bv_id != '':
        hc.nhom_duoc_ly1_bv_id = int(nhom_duoc_ly1_bv_id)
    if nhom_duoc_ly2_bv_id != '':
        hc.nhom_duoc_ly2_bv_id = int(nhom_duoc_ly2_bv_id)
    if nhom_hoa_duoc_bv_id != '':
        hc.nhom_hoa_duoc_bv_id = int(nhom_hoa_duoc_bv_id)
    if hoat_chat_bhyt_id != '':
        hc.atc_id = int(hoat_chat_bhyt_id)
    if hoat_chat_syt_id != '':
        hc.hoat_chat_syt_id = int(hoat_chat_syt_id)
    db.session.commit()
    query = HoatChat.query.filter_by(hospital_id=current_user.hospital.id, show="1").order_by(HoatChat.name.asc()).all()
    danh_muc_hoat_chat = [t.danh_muc_to_dict() for t in query]
    return jsonify(danh_muc_hoat_chat=danh_muc_hoat_chat)


@app.route('/gop-gia-tri', methods=['POST'])
@login_required
def gop_gia_tri():
    danh_muc = request.form['danh_muc']
    if danh_muc == 'thuoc':
        id_list = request.form.getlist('id_list[]')
        last_id = id_list.pop()

        last_thuoc = Thuoc.query.get(int(last_id))
        last_code = last_thuoc.code
        for id in id_list:
            thuoc = Thuoc.query.get(int(id))
            thuoc.general_id = last_thuoc.id
            thuoc.code = last_code
        db.session.commit()
        query = Thuoc.query.filter(Thuoc.hospital_id == current_user.hospital.id).order_by(Thuoc.name.asc()).all()
    else:
        index = DM.index(danh_muc)
        model = MODELS[index]
        id_name = IDS[index]
        id_col = getattr(KetQuaTrungThau, id_name)

        id_list = request.form.getlist('id_list[]')
        last_id = id_list.pop()
        if model != HoatChat:
            for record in KetQuaTrungThau.query.filter(id_col.in_(id_list),
                                                       KetQuaTrungThau.hospital_id == current_user.hospital.id):
                setattr(record, id_name, last_id)
        last_obj = model.query.get(int(last_id))
        delete_obj = model.query.filter(model.id.in_(id_list)).all()
        for o in delete_obj:
            o.general_id = last_obj.id
            if model == HoatChat:
                o.code = last_obj.code
                o.atc_id = last_obj.atc_id
                o.nhom_duoc_ly1_bv_id = last_obj.nhom_duoc_ly1_bv_id
                o.nhom_duoc_ly2_bv_id = last_obj.nhom_duoc_ly2_bv_id
                o.nhom_hoa_duoc_bv_id = last_obj.nhom_hoa_duoc_bv_id
                o.hoat_chat_syt_id = last_obj.hoat_chat_syt_id
            else:
                o.show = "0"
        db.session.commit()
        query = model.query.filter_by(hospital=current_user.hospital, show="1").order_by(model.name.asc()).all()
    danh_muc_dict = [t.danh_muc_to_dict() for t in query]
    return jsonify(danh_muc_dict=danh_muc_dict)


@app.route('/luu-thay-doi', methods=['POST'])
@login_required
def luu_thay_doi():
    data = request.get_json()
    danh_muc = data['danh_muc']
    index = DM.index(danh_muc)
    model = MODELS[index]

    changed_data = data['changed_data']
    if danh_muc == 'thuoc':
        for r in changed_data:
            t = model.query.filter_by(id=int(r[-1])).first()
            t.name = r[0]
            t.sdk = r[1]
    else:
        for r in changed_data:
            t = model.query.filter_by(id=int(r[-1])).first()
            t.name = r[0]
    db.session.commit()

    query = model.query.filter_by(hospital=current_user.hospital, show="1").order_by(model.name.asc()).all()
    danh_muc_dict = [t.danh_muc_to_dict() for t in query]
    return jsonify(danh_muc_dict=danh_muc_dict)


@app.route('/them-nhom', methods=['POST'])
@login_required
def them_nhom():
    danh_muc = request.form['danh_muc']
    content = request.form['content']
    index = DM.index(danh_muc)
    model = MODELS[index]

    if content != '':
        t = model(name=content, hospital_id=current_user.hospital.id)
        db.session.add(t)
        db.session.commit()
    query = model.query.filter_by(hospital=current_user.hospital).order_by(model.name.asc()).all()
    danh_muc_dict = [t.danh_muc_to_dict() for t in query]
    return jsonify(danh_muc_dict=danh_muc_dict)


@app.route('/xoa-nhom', methods=['POST'])
@login_required
def xoa_nhom():
    danh_muc = request.form['danh_muc']
    id = request.form['id']
    index = DM.index(danh_muc)
    model = MODELS[index]

    if id != '':
        t = model.query.filter_by(id=int(id)).first()
        db.session.delete(t)
        db.session.commit()
    query = model.query.filter_by(hospital=current_user.hospital).order_by(model.name.asc()).all()
    danh_muc_dict = [t.danh_muc_to_dict() for t in query]
    return jsonify(danh_muc_dict=danh_muc_dict)


@app.route('/<url>/theo-doi-cung-ung')
@login_required
def theo_doi_cung_ung(url):
    import_history = ImportHistoryNXT.query.filter_by(hospital_id=current_user.hospital.id).order_by(
        ImportHistoryNXT.time.desc()).all()
    return render_template('theo_doi_cung_ung.html', user=current_user, import_history=import_history)


@app.route('/get-thuoc-list', methods=['POST'])
@login_required
def get_thuoc_list():
    startLetter = request.form['startLetter'].upper()
    thuoc = db.session.query(func.distinct(Thuoc.codeBV)).select_from(TongHopThau). \
        join(Thuoc, Thuoc.id == TongHopThau.thuoc_id). \
        join(KetQuaTrungThau, KetQuaTrungThau.thuoc_id == TongHopThau.thuoc_id). \
        join(DotThau, DotThau.id == KetQuaTrungThau.dot_thau_id). \
        filter(DotThau.end.is_(None),
               Thuoc.hospital_id == current_user.hospital.id,
               func.lower(Thuoc.name).like(func.lower(f'{startLetter}%'))
               ).all()
    thuoc_list = []
    for c in thuoc:
        t = Thuoc.query.filter(Thuoc.codeBV == c[0], Thuoc.hospital_id == current_user.hospital.id).first()
        thuoc_list.append(t.danh_muc_to_dict())
    return jsonify(thuoc_list=thuoc_list)


@app.route('/cung-ung-theo-thuoc', methods=['POST'])
@login_required
def cung_ung_theo_thuoc():
    codeBV = request.form['code']
    tht = db.session.query(func.sum(TongHopThau.tong_ke_hoach), func.sum(TongHopThau.tong_su_dung),
                           func.sum(TongHopThau.so_lan_du_tru)). \
        join(Thuoc, Thuoc.id == TongHopThau.thuoc_id). \
        join(KetQuaTrungThau, KetQuaTrungThau.thuoc_id == TongHopThau.thuoc_id). \
        join(DotThau, DotThau.id == KetQuaTrungThau.dot_thau_id). \
        filter(TongHopThau.hospital_id == current_user.hospital.id,
               Thuoc.codeBV == codeBV,
               DotThau.end.is_(None)). \
        group_by(Thuoc.codeBV).first()

    if not tht:
        tht = (0, 0, 0.0)

    total = {
        'tong_ke_hoach': tht[0],
        'tong_su_dung': tht[1],
        'so_lan_du_tru': tht[2],
    }

    tkh = ThongKeKho.query.join(Thuoc, Thuoc.id == ThongKeKho.thuoc_id). \
        filter(ThongKeKho.hospital_id == current_user.hospital.id,
               Thuoc.codeBV == codeBV,
               DotThau.end.is_(None)). \
        order_by(ThongKeKho.ngay_nhap_chan.asc()).all()
    thongkekho = [t.to_dict() for t in tkh]
    return jsonify(total=total, thongkekho=thongkekho)


@app.route('/get-nhom-theo-hoat-chat', methods=['POST'])
@login_required
def get_nhom_theo_hoat_chat():
    search_id = request.form['hoat_chat_id']
    if 'A' in search_id:
        search_id = search_id[:-1]
        hc = HoatChat.query.filter_by(atc_id=int(search_id)).first()
    else:
        hc = HoatChat.query.get(int(search_id))
    return jsonify(nhom_duoc_ly1=str(hc.nhom_duoc_ly1_bv.id), nhom_duoc_ly2=str(hc.nhom_duoc_ly2_bv.id),
                   nhom_hoa_duoc=str(hc.nhom_hoa_duoc_bv.id))


@app.route('/get-nhom-list', methods=['POST'])
@login_required
def get_nhom_list():
    if request.form['nhom'] == 'nhom_thau':
        tht = db.session.query(func.distinct(HoatChat.code), ATC.id, ATC.name, HoatChat.id, HoatChat.name). \
            select_from(TongHopThau). \
            join(Thuoc, Thuoc.id == TongHopThau.thuoc_id). \
            join(KetQuaTrungThau, KetQuaTrungThau.thuoc_id == Thuoc.id). \
            join(HoatChat, HoatChat.id == KetQuaTrungThau.hoat_chat_id). \
            join(ATC, HoatChat.atc_id == ATC.id, isouter=True). \
            join(DotThau, DotThau.id == KetQuaTrungThau.dot_thau_id). \
            filter(TongHopThau.hospital_id == current_user.hospital.id, DotThau.end.is_(None)). \
            order_by(HoatChat.name).all()
        hoat_chat_list = []
        for hc in tht:
            if hc[1] is not None:
                hoat_chat_list.append({'id': str(hc[1]) + 'A', 'name': hc[2]})
            else:
                hoat_chat_list.append({'id': hc[3], 'name': hc[4]})
        return jsonify(hoat_chat_list=hoat_chat_list)
    elif request.form['nhom'] == 'nhom_duoc_ly1':
        tht = db.session.query(func.distinct(NhomDuocLy1BV.id), NhomDuocLy1BV.name).select_from(TongHopThau). \
            join(Thuoc, Thuoc.id == TongHopThau.thuoc_id). \
            join(KetQuaTrungThau, KetQuaTrungThau.thuoc_id == Thuoc.id). \
            join(HoatChat, HoatChat.id == KetQuaTrungThau.hoat_chat_id). \
            join(NhomDuocLy1BV, NhomDuocLy1BV.id == HoatChat.nhom_duoc_ly1_bv_id). \
            join(DotThau, DotThau.id == KetQuaTrungThau.dot_thau_id). \
            filter(TongHopThau.hospital_id == current_user.hospital.id, DotThau.end.is_(None)). \
            order_by(NhomDuocLy1BV.name).all()
        nhom_duoc_ly_list = []
        for hc in tht:
            nhom_duoc_ly_list.append({'id': hc[0], 'name': hc[1]})
        return jsonify(nhom_duoc_ly_list=nhom_duoc_ly_list)
    elif request.form['nhom'] == 'nhom_duoc_ly2':
        tht = db.session.query(func.distinct(NhomDuocLy2BV.id), NhomDuocLy2BV.name).select_from(TongHopThau). \
            join(Thuoc, Thuoc.id == TongHopThau.thuoc_id). \
            join(KetQuaTrungThau, KetQuaTrungThau.thuoc_id == Thuoc.id). \
            join(HoatChat, HoatChat.id == KetQuaTrungThau.hoat_chat_id). \
            join(NhomDuocLy2BV, NhomDuocLy2BV.id == HoatChat.nhom_duoc_ly2_bv_id). \
            join(DotThau, DotThau.id == KetQuaTrungThau.dot_thau_id). \
            filter(TongHopThau.hospital_id == current_user.hospital.id, DotThau.end.is_(None)). \
            order_by(NhomDuocLy2BV.name).all()
        nhom_duoc_ly_list = []
        for hc in tht:
            nhom_duoc_ly_list.append({'id': hc[0], 'name': hc[1]})
        return jsonify(nhom_duoc_ly_list=nhom_duoc_ly_list)
    else:
        tht = db.session.query(func.distinct(NhomHoaDuocBV.id), NhomHoaDuocBV.name).select_from(TongHopThau). \
            join(Thuoc, Thuoc.id == TongHopThau.thuoc_id). \
            join(KetQuaTrungThau, KetQuaTrungThau.thuoc_id == Thuoc.id). \
            join(HoatChat, HoatChat.id == KetQuaTrungThau.hoat_chat_id). \
            join(NhomHoaDuocBV, NhomHoaDuocBV.id == HoatChat.nhom_hoa_duoc_bv_id). \
            join(DotThau, DotThau.id == KetQuaTrungThau.dot_thau_id). \
            filter(TongHopThau.hospital_id == current_user.hospital.id, DotThau.end.is_(None)). \
            order_by(NhomHoaDuocBV.name).all()
        nhom_hoa_duoc_list = []
        for hc in tht:
            nhom_hoa_duoc_list.append({'id': hc[0], 'name': hc[1]})
        return jsonify(nhom_hoa_duoc_list=nhom_hoa_duoc_list)


@app.route('/cung-ung-theo-nhom', methods=['POST'])
@login_required
def cung_ung_theo_nhom():
    if 'hoat_chat' in request.form:
        search_id = request.form['hoat_chat']
        if 'A' in search_id:
            atc_id = int(search_id[:-1])
            tht = TongHopThau.query. \
                join(Thuoc, Thuoc.id == TongHopThau.thuoc_id). \
                join(KetQuaTrungThau, KetQuaTrungThau.thuoc_id == Thuoc.id). \
                join(HoatChat, HoatChat.id == KetQuaTrungThau.hoat_chat_id). \
                join(DotThau, DotThau.id == KetQuaTrungThau.dot_thau_id). \
                filter(TongHopThau.hospital_id == current_user.hospital.id,
                       HoatChat.atc_id == atc_id, DotThau.end.is_(None)).all()
        else:
            hoat_chat_id = int(search_id)
            tht = TongHopThau.query. \
                join(Thuoc, Thuoc.id == TongHopThau.thuoc_id). \
                join(KetQuaTrungThau, KetQuaTrungThau.thuoc_id == Thuoc.id). \
                join(HoatChat, HoatChat.id == KetQuaTrungThau.hoat_chat_id). \
                join(DotThau, DotThau.id == KetQuaTrungThau.dot_thau_id). \
                filter(TongHopThau.hospital_id == current_user.hospital.id,
                       HoatChat.id == hoat_chat_id, DotThau.end.is_(None)).all()
        danhsachthau = [t.to_dict() for t in tht]
        return jsonify(danhsachthau=danhsachthau)
    elif 'nhom_duoc_ly1' in request.form:
        nhom_duoc_ly_id = int(request.form['nhom_duoc_ly1'])
        tht = TongHopThau.query. \
            join(Thuoc, Thuoc.id == TongHopThau.thuoc_id). \
            join(KetQuaTrungThau, KetQuaTrungThau.thuoc_id == Thuoc.id). \
            join(HoatChat, HoatChat.id == KetQuaTrungThau.hoat_chat_id). \
            join(DotThau, DotThau.id == KetQuaTrungThau.dot_thau_id). \
            filter(TongHopThau.hospital_id == current_user.hospital.id,
                   HoatChat.nhom_duoc_ly1_bv_id == nhom_duoc_ly_id, DotThau.end.is_(None)).all()
        danhsachthau = [t.to_dict() for t in tht]
        return jsonify(danhsachthau=danhsachthau)
    elif 'nhom_duoc_ly2' in request.form:
        nhom_duoc_ly_id = int(request.form['nhom_duoc_ly2'])
        tht = TongHopThau.query. \
            join(Thuoc, Thuoc.id == TongHopThau.thuoc_id). \
            join(KetQuaTrungThau, KetQuaTrungThau.thuoc_id == Thuoc.id). \
            join(HoatChat, HoatChat.id == KetQuaTrungThau.hoat_chat_id). \
            join(DotThau, DotThau.id == KetQuaTrungThau.dot_thau_id). \
            filter(TongHopThau.hospital_id == current_user.hospital.id,
                   HoatChat.nhom_duoc_ly2_bv_id == nhom_duoc_ly_id, DotThau.end.is_(None)).all()
        danhsachthau = [t.to_dict() for t in tht]
        return jsonify(danhsachthau=danhsachthau)
    else:
        nhom_hoa_duoc_id = int(request.form['nhom_hoa_duoc'])
        tht = TongHopThau.query. \
            join(Thuoc, Thuoc.id == TongHopThau.thuoc_id). \
            join(KetQuaTrungThau, KetQuaTrungThau.thuoc_id == Thuoc.id). \
            join(HoatChat, HoatChat.id == KetQuaTrungThau.hoat_chat_id). \
            join(DotThau, DotThau.id == KetQuaTrungThau.dot_thau_id). \
            filter(TongHopThau.hospital_id == current_user.hospital.id,
                   HoatChat.nhom_hoa_duoc_bv_id == nhom_hoa_duoc_id, DotThau.end.is_(None)).all()
        danhsachthau = [t.to_dict() for t in tht]
        return jsonify(danhsachthau=danhsachthau)


@app.route('/su-dung-con-lai', methods=['POST'])
@login_required
def su_dung_con_lai():
    if 'su_dung' in request.form:
        su_dung = float(request.form['su_dung']) / 100
        tht = TongHopThau.query. \
            join(Thuoc, Thuoc.id == TongHopThau.thuoc_id). \
            join(KetQuaTrungThau, KetQuaTrungThau.thuoc_id == Thuoc.id). \
            join(DotThau, DotThau.id == KetQuaTrungThau.dot_thau_id). \
            filter(TongHopThau.tong_su_dung / TongHopThau.tong_ke_hoach < su_dung,
                   TongHopThau.hospital_id == current_user.hospital.id,
                   DotThau.end.is_(None)).paginate(page=1, per_page=20, error_out=False)
        danhsachthau = []
        if tht:
            danhsachthau = [t.to_dict() for t in tht]
        return jsonify(danhsachthau=danhsachthau)
    else:
        con_lai = float(request.form['con_lai']) / 100
        tht = TongHopThau.query. \
            join(Thuoc, Thuoc.id == TongHopThau.thuoc_id). \
            join(KetQuaTrungThau, KetQuaTrungThau.thuoc_id == Thuoc.id). \
            join(DotThau, DotThau.id == KetQuaTrungThau.dot_thau_id). \
            filter(TongHopThau.con_lai / TongHopThau.tong_ke_hoach < con_lai,
                   TongHopThau.hospital_id == current_user.hospital.id,
                   DotThau.end.is_(None)).paginate(page=1, per_page=20, error_out=False)
        danhsachthau = []
        if tht:
            danhsachthau = [t.to_dict() for t in tht]
        return jsonify(danhsachthau=danhsachthau)


@app.route('/ton-le', methods=['POST'])
@login_required
def ton_le():
    if 'ton_le_nho' in request.form:
        ton_le_nho = float(request.form['ton_le_nho']) / 100
        tht = TongHopThau.query. \
            join(Thuoc, Thuoc.id == TongHopThau.thuoc_id). \
            join(KetQuaTrungThau, KetQuaTrungThau.thuoc_id == Thuoc.id). \
            join(DotThau, DotThau.id == KetQuaTrungThau.dot_thau_id). \
            filter(TongHopThau.ton_le_moi_nhat / TongHopThau.nhap_le_moi_nhat < ton_le_nho,
                   TongHopThau.hospital_id == current_user.hospital.id,
                   DotThau.end.is_(None)).paginate(page=1, per_page=20, error_out=False)
        danhsachthau = []
        if tht:
            danhsachthau = [t.to_dict() for t in tht]
        return jsonify(danhsachthau=danhsachthau)
    else:
        ton_le_lon = float(request.form['ton_le_lon']) / 100
        tht = TongHopThau.query. \
            join(Thuoc, Thuoc.id == TongHopThau.thuoc_id). \
            join(KetQuaTrungThau, KetQuaTrungThau.thuoc_id == Thuoc.id). \
            join(DotThau, DotThau.id == KetQuaTrungThau.dot_thau_id). \
            filter(TongHopThau.ton_le_moi_nhat / TongHopThau.nhap_le_moi_nhat > ton_le_lon,
                   TongHopThau.hospital_id == current_user.hospital.id,
                   DotThau.end.is_(None)).all()
        danhsachthau = []
        if tht:
            danhsachthau = [t.to_dict() for t in tht]
        return jsonify(danhsachthau=danhsachthau)


@app.route('/su-dung-theo-thang', methods=['GET'])
@login_required
def su_dung_theo_thang():
    suDungTheoThang = []
    danhsachthuoc = []
    results = db.session.query(Thuoc.name, ThongKeKho.ngay_nhap_chan, ThongKeKho.nhap_chan, DotThau.code, Thuoc.codeBV). \
        select_from(ThongKeKho). \
        join(Thuoc, Thuoc.id == ThongKeKho.thuoc_id). \
        join(KetQuaTrungThau, KetQuaTrungThau.thuoc_id == ThongKeKho.thuoc_id). \
        join(DotThau, DotThau.id == KetQuaTrungThau.dot_thau_id). \
        filter(ThongKeKho.hospital_id == current_user.hospital.id,
               DotThau.end.is_(None)). \
        order_by(ThongKeKho.ngay_nhap_chan.asc()).all()
    for r in results:
        row = [r[0], r[1].strftime("%Y-%m-%d"), r[2], r[3], r[4]]
        suDungTheoThang.append(row)

    tht = db.session.query(Thuoc.name, HoatChat.name, TongHopThau.tong_ke_hoach, DotThau.code, Thuoc.codeBV) \
        .select_from(TongHopThau). \
        join(Thuoc, Thuoc.id == TongHopThau.thuoc_id). \
        join(KetQuaTrungThau, KetQuaTrungThau.thuoc_id == TongHopThau.thuoc_id). \
        join(HoatChat, HoatChat.id == KetQuaTrungThau.hoat_chat_id). \
        join(DotThau, DotThau.id == KetQuaTrungThau.dot_thau_id). \
        filter(TongHopThau.hospital_id == current_user.hospital.id,
               DotThau.end.is_(None)). \
        order_by(Thuoc.name).all()
    for t in tht:
        row = [x for x in t]
        danhsachthuoc.append(row)
    ketQuaCungUng = {'danhsachthuoc': danhsachthuoc, 'suDungTheoThang': suDungTheoThang}
    return jsonify(ketQuaCungUng=ketQuaCungUng)


@app.route('/ket-qua-cung-ung', methods=['GET'])
@login_required
def final_ket_qua_cung_ung():
    ketQuaCungUng = ket_qua_cung_ung('NXT')
    return jsonify(ketQuaCungUng=ketQuaCungUng)


@app.route('/delete-import-history-nxt', methods=['POST'])
@login_required
def delete_import_history_nxt():
    id = int(request.form['id'])
    ih = ImportHistoryNXT.query.get(id)
    db.session.delete(ih)
    db.session.commit()
    ihs = ImportHistoryNXT.query.filter_by(hospital_id=current_user.hospital.id).order_by(
        ImportHistoryNXT.time.desc()).all()
    import_history = []
    for i in ihs:
        import_history.append(i.import_history_to_dict())
    return jsonify(import_history=import_history)


@app.route('/file-cung-ung', methods=['POST'])
@login_required
def file_cung_ung():
    file = request.files.get('file')  # Lấy file được gửi lên

    thuoc_not_available = []
    if file:
        time = request.form.get('month')
        year, month = time.split('-')
        month = datetime(int(year), int(month), 1)
        db.session.query(FileInformation).filter(FileInformation.hospital_id == current_user.hospital.id).delete()
        if not ImportHistoryNXT.query.filter(ImportHistoryNXT.name == file.filename,
                                             ImportHistoryNXT.hospital_id == current_user.hospital.id).first():
            ih = ImportHistoryNXT(name=file.filename, month=month, hospital_id=current_user.hospital.id)
            db.session.add(ih)
            db.session.flush()

            df = pd.read_excel(file)
            df = df.where(pd.notna(df), None)
            for i in range(0, df.shape[0] - 1):
                code = df.loc[i, 'Service ID']
                t = Thuoc.query.filter(Thuoc.hospital_id == current_user.hospital.id, Thuoc.codeBV == code).first()
                if t:
                    thuoc_id = t.id
                    kq = KetQuaTrungThau.query.filter(KetQuaTrungThau.hospital_id == current_user.hospital.id,
                                                      KetQuaTrungThau.thuoc_id == thuoc_id).first()
                    if kq:
                        ton_bv = int(df.loc[i, 'Ton BV'])
                        nhap = int(df.loc[i, 'Nhap'])
                        xuat = int(df.loc[i, 'Xuat'])
                        ton_cuoi_bv = int(df.loc[i, 'Ton Cuoi BV'])
                        kq = KetQuaTrungThau.query.filter(KetQuaTrungThau.hospital_id == current_user.hospital.id,
                                                          KetQuaTrungThau.thuoc_id == thuoc_id).first()
                        dot_thau_id = kq.dot_thau_id
                        r = NXT(thuoc_id=thuoc_id, ton_bv=ton_bv, nhap=nhap, xuat=xuat, ton_cuoi_bv=ton_cuoi_bv,
                                import_history_id=ih.id, hospital_id=current_user.hospital.id, dot_thau_id=dot_thau_id)
                        db.session.add(r)
                    else:
                        thuoc_not_available.append(df.loc[i, 'Service Name'])
                else:
                    thuoc_not_available.append(df.loc[i, 'Service Name'])
        else:
            flash(f'Đã import dữ liệu {month}, nếu muốn chỉnh sửa, vui lòng xoá import cũ.', 'danger')
            flash_messages = [{'category': category, 'message': message} for category, message in
                              get_flashed_messages(with_categories=True)]
            return jsonify(flash_messages=flash_messages)
    db.session.query(TongHopThau).filter(TongHopThau.hospital_id == current_user.hospital.id).delete()
    db.session.query(ThongKeKho).filter(ThongKeKho.hospital_id == current_user.hospital.id).delete()
    danh_sach_thuoc = db.session.query(NXT.thuoc_id).filter(NXT.hospital == current_user.hospital,
                                                            NXT.nhap > 0).distinct().all()
    for t in danh_sach_thuoc:
        ketQuaTrungThau = KetQuaTrungThau.query.filter(KetQuaTrungThau.hospital == current_user.hospital,
                                                       KetQuaTrungThau.thuoc_id == t.thuoc_id).first()
        tongKeHoach = ketQuaTrungThau.so_luong
        ngayThau = ketQuaTrungThau.dot_thau.ngayQD

        # Thong ke kho
        duTruConLai = tongKeHoach
        nhap_chan = NXT.query. \
            join(ImportHistoryNXT, ImportHistoryNXT.id == NXT.import_history_id). \
            filter(NXT.thuoc_id == t.thuoc_id, NXT.nhap > 0,
                   NXT.hospital_id == current_user.hospital.id). \
            order_by(ImportHistoryNXT.month).all()
        sumNhapChan = 0
        trungBinhNhapChan = 0
        soLanNhap = 0
        for r in nhap_chan:
            soLanNhap += 1
            nhap = r.nhap
            ngayNhapChan = r.import_history.month
            tonLe = r.ton_bv
            sumNhapChan += nhap
            trungBinhNhapChan = int(round(sumNhapChan / soLanNhap, 0))
            duTruConLai -= nhap
            tkh = ThongKeKho(ngay_nhap_chan=ngayNhapChan, thuoc_id=t.thuoc_id, nhap_chan=nhap,
                             ton_le_truoc_nhap_chan=tonLe,
                             trung_binh_nhap_chan=trungBinhNhapChan, du_tru_con_lai=duTruConLai,
                             hospital_id=current_user.hospital.id)
            db.session.add(tkh)
        # Tong hop thau
        tongSuDung = db.session.query(func.sum(ThongKeKho.nhap_chan)).filter(
            ThongKeKho.hospital == current_user.hospital,
            ThongKeKho.thuoc_id == t.thuoc_id
        ).scalar()
        if not tongSuDung:
            tongSuDung = 0
        conLai = tongKeHoach - tongSuDung
        dt = db.session.query(NXT.ton_bv, NXT.ton_cuoi_bv).filter(NXT.hospital == current_user.hospital,
                                                                  NXT.thuoc_id == t.thuoc_id).order_by(
            NXT.id.desc()).limit(25).first()
        ton_chan = dt.ton_bv
        tonLeCuoiCung = dt.ton_cuoi_bv
        try:
            nhapLeCuoiCung = db.session.query(NXT.xuat).filter(NXT.hospital == current_user.hospital,
                                                               NXT.thuoc_id == t.thuoc_id,
                                                               NXT.xuat > 0).order_by(
                NXT.id.desc()).limit(25).first().xuat
        except:
            nhapLeCuoiCung = 0
        soLanDuTru = round(conLai / trungBinhNhapChan, 2) if trungBinhNhapChan > 0 else 0
        tht = TongHopThau(time=ngayThau, thuoc_id=t.thuoc_id, tong_ke_hoach=tongKeHoach,
                          tong_su_dung=tongSuDung, hospital_id=current_user.hospital.id, ton_chan=ton_chan,
                          con_lai=conLai, nhap_le_moi_nhat=nhapLeCuoiCung, ton_le_moi_nhat=tonLeCuoiCung,
                          trung_binh_nhap_chan=trungBinhNhapChan, so_lan_du_tru=soLanDuTru)
        db.session.add(tht)
    db.session.commit()
    ih = ImportHistoryNXT.query.filter_by(hospital_id=current_user.hospital.id).order_by(
        ImportHistoryNXT.time.desc()).all()
    import_history = []
    for i in ih:
        import_history.append(i.import_history_to_dict())
    return jsonify(import_history=import_history, thuoc_not_available=thuoc_not_available)


def ket_qua_cung_ung(data):
    ketQuaCungUng = {}
    danhsachthau = []
    danhsachthuoc = []
    dst = db.session.query(Thuoc.name.label('thuoc'), HoatChat.name.label('hoat_chat'),
                           KetQuaTrungThau.so_luong.label('tong_ke_hoach'), DotThau.code.label('ma_dot_thau')). \
        select_from(TongHopThau). \
        filter(TongHopThau.hospital_id == current_user.hospital.id). \
        join(Thuoc, TongHopThau.thuoc_id == Thuoc.id). \
        join(KetQuaTrungThau, KetQuaTrungThau.thuoc_id == TongHopThau.thuoc_id). \
        join(HoatChat, HoatChat.id == KetQuaTrungThau.hoat_chat_id). \
        join(DotThau, DotThau.id == KetQuaTrungThau.dot_thau_id). \
        order_by(Thuoc.name, DotThau.ngayQD).all()
    for t in dst:
        danhsachthuoc.append([t.thuoc, t.hoat_chat, t.tong_ke_hoach, t.ma_dot_thau])

    dst = TongHopThau.query.join(Thuoc, Thuoc.id == TongHopThau.thuoc_id). \
        filter(TongHopThau.hospital_id == current_user.hospital.id). \
        order_by(Thuoc.name).all()
    for t in dst:
        danhsachthau.append(t.to_dict())
    ketQuaCungUng['danhsachthau'] = danhsachthau
    ketQuaCungUng['danhsachthuoc'] = danhsachthuoc

    suDungTheoThang = []
    if data == 'NXT':
        print(1)
        results = db.session.query(NXT.id, NXT.thuoc_id, func.sum(NXT.nhap), NXT.import_history_id).filter(
            NXT.nhap > 0, NXT.hospital_id == current_user.hospital.id). \
            join(ImportHistoryNXT, ImportHistoryNXT.id == NXT.import_history_id). \
            join(DotThau, DotThau.id == NXT.dot_thau_id). \
            group_by(
            NXT.thuoc_id, NXT.import_history_id, NXT.id).order_by(ImportHistoryNXT.month).all()
        for r in results:
            row = [r.import_history_id, r.thuoc_id]
            nxt = NXT.query.get(r.id)
            row.append(nxt.thuoc.name)
            row.append(nxt.import_history.month.strftime("%Y-%m-%d"))
            row.append(nxt.nhap)
            row.append(nxt.dot_thau.code)
            suDungTheoThang.append(row)
        ketQuaCungUng['suDungTheoThang'] = suDungTheoThang
    elif data == 'KHO':
        print(2)
        results = db.session.query(KhoChan.thuoc_id,
                                   func.concat(
                                       func.extract('year', KhoChan.time),
                                       "-",
                                       func.lpad(func.extract('month', KhoChan.time), 2, '0')
                                   ).label('year_month'),
                                   func.sum(KhoChan.nhap).label('nhap'),
                                   KhoChan.file_id,
                                   KhoChan.dot_thau_id
                                   ).filter(KhoChan.nhap > 0, KhoChan.hospital_id == current_user.hospital.id
                                            ). \
            group_by('year_month', KhoChan.file_id, KhoChan.thuoc_id, KhoChan.dot_thau_id
                     ).order_by(func.max(KhoChan.time)).all()
        for r in results:
            row = [r.file_id, r.thuoc_id, Thuoc.query.filter_by(id=r.thuoc_id).first().name, r.year_month, r.nhap]
            dt = DotThau.query.get(r.dot_thau_id)
            row.append(dt.code)
            suDungTheoThang.append(row)
        ketQuaCungUng['suDungTheoThang'] = suDungTheoThang
    thongkekho = []
    tkh = ThongKeKho.query.filter_by(hospital_id=current_user.hospital.id).order_by(
        ThongKeKho.ngay_nhap_chan.asc()).all()
    for t in tkh:
        thongkekho.append(t.to_dict())
    ketQuaCungUng['thongkekho'] = thongkekho
    return ketQuaCungUng


@app.route('/files', methods=['POST'])
@login_required
def uploadfiles():
    if 'date' in request.form:
        files = request.files.getlist('files')
        dates = request.form.getlist('date')
        for i in range(len(dates)):
            if not FileInformation.query.filter(FileInformation.name == files[i].filename,
                                                FileInformation.hospital == current_user.hospital).first():
                f = FileInformation(name=files[i].filename, time=dates[i], hospital_id=current_user.hospital.id)
                db.session.add(f)
                db.session.flush()
                if not nhapDuLieuKho(f.id, files[i]):
                    db.session.delete(f)
            else:
                f = FileInformation.query.filter(FileInformation.name == files[i].filename,
                                                 FileInformation.hospital == current_user.hospital).first()
                if f.time != dates[i]:
                    f.time = dates[i]
                    nhapDuLieuKho(f.id, files[i])
        flash('Nhập dữ liệu thành công.', 'success')
    flash_messages = [{'category': category, 'message': message} for category, message in
                      get_flashed_messages(with_categories=True)]
    return jsonify(flash_messages=flash_messages)


@app.route('/du-lieu-kho', methods=['GET'])
def du_lieu_kho():
    mergeDuLieuKho()
    ketQuaCungUng = ket_qua_cung_ung('KHO')
    return jsonify(ketQuaCungUng=ketQuaCungUng)


def nhapDuLieuKho(file_id, file):
    df = pd.read_excel(file, engine='openpyxl')
    df = df.where(pd.notna(df), None)
    headers = df.columns.tolist()
    tenThuoc = headers[2].split(' : ')[1].strip().lower()
    thuoc = Thuoc.query.filter(Thuoc.hospital == current_user.hospital, func.lower(Thuoc.name) == tenThuoc).first()
    if thuoc:
        thuoc_id = thuoc.id
        if "kho chẵn" in file.filename.lower():
            insertKho(df, KhoChan, thuoc_id, file_id)
        else:
            insertKho(df, KhoLe, thuoc_id, file_id)
        return True
    else:
        flash(f'Không có thuốc {tenThuoc} trong danhmuc', 'info')
        return False


def insertKho(df, KhoModel, thuoc_id, file_id):
    fs = KhoModel.query.filter(KhoModel.hospital_id == current_user.hospital_id, KhoModel.file_id == file_id).all()
    if len(fs) > 0:
        db.session.delete(fs)
    first_row = df.iloc[2].tolist()
    for i in range(2, df.shape[0] - 1):
        row = df.iloc[i].tolist()
        ngay = row[0]
        nhap = int(row[4])
        ton = int(row[6])
        xuat = int(row[5])
        r = KhoModel(file_id=file_id, time=ngay, thuoc_id=thuoc_id, nhap=nhap, xuat=xuat, ton=ton,
                     hospital_id=current_user.hospital.id)
        if KhoModel == KhoChan:
            dt = DotThau.query.filter(DotThau.hospital_id == current_user.hospital_id, DotThau.ngayQD < first_row[0]). \
                order_by(DotThau.ngayQD.desc()).first()
            r.dot_thau_id = dt.id
        db.session.add(r)
    db.session.commit()


def mergeDuLieuKho():
    db.session.query(TongHopThau).filter(TongHopThau.hospital_id == current_user.hospital.id).delete()
    db.session.query(ThongKeKho).filter(ThongKeKho.hospital_id == current_user.hospital.id).delete()

    danh_sach_thuoc = db.session.query(KhoChan.thuoc_id).filter(
        KhoChan.hospital_id == current_user.hospital.id).distinct(
        KhoChan.thuoc_id).all()
    for t in danh_sach_thuoc:
        if KhoLe.query.filter(KhoLe.hospital == current_user.hospital, KhoLe.thuoc_id == t.thuoc_id).first():
            tongKeHoach = db.session.query(func.sum(KetQuaTrungThau.so_luong)). \
                filter(KetQuaTrungThau.hospital == current_user.hospital,
                       KetQuaTrungThau.thuoc_id == t.thuoc_id).scalar()
            ngayThau = db.session.query(DotThau.ngayQD).join(KetQuaTrungThau,
                                                             KetQuaTrungThau.dot_thau_id == DotThau.id). \
                filter(KetQuaTrungThau.thuoc_id == t.thuoc_id,
                       KetQuaTrungThau.hospital_id == current_user.hospital.id).order_by(DotThau.ngayQD.desc()).limit(
                1).scalar()
            # Thong ke kho
            duTruConLai = tongKeHoach
            nhap_chan = KhoChan.query.filter(KhoChan.nhap > 0, KhoChan.hospital_id == current_user.hospital.id,
                                             KhoChan.thuoc_id == t.thuoc_id).all()
            ngayNhapChanList = []
            nhapChanList = []
            sumNhapChan = 0
            nhapChanCungNgay = 0
            trungBinhNhapChan = 0
            for r in nhap_chan:
                nhapChanList.append(r.nhap)
                ngayNhapChanList.append(r.time)

            ton_le = KhoLe.query.filter(KhoLe.hospital_id == current_user.hospital.id,
                                        KhoLe.thuoc_id == t.thuoc_id).all()
            tonLeList = []
            ngayTonLeList = []
            soLanNhap = 0
            for r in ton_le:
                tonLeList.append(r.ton)
                ngayTonLeList.append(r.time)
            for i in range(len(ngayNhapChanList)):
                ngay = ngayNhapChanList[i]
                nhap = nhapChanList[i]
                nhapChanCungNgay += nhap
                if i < len(ngayNhapChanList) - 1:
                    if ngay == ngayNhapChanList[i + 1]:
                        continue
                    else:
                        nhap = nhapChanCungNgay
                        soLanNhap += 1
                        nhapChanCungNgay = 0
                else:
                    nhap = nhapChanCungNgay
                    soLanNhap = len(set(ngayNhapChanList))
                sumNhapChan += nhap
                trungBinhNhapChan = int(round(sumNhapChan / soLanNhap, 0))

                ngayNhapChan = ngay
                if ngay <= ngayTonLeList[0]:
                    tonLe = 0
                    closest_date = ngay
                elif ngay in ngayTonLeList:
                    index = ngayTonLeList.index(ngay) - 1
                    closest_date = ngayTonLeList[index]
                    tonLe = tonLeList[index]
                else:
                    while ngay not in ngayTonLeList:
                        ngay = ngay - timedelta(days=1)
                    index = None
                    for idx in range(len(ngayTonLeList) - 1, -1, -1):
                        if ngayTonLeList[idx] == ngay:
                            index = idx
                            break

                    closest_date = ngayTonLeList[index]
                    tonLe = tonLeList[index]
                duTruConLai -= nhap
                tkh = ThongKeKho(ngay_nhap_chan=ngayNhapChan, thuoc_id=t.thuoc_id, nhap_chan=nhap,
                                 ton_le_truoc_nhap_chan=tonLe,
                                 trung_binh_nhap_chan=trungBinhNhapChan, du_tru_con_lai=duTruConLai,
                                 hospital_id=current_user.hospital.id)
                db.session.add(tkh)
            # Tong hop thau
            tongSuDung = db.session.query(func.sum(KhoChan.nhap)).filter(
                KhoChan.hospital_id == 1,
                KhoChan.thuoc_id == t.thuoc_id).scalar()
            conLai = tongKeHoach - tongSuDung
            tonLeCuoiCung = db.session.query(KhoLe.ton).filter(KhoLe.hospital_id == current_user.hospital.id,
                                                               KhoLe.thuoc_id == t.thuoc_id).order_by(
                KhoLe.time.desc()).limit(25).first().ton
            nhapLeCuoiCung = db.session.query(KhoLe.nhap).filter(KhoLe.hospital_id == current_user.hospital.id,
                                                                 KhoLe.thuoc_id == t.thuoc_id, KhoLe.nhap > 0).order_by(
                KhoLe.time.desc()).limit(25).first().nhap
            ton_chan = db.session.query(KhoChan.ton).filter(
                KhoChan.hospital_id == current_user.hospital.id,
                KhoChan.thuoc_id == t.thuoc_id).order_by(
                KhoChan.time.desc()).limit(25).first().ton
            soLanDuTru = round(conLai / trungBinhNhapChan, 2)
            tht = TongHopThau(time=ngayThau, thuoc_id=t.thuoc_id, tong_ke_hoach=tongKeHoach,
                              tong_su_dung=tongSuDung, hospital_id=current_user.hospital.id, ton_chan=ton_chan,
                              con_lai=conLai, nhap_le_moi_nhat=nhapLeCuoiCung, ton_le_moi_nhat=tonLeCuoiCung,
                              trung_binh_nhap_chan=trungBinhNhapChan, so_lan_du_tru=soLanDuTru)
            db.session.add(tht)
        db.session.commit()


@app.route('/<url>/phan-tich-su-dung-thuoc')
@login_required
def phan_tich_su_dung_thuoc(url):
    return render_template('phan_tich_su_dung_thuoc.html', user=current_user)


@app.route('/nhap-du-lieu-abc-ven', methods=['POST', 'GET'])
@login_required
def nhap_du_lieu_abc_ven():
    db.session.query(SuDungThuocABCVEN).filter(SuDungThuocABCVEN.hospital_id == current_user.hospital.id).delete()
    if request.method == 'GET':
        tong_hop_abc_ven_du_lieu_co_san(period=1)
    else:
        if 'available_1_time[date_from]' in request.form:
            date_from = request.form.get('available_1_time[date_from]')
            date_to = request.form.get('available_1_time[date_to]')
            tong_hop_abc_ven_du_lieu_co_san(date_from=date_from, date_to=date_to, period=1)
        elif 'available_2_time[date_from1]' in request.form:
            date_from1 = request.form.get('available_2_time[date_from1]')
            date_to1 = request.form.get('available_2_time[date_to1]')
            print(date_from1, date_to1)
            tong_hop_abc_ven_du_lieu_co_san(date_from=date_from1, date_to=date_to1, period=1)
            date_from2 = request.form.get('available_2_time[date_from2]')
            date_to2 = request.form.get('available_2_time[date_to2]')
            print(date_from2, date_to2)
            tong_hop_abc_ven_du_lieu_co_san(date_from=date_from2, date_to=date_to2, period=2)
        elif 'file' in request.files:
            print('here')
            file = request.files.get('file')
            tong_hop_abc_ven_file(file, 1)
        elif 'file1' in request.files:
            file1 = request.files.get('file1')
            tong_hop_abc_ven_file(file1, 1)
            file2 = request.files.get('file2')
            tong_hop_abc_ven_file(file2, 2)
    ketQuaABCVEN = phan_tich_abc_ven(1)
    return jsonify(ketQuaABCVEN=ketQuaABCVEN)


def tong_hop_abc_ven_du_lieu_co_san(**kwargs):
    period = kwargs['period']
    if 'date_from' in kwargs:
        date_from = datetime.strptime(kwargs['date_from'], '%Y-%m-%d').date()
        date_to = datetime.strptime(kwargs['date_to'], '%Y-%m-%d').date()
        dst = db.session.query(func.distinct(ThongKeKho.thuoc_id), Thuoc.name, Thuoc.ven). \
            join(Thuoc, Thuoc.id == ThongKeKho.thuoc_id). \
            filter(ThongKeKho.hospital_id == current_user.hospital.id,
                   ThongKeKho.ngay_nhap_chan >= date_from,
                   ThongKeKho.ngay_nhap_chan <= date_to, ). \
            order_by(Thuoc.name).all()
    else:
        dst = db.session.query(func.distinct(ThongKeKho.thuoc_id), Thuoc.name, Thuoc.ven). \
            join(Thuoc, Thuoc.id == ThongKeKho.thuoc_id). \
            filter(ThongKeKho.hospital_id == current_user.hospital.id). \
            order_by(Thuoc.name).all()
    tong_tien = 0
    tong_so_luong = len(dst)
    for t in dst:
        thuoc = t[1]
        kqtts = KetQuaTrungThau.query.filter(KetQuaTrungThau.thuoc_id == t[0],
                                             KetQuaTrungThau.hospital_id == current_user.hospital.id).all()
        kqtt = kqtts[0]
        hoat_chat = kqtt.hoat_chat.name
        ven = t[2]
        noi_ngoai = kqtt.nuoc_san_xuat.place
        nhom_duoc_ly = kqtt.hoat_chat.nhom_duoc_ly1_bv.name if kqtt.hoat_chat.nhom_duoc_ly1_bv else 'Chưa có nhóm'
        nhom_hoa_duoc = kqtt.hoat_chat.nhom_hoa_duoc_bv.name if kqtt.hoat_chat.nhom_hoa_duoc_bv else 'Chưa có nhóm'
        nhom_thau = kqtt.nhom_thau.name
        if nhom_thau == 'BDG':
            biet_duoc = 'B'
            generic = ''
        else:
            biet_duoc = ''
            generic = 'G'
        don_vi_tinh = kqtt.don_vi_tinh.name
        thanh_tien = 0
        so_luong = 0

        if 'date_from' in kwargs:
            date_from = datetime.strptime(kwargs['date_from'], '%Y-%m-%d').date()
            date_to = datetime.strptime(kwargs['date_to'], '%Y-%m-%d').date()
            tkh = ThongKeKho.query.filter(ThongKeKho.thuoc_id == t[0],
                                          ThongKeKho.ngay_nhap_chan >= date_from,
                                          ThongKeKho.ngay_nhap_chan <= date_to,
                                          ThongKeKho.hospital_id == current_user.hospital.id).all()
        else:
            tkh = ThongKeKho.query.filter(ThongKeKho.thuoc_id == t[0],
                                          ThongKeKho.hospital_id == current_user.hospital.id).all()

        dotthaus = [kq.dot_thau for kq in kqtts]
        sorted_lst_dotthau = sorted(dotthaus, key=lambda DotThau: DotThau.ngayQD, reverse=True)
        for tk in tkh:
            nhap = tk.nhap_chan
            so_luong += nhap
            for dt in sorted_lst_dotthau:
                if tk.ngay_nhap_chan > dt.ngayQD:
                    don_gia = KetQuaTrungThau.query. \
                        filter(KetQuaTrungThau.thuoc_id == t[0], KetQuaTrungThau.dot_thau_id == dt.id,
                               KetQuaTrungThau.hospital_id == current_user.hospital.id). \
                        first().don_gia
                    thanh_tien += nhap * don_gia
                    break
        tong_tien += thanh_tien
        x = SuDungThuocABCVEN(thuoc=thuoc, hoat_chat=hoat_chat, biet_duoc=biet_duoc, generic=generic, ven=ven,
                              noi_ngoai=noi_ngoai, nhom_duoc_ly=nhom_duoc_ly, nhom_hoa_duoc=nhom_hoa_duoc,
                              nhom_thau=nhom_thau, don_vi_tinh=don_vi_tinh, so_luong=so_luong, thanh_tien=thanh_tien,
                              hospital_id=current_user.hospital.id, period=period)
        db.session.add(x)
    db.session.commit()
    phan_loai_abc(tong_tien, tong_so_luong, period)


def tong_hop_abc_ven_file(file, period):
    df = pd.read_excel(file, engine='openpyxl')
    df = df.where(pd.notna(df), None)

    tong_tien = df['Thành tiền'].sum()

    for i in range(df.shape[0]):
        thuoc = df.loc[i, 'Tên thuốc']
        hoat_chat = df.loc[i, 'Hoạt chất']
        biet_duoc = '' if str(df.loc[i, 'Biệt dược']) == 'nan' else df.loc[i, 'Biệt dược']
        generic = '' if str(df.loc[i, 'Generic']) == 'nan' else df.loc[i, 'Generic']
        ven = df.loc[i, 'VEN']
        noi_ngoai = 'Nội' if str(df.loc[i, 'Nước sản xuất']).lower() == 'việt nam' or \
                             str(df.loc[i, 'Nước sản xuất']).lower == 'vn' else 'Ngoại'
        nhom_duoc_ly = '' if str(df.loc[i, 'Nhóm dược lý']) == 'nan' else df.loc[i, 'Nhóm dược lý']
        nhom_hoa_duoc = '' if str(df.loc[i, 'Nhóm hoá dược']) == 'nan' else df.loc[i, 'Nhóm hoá dược']
        nhom_thau = '' if str(df.loc[i, 'Nhóm thầu']) == 'nan' else df.loc[i, 'Nhóm thầu']
        don_vi_tinh = df.loc[i, 'ĐVT']
        so_luong = int(df.loc[i, 'Số lượng'])
        don_gia = int(df.loc[i, 'Đơn giá VAT'])
        thanh_tien = int(df.loc[i, 'Thành tiền'])
        x = SuDungThuocABCVEN(thuoc=thuoc, hoat_chat=hoat_chat, biet_duoc=biet_duoc, generic=generic, ven=ven,
                              noi_ngoai=noi_ngoai, nhom_duoc_ly=nhom_duoc_ly, nhom_hoa_duoc=nhom_hoa_duoc,
                              nhom_thau=nhom_thau, don_vi_tinh=don_vi_tinh, so_luong=so_luong, thanh_tien=thanh_tien,
                              hospital_id=current_user.hospital.id, period=period)
        db.session.add(x)
    db.session.commit()
    phan_loai_abc(tong_tien, df.shape[0], period)


def phan_loai_abc(tong_tien, tong_so_luong, period):
    results = SuDungThuocABCVEN.query.filter(SuDungThuocABCVEN.hospital_id == current_user.hospital.id,
                                             SuDungThuocABCVEN.period == period). \
        order_by(SuDungThuocABCVEN.thanh_tien.desc()).all()
    xep_hang_abc = 0
    tien_tich_luy = 0
    for r in results:
        r.phan_tram_tong_tien = r.thanh_tien / tong_tien
        xep_hang_abc += 1
        r.xep_hang_abc = xep_hang_abc
        tien_tich_luy += r.thanh_tien
        r.phan_tram_tich_luy_tong_tien = tien_tich_luy / tong_tien
        if r.phan_tram_tich_luy_tong_tien <= 0.75:
            r.nhom_abc = 'A'
        elif r.phan_tram_tich_luy_tong_tien <= 0.9:
            r.nhom_abc = 'B'
        else:
            r.nhom_abc = 'C'
        r.gop_abc_ven = r.nhom_abc + r.ven
        if r.gop_abc_ven in ['AV', 'AE', 'AN', 'BV', 'CV']:
            r.abc_ven_matrix = 'I'
        elif r.gop_abc_ven in ['BE', 'BN', 'CE']:
            r.abc_ven_matrix = 'II'
        else:
            r.abc_ven_matrix = 'III'
        r.phan_tram_so_luong = 1 / tong_so_luong
        r.phan_tram_so_luong_tich_luy = xep_hang_abc / tong_so_luong
    db.session.commit()


def phan_tich_abc_ven(period):
    abc = db.session.query(SuDungThuocABCVEN.nhom_abc, func.count(SuDungThuocABCVEN.thuoc),
                           func.sum(SuDungThuocABCVEN.thanh_tien)). \
        filter(SuDungThuocABCVEN.hospital_id == current_user.hospital.id,
               SuDungThuocABCVEN.period == period). \
        group_by(SuDungThuocABCVEN.nhom_abc).order_by(SuDungThuocABCVEN.nhom_abc).all()
    abc = [tuple(r) for r in abc]

    an = db.session.query(SuDungThuocABCVEN.thuoc, SuDungThuocABCVEN.hoat_chat, SuDungThuocABCVEN.ven,
                          SuDungThuocABCVEN.don_vi_tinh, SuDungThuocABCVEN.so_luong, SuDungThuocABCVEN.thanh_tien). \
        filter(SuDungThuocABCVEN.hospital_id == current_user.hospital.id,
               SuDungThuocABCVEN.period == period,
               SuDungThuocABCVEN.nhom_abc == 'A',
               SuDungThuocABCVEN.ven == 'N').all()
    an = [tuple(r) for r in an]

    av = db.session.query(SuDungThuocABCVEN.thuoc, SuDungThuocABCVEN.hoat_chat, SuDungThuocABCVEN.ven,
                          SuDungThuocABCVEN.don_vi_tinh, SuDungThuocABCVEN.so_luong, SuDungThuocABCVEN.thanh_tien). \
        filter(SuDungThuocABCVEN.hospital_id == current_user.hospital.id,
               SuDungThuocABCVEN.period == period,
               SuDungThuocABCVEN.nhom_abc == 'A',
               SuDungThuocABCVEN.ven == 'V').all()
    av = [tuple(r) for r in av]

    ae = db.session.query(SuDungThuocABCVEN.thuoc, SuDungThuocABCVEN.hoat_chat, SuDungThuocABCVEN.ven,
                          SuDungThuocABCVEN.don_vi_tinh, SuDungThuocABCVEN.so_luong, SuDungThuocABCVEN.thanh_tien). \
        filter(SuDungThuocABCVEN.hospital_id == current_user.hospital.id,
               SuDungThuocABCVEN.period == period,
               SuDungThuocABCVEN.nhom_abc == 'A',
               SuDungThuocABCVEN.ven == 'E').all()
    ae = [tuple(r) for r in ae]

    nabc = db.session.query(SuDungThuocABCVEN.abc_ven_matrix, func.count(SuDungThuocABCVEN.abc_ven_matrix),
                            func.sum(SuDungThuocABCVEN.thanh_tien)). \
        filter(SuDungThuocABCVEN.hospital_id == current_user.hospital.id,
               SuDungThuocABCVEN.period == period). \
        group_by(SuDungThuocABCVEN.abc_ven_matrix).order_by(SuDungThuocABCVEN.abc_ven_matrix).all()
    nabc = [tuple(r) for r in nabc]

    bn = db.session.query(SuDungThuocABCVEN.thuoc, SuDungThuocABCVEN.hoat_chat, SuDungThuocABCVEN.ven,
                          SuDungThuocABCVEN.don_vi_tinh, SuDungThuocABCVEN.so_luong, SuDungThuocABCVEN.thanh_tien). \
        filter(SuDungThuocABCVEN.hospital_id == current_user.hospital.id,
               SuDungThuocABCVEN.period == period,
               SuDungThuocABCVEN.nhom_abc == 'B',
               SuDungThuocABCVEN.ven == 'N').all()
    bn = [tuple(r) for r in bn]

    cn = db.session.query(SuDungThuocABCVEN.thuoc, SuDungThuocABCVEN.hoat_chat, SuDungThuocABCVEN.ven,
                          SuDungThuocABCVEN.don_vi_tinh, SuDungThuocABCVEN.so_luong, SuDungThuocABCVEN.thanh_tien). \
        filter(SuDungThuocABCVEN.hospital_id == current_user.hospital.id,
               SuDungThuocABCVEN.period == period,
               SuDungThuocABCVEN.nhom_abc == 'C',
               SuDungThuocABCVEN.ven == 'N').all()
    cn = [tuple(r) for r in cn]

    subquery = db.session.query(SuDungThuocABCVEN.nhom_abc,
                                func.sum(case((SuDungThuocABCVEN.noi_ngoai == 'Nội', 1), else_=0)).label('noi'),
                                func.sum(case((SuDungThuocABCVEN.noi_ngoai == 'Ngoại', 1), else_=0)).label('ngoai'),
                                func.count(SuDungThuocABCVEN.nhom_abc).label('count')). \
        filter(SuDungThuocABCVEN.hospital_id == current_user.hospital.id,
               SuDungThuocABCVEN.period == period). \
        group_by(SuDungThuocABCVEN.nhom_abc, SuDungThuocABCVEN.noi_ngoai). \
        order_by(SuDungThuocABCVEN.nhom_abc).subquery()
    slnoingoai = db.session.query(subquery.c.nhom_abc,
                                  func.sum(subquery.c.noi),
                                  func.sum(subquery.c.ngoai),
                                  func.sum(subquery.c.count)). \
        group_by(subquery.c.nhom_abc).order_by(subquery.c.nhom_abc).all()
    slnoingoai = [tuple(r) for r in slnoingoai]

    subquery = db.session.query(SuDungThuocABCVEN.nhom_abc,
                                func.sum(case((SuDungThuocABCVEN.noi_ngoai == 'Nội', SuDungThuocABCVEN.thanh_tien),
                                              else_=0)).label('noi'),
                                func.sum(case((SuDungThuocABCVEN.noi_ngoai == 'Ngoại', SuDungThuocABCVEN.thanh_tien),
                                              else_=0)).label('ngoai'),
                                func.sum(SuDungThuocABCVEN.thanh_tien).label('thanh_tien')). \
        filter(SuDungThuocABCVEN.hospital_id == current_user.hospital.id,
               SuDungThuocABCVEN.period == period). \
        group_by(SuDungThuocABCVEN.nhom_abc, SuDungThuocABCVEN.noi_ngoai). \
        order_by(SuDungThuocABCVEN.nhom_abc).subquery()
    gtnoingoai = db.session.query(subquery.c.nhom_abc,
                                  func.sum(subquery.c.noi),
                                  func.sum(subquery.c.ngoai),
                                  func.sum(subquery.c.thanh_tien)). \
        group_by(subquery.c.nhom_abc).order_by(subquery.c.nhom_abc).all()
    gtnoingoai = [tuple(r) for r in gtnoingoai]

    ven = db.session.query(SuDungThuocABCVEN.ven, func.count(SuDungThuocABCVEN.ven),
                           func.sum(SuDungThuocABCVEN.thanh_tien)). \
        filter(SuDungThuocABCVEN.hospital_id == current_user.hospital.id,
               SuDungThuocABCVEN.period == period). \
        group_by(SuDungThuocABCVEN.ven). \
        order_by(case(
        (SuDungThuocABCVEN.ven == 'V', 1),
        (SuDungThuocABCVEN.ven == 'E', 2),
        (SuDungThuocABCVEN.ven == 'N', 3),
        else_=4
    )).all()
    ven = [tuple(r) for r in ven]

    nhom_duoc_ly_r = db.session.query(SuDungThuocABCVEN.nhom_duoc_ly, SuDungThuocABCVEN.nhom_abc,
                                      func.count(SuDungThuocABCVEN.thuoc),
                                      func.sum(SuDungThuocABCVEN.thanh_tien)). \
        filter(SuDungThuocABCVEN.hospital_id == current_user.hospital.id,
               SuDungThuocABCVEN.period == period). \
        group_by(SuDungThuocABCVEN.nhom_duoc_ly, SuDungThuocABCVEN.nhom_abc).order_by(SuDungThuocABCVEN.nhom_abc).all()
    nhom_duoc_ly = []
    nhom_duoc_ly_list = []
    for r in nhom_duoc_ly_r:
        nhom_duoc_ly.append(tuple(r))
        if r.nhom_duoc_ly not in nhom_duoc_ly_list:
            nhom_duoc_ly_list.append(r.nhom_duoc_ly)
    nhom_duoc_ly_list = sorted(nhom_duoc_ly_list)

    nhom_hoa_duoc_r = db.session.query(SuDungThuocABCVEN.nhom_hoa_duoc, SuDungThuocABCVEN.nhom_abc,
                                       func.count(SuDungThuocABCVEN.thuoc),
                                       func.sum(SuDungThuocABCVEN.thanh_tien)). \
        filter(SuDungThuocABCVEN.hospital_id == current_user.hospital.id,
               SuDungThuocABCVEN.period == period). \
        group_by(SuDungThuocABCVEN.nhom_hoa_duoc, SuDungThuocABCVEN.nhom_abc).order_by(SuDungThuocABCVEN.nhom_abc).all()
    nhom_hoa_duoc = []
    nhom_hoa_duoc_list = []
    for r in nhom_hoa_duoc_r:
        nhom_hoa_duoc.append(tuple(r))
        if r.nhom_hoa_duoc not in nhom_hoa_duoc_list:
            nhom_hoa_duoc_list.append(r.nhom_hoa_duoc)
    nhom_hoa_duoc_list = sorted(nhom_hoa_duoc_list)

    subquery = db.session.query(SuDungThuocABCVEN.nhom_abc,
                                func.sum(case((SuDungThuocABCVEN.biet_duoc == 'B', 1),
                                              else_=0)).label('biet_duoc'),
                                func.sum(case((SuDungThuocABCVEN.generic == 'G', 1),
                                              else_=0)).label('generic'),
                                func.count(SuDungThuocABCVEN.nhom_abc).label('count')). \
        filter(SuDungThuocABCVEN.hospital_id == current_user.hospital.id,
               SuDungThuocABCVEN.period == period). \
        group_by(SuDungThuocABCVEN.nhom_abc). \
        order_by(SuDungThuocABCVEN.nhom_abc).subquery()
    bdg_generic_sl = db.session.query(subquery.c.nhom_abc,
                                      func.sum(subquery.c.biet_duoc),
                                      func.sum(subquery.c.generic),
                                      func.sum(subquery.c.count)). \
        group_by(subquery.c.nhom_abc).order_by(subquery.c.nhom_abc).all()
    bdg_generic_sl = [tuple(r) for r in bdg_generic_sl]

    subquery = db.session.query(SuDungThuocABCVEN.nhom_abc,
                                func.sum(case((SuDungThuocABCVEN.biet_duoc == 'B', SuDungThuocABCVEN.thanh_tien),
                                              else_=0)).label('biet_duoc'),
                                func.sum(case((SuDungThuocABCVEN.generic == 'G', SuDungThuocABCVEN.thanh_tien),
                                              else_=0)).label('generic'),
                                func.sum(SuDungThuocABCVEN.thanh_tien).label('thanh_tien')). \
        filter(SuDungThuocABCVEN.hospital_id == current_user.hospital.id,
               SuDungThuocABCVEN.period == period). \
        group_by(SuDungThuocABCVEN.nhom_abc). \
        order_by(SuDungThuocABCVEN.nhom_abc).subquery()
    bdg_generic_gt = db.session.query(subquery.c.nhom_abc,
                                      func.sum(subquery.c.biet_duoc),
                                      func.sum(subquery.c.generic),
                                      func.sum(subquery.c.thanh_tien)). \
        group_by(subquery.c.nhom_abc).order_by(subquery.c.nhom_abc).all()
    bdg_generic_gt = [tuple(r) for r in bdg_generic_gt]

    subquery = db.session.query(SuDungThuocABCVEN.nhom_abc,
                                func.sum(case((SuDungThuocABCVEN.nhom_thau == 'Nhóm 1', 1),
                                              else_=0)).label('nhom_1'),
                                func.sum(case((SuDungThuocABCVEN.nhom_thau == 'Nhóm 2', 1),
                                              else_=0)).label('nhom_2'),
                                func.sum(case((SuDungThuocABCVEN.nhom_thau == 'Nhóm 3', 1),
                                              else_=0)).label('nhom_3'),
                                func.sum(case((SuDungThuocABCVEN.nhom_thau == 'Nhóm 4', 1),
                                              else_=0)).label('nhom_4'),
                                func.sum(case((SuDungThuocABCVEN.nhom_thau == 'Nhóm 5', 1),
                                              else_=0)).label('nhom_5'),
                                func.count(SuDungThuocABCVEN.nhom_abc).label('count')). \
        filter(SuDungThuocABCVEN.hospital_id == current_user.hospital.id,
               SuDungThuocABCVEN.period == period,
               SuDungThuocABCVEN.nhom_thau != 'BDG'). \
        group_by(SuDungThuocABCVEN.nhom_abc). \
        order_by(SuDungThuocABCVEN.nhom_abc).subquery()
    nhom_thau_sl = db.session.query(subquery.c.nhom_abc,
                                    func.sum(subquery.c.nhom_1),
                                    func.sum(subquery.c.nhom_2),
                                    func.sum(subquery.c.nhom_3),
                                    func.sum(subquery.c.nhom_4),
                                    func.sum(subquery.c.nhom_5),
                                    func.sum(subquery.c.count)). \
        group_by(subquery.c.nhom_abc).order_by(subquery.c.nhom_abc).all()
    nhom_thau_sl = [tuple(r) for r in nhom_thau_sl]

    subquery = db.session.query(SuDungThuocABCVEN.nhom_abc,
                                func.sum(case((SuDungThuocABCVEN.nhom_thau == 'Nhóm 1', SuDungThuocABCVEN.thanh_tien),
                                              else_=0)).label('nhom_1'),
                                func.sum(case((SuDungThuocABCVEN.nhom_thau == 'Nhóm 2', SuDungThuocABCVEN.thanh_tien),
                                              else_=0)).label('nhom_2'),
                                func.sum(case((SuDungThuocABCVEN.nhom_thau == 'Nhóm 3', SuDungThuocABCVEN.thanh_tien),
                                              else_=0)).label('nhom_3'),
                                func.sum(case((SuDungThuocABCVEN.nhom_thau == 'Nhóm 4', SuDungThuocABCVEN.thanh_tien),
                                              else_=0)).label('nhom_4'),
                                func.sum(case((SuDungThuocABCVEN.nhom_thau == 'Nhóm 5', SuDungThuocABCVEN.thanh_tien),
                                              else_=0)).label('nhom_5'),
                                func.sum(SuDungThuocABCVEN.thanh_tien).label('thanh_tien')). \
        filter(SuDungThuocABCVEN.hospital_id == current_user.hospital.id,
               SuDungThuocABCVEN.period == period,
               SuDungThuocABCVEN.nhom_thau != 'BDG'). \
        group_by(SuDungThuocABCVEN.nhom_abc). \
        order_by(SuDungThuocABCVEN.nhom_abc).subquery()
    nhom_thau_gt = db.session.query(subquery.c.nhom_abc,
                                    func.sum(subquery.c.nhom_1),
                                    func.sum(subquery.c.nhom_2),
                                    func.sum(subquery.c.nhom_3),
                                    func.sum(subquery.c.nhom_4),
                                    func.sum(subquery.c.nhom_5),
                                    func.sum(subquery.c.thanh_tien)). \
        group_by(subquery.c.nhom_abc).order_by(subquery.c.nhom_abc).all()
    nhom_thau_gt = [tuple(r) for r in nhom_thau_gt]

    top_nhom_duoc_ly = db.session.query(SuDungThuocABCVEN.nhom_duoc_ly,
                                        func.count(SuDungThuocABCVEN.thuoc),
                                        func.sum(SuDungThuocABCVEN.thanh_tien).label('thanh_tien')). \
        filter(SuDungThuocABCVEN.hospital_id == current_user.hospital.id,
               SuDungThuocABCVEN.period == period). \
        group_by(SuDungThuocABCVEN.nhom_duoc_ly).order_by(desc('thanh_tien')).all()
    top_nhom_duoc_ly = [tuple(r) for r in top_nhom_duoc_ly]

    top_nhom_hoa_duoc = db.session.query(SuDungThuocABCVEN.nhom_hoa_duoc,
                                         func.count(SuDungThuocABCVEN.thuoc),
                                         func.sum(SuDungThuocABCVEN.thanh_tien).label('thanh_tien')). \
        filter(SuDungThuocABCVEN.hospital_id == current_user.hospital.id,
               SuDungThuocABCVEN.period == period). \
        group_by(SuDungThuocABCVEN.nhom_hoa_duoc).order_by(desc('thanh_tien')).all()
    top_nhom_hoa_duoc = [tuple(r) for r in top_nhom_hoa_duoc]

    subquery = db.session.query(SuDungThuocABCVEN.nhom_abc,
                                func.sum(case((SuDungThuocABCVEN.period == 1, 1), else_=0)).label('t1'),
                                func.sum(case((SuDungThuocABCVEN.period == 2, 1), else_=0)).label('t2'),
                                func.count(SuDungThuocABCVEN.nhom_abc).label('count')). \
        filter(SuDungThuocABCVEN.hospital_id == current_user.hospital.id). \
        group_by(SuDungThuocABCVEN.nhom_abc).order_by(SuDungThuocABCVEN.nhom_abc).subquery()
    abc_2_sl = db.session.query(subquery.c.nhom_abc,
                                func.sum(subquery.c.t1),
                                func.sum(subquery.c.t2),
                                func.sum(subquery.c.count)). \
        group_by(subquery.c.nhom_abc).order_by(subquery.c.nhom_abc).all()
    abc_2_sl = [tuple(r) for r in abc_2_sl]

    subquery = db.session.query(SuDungThuocABCVEN.nhom_abc,
                                func.sum(case((SuDungThuocABCVEN.period == 1, SuDungThuocABCVEN.thanh_tien), else_=0))
                                .label('t1'),
                                func.sum(case((SuDungThuocABCVEN.period == 2, SuDungThuocABCVEN.thanh_tien), else_=0))
                                .label('t2'),
                                func.count(SuDungThuocABCVEN.thanh_tien).label('thanh_tien')). \
        filter(SuDungThuocABCVEN.hospital_id == current_user.hospital.id). \
        group_by(SuDungThuocABCVEN.nhom_abc).order_by(SuDungThuocABCVEN.nhom_abc).subquery()
    abc_2_gt = db.session.query(subquery.c.nhom_abc,
                                func.sum(subquery.c.t1),
                                func.sum(subquery.c.t2),
                                func.sum(subquery.c.thanh_tien)). \
        group_by(subquery.c.nhom_abc).order_by(subquery.c.nhom_abc).all()
    abc_2_gt = [tuple(r) for r in abc_2_gt]

    subquery = db.session.query(SuDungThuocABCVEN.abc_ven_matrix,
                                func.sum(case((SuDungThuocABCVEN.period == 1, 1), else_=0)).label('t1'),
                                func.sum(case((SuDungThuocABCVEN.period == 2, 1), else_=0)).label('t2'),
                                func.count(SuDungThuocABCVEN.abc_ven_matrix).label('count')). \
        filter(SuDungThuocABCVEN.hospital_id == current_user.hospital.id). \
        group_by(SuDungThuocABCVEN.abc_ven_matrix).order_by(SuDungThuocABCVEN.abc_ven_matrix).subquery()
    matran_2_sl = db.session.query(subquery.c.abc_ven_matrix,
                                   func.sum(subquery.c.t1),
                                   func.sum(subquery.c.t2),
                                   func.sum(subquery.c.count)). \
        group_by(subquery.c.abc_ven_matrix).order_by(subquery.c.abc_ven_matrix).all()
    matran_2_sl = [tuple(r) for r in matran_2_sl]

    subquery = db.session.query(SuDungThuocABCVEN.abc_ven_matrix,
                                func.sum(case((SuDungThuocABCVEN.period == 1, SuDungThuocABCVEN.thanh_tien), else_=0))
                                .label('t1'),
                                func.sum(case((SuDungThuocABCVEN.period == 2, SuDungThuocABCVEN.thanh_tien), else_=0))
                                .label('t2'),
                                func.count(SuDungThuocABCVEN.thanh_tien).label('thanh_tien')). \
        filter(SuDungThuocABCVEN.hospital_id == current_user.hospital.id). \
        group_by(SuDungThuocABCVEN.abc_ven_matrix).order_by(SuDungThuocABCVEN.abc_ven_matrix).subquery()
    matran_2_gt = db.session.query(subquery.c.abc_ven_matrix,
                                   func.sum(subquery.c.t1),
                                   func.sum(subquery.c.t2),
                                   func.sum(subquery.c.thanh_tien)). \
        group_by(subquery.c.abc_ven_matrix).order_by(subquery.c.abc_ven_matrix).all()
    matran_2_gt = [tuple(r) for r in matran_2_gt]

    ketQuaABCVEN = {'abc': abc, 'an': an, 'av': av, 'ae': ae, 'nabc': nabc, 'bn': bn, 'cn': cn,
                    'slnoingoai': slnoingoai, 'gtnoingoai': gtnoingoai, 'ven': ven, 'nhom_duoc_ly': nhom_duoc_ly,
                    'nhom_hoa_duoc': nhom_hoa_duoc, 'nhom_hoa_duoc_list': nhom_hoa_duoc_list,
                    'nhom_duoc_ly_list': nhom_duoc_ly_list, 'bdg_generic_sl': bdg_generic_sl,
                    'bdg_generic_gt': bdg_generic_gt, 'top_nhom_hoa_duoc': top_nhom_hoa_duoc,
                    'top_nhom_duoc_ly': top_nhom_duoc_ly, 'nhom_thau_sl': nhom_thau_sl, 'nhom_thau_gt': nhom_thau_gt,
                    'abc_2_sl': abc_2_sl, 'abc_2_gt': abc_2_gt, 'matran_2_sl': matran_2_sl,
                    'matran_2_gt': matran_2_gt}
    return ketQuaABCVEN


@app.route('/<url>/xay-dung-danh-muc')
@login_required
def xay_dung_danh_muc(url):
    return render_template('xay_dung_danh_muc.html', user=current_user)


@app.route('/date-xay-dung-danh-muc', methods=['POST'])
@login_required
def date_xddm():
    date_from = datetime.strptime(request.form['date_from'], "%Y-%m-%d")
    date_to = datetime.strptime(request.form['date_to'], "%Y-%m-%d")

    results = KetQuaTrungThau.query. \
        join(DotThau, DotThau.id == KetQuaTrungThau.dot_thau_id). \
        filter(KetQuaTrungThau.hospital_id == current_user.hospital.id,
               DotThau.end.is_(None),
               DotThau.ngayQD >= date_from,
               DotThau.ngayQD <= date_to).all()

    ketQuaXDDM = get_data_XDDM(results)
    return jsonify(ketQuaXDDM=ketQuaXDDM)


@app.route('/xay-dung-danh-muc-data', methods=['GET'])
def xay_dung_danh_muc_data():
    results = KetQuaTrungThau.query.filter_by(hospital=current_user.hospital).all()
    ketQuaXDDM = get_data_XDDM(results)
    return jsonify(ketQuaXDDM=ketQuaXDDM)


def get_data_XDDM(results):
    bao_cao_dict = []
    for r in results:
        ven = r.thuoc.ven
        t = SuDungThuocABCVEN.query.filter(SuDungThuocABCVEN.thuoc == r.thuoc.name,
                                           SuDungThuocABCVEN.hospital_id == current_user.hospital.id).first()
        abc = t.nhom_abc if t else ''
        tht = TongHopThau.query.filter_by(hospital_id=current_user.hospital_id, thuoc_id=r.thuoc.id).first()
        if tht:
            tong_su_dung = tht.tong_su_dung
        else:
            tong_su_dung = 0
        hc = r.hoat_chat
        ndl1 = hc.nhom_duoc_ly1_bv
        ndl2 = hc.nhom_duoc_ly2_bv
        nhd = hc.nhom_hoa_duoc_bv
        atc_id = hc.atc_id
        bao_cao_dict.append(
            [r.dot_thau.code, r.dot_thau.ngayQD.strftime("%Y-%m-%d"), r.thuoc.name, hc.name, r.ham_luong.name,
             r.thuoc.sdk, r.duong_dung.name, r.dang_bao_che.name,
             r.quy_cach_dong_goi.name,
             r.don_vi_tinh.name, r.co_so_san_xuat.name, r.nuoc_san_xuat.place,
             r.nha_thau.name, r.nhom_thau.name,
             r.so_luong, r.don_gia, r.thanh_tien,
             ndl1.name if ndl1 else '',
             ndl2.name if ndl2 else '',
             nhd.name if nhd else '',
             abc, ven, tong_su_dung,
             str(atc_id) + 'A' if atc_id else str(hc.id), r.id])
    hoatchats = db.session.query(func.distinct(HoatChat.code), ATC.id, ATC.name, HoatChat.id, HoatChat.name). \
        select_from(HoatChat). \
        join(ATC, ATC.id == HoatChat.atc_id, isouter=True). \
        filter(HoatChat.hospital_id == current_user.hospital_id). \
        order_by(HoatChat.name).all()
    hoatchatlist = []
    for hc in hoatchats:
        if hc[1]:
            hoatchatlist.append({'id': str(hc[1]) + 'A', 'name': hc[2]})
        else:
            hoatchatlist.append({'id': str(hc[3]), 'name': hc[4]})
    ndls = NhomDuocLy1BV.query.filter_by(hospital_id=current_user.hospital.id).order_by(NhomDuocLy1BV.name).all()
    ndllist = [{'id': h.id, 'name': h.name} for h in ndls]
    ndl2s = NhomDuocLy2BV.query.filter_by(hospital_id=current_user.hospital.id).order_by(NhomDuocLy2BV.name).all()
    ndllist2 = [{'id': h.id, 'name': h.name} for h in ndl2s]
    nhds = NhomHoaDuocBV.query.filter_by(hospital_id=current_user.hospital.id).order_by(NhomHoaDuocBV.name).all()
    nhdlist = [{'id': h.id, 'name': h.name} for h in nhds]
    ketQuaXDDM = {'danhmuc': bao_cao_dict, 'hoatchatlist': hoatchatlist, 'ndllist': ndllist,
                  'nhdlist': nhdlist, 'ndllist2': ndllist2}
    return ketQuaXDDM


@app.route('/')
@login_required
def index():
    return redirect(url_for('user', url=current_user.hospital.url))


@app.route('/<url>')
@login_required
def user(url):
    return render_template('base.html', user=current_user)
