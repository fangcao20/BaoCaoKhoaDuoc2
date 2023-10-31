var selectedRows = [];
var changedRows = [];
var tabs = document.querySelectorAll('.col-2 a');
tabs.forEach(function(tab) {
    $(tab).on('click', function() {
        selectedRows = [];
    })
})
function show_danh_muc(danh_muc_dict, selector) {
    var html = '';
    var i = 1;
    for (const r of danh_muc_dict) {
        html += `<tr>
            <th>${i}</td>
            <td>${r.name}</td>
            <td style="display: none">${r.id}</td>
        </tr>`
        i++;
    }
    var table = document.querySelector(selector);
    table.innerHTML = html;
    select_row(table);
}

$.get('/get-danh-muc'
).done (function (response) {
    var danh_muc = response.danh_muc;
    if (danh_muc) {
        show_danh_muc(danh_muc.ham_luong_dict, '#ham_luong_c > div:nth-child(2) > table > tbody');
        show_danh_muc(danh_muc.nhom_duoc_ly_dict, '#nhom_duoc_ly_c > div:nth-child(2) > table > tbody');
        show_danh_muc(danh_muc.nhom_hoa_duoc_dict, '#nhom_hoa_duoc_c > div:nth-child(2) > table > tbody');
        show_danh_muc(danh_muc.duong_dung_dict, '#duong_dung_c > div:nth-child(2) > table > tbody');
        show_danh_muc(danh_muc.dang_bao_che_dict, '#dang_bao_che_c > div:nth-child(2) > table > tbody');
        show_danh_muc(danh_muc.quy_cach_dong_goi_dict, '#quy_cach_dong_goi_c > div:nth-child(2) > table > tbody');
        show_danh_muc(danh_muc.don_vi_tinh_dict, '#don_vi_tinh_c > div:nth-child(2) > table > tbody');
        show_danh_muc(danh_muc.co_so_san_xuat_dict, '#co_so_san_xuat_c > div:nth-child(2) > table > tbody');
        show_danh_muc(danh_muc.nhom_thau_dict, '#nhom_thau_c > div:nth-child(1) > table > tbody');
        show_danh_muc(danh_muc.nha_thau_dict, '#nha_thau_c > div:nth-child(2) > table > tbody');
        show_thuoc(danh_muc.thuoc_dict);
        show_hoat_chat(danh_muc.hoat_chat_dict);
        show_nuoc_san_xuat(danh_muc.nuoc_san_xuat_dict);
        $('#hoat_chat_tt20')[0].innerHTML = select_nhom(danh_muc.hoat_chat_tt20_dict);
        $('#hoat_chat_syt')[0].innerHTML = select_nhom(danh_muc.hoat_chat_syt_dict);
        $('#select_nhom_duoc_ly')[0].innerHTML = select_nhom(danh_muc.nhom_duoc_ly_dict);
        $('#select_nhom_hoa_duoc')[0].innerHTML = select_nhom(danh_muc.nhom_hoa_duoc_dict);
    }
}).fail(function() {
    console.log('Lỗi: Không thể kết nối với máy chủ.');
})

function show_thuoc(danh_muc_dict) {
    var html = '';
    var i = 1
    for (const r of danh_muc_dict) {
        html += `<tr>
            <th>${i}</td>
            <th>${r.code}</td>
            <th>${r.codeBV}</td>
            <td>${r.name}</td>
            <td>${r.sdk}</td>
            <td style="display: none">${r.id}</td>
        </tr>`
        i++;
    }
    document.querySelector('#thuoc_c > div:nth-child(2) > table > tbody').innerHTML = html;
    select_row(document.querySelector('#thuoc_c > div:nth-child(2) > table > tbody'));
}

function select_nhom(danh_muc_dict) {
    var html = '<option value="">Chọn</option>';
    for (const r of danh_muc_dict) {
        html += `<option value="${r.id}">${r.name}</option>`;
    }
    return html;
}

function show_hoat_chat(danh_muc_dict) {
    var html = '';
    var i = 1
    for (const r of danh_muc_dict) {
        html += `<tr>
            <th>${i}</td>
            <th style="width: 120px">${r.code}</td>
            <td>${r.name}</td>
            <td>${r.hoat_chat_tt20}</td>
            <td>${r.hoat_chat_syt}</td>
            <td>${r.nhom_duoc_ly}</td>
            <td>${r.nhom_hoa_duoc}</td>
            <td style="display: none">${r.id}</td>
        </tr>`
        i++;
    }
    document.querySelector('#hoat_chat_c > div:nth-child(3) > table > tbody').innerHTML = html;
    select_row(document.querySelector('#hoat_chat_c > div:nth-child(3) > table > tbody'));
}

