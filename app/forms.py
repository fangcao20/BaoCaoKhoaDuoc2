from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, SelectField
from wtforms.validators import DataRequired, EqualTo


class LoginForms(FlaskForm):
    username = StringField('Tên đăng nhập', validators=[DataRequired()])
    password = PasswordField('Mật khẩu', validators=[DataRequired()])
    submit = SubmitField('Đăng nhập')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Mật khẩu cũ', validators=[DataRequired()])
    new_password = PasswordField('Mật khẩu mới', validators=[DataRequired()])
    new_password2 = PasswordField('Xác nhận mật khẩu', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Lưu')


class ResetPasswordRequestForm(FlaskForm):
    username = StringField('Tên đăng nhập', validators=[DataRequired()])
    submit = SubmitField('Gửi')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Mật khẩu', validators=[DataRequired()])
    password2 = PasswordField('Xác nhận mật khẩu', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Lưu')


class InputDotThau(FlaskForm):
    code = StringField('Mã đợt thầu', validators=[DataRequired()])
    name = StringField('Tên đợt thầu', validators=[DataRequired()])
    phase = StringField('Giai đoạn', validators=[DataRequired()])
    formality = SelectField('Hình thức đấu thầu',
                            choices=[('rr', 'Đấu thầu rộng rãi'), ('hc', 'Đấu thầu hạn chế'), ('cd', 'Chỉ định thầu'),
                                     ('ch', 'Chào hàng cạnh tranh'), ('ms', 'Mua sắm trực tiếp'),
                                     ('tth', 'Tự thực hiện')],
                            validators=[DataRequired()])
    soQD = StringField('Số quyết định', validators=[DataRequired()])
    ngayQD = DateField('Ngày quyết định', validators=[DataRequired()])
    ngayHH = DateField('Ngày hết hạn', validators=[DataRequired()])
    note = StringField('Ghi chú')
    submit = SubmitField('Thêm mới')
    update = SubmitField('Cập nhật')
    delete = SubmitField('Xoá')
    id = StringField('ID')