function show_nuoc_san_xuat(danh_muc_dict) {
    var html = '';
    var i = 1
    for (const r of danh_muc_dict) {
        html += `<tr>
            <th>${i}</td>
            <td>${r.name}</td>
            <td>${r.place}</td>
            <td style="display: none">${r.id}</td>
        </tr>`
        i++;
    }
    document.querySelector('#nuoc_san_xuat_c > div:nth-child(2) > table > tbody').innerHTML = html;
    select_row(document.querySelector('#nuoc_san_xuat_c > div:nth-child(2) > table > tbody'));
}

function select_row(table) {
    selectedRows = [];
    changedRows = [];
    var tableRows = table.querySelectorAll('tr');
    tableRows.forEach(function(row) {
        row.addEventListener('click', function() {
            var selectedTab = document.querySelector('[aria-selected="true"]');
            var danh_muc = selectedTab.id;
            if (this.cells.length === 8) {
                $('#search_hoat_chat')[0].value = row.cells[2].innerText;
                changeSelectByText('hoat_chat_tt20', row.cells[3].innerText);
                changeSelectByText('hoat_chat_syt', row.cells[4].innerText);
                changeSelectByText('select_nhom_duoc_ly', row.cells[5].innerText);
                changeSelectByText('select_nhom_hoa_duoc', row.cells[6].innerText);
            } else if (danh_muc == 'nhom_duoc_ly') {
                $('#searchNDL')[0].value = row.cells[1].innerText;
            } else if (danh_muc == 'nhom_hoa_duoc') {
                $('#searchNHD')[0].value = row.cells[1].innerText;
            }

            if (!selectedRows.includes(this)) {
                selectedRows.push(this);
                this.classList.add('table-primary');
            } else {
                selectedRows = selectedRows.filter(item => item !== this);
                this.classList.remove('table-primary');
                if (this.cells.length === 8) {
                    $('#search_hoat_chat')[0].value = '';
                    $('#hoat_chat_tt20').val('').trigger('change');
                    $('#hoat_chat_syt').val('').trigger('change');
                    $('#select_nhom_duoc_ly').val('').trigger('change');
                    $('#select_nhom_hoa_duoc').val('').trigger('change');
                } else if (danh_muc == 'nhom_duoc_ly') {
                    $('#searchNDL')[0].value = '';
                } else if (danh_muc == 'nhom_hoa_duoc') {
                    $('#searchNHD')[0].value = '';
                }
            }
        });

        var cells = Array.from(row.querySelectorAll('td'));
        if (cells.length === 6) {
            var hoat_chat = cells[0];
            var hoat_chat_id = cells[cells.length - 1];
            cells = [];
            cells.push(hoat_chat);
            cells.push(hoat_chat_id);
        }
        cells.forEach(function(cell) {
            cell.addEventListener('dblclick', function() {
                cell.setAttribute('contenteditable', 'true');
                cell.setAttribute('data-original-content', cell.innerText);
                cell.addEventListener('keydown', function(e) {
                    if (e.key === "Enter") {
                        cell.blur();
                    }
                });
            });

            cell.addEventListener('blur', function() {
                // Khi ô mất trạng thái chỉnh sửa (blur), kiểm tra nội dung có thay đổi không
                var originalContent = cell.getAttribute('data-original-content');
                var currentContent = cell.innerText;

                if (originalContent !== currentContent) {
                    var contents = [];
                    for (const c of cells) {
                        contents.push(c.innerText);
                    }
                    changedRows.push(contents);
                }
                // Xóa thuộc tính data-original-content
                cell.removeAttribute('data-original-content');
            });
        });
    });
}

function gopGiaTri() {
    var selectedTab = document.querySelector('[aria-selected="true"]');
    var danh_muc = selectedTab.id;
    var id_list = [];
    for (const r of selectedRows) {
        id_list.push(r.cells[r.cells.length - 1].innerText);
    }

    $.post('/gop-gia-tri', {'danh_muc': danh_muc, 'id_list': id_list}
    ).done(function(response) {
        var danh_muc_dict = response.danh_muc_dict;
        if (danh_muc_dict) {
            if (danh_muc == "thuoc") {
                show_thuoc(danh_muc_dict);
            }
            else if (danh_muc == "hoat_chat") {
                show_hoat_chat(danh_muc_dict);
            }
            else if (danh_muc == "nuoc_san_xuat") {
                show_nuoc_san_xuat(danh_muc_dict);
            }
            else {
                show_danh_muc(danh_muc_dict, `#${danh_muc}_c > div:nth-child(2) > table > tbody`);
            }
        }
    }).fail(function() {
        console.log('Lỗi: Không thể kết nối với máy chủ.');
    })
}

function luuThayDoi() {
    var selectedTab = document.querySelector('[aria-selected="true"]');
    var danh_muc = selectedTab.id;
    var data = {
        'danh_muc': danh_muc,
        'changed_data': changedRows
    };
    $.ajax({
        url: '/luu-thay-doi',
        type: 'POST',
        data: JSON.stringify(data),
        success: function (response) {
            var danh_muc_dict = response.danh_muc_dict;
            if (danh_muc_dict) {
                if (danh_muc == "thuoc") {
                    show_thuoc(danh_muc_dict);
                }
                else if (danh_muc == "hoat_chat") {
                    show_hoat_chat(danh_muc_dict);
                }
                else if (danh_muc == "nuoc_san_xuat") {
                    show_nuoc_san_xuat(danh_muc_dict);
                }
                else {
                    show_danh_muc(danh_muc_dict, `#${danh_muc}_c > div:nth-child(2) > table > tbody`);
                }
            }
        },
        cache: false,
        contentType: 'application/json',
        processData: false
    });
}

function changeSelectByText(selectId, desiredText) {
    if (desiredText === '') {
        desiredText = 'Chọn';
    }
    var select = document.getElementById(selectId);
    for (var i = 0; i < select.options.length; i++) {
        if (select.options[i].text === desiredText) {
            var value = select.options[i].value;
            $('#'+selectId).val(value).trigger('change');
            return;
        }
    }
}

function selectHoatChatTT20() {
    var hoat_chat_tt20_id = $('#hoat_chat_tt20')[0].value;
    if (hoat_chat_tt20_id != '') {
        $.post('/get-nhom-dl-hd', {'id': hoat_chat_tt20_id
            }).done(function (response) {
                var nhom_dl_hd = response.nhom_dl_hd;
                if (nhom_dl_hd) {
                    changeSelectByText('select_nhom_duoc_ly', nhom_dl_hd.nhom_duoc_ly);
                    changeSelectByText('select_nhom_hoa_duoc', nhom_dl_hd.nhom_hoa_duoc);
                }
            }).fail(function() {
                console.log('Lỗi: Không thể kết nối với máy chủ.');
            })
    }
}

function luu_hoat_chat() {
    var data = {
        'hoat_chat': $('#search_hoat_chat')[0].value,
        'nhom_duoc_ly_bv_id': $('#select_nhom_duoc_ly')[0].value,
        'nhom_hoa_duoc_bv_id': $('#select_nhom_hoa_duoc')[0].value,
        'hoat_chat_tt20_id': $('#hoat_chat_tt20')[0].value,
        'hoat_chat_syt_id': $('#hoat_chat_syt')[0].value,
    };
    $.post('/luu-hoat-chat', data
    ).done(function (response) {
        var danh_muc_hoat_chat = response.danh_muc_hoat_chat;
        if (danh_muc_hoat_chat) {
            show_hoat_chat(danh_muc_hoat_chat);
        }
    }).fail(function() {
        console.log('Lỗi: Không thể kết nối với máy chủ.');
    })
}

function searchTable(input) {
    var filter, table, tr, td, i, txtValue;
    filter = input.value.toUpperCase();
    table = input.parentElement.parentElement.querySelector('table');
    tr = table.getElementsByTagName("tr");

    for (i = 0; i < tr.length; i++) {
        td = tr[i].getElementsByTagName("td")[0];
        if (td) {
          txtValue = td.textContent || td.innerText;
          if (txtValue.toUpperCase().indexOf(filter) > -1) {
            tr[i].style.display = "";
          } else {
            tr[i].style.display = "none";
          }
        }
    }
}

function them_nhom(btn) {
    var input = btn.parentElement.previousElementSibling;
    var selectedTab = document.querySelector('[aria-selected="true"]');
    var danh_muc = selectedTab.id;
    var content = input.value;
    var table = btn.parentElement.parentElement.parentElement.querySelector('table');
    for (const r of table.rows) {
        if (r.cells[1].innerText == content) {
            alert(`Đã có nhóm ${content}!`);
            return;
        }
    }
    $.post('/them-nhom', {'danh_muc': danh_muc, 'content': content
    }).done(function(response) {
        var danh_muc_dict = response.danh_muc_dict;
        if (danh_muc_dict) {
                show_danh_muc(danh_muc_dict, `#${danh_muc}_c > div:nth-child(2) > table > tbody`);
        }
    }).fail(function() {
        console.log('Lỗi: Không thể kết nối với máy chủ.');
    })
}

function xoa_nhom() {
    var selectedTab = document.querySelector('[aria-selected="true"]');
    var danh_muc = selectedTab.id;
    var row = selectedRows[selectedRows.length - 1];
    var id = row.cells[row.cells.length - 1].innerText;
    $.post('/xoa-nhom', {'danh_muc': danh_muc, 'id': id
    }).done(function(response) {
        var danh_muc_dict = response.danh_muc_dict;
        if (danh_muc_dict) {
                show_danh_muc(danh_muc_dict, `#${danh_muc}_c > div:nth-child(2) > table > tbody`);
        }
    }).fail(function() {
        console.log('Lỗi: Không thể kết nối với máy chủ.');
    })
}